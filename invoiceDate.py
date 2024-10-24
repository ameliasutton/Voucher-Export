# Depricated - invoice date is now included in Voucher Exports by default

import json
from popupWindow import popupWindow
import logging


def addInvoiceDates(filename, configName, requester):
    logging.info("Adding invoice dates to vouchers...")
    try:
        with open(configName, 'r') as config:
            config = json.load(config)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Config File \"{config}\": Not Found")
    with open(filename, 'r') as json_in:
        json_data = json.load(json_in)
    for i, voucher in enumerate(json_data['batchedVouchers']):
        identifier = voucher['voucherNumber']
        try:
            response = requester.singleGet(f"invoice/invoices?query=voucherNumber="
                                            f"\"{str(identifier)}\"")
            logging.info(response)
            json_data['batchedVouchers'][i]["invoiceDate"] = response['invoices'][0]['invoiceDate']
        except Exception as exc:
            logging.warning(exc)

    with open(filename, 'w') as json_out:
        json_out.write(json.dumps(json_data, indent=4))
    logging.info("Invoice dates added!")

