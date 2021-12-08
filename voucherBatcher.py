import requests
import json
import folio_api_aneslin as api


class VoucherBatchRetriever:
    def __init__(self, config):
        self.configFileName = config
        with open(config, "r") as c:
            config = json.load(c)

        self.batchStartDate = config["batchStartDate"]
        self.batchEndDate = config["batchEndDate"]

        # Creates the requester object
        self.requester = api.requestObject(config["url"], config["tenant"])
        self.requester.setToken(config["token"])
        self.requester.testToken()
        self.updateConfig()

        # Creates the session object
        self.batchGroup = config["batchGroup"]
        headers = {'Content-Type': 'application/json',
                   'x-okapi-tenant': config["tenant"],
                   'x-okapi-token': self.requester.token,
                   'Accept': 'application/json'}
        self.session = requests.Session()
        self.session.headers = headers
        self.session.params = {"limit": "1000"}


        self.batchGroupId = self.requester.singleRequest("batch-groups?query=name=" + self.batchGroup, self.session)["batchGroups"][0]["id"]
        self.batchId = self.getBatchId()
        self.voucherId = self.getVoucherId()

    def updateConfig(self):
        with open(self.configFileName, "r") as readConf:
            configJson = json.load(readConf)
            configJson["batchEndDate"] = self.batchEndDate
            configJson["batchStartDate"] = self.batchStartDate
            configJson["token"] = self.requester.token
        with open(self.configFileName, "w") as writeConf:
            writeConf.write(json.dumps(configJson, indent=4))

    def getBatchId(self):
        batch = self.requester.singleRequest("batch-voucher/batch-voucher-exports?query=(batchGroupId==\""
                                             + self.batchGroupId + "\" AND start==\"" + self.batchStartDate
                                             + "\" AND end==\"" + self.batchEndDate + "\")&sort(-metadata.updatedDate)",
                                             self.session)["batchVoucherExports"][0]["id"]
        return batch

    def getVoucherId(self):
        batch = self.requester.singleRequest("batch-voucher/batch-voucher-exports?query=(batchGroupId==\""
                                             + self.batchGroupId + "\" AND start==\"" + self.batchStartDate
                                             + "\" AND end==\"" + self.batchEndDate + "\")&sort(-metadata.updatedDate)",
                                             self.session)["batchVoucherExports"][0]
        if batch["status"] == "Error":
            print("Selected Batch encountered an error: " + batch["message"] + " no vouchers were created.")
            self.voucherId = None
        elif batch["status"] == "Pending":
            print("Selected Batch process is still running.")
            self.voucherId = None
        else:
            self.voucherId = batch["batchVoucherId"]
        return self.voucherId

    def selectNextVoucher(self):
        batch = self.requester.singleRequest("batch-voucher/batch-voucher-exports?query=(batchGroupId==\""
                                             + self.batchGroupId + "\" AND start==\"" + self.batchEndDate
                                             + "\")&sort(-metadata.updatedDate)", self.session)
        if batch["totalRecords"] == 0:
            print("Most recent batch already selected")
        else:
            self.batchId = batch["batchVoucherExports"][0]["id"]
            self.batchEndDate = batch["batchVoucherExports"][0]["end"][0:23] + "*"
            self.batchStartDate = batch["batchVoucherExports"][0]["start"][0:23] + "*"
            print("Next Batch Selected\n"
                  "Run Date: " + self.batchEndDate)
        return

    def selectPreviousVoucher(self):
        batch = self.requester.singleRequest("batch-voucher/batch-voucher-exports?query=(batchGroupId==\""
                                             + self.batchGroupId + "\" AND end==\"" + self.batchStartDate
                                             + "\")&sort(-metadata.updatedDate)", self.session)
        if batch["totalRecords"] == 0:
            print("Oldest Batch already selected")
        else:
            self.batchId = batch["batchVoucherExports"][0]["id"]
            self.batchEndDate = batch["batchVoucherExports"][0]["end"][0:23] + "*"
            self.batchStartDate = batch["batchVoucherExports"][0]["start"][0:23] + "*"
            print("Previous Batch Selected\n"
                  "Run Date: " + self.batchEndDate)
        return

    def retrieveVoucher(self):
        self.voucherId = self.getVoucherId()
        if self.voucherId:
            returned = self.requester.singleRequest("batch-voucher/batch-vouchers/" + self.voucherId, self.session)
            return returned
        else:
            return


if __name__ == "__main__":
    configName = "config.json"
    retriever = VoucherBatchRetriever(configName)
