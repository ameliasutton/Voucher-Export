import json
import xml.etree.ElementTree as xmlET
import os
import glob
from xml.dom import minidom


def openMostRecentJson(batchGroup):
    folder_path = os.getcwd() + "/jsonBatchVouchers/" + batchGroup
    file_type = '/*json'
    files = glob.glob(folder_path + file_type)
    try:
        max_file = max(files, key=os.path.getctime)
    except FileNotFoundError:
        exit(f"No json files found in {folder_path}")
    file_out = json.load(open(max_file, 'r'))
    return file_out


# Takes in a json dict
def ConvertFOLIOBatchVoucher(config, voucherIn):
    try:
        with open(config, "r") as readFile:
            config = json.load(readFile)
            user = config["jaggaerIdentity"]
            secret = config["jaggaerSecret"]
    except FileNotFoundError:
        exit(f"Config File \"{config}\" Not Found")
    if voucherIn["batchGroup"] != config["batchGroup"]:
        print("Batch Group in Voucher json does not match Batch Group in config.")
        return

    xml_root = xmlET.Element("BuyerInvoiceOcrMessage")
    xml_root.attrib = {"version": "1.0"}

    # Creates XML header (this is correct)
    header = xmlET.Element("Header")
    xml_root.append(header)

    message_id = xmlET.SubElement(header, "MessageId")
    message_id.text = voucherIn["id"]

    timestamp = xmlET.SubElement(header, "Timestamp")
    timestamp.text = voucherIn["end"]

    authentication = xmlET.SubElement(header, "Authentication")
    identity = xmlET.SubElement(authentication, "Identity")
    identity.text = user
    shared_secret = xmlET.SubElement(authentication, "SharedSecret")
    shared_secret.text = secret


    # TODO: Remove these printing lines they are here for testing:
    xmlstr = minidom.parseString(xmlET.tostring(xml_root)).toprettyxml(indent="   ")
    print (xmlstr)


# TODO: OLD DEAD SCRIPT TO BE REPURPOSED
def OLD(i):
    # extracts data from each voucher and adds it to the xml tree
    # TODO THIS SECTION TO BE UPDATED
    for voucher in inputJson.pop("batchedVouchers"):
        invoiceStatuses = xmlET.SubElement(xmlRoot, "BuyerInvoiceOrc")
        invoice = xmlET.SubElement(invoiceStatuses, "BuyerInvoiceHeader")

        invoiceNumber = xmlET.SubElement(invoice, "SupplierInvoiceNumber")
        invoiceNumber.text = voucher.pop("vendorInvoiceNo")

        invoiceType = xmlET.SubElement(invoice, "InvoiceType")
        invoiceType.text = "Invoice"

        status = xmlET.SubElement(invoice, "Status")
        status.text = "TODO: status"

        paymentMethod = xmlET.SubElement(invoice, "PaymentMethod")
        paymentMethod.text = "TODO: payment method"

        recordNumber = xmlET.SubElement(invoice, "RecordNumber")
        recordNumber.text = "TODO: record number"

        recordDate = xmlET.SubElement(invoice, "RecordDate")
        recordDate.text = "TODO: record date"

        accountingDate = xmlET.SubElement(invoice, "AccountingDate")
        accountingDate.text = "TODO: accounting date"

        notes = xmlET.SubElement(invoice, "Notes")
        notes.text = "TODO: Notes"

        customFieldValues = xmlET.SubElement(invoice, "CustomFieldValues")
        customFieldValue = xmlET.SubElement(customFieldValues, "CustomFieldValues")
        customFieldValue.attrib = {"exampleCustomField": "exampleCustomValue"}

    # tree = xmlET.ElementTree(xmlRoot)
    # with open("output/invoicesExport.xml", 'wb') as out:
    #    tree.write(out)

    from xml.dom import minidom

    xmlstr = minidom.parseString(xmlET.tostring(xmlRoot)).toprettyxml(indent="   ")
    with open("output/invoicesExport.xml", "w") as f:
        f.write(xmlstr)

    with open("output/invoicesExport.xml", 'r+') as out:
        fileHeaders = "<?xml version=\"1.0\"?>\n<!DOCTYPE BuyerInvoiceOcrMessage SYSTEM\n \"https://integrations.sciquest.com/app_docs/dtd/buyerinvoice/BuyerInvoiceOCR.dtd\">"
        content = out.read()
        print(content[22:])
        out.seek(0, 0)
        out.write(fileHeaders.rstrip('\r\n') + content[22:])

    exit("Complete")


if __name__ == "__main__":
    jsonIn = openMostRecentJson("FOLIO")
    ConvertFOLIOBatchVoucher("config.json", jsonIn)
