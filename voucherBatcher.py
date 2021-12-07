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
            writeConf.write(json.dumps(configJson))

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
            print("Batch encountered an error: " + batch["message"] + " no vouchers were created.")
            self.voucherId = None
        elif batch["status"] == "Pending":
            print("Batch process is still running.")
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
        return

    def selectPreviousVoucher(self):
        batch = self.requester.singleRequest("batch-voucher/batch-voucher-exports?query=(batchGroupId==\""
                                             + self.batchGroupId + "\" AND end==\"" + self.batchStartDate
                                             + "\")&sort(-metadata.updatedDate)", self.session)
        if batch["totalRecords"] == 0:
            print("Oldest batch already selected")
        else:
            self.batchId = batch["batchVoucherExports"][0]["id"]
            self.batchEndDate = batch["batchVoucherExports"][0]["end"][0:23] + "*"
            self.batchStartDate = batch["batchVoucherExports"][0]["start"][0:23] + "*"
        return

    def retrieveVoucher(self):
        if self.voucherId:
            returned = self.requester.singleRequest("batch-voucher/batch-vouchers/" + self.voucherId, self.session)
            return returned
        else:
            print("Current Batch ")
            return


if __name__ == "__main__":
    configName = "config.json"

    input()
    retriever = VoucherBatchRetriever(configName)
    retriever.selectPreviousVoucher()
    print("Voucher Id: " + str(retriever.getVoucherId()))
    print(retriever.retrieveVoucher())

#test Commit