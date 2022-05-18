import json
import folio_api_aneslin as api
import requests
from logger import logger


class invoicePayer:

    def __init__(self, config: str, identifiers: list[int]):
        self.log = logger("mark_paid_log")
        self.identifiers = identifiers

        # Read Config File
        self.configFileName = config
        try:
            with open(config, "r") as c:
                config = json.load(c)
        except FileNotFoundError:
            print(f"Config file \"{config}\" not found")
            raise FileNotFoundError

        # Create Requester
        self.requester = api.requestObject(config["url"], config["tenant"])
        self.requester.setToken(config["token"])
        self.log.pauseLogging()
        self.requester.testToken()
        self.log.resumeLogging()
        self.updateToken()

        # Create Session
        headers = {'Content-Type': 'application/json',
                   'x-okapi-tenant': config["tenant"],
                   'x-okapi-token': self.requester.token,
                   'Accept': 'application/json'}
        self.session = requests.Session()
        self.session.headers = headers

    def updateToken(self) -> int:
        with open(self.configFileName, "r") as readConf:
            config = json.load(readConf)
        config["token"] = self.requester.token
        with open(self.configFileName, "w") as writeConf:
            writeConf.write(json.dumps(config, indent=4))
        print("Token in config is up to date.")
        return 0

    def getInvoice(self, identifier: int) -> {}:
        response = self.requester.singleGet(f"invoice/invoices?query=voucherNumber="
                                            f"\"{str(identifier)}\"", self.session)
        if response["totalRecords"] == 1:
            return response["invoices"][0]
        else:
            return {}

    def payInvoice(self, invoiceJson: dict) -> int:
        print(f"...FOLIO Invoice Number: {invoiceJson['folioInvoiceNo']}")
        if invoiceJson["status"] != "Approved":
            return -2
        invoiceJson["status"] = "Paid"
        uuid = invoiceJson["id"]
        response = self.requester.put(f"invoice/invoices/{str(uuid)}", self.session, invoiceJson)
        if response == {}:
            return 0
        else:
            return -1

    def batchPayInvoices(self) -> dict:
        print("Setting Invoices to Paid Status...")
        invoices = []
        results_dict = {}
        for item in self.identifiers:
            retrieved_invoice = self.getInvoice(item)
            if retrieved_invoice == {}:
                results_dict[item] = "No matching invoice found"
            else:
                invoices.append(retrieved_invoice)
        for invoice in invoices:
            paid = self.payInvoice(invoice)
            if paid == 0:
                results_dict[invoice["folioInvoiceNo"]] = "Marked Paid"
            elif paid == -1:
                results_dict[invoice["folioInvoiceNo"]] = "Request Failed, see above for details."
            elif paid == -2:
                results_dict[invoice["folioInvoiceNo"]] = "Invoice has not been approved or has already been paid"
        return results_dict


if __name__ == "__main__":
    payer = invoicePayer("config.json", [1099])
    results = payer.batchPayInvoices()
    print("\n****************************************************************************\n")
    print("Results:\n")
    print(json.dumps(results, indent=4))
