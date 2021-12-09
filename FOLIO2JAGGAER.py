import json
import xml.etree.ElementTree as xmlET
import os
import glob


def openMostRecentJson(batchGroup):
    folder_path = os.getcwd() + "/jsonBatchVouchers/" + batchGroup
    file_type = '/*json'
    files = glob.glob(folder_path + file_type)
    max_file = max(files, key=os.path.getctime)
    file_out = open(max_file, 'r')
    return file_out


if __name__ == "__main__":
    print("\n" * 40)
    print(openMostRecentJson("FOLIO").read())
    exit()


# TODO: OLD DEAD SCRIPT TO BE REPURPOSED

def OLD(i):
    # finds and loads file in the "/input" directory
    if not os.listdir(os.getcwd() + "/input"):
        exit("No input file found")
    for file in os.listdir(os.getcwd() + "/input"):
        with open("input/" + file, 'r') as inFile:
            inputJson = json.load(inFile)

    # TODO: USE THIS IN THE CONVERT SCRIPT TO GET THIS INFORMATION FROM THE CONFIG FILE
    with open("jaggaerLogin.json", 'r') as login:
        loginData = json.load(login)
        user = loginData.pop("identity")
        secret = loginData.pop("secret")

    # checks for expected batchGroup name
    batchGroupExpected = "UMass"
    batchGroupActual = inputJson.pop("batchGroup")

    if batchGroupActual != batchGroupExpected:
        exit(
            "Input file batch group, \"" + batchGroupActual + "\" does not match the expected \"" + batchGroupExpected + "\"")

    # creates output xml tree with a root xmlRoot
    xmlRoot = xmlET.Element("BuyerInvoiceOcrMessage")
    xmlRoot.attrib = {"version": "1.0"}

    # Creates XML header (this is correct)
    header = xmlET.Element("Header")
    xmlRoot.append(header)

    messageID = xmlET.SubElement(header, "MessageId")
    messageID.text = inputJson.pop("id")

    timestamp = xmlET.SubElement(header, "Timestamp")
    timestamp.text = inputJson.pop("end")

    authentication = xmlET.SubElement(header, "Authentication")
    identity = xmlET.SubElement(authentication, "Identity")
    identity.text = user
    sharedSecret = xmlET.SubElement(authentication, "SharedSecret")
    sharedSecret.text = secret

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
