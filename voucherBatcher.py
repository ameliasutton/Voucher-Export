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
        print("Creating Requester")
        self.requester = api.requestObject(config["url"], config["tenant"])
        self.requester.setToken(config["token"])
        self.requester.testToken()
        self.updateConfig()

        print("Creating Session")
        # Creates the session
        self.batchGroup = config["batchGroup"]
        headers = {'Content-Type': 'application/json',
                   'x-okapi-tenant': config["tenant"],
                   'x-okapi-token': self.requester.token,
                   'Accept': 'application/json'}
        self.session = requests.Session()
        self.session.headers = headers
        self.session.params = {"limit": "1000"}

        print("Getting Batch Group ID")
        batchGroupResponse = self.requester.singleRequest("batch-groups?query=name=\"" + self.batchGroup + "\"", self.session)
        batchGroupsJson = batchGroupResponse["batchGroups"]
        batchGroupJson = batchGroupsJson[0]
        self.batchGroupId = batchGroupJson["id"]
        print("Getting Batch ID")
        self.batchId = self.getBatchId()
        print("Getting Voucher ID")
        self.voucherId = self.getVoucherId()

    # Updates config file with currently selected Start Date, End Date, and API Token
    def updateConfig(self):
        with open(self.configFileName, "r") as readConf:
            configJson = json.load(readConf)
            configJson["batchEndDate"] = self.batchEndDate
            configJson["batchStartDate"] = self.batchStartDate
            configJson["token"] = self.requester.token
        with open(self.configFileName, "w") as writeConf:
            writeConf.write(json.dumps(configJson, indent=4))

    # Returns the Batch ID associated with the selected Dates
    # TODO: Verify that Batch ID exists first
    def getBatchId(self):
        batch = self.requester.singleRequest("batch-voucher/batch-voucher-exports?query=(batchGroupId==\""
                                             + self.batchGroupId + "\" AND start==\"" + self.batchStartDate
                                             + "\" AND end==\"" + self.batchEndDate + "\")&sort(-metadata.updatedDate)",
                                             self.session)["batchVoucherExports"][0]["id"]
        return batch

    # Returns the Voucher ID associated with the selected Batch if it exists
    # Returns None otherwise
    # TODO: Verify that Batch ID exists first
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

    # Moves Start and End Dates to point towards the next Batch
    def selectNextBatch(self):
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

    # Moves Start and End Dates to point towards the previous Batch
    def selectPreviousBatch(self):
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

    # Returns a dict of the Batched Vouchers
    def retrieveVoucher(self):
        self.voucherId = self.getVoucherId()
        if self.voucherId:
            returned = self.requester.singleRequest("batch-voucher/batch-vouchers/" + self.voucherId, self.session)
            return returned
        else:
            return

    # Starts a new voucher batching process in FOLIO
    # TODO Create this Function
    def triggerBatch(self):
        print(self)
        print("Not Implemented Yet")


if __name__ == "__main__":
    configName = "config.json"
    retriever = VoucherBatchRetriever(configName)
