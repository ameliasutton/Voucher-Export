import json
import folio_api_aneslin as api
import datetime
import logging

class VoucherBatchRetriever:
    def __init__(self, config, requester):
        logging.info("Initializing Retriever...")
        self.configFileName = config
        try:
            with open(config, "r") as c:
                config = json.load(c)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config File \"{config}\": Not Found")
        self.batchStartDate = config["batchStartDate"]
        self.batchEndDate = config["batchEndDate"]

        self.requester = requester
        self.updateConfig()
        self.batchGroup = config["batchGroup"]

        logging.info("Getting Batch Group ID...")
        try:
            self.batchGroupId = self.getBatchGroupId()
        except Exception as e:
            raise e
        logging.info("Batch Group ID Retrieved!")

        logging.info("Getting Batch ID...")
        self.batchId = None
        if self.getBatchId() == -1:
            logging.warning("No Selected Batch Found, Triggering New Batch")
            self.triggerBatch()
        logging.info("Batch ID Retrieved!")

        logging.info("Getting Voucher ID...")
        self.voucherId = None
        if self.getVoucherId == 0:
            logging.info("Voucher ID Retrieved!")
        else:
            logging.info("Selected batch contains no vouchers.")
        
        logging.info("Retriever Created!")

    # Updates config file with currently selected Start Date, End Date, and API Token
    def updateConfig(self):
        with open(self.configFileName, "r") as readConf:
            config = json.load(readConf)
            config["batchEndDate"] = self.batchEndDate
            config["batchStartDate"] = self.batchStartDate
        with open(self.configFileName, "w") as writeConf:
            writeConf.write(json.dumps(config, indent=4))
            logging.info("Config updated")

    # Returns Batch Group ID matching Batch Group Name provided in config file
    def getBatchGroupId(self):
        response = self.requester.singleGet(f"batch-groups?query=name=\"{self.batchGroup}\"")
        if response["totalRecords"] == 0:
            raise RuntimeError("Batch group name in config did not match any in FOLIO")
        elif response["totalRecords"] > 1:
            raise RuntimeError("Batch group name in config matched with more than one batch group in FOLIO")
        logging.info(response["batchGroups"][0]["id"])
        return response["batchGroups"][0]["id"]

    # Returns the Batch ID associated with the selected Dates
    def getBatchId(self):
        batch = self.requester.singleGet(f"batch-voucher/batch-voucher-exports?query=(batchGroupId==\""
                                         f"{self.batchGroupId}\" AND start==\"{self.batchStartDate}\" AND end==\""
                                         f"{self.batchEndDate}\")")
        if batch["totalRecords"] == 0:
            logging.info("Selecting Most Recent Batch Date...")
            self.selectMostRecentBatch()
            return
        batch = batch["batchVoucherExports"][0]["id"]
        return batch

    # Returns the Voucher ID associated with the selected Batch if it exists
    # Returns None otherwise
    def getVoucherId(self):
        try:
            batch = self.requester.singleGet(f"batch-voucher/batch-voucher-exports?query=(batchGroupId==\""
                                             f"{self.batchGroupId}\" AND start==\"{self.batchStartDate}\" AND end==\""
                                             f"{self.batchEndDate}\")")
            self.voucherId = batch["batchVoucherExports"][0]["batchVoucherId"]
        except:
            self.voucherId = None
            return -1
        return 0

    def getVoucherStatus(self):
        response = self.requester.singleGet(f"batch-voucher/batch-voucher-exports?query=batchGroupId==\"{self.batchGroupId}\" AND start==\"{self.batchStartDate}\" AND end==\"{self.batchEndDate}\"")
        batch = response["batchVoucherExports"][0]
        try:
            logging.info(batch["batchVoucherId"])
        except KeyError:
            logging.warning("Selected Batch encountered an error: " + batch["message"])
            return batch["message"]
        return "Successful"

    # Moves Start and End Dates to point towards the next Batch
    def selectNextBatch(self):
        batch = self.requester.singleGet(f"batch-voucher/batch-voucher-exports?query=batchGroupId==\"{self.batchGroupId}\" AND start==\"{self.batchEndDate}\"")
        if batch["totalRecords"] == 0:
            logging.info("Most recent batch already selected")
            return -1
        else:
            self.batchId = batch["batchVoucherExports"][0]["id"]
            self.batchEndDate = batch["batchVoucherExports"][0]["end"][0:23] + "*"
            self.batchStartDate = batch["batchVoucherExports"][0]["start"][0:23] + "*"
            logging.info("Next Batch Selected"
                  "Run Date: " + self.batchEndDate)
            self.updateConfig()
            return 0

    # Moves Start and End Dates to point towards the next successfully completed batch
    def selectNextSuccessful(self):
        current_id = self.batchId
        current_end = self.batchEndDate
        current_start = self.batchStartDate
        logging.info("Attempting to select next Successful batch...")
        if self.selectNextBatch() == -1:
            self.batchId = current_id
            self.batchEndDate = current_end
            self.batchStartDate = current_start
            self.updateConfig()
            logging.info("No more recent batches were successful initial batch reselected.")
            return -1
        while self.getVoucherId() == -1:
            if self.selectNextBatch() == -1:
                self.batchId = current_id
                self.batchEndDate = current_end
                self.batchStartDate = current_start
                self.updateConfig()
                logging.info("No more recent batches were successful initial batch reselected.")
                return -1
        logging.info("Next Successful batch selected!")
        return 0

    # Moves Start and End Dates to point towards the most recently run Batch
    def selectMostRecentBatch(self):
        batch = self.requester.singleGet(f"batch-voucher/batch-voucher-exports?query=batchGroupId==\""
                                         f"{self.batchGroupId}\" sortby end/sort.descending")
        if batch["totalRecords"] == 0:
            logging.warn(f"No Batches Found With Batch Group: {self.batchGroup}")
            return -1
        batch = batch["batchVoucherExports"][0]
        self.batchId = batch["id"]
        self.batchEndDate = batch["end"][0:23] + "*"
        self.batchStartDate = batch["start"][0:23] + "*"
        logging.info(f"Most Recent Batch Selected (Run Date: {self.batchEndDate})")
        self.updateConfig()
        return 0

    # Moves Start and End Dates to point towards the most recent Successful batch
    def mostRecentSuccessful(self):
        self.selectMostRecentBatch()
        if self.selectPreviousSuccessful() == -1:
            logging.info("No Successful batches found")
            return -1
        logging.info("Most recent Successful batch selected")
        return 0

    # Moves Start and End Dates to point towards the previous Batch
    def selectPreviousBatch(self):
        batch = self.requester.singleGet(f"batch-voucher/batch-voucher-exports?query=batchGroupId==\""
                                         f"{self.batchGroupId}\" AND end==\"{self.batchStartDate}\"")
        if batch["totalRecords"] == 0:
            logging.info("Oldest Batch already selected")
            return -1
        else:
            self.batchId = batch["batchVoucherExports"][0]["id"]
            self.batchEndDate = batch["batchVoucherExports"][0]["end"][0:23] + "*"
            self.batchStartDate = batch["batchVoucherExports"][0]["start"][0:23] + "*"
            logging.info(f"Previous Batch Selected: Start Date: {self.batchStartDate}, End Date: {self.batchEndDate}, Batch ID: {self.batchId}")
            self.updateConfig()
            return 0

    # Moves Start and End Dates to point towards the previous successfully completed batch
    def selectPreviousSuccessful(self):
        current_id = self.batchId
        current_end = self.batchEndDate
        current_start = self.batchStartDate
        logging.info("Attempting to select previous Successful batch...")
        if self.selectPreviousBatch() == -1:
            self.batchId = current_id
            self.batchEndDate = current_end
            self.batchStartDate = current_start
            self.updateConfig()
            logging.info("No older batches were successful initial batch reselected.")
            return -1
        while self.getVoucherId() == -1:
            if self.selectPreviousBatch() == -1:
                self.batchId = current_id
                self.batchEndDate = current_end
                self.batchStartDate = current_start
                self.updateConfig()
                logging.info("No older batches were successful initial batch reselected.")
                return -1
        logging.info("Previous Successful batch selected!")
        return 0

    # Returns a dict of the Batched Vouchers
    def retrieveVoucher(self):
        self.getVoucherId()
        if self.voucherId:
            returned = self.requester.singleGet(f"batch-voucher/batch-vouchers/{self.voucherId}")
            return returned
        else:
            return {}

    # Starts a new voucher batching process in FOLIO
    def triggerBatch(self):
        logging.info("Selecting Most Recent Batch...")
        self.selectMostRecentBatch()
        logging.info("Starting batch...")
        # NOTE: If server time is ever changed update this timedelta
        current_time = datetime.datetime.utcnow()
        start_time = f"{self.batchEndDate[:-1]}+0000"
        end_time = f"{current_time.year:02}-{current_time.month:02}-{current_time.day:02}T{current_time.hour:02}:" \
                   f"{current_time.minute:02}:{current_time.second:02}.{str(current_time.microsecond)[0:3]}+0000"

        payload = {
            "batchGroupId": self.batchGroupId,
            "start": start_time,
            "end": end_time
        }
        url = "batch-voucher/batch-voucher-exports"
        logging.info(json.dumps(payload, indent=4))
        response = self.requester.post(url, payload)
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
            logging.info("Saving Voucher Batch...")
            file_out = "jsonBatchVouchers/" + self.batchGroup + "/" + self.batchEndDate[0:-5].replace(":", "-").replace("T", "_") + ".json"
            with open(file_out, "w", encoding='utf-8') as out:
                out.write(json.dumps(vouchers, indent=4))
            logging.info("Voucher Batch Saved.")
            return 0
        else:
            return -1
