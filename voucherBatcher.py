import requests
import json
import folio_api_aneslin as api
import datetime


class VoucherBatchRetriever:
    def __init__(self, config):
        self.configFileName = config
        try:
            with open(config, "r") as c:
                config = json.load(c)
        except FileNotFoundError:
            exit(f"Config File \"{config}\" Not Found")
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
        self.batchGroupId = self.getBatchGroupId()
        print("Batch Group ID Retrieved")
        print("Getting Batch ID")
        self.batchId = self.getBatchId()
        print("Batch ID Retrieved")
        print("Getting Voucher ID")
        self.voucherId = self.getVoucherId()

    # Updates config file with currently selected Start Date, End Date, and API Token
    def updateConfig(self):
        with open(self.configFileName, "r") as readConf:
            config = json.load(readConf)
            config["batchEndDate"] = self.batchEndDate
            config["batchStartDate"] = self.batchStartDate
            config["token"] = self.requester.token
        with open(self.configFileName, "w") as writeConf:
            writeConf.write(json.dumps(config, indent=4))

    # Returns Batch Group ID matching Batch Group Name provided in config file
    def getBatchGroupId(self):
        response = self.requester.singleGet(f"batch-groups?query=name=\"{self.batchGroup}\"", self.session)
        if response["totalRecords"] == 0:
            exit("Batch group name did not match any in FOLIO")
        elif response["totalRecords"] > 1:
            exit("Batch group name matched with more than one batch group in FOLIO")
        print(response["batchGroups"][0]["id"])
        return response["batchGroups"][0]["id"]

    # Returns the Batch ID associated with the selected Dates
    def getBatchId(self):
        batch = self.requester.singleGet(f"batch-voucher/batch-voucher-exports?query=(batchGroupId==\""
                                         f"{self.batchGroupId}\" AND start==\"{self.batchStartDate}\" AND end==\""
                                         f"{self.batchEndDate}\")", self.session)
        if batch["totalRecords"] == 0:
            print("Selecting Most Recent Batch Date...")
            self.selectMostRecentBatch()
            return
        batch = batch["batchVoucherExports"][0]["id"]
        return batch

    # Returns the Voucher ID associated with the selected Batch if it exists
    # Returns None otherwise
    def getVoucherId(self):
        batch = self.requester.singleGet(f"batch-voucher/batch-voucher-exports?query=(batchGroupId==\""
                                         f"{self.batchGroupId}\" AND start==\"{self.batchStartDate}\" AND end==\""
                                         f"{self.batchEndDate}\")", self.session)["batchVoucherExports"][0]
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
        batch = self.requester.singleGet(f"batch-voucher/batch-voucher-exports?query=batchGroupId==\""
                                         f"{self.batchGroupId}\" AND start==\"{self.batchEndDate}\"", self.session)
        if batch["totalRecords"] == 0:
            print("Most recent batch already selected")
        else:
            self.batchId = batch["batchVoucherExports"][0]["id"]
            self.batchEndDate = batch["batchVoucherExports"][0]["end"][0:23] + "*"
            self.batchStartDate = batch["batchVoucherExports"][0]["start"][0:23] + "*"
            print("Next Batch Selected\n"
                  "Run Date: " + self.batchEndDate)
            self.updateConfig()
        return

    # Moves Start and End Dates to point towards the most recently run Batch
    def selectMostRecentBatch(self):
        batch = self.requester.singleGet(f"batch-voucher/batch-voucher-exports?query=batchGroupId==\""
                                         f"{self.batchGroupId}\" sortby end/sort.descending", self.session)
        if batch["totalRecords"] == 0:
            print(f"No Batches Found With Batch Group: {self.batchGroup}")
        batch = batch["batchVoucherExports"][0]
        self.batchId = batch["id"]
        self.batchEndDate = batch["end"][0:23] + "*"
        self.batchStartDate = batch["start"][0:23] + "*"
        print("Most Recent Batch Selected\n"
              "Run Date: " + self.batchEndDate)
        self.updateConfig()

    # Moves Start and End Dates to point towards the previous Batch
    def selectPreviousBatch(self):
        batch = self.requester.singleGet(f"batch-voucher/batch-voucher-exports?query=batchGroupId==\""
                                         f"{self.batchGroupId}\" AND end==\"{self.batchStartDate}\"", self.session)
        if batch["totalRecords"] == 0:
            print("Oldest Batch already selected")
        else:
            self.batchId = batch["batchVoucherExports"][0]["id"]
            self.batchEndDate = batch["batchVoucherExports"][0]["end"][0:23] + "*"
            self.batchStartDate = batch["batchVoucherExports"][0]["start"][0:23] + "*"
            print("Previous Batch Selected\n"
                  "Run Date: " + self.batchEndDate)
            self.updateConfig()
        return

    # Returns a dict of the Batched Vouchers
    def retrieveVoucher(self):
        self.voucherId = self.getVoucherId()
        if self.voucherId:
            returned = self.requester.singleGet(f"batch-voucher/batch-vouchers/{self.voucherId}", self.session)
            return returned
        else:
            return

    # Starts a new voucher batching process in FOLIO
    # TODO Create this Function
    def triggerBatch(self):
        print("Selecting Most Recent Batch...")
        self.selectMostRecentBatch()
        print("Starting batch...")
        current_time = datetime.datetime.now()+datetime.timedelta(hours=5)
        end_time = f"{current_time.year:02}-{current_time.month:02}-{current_time.day:02}T{current_time.hour:02}:" \
                   f"{current_time.minute:02}:{current_time.second:02}.{str(current_time.microsecond)[0:3]}+0000"

        payload = {
            "batchGroupId": self.batchGroupId,
            "start": self.batchEndDate[0:23]+"+0000",
            "end": end_time,
            "status": "Pending"
        }
        url = "batch-voucher/batch-voucher-exports"
        print("\n\n" + url + "\n\n")
        print(json.dumps(payload, indent=4))
        response = self.requester.post(url, self.session, payload)
        self.selectNextBatch()
        print("New batch created and selected")
        return response


if __name__ == "__main__":
    configName = "config.json"
    retriever = VoucherBatchRetriever(configName)
    print("Attempting to trigger batch...")
    retriever.triggerBatch()
