import requests
import json
import folio_api_aneslin as api
import datetime
from invoiceDate import addInvoiceDates


class VoucherBatchRetriever:
    def __init__(self, config):
        print("Initializing Retriever...")
        self.configFileName = config
        try:
            with open(config, "r") as c:
                config = json.load(c)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config File \"{config}\": Not Found")
        self.batchStartDate = config["batchStartDate"]
        self.batchEndDate = config["batchEndDate"]

        # Creates the requester object
        print("Creating Requester...")
        self.requester = api.requestObject(config["url"], config["tenant"])
        self.requester.setToken(config["token"])
        if self.requester.testToken() == -1:
            raise Exception('Token rejected, new login credentials required')
        self.updateConfig()
        print("Requester Created!")
        print("Creating Session...")
        # Creates the session
        self.batchGroup = config["batchGroup"]
        headers = {'Content-Type': 'application/json',
                   'x-okapi-tenant': config["tenant"],
                   'x-okapi-token': self.requester.token,
                   'Accept': 'application/json'}
        self.session = requests.Session()
        self.session.headers = headers
        self.session.params = {"limit": "1000"}
        print("Session Created!")
        print("Getting Batch Group ID...")
        self.batchGroupId = self.getBatchGroupId()
        print("Batch Group ID Retrieved!")
        print("Getting Batch ID...")
        self.batchId = self.getBatchId()
        print("Batch ID Retrieved!")
        print("Getting Voucher ID...")
        self.voucherId = None
        self.getVoucherId()
        print("Retriever Created!")

    # Updates config file with currently selected Start Date, End Date, and API Token
    def updateConfig(self):
        with open(self.configFileName, "r") as readConf:
            config = json.load(readConf)
            config["batchEndDate"] = self.batchEndDate
            config["batchStartDate"] = self.batchStartDate
            config["token"] = self.requester.token
        with open(self.configFileName, "w") as writeConf:
            writeConf.write(json.dumps(config, indent=4))
            print("Config updated")

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
        try:
            self.voucherId = batch["batchVoucherId"]
        except KeyError:
            print("| Warn | Selected Batch encountered an error: " + batch["message"])
            self.voucherId = None
            return -1
        return 0

    def getVoucherStatus(self):
        batch = self.requester.singleGet(f"batch-voucher/batch-voucher-exports?query=(batchGroupId==\""
                                         f"{self.batchGroupId}\" AND start==\"{self.batchStartDate}\" AND end==\""
                                         f"{self.batchEndDate}\")", self.session)["batchVoucherExports"][0]
        try:
            print(batch["batchVoucherId"])
        except KeyError:
            print("| Warn | Selected Batch encountered an error: " + batch["message"])
            return batch["message"]
        return "Successful"

    # Moves Start and End Dates to point towards the next Batch
    def selectNextBatch(self):
        batch = self.requester.singleGet(f"batch-voucher/batch-voucher-exports?query=batchGroupId==\""
                                         f"{self.batchGroupId}\" AND start==\"{self.batchEndDate}\"", self.session)
        if batch["totalRecords"] == 0:
            print("Most recent batch already selected")
            return -1
        else:
            self.batchId = batch["batchVoucherExports"][0]["id"]
            self.batchEndDate = batch["batchVoucherExports"][0]["end"][0:23] + "*"
            self.batchStartDate = batch["batchVoucherExports"][0]["start"][0:23] + "*"
            print("Next Batch Selected\n"
                  "Run Date: " + self.batchEndDate)
            self.updateConfig()
            return 0

    # Moves Start and End Dates to point towards the next successfully completed batch
    def selectNextSuccessful(self):
        current_id = self.batchId
        current_end = self.batchEndDate
        current_start = self.batchStartDate
        print("Attempting to select next Successful batch...")
        if self.selectNextBatch() == -1:
            self.batchId = current_id
            self.batchEndDate = current_end
            self.batchStartDate = current_start
            self.updateConfig()
            print("No more recent batches were successful initial batch reselected.")
            return -1
        while self.getVoucherId() == -1:
            if self.selectNextBatch() == -1:
                self.batchId = current_id
                self.batchEndDate = current_end
                self.batchStartDate = current_start
                self.updateConfig()
                print("No more recent batches were successful initial batch reselected.")
                return -1
        print("Next Successful batch selected!")
        return 0

    # Moves Start and End Dates to point towards the most recently run Batch
    def selectMostRecentBatch(self):
        batch = self.requester.singleGet(f"batch-voucher/batch-voucher-exports?query=batchGroupId==\""
                                         f"{self.batchGroupId}\" sortby end/sort.descending", self.session)
        if batch["totalRecords"] == 0:
            print(f"No Batches Found With Batch Group: {self.batchGroup}")
            return -1
        batch = batch["batchVoucherExports"][0]
        self.batchId = batch["id"]
        self.batchEndDate = batch["end"][0:23] + "*"
        self.batchStartDate = batch["start"][0:23] + "*"
        print("Most Recent Batch Selected\n"
              "Run Date: " + self.batchEndDate)
        self.updateConfig()
        return 0

    # Moves Start and End Dates to point towards the most recent Successful batch
    def mostRecentSuccessful(self):
        self.selectMostRecentBatch()
        if self.selectPreviousSuccessful() == -1:
            print("No Successful batches found")
            return -1
        print("Most recent Successful batch selected")
        return 0

    # Moves Start and End Dates to point towards the previous Batch
    def selectPreviousBatch(self):
        batch = self.requester.singleGet(f"batch-voucher/batch-voucher-exports?query=batchGroupId==\""
                                         f"{self.batchGroupId}\" AND end==\"{self.batchStartDate}\"", self.session)
        if batch["totalRecords"] == 0:
            print("Oldest Batch already selected")
            return -1
        else:
            self.batchId = batch["batchVoucherExports"][0]["id"]
            self.batchEndDate = batch["batchVoucherExports"][0]["end"][0:23] + "*"
            self.batchStartDate = batch["batchVoucherExports"][0]["start"][0:23] + "*"
            print(f"Previous Batch Selected\n"
                  f"Start Date: {self.batchStartDate}\n"
                  f"End Date: {self.batchEndDate}\n"
                  f"Batch ID: {self.batchId}")
            self.updateConfig()
            return 0

    # Moves Start and End Dates to point towards the previous successfully completed batch
    def selectPreviousSuccessful(self):
        current_id = self.batchId
        current_end = self.batchEndDate
        current_start = self.batchStartDate
        print("Attempting to select previous Successful batch...")
        if self.selectPreviousBatch() == -1:
            self.batchId = current_id
            self.batchEndDate = current_end
            self.batchStartDate = current_start
            self.updateConfig()
            print("No older batches were successful initial batch reselected.")
            return -1
        while self.getVoucherId() == -1:
            if self.selectPreviousBatch() == -1:
                self.batchId = current_id
                self.batchEndDate = current_end
                self.batchStartDate = current_start
                self.updateConfig()
                print("No older batches were successful initial batch reselected.")
                return -1
        print("Previous Successful batch selected!")
        return 0

    # Returns a dict of the Batched Vouchers
    def retrieveVoucher(self):
        self.getVoucherId()
        if self.voucherId:
            returned = self.requester.singleGet(f"batch-voucher/batch-vouchers/{self.voucherId}", self.session)
            return returned
        else:
            return {}

    # Starts a new voucher batching process in FOLIO
    def triggerBatch(self):
        print("Selecting Most Recent Batch...")
        self.selectMostRecentBatch()
        print("Starting batch...")
        # NOTE: If server time is ever changed update this timedelta
        current_time = datetime.datetime.now()+datetime.timedelta(hours=5)
        start_time = f"{self.batchEndDate[:-1]}+0000"
        end_time = f"{current_time.year:02}-{current_time.month:02}-{current_time.day:02}T{current_time.hour:02}:" \
                   f"{current_time.minute:02}:{current_time.second:02}.{str(current_time.microsecond)[0:3]}+0000"

        payload = {
            "batchGroupId": self.batchGroupId,
            "start": start_time,
            "end": end_time
        }
        url = "batch-voucher/batch-voucher-exports"
        print("\n\n" + url + "\n\n")
        print(json.dumps(payload, indent=4))
        response = self.requester.post(url, self.session, payload)
        try:
            if response["error"]:
                return -1
        finally:
            self.selectMostRecentBatch()
            return 0

    # Saves voucher to JSON using BatchEndDate as file name
    def saveVoucherJSON(self):
        vouchers = self.retrieveVoucher()
        if vouchers != {}:
            print("Saving Voucher Batch...")
            file_out = "jsonBatchVouchers/" + self.batchGroup + "/" + self.batchEndDate[0:-5].replace(":", "-").replace("T", "_") + ".json"
            with open(file_out, "w") as out:
                out.write(json.dumps(vouchers, indent=4))
            print("Voucher Batch Saved.")
            addInvoiceDates(file_out, self.configFileName)
            return 0
        else:
            return -1


if __name__ == "__main__":
    configName = "config.json"
    retriever = VoucherBatchRetriever(configName)
    retriever.mostRecentSuccessful()
