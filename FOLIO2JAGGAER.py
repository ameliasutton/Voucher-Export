import json
import xml.etree.ElementTree as xmlET
import os
import glob
from xml.dom import minidom
import pandas


class voucherDataConverter:

    def __init__(self, config, jsonName=None, xmlName=None):
        print("Initializing Voucher Data Converter")
        try:
            with open(config, "r") as readFile:
                config = json.load(readFile)
                self.user = config["jaggaerIdentity"]
                self.secret = config["jaggaerSecret"]
                self.batchGroup = config["batchGroup"]
        except FileNotFoundError:
            raise FileNotFoundError(f"Config File: {config} Not Found")
        try:
            with open(config["chartfield"]) as chart:
                self.chartfield = pandas.read_csv(chart, delimiter="|", index_col="speedtype", dtype="string")
        except FileNotFoundError:
            raise FileNotFoundError(f"Chartfield File: {config['chartfield']} not found")

        self.JsonName = jsonName
        if jsonName:
            with open(f"jsonBatchVouchers/{self.batchGroup}/{jsonName}", "r") as jsonIn:
                self.selectedJson = json.load(jsonIn)
        else:
            self.retrieveMostRecentJSON()
        self.voucherIdentifiers = self.getVoucherIdentifiersList()
        print(f"File Selected for Conversion: {self.JsonName}")

        if xmlName:
            self.createdXML = xmlET.parse(xmlName)
            self.XMLstring = self.getXMLString()
        else:
            self.createdXML = None
            self.XMLstring = None

    # locates most recently created json
    def retrieveMostRecentJSON(self):
        folder_path = os.getcwd() + "/jsonBatchVouchers/" + self.batchGroup
        file_type = '/*json'
        files = glob.glob(folder_path + file_type)
        try:
            max_file = max(files, key=os.path.getmtime)
        except Exception:
            raise FileNotFoundError(f"No Batch Vouchers Found for Batch Group: {self.batchGroup}")
        self.JsonName = max_file
        file_out = json.load(open(max_file, 'r'))
        self.selectedJson = file_out
        return self.selectedJson

    # retrieves list of voucher numbers from the input json
    def getVoucherIdentifiersList(self):
        if not self.selectedJson:
            raise FileNotFoundError("No JSON file selected")
        id_list = []
        for invoice in self.selectedJson["batchedVouchers"]:
            id_list.append(invoice["voucherNumber"])

        return id_list

    # saves list of voucher numbers for later use
    def saveVoucherIdentifiers(self):
        if not self.voucherIdentifiers:
            raise ValueError("List of Voucher Identifiers Not Created.")
        file_out_path = f'voucherIdentifiers\\{self.batchGroup}\\{self.JsonName[-24:-5]}.txt'
        print(file_out_path)
        with open(file_out_path, "w") as f:
            for item in self.voucherIdentifiers:
                f.write(item+'\n')
        return file_out_path

    # Takes in a json dict and generates an XML ElementTree
    def ConvertFOLIOBatchVoucher(self):
        if not self.selectedJson:
            raise FileNotFoundError("No JSON file selected")
        if self.selectedJson["batchGroup"] != self.batchGroup:
            raise ValueError("Batch Group in Voucher json does not match Batch Group in config.")

        xml_root = xmlET.Element("BuyerInvoiceOcrMessage")
        xml_root.attrib["xmlns:xop"] = "http://www.w3.org/2004/08/xop/include/"
        xml_root.attrib["version"] = "1.0"

        # Creates XML header (this is correct)
        header = xmlET.Element("Header")
        xml_root.append(header)

        message_id = xmlET.SubElement(header, "MessageId")
        message_id.text = self.selectedJson["id"]

        timestamp = xmlET.SubElement(header, "Timestamp")
        timestamp.text = self.selectedJson["end"][0:-5]

        authentication = xmlET.SubElement(header, "Authentication")
        identity = xmlET.SubElement(authentication, "Identity")
        identity.text = self.user
        shared_secret = xmlET.SubElement(authentication, "SharedSecret")
        shared_secret.text = self.secret
        for voucher in self.selectedJson["batchedVouchers"]:
            # Invoice Header Begins

            # Invoice Header Header
            invoice_line = xmlET.SubElement(xml_root, "BuyerInvoiceOcr")
            invoice_header = xmlET.SubElement(invoice_line, "BuyerInvoiceHeader")

            invoice_number = xmlET.SubElement(invoice_header, "SupplierInvoiceNumber")
            invoice_number.text = voucher["vendorInvoiceNo"]

            invoice_type = xmlET.SubElement(invoice_header, "InvoiceType")
            invoice_type.text = "Invoice"

            if voucher["accountingCode"] == voucher["accountNo"]:
                if voucher["accountingCode"].find("(") != -1:
                    supplier_no = voucher["accountingCode"][:voucher["accountingCode"].find("(")].strip()
                    supplier_address_code = voucher["accountingCode"][voucher["accountingCode"]
                                                                      .find("(") + 1:voucher["accountingCode"].find(")")]
                else:
                    supplier_no = voucher["accountingCode"]
                    supplier_address_code = ''
            elif voucher["accountingCode"].find("(") != -1:
                raise ValueError("Accounting Code and Account No do not Match")
            else:
                supplier_no = voucher["accountNo"]
                supplier_address_code = voucher["accountingCode"]

            # TODO Make sure this is correct
            remit_to = xmlET.SubElement(invoice_header, "BillTo")
            remit_to_address = xmlET.SubElement(remit_to, "Address")
            address_code = xmlET.SubElement(remit_to_address, "AddressCode")
            address_code.text = supplier_address_code

            in_date = voucher["invoiceDate"][:10]
            invoice_date = xmlET.SubElement(invoice_header, "InvoiceDate")
            invoice_date.text = in_date

            username = xmlET.SubElement(invoice_header, "UserName")
            user_id = xmlET.SubElement(username, "UserID")
            user_id.text = "10153343"

            # Terms Information (Under Invoice Header)
            # terms = xmlET.SubElement(invoice_header, "Terms")
            # discount_amount = xmlET.SubElement(terms, "DiscountAmount")
            # money = xmlET.SubElement(discount_amount, "Money")
            # money.attrib = {"currency": "USD"}
            # money.text = "0"

            # Due Date Information (Under Invoice Header)
            # due_date = xmlET.SubElement(invoice_header, "DueDate")
            # due_date.text = "TODO Due Date"

            # Grand Total Information (Under Invoice Header)

            grand_total = xmlET.SubElement(invoice_header, "GrandTotal")
            grand_total_money = xmlET.SubElement(grand_total, "Money")
            grand_total_money.attrib = {"currency": "USD"}
            grand_total_money.text = str(voucher["amount"])

            supplier = xmlET.SubElement(invoice_header, "Supplier")
            supplier_number = xmlET.SubElement(supplier, "SupplierNumber")
            supplier_number.text = supplier_no

            # supplier_contact = xmlET.SubElement(supplier, "ContactInfo")
            # supplier_phone = xmlET.SubElement(supplier_contact, "Phone")
            # supplier_phone_number = xmlET.SubElement(supplier_phone, "TelephoneNumber")
            # supplier_phone_country = xmlET.SubElement(supplier_phone_number, "CountryCode")
            # supplier_phone_country.text = "TODO: country code"
            # supplier_phone_area = xmlET.SubElement(supplier_phone_number, "AreaCode")
            # supplier_phone_area.text = "TODO: area code"
            # supplier_phone_number_number = xmlET.SubElement(supplier_phone_number, "Number")
            # supplier_phone_number_number.text = "TODO: Phone Number"

            ocr_images = xmlET.SubElement(invoice_header, "OCRImages")
            ocr_image = xmlET.SubElement(ocr_images, "OCRImage")
            ocr_image.attrib["id"] = "123"
            ocr_image.attrib["type"] = "URL"
            ocr_image_url = xmlET.SubElement(ocr_image, "OCRImageURL")
            ocr_image_url.text = "www.nowhere.com"
            ocr_image_name = xmlET.SubElement(ocr_image, "OCRImageName")
            ocr_image_name.text = "123"

            # Sub Total Information (Under Invoice Header)
            # sub_total = xmlET.SubElement(invoice_header, "SubTotal")
            # sub_total_money = xmlET.SubElement(sub_total, "Money")
            # sub_total_money.attrib = {"currency": "USD"}
            # sub_total_money.text = str(voucher["amount"])

            # Notes (Under Invoice Header)
            # notes = xmlET.SubElement(invoice_header, "Notes")
            # notes.text = "TODO: Notes"

            # Business Unit (Under Invoice Header)
            # business_unit = xmlET.SubElement(invoice_header, "BusinessUnit")
            # business_unit.attrib = {"internalName": "TODO internal name"}

            # Shipping Charges Information (Under Invoice Header)
            # shipping_charges = xmlET.SubElement(invoice_header, "ShippingCharges")
            # shipping_charges_money = xmlET.SubElement(shipping_charges, "Money")
            # shipping_charges_money.attrib = {"currency": "USD"}
            # shipping_charges_money.text = "TODO: Shiping Charge"

            # Handling Charges Information (Under Invoice Header)
            # handling_charges = xmlET.SubElement(invoice_header, "HandlingCharges")
            # handling_charges_money = xmlET.SubElement(handling_charges, "Money")
            # handling_charges_money.attrib = {"currency": "USD"}
            # handling_charges_money.text = "TODO Money"

            # Tax 1 Information (Under Invoice Header)
            # tax_1 = xmlET.SubElement(invoice_header, "Tax1")
            # tax1_money = xmlET.SubElement(tax_1, "Money")
            # tax1_money.attrib = {"currency": "USD"}
            # tax1_money.text = "TODO Tax 1"

            # Tax 2 Information (Under Invoice Header)
            # tax_2 = xmlET.SubElement(invoice_header, "Tax2")
            # tax2_money = xmlET.SubElement(tax_2, "Money")
            # tax2_money.attrib = {"currency": "USD"}
            # tax2_money.text = "TODO Tax 2"

            # OCR Images (Under Invoice Header)
            # ocr_images = xmlET.SubElement(invoice_header, "OCRImages")
            # ocr_image = xmlET.SubElement(ocr_images, "OCRImage")
            # ocr_image.attrib = {"id": "", "type": "URL"}
            # ocr_image_url = xmlET.SubElement(ocr_image, "OCRImageURL")
            # ocr_image_url.text = "TODO: URL"
            # ocr_image_name = xmlET.SubElement(ocr_image, "OCRImageName")
            # ocr_image_name.text = "TODO: Name"

            # Buyer Invoice Line Begins

            buyer_invoice_line = xmlET.SubElement(invoice_line, "BuyerInvoiceLine")
            buyer_invoice_line.attrib = {"lineNumber": "001"}

            # Item (Under Buyer Invoice Line)
            # item = xmlET.SubElement(buyer_invoice_line, "Item")
            # item_cat_no = xmlET.SubElement(item, "CatalogNumber")
            # item_cat_no.text = "TODO CatNo"
            # item_units = xmlET.SubElement(item, "UnitOfMeasure")
            # item_units.text = "TODO Units"

            # Quantity (Under Buyer Invoice Line)
            quantity = xmlET.SubElement(buyer_invoice_line, "Quantity")
            quantity.text = "1"

            # Unit Price (Under Buyer Invoice Line)
            unit_price = xmlET.SubElement(buyer_invoice_line, "UnitPrice")
            unit_price_money = xmlET.SubElement(unit_price, "Money")
            unit_price_money.attrib = {"currency": "USD"}
            unit_price_money.text = str(voucher["amount"])

            # Splittable Field Set Group Start (Under Buyer Invoice Line)

            split_set_group = xmlET.SubElement(buyer_invoice_line, "SplittableFieldSetGroup")

            # Location of the hyphen in the externalAccountNumber string
            hyphen = voucher["batchedVoucherLines"][0]["externalAccountNumber"].find('-')
            speedtype = voucher["batchedVoucherLines"][0]["externalAccountNumber"][:hyphen]
            account = voucher["batchedVoucherLines"][0]["externalAccountNumber"][hyphen + 1:]
            print(voucher["batchedVoucherLines"][0]["externalAccountNumber"])
            print(f"Account: {account}")
            print(f"SpeedType = {speedtype}")
            try:
                fund = self.chartfield.loc[speedtype][1]
                dep_id = self.chartfield.loc[speedtype][0]
            except Exception:
                raise ValueError(f"Speedtype: \"{speedtype}\" does not exist in the Chartfield")

            # Split Field 1 (Campus) (Under Buyer Invoice Line)
            split_set_1 = xmlET.SubElement(split_set_group, "SplittableFieldIndexSet")
            split_set_1.attrib = {"distributiontype": "PercentOfPrice", "context": "Line"}
            split_index_1 = xmlET.SubElement(split_set_1, "SplittableFieldIndex")
            split_index_1.attrib = {"distributionvalue": "100", "splitindex": "0"}
            split_1_custom = xmlET.SubElement(split_index_1, "CustomFieldValue")
            split_1_custom.attrib = {"name": "Campus"}
            split_1_custom_val = xmlET.SubElement(split_1_custom, "Value")
            split_1_custom_val.text = "UMAMH"
            print("Split Set 1, Campus: \'UMAMH\'")

            # Split Field 2 (Speedtype) (Under Buyer Invoice Line)
            split_set_2 = xmlET.SubElement(split_set_group, "SplittableFieldIndexSet")
            split_set_2.attrib = {"distributiontype": "PercentOfPrice", "context": "Line"}
            split_index_2 = xmlET.SubElement(split_set_2, "SplittableFieldIndex")
            split_index_2.attrib = {"distributionvalue": "100", "splitindex": "0"}
            split_2_custom = xmlET.SubElement(split_index_2, "CustomFieldValue")
            split_2_custom.attrib = {"name": "Speedtype"}
            split_2_custom_val = xmlET.SubElement(split_2_custom, "Value")
            split_2_custom_val.text = f'{speedtype}-A'
            print(f"Split Set 2, SpeedType: {speedtype}-A")

            # Split Field 3 (Fund) (Under Buyer Invoice Line)
            split_set_3 = xmlET.SubElement(split_set_group, "SplittableFieldIndexSet")
            split_set_3.attrib = {"distributiontype": "PercentOfPrice", "context": "Line"}
            split_index_3 = xmlET.SubElement(split_set_3, "SplittableFieldIndex")
            split_index_3.attrib = {"distributionvalue": "100", "splitindex": "0"}
            split_3_custom = xmlET.SubElement(split_index_3, "CustomFieldValue")
            split_3_custom.attrib = {"name": "Fund"}
            split_3_custom_val = xmlET.SubElement(split_3_custom, "Value")
            split_3_custom_val.text = f'{fund}-A'
            print(f"Split Set 3, Fund: {fund}-A")

            # Split Field 4 (Account) (Under Buyer Invoice Line)
            split_set_4 = xmlET.SubElement(split_set_group, "SplittableFieldIndexSet")
            split_set_4.attrib = {"distributiontype": "PercentOfPrice", "context": "Line"}
            split_index_4 = xmlET.SubElement(split_set_4, "SplittableFieldIndex")
            split_index_4.attrib = {"distributionvalue": "100", "splitindex": "0"}
            split_4_custom = xmlET.SubElement(split_index_4, "CustomFieldValue")
            split_4_custom.attrib = {"name": "Account"}
            split_4_custom_val = xmlET.SubElement(split_4_custom, "Value")
            split_4_custom_val.text = f'{account}-A'
            print(f"Split Set 4, Account: {account}-A")

            # Split Field 5 (Program) (Under Buyer Invoice Line)
            split_set_5 = xmlET.SubElement(split_set_group, "SplittableFieldIndexSet")
            split_set_5.attrib = {"distributiontype": "PercentOfPrice", "context": "Line"}
            split_index_5 = xmlET.SubElement(split_set_5, "SplittableFieldIndex")
            split_index_5.attrib = {"distributionvalue": "100", "splitindex": "0"}
            split_5_custom = xmlET.SubElement(split_index_5, "CustomFieldValue")
            split_5_custom.attrib = {"name": "Program"}
            split_5_custom_val = xmlET.SubElement(split_5_custom, "Value")
            split_5_custom_val.text = "D13-A"
            print("Split Set 5, Program: \'D13-A\'")

            # Split Field 6 (Department) (Under Buyer Invoice Line)
            split_set_6 = xmlET.SubElement(split_set_group, "SplittableFieldIndexSet")
            split_set_6.attrib = {"distributiontype": "PercentOfPrice", "context": "Line"}
            split_index_6 = xmlET.SubElement(split_set_6, "SplittableFieldIndex")
            split_index_6.attrib = {"distributionvalue": "100", "splitindex": "0"}
            split_6_custom = xmlET.SubElement(split_index_6, "CustomFieldValue")
            split_6_custom.attrib = {"name": "Department"}
            split_6_custom_val = xmlET.SubElement(split_6_custom, "Value")
            split_6_custom_val.text = f'{dep_id}-A'
            print(f"Split Set 6, Department: {dep_id}-A")

            # Split Field 7 (SpeedType Class [classLink]) (Under Buyer Invoice Line)
            split_set_7 = xmlET.SubElement(split_set_group, "SplittableFieldIndexSet")
            split_set_7.attrib = {"distributiontype": "PercentOfPrice", "context": "Line"}
            split_index_7 = xmlET.SubElement(split_set_7, "SplittableFieldIndex")
            split_index_7.attrib = {"distributionvalue": "100", "splitindex": "0"}
            split_7_custom = xmlET.SubElement(split_index_7, "CustomFieldValue")
            split_7_custom.attrib = {"name": "classLink"}
            split_7_custom_val = xmlET.SubElement(split_7_custom, "Value")
            split_7_custom_val.text = "none-A"
            print("Split Set 7, SpeedType Class [classLink]: \'none-A\'")

            # Split Field 8 (Class) (Under Buyer Invoice Line)
            split_set_8 = xmlET.SubElement(split_set_group, "SplittableFieldIndexSet")
            split_set_8.attrib = {"distributiontype": "PercentOfPrice", "context": "Line"}
            split_index_8 = xmlET.SubElement(split_set_8, "SplittableFieldIndex")
            split_index_8.attrib = {"distributionvalue": "100", "splitindex": "0"}
            split_8_custom = xmlET.SubElement(split_index_8, "CustomFieldValue")
            split_8_custom.attrib = {"name": "Class"}
            split_8_custom_val = xmlET.SubElement(split_8_custom, "Value")
            split_8_custom_val.text = "none"
            print("Split Set 8, Class: \'none\'")

            # Split Field 9 (Project) (Under Buyer Invoice Line)
            split_set_9 = xmlET.SubElement(split_set_group, "SplittableFieldIndexSet")
            split_set_9.attrib = {"distributiontype": "PercentOfPrice", "context": "Line"}
            split_index_9 = xmlET.SubElement(split_set_9, "SplittableFieldIndex")
            split_index_9.attrib = {"distributionvalue": "100", "splitindex": "0"}
            split_9_custom = xmlET.SubElement(split_index_9, "CustomFieldValue")
            split_9_custom.attrib = {"name": "Project"}
            split_9_custom_val = xmlET.SubElement(split_9_custom, "Value")
            split_9_custom_val.text = "none"
            print("Split Set 9, Project: \'none\'")

            # Split Field 10 (Activity Id) (Under Buyer Invoice Line)
            split_set_10 = xmlET.SubElement(split_set_group, "SplittableFieldIndexSet")
            split_set_10.attrib = {"distributiontype": "PercentOfPrice", "context": "Line"}
            split_index_10 = xmlET.SubElement(split_set_10, "SplittableFieldIndex")
            split_index_10.attrib = {"distributionvalue": "100", "splitindex": "0"}
            split_10_custom = xmlET.SubElement(split_index_10, "CustomFieldValue")
            split_10_custom.attrib = {"name": "Activity Id"}
            split_10_custom_val = xmlET.SubElement(split_10_custom, "Value")
            split_10_custom_val.text = "none"
            print("Split Set 10, Activity Id: \'none\'")


        self.createdXML = xml_root
        print("XML Object Created")
        return self.createdXML

    # retrieves the XML Element Tree as a string
    def getXMLString(self, xml_root=None):
        print("Retrieving XML String...")
        if not xml_root:
            if not self.createdXML:
                print("No XML Created Yet")
                return
            else:
                xml_root = self.createdXML
        xml_string = xmlET.tostring(xml_root)
        xml_string = minidom.parseString(xml_string)
        xml_string = xml_string.toprettyxml(indent="   ")
        print("XML String Retrieved")
        print(xml_string)
        return xml_string

    def saveXML(self, xml_string=None):
        print("Saving XML to file")
        if not xml_string:
            if not self.XMLstring:
                self.XMLstring = self.getXMLString()
            xml_string = self.XMLstring

        file_out_path = f"xmlBatchVouchers\\{self.batchGroup}\\{self.JsonName[-24:-5]}.xml"
        with open(file_out_path, "w") as f:
            f.write(xml_string)

        with open(file_out_path, 'r+') as out:
            file_headers = "<?xml version=\"1.0\"?>\n<!DOCTYPE BuyerInvoiceOcrMessage SYSTEM\n" \
                           "\"https://integrations.sciquest.com/app_docs/dtd/buyerinvoice/BuyerInvoiceOCR.dtd\">"
            content = out.read()
            print(content[22:])
            out.seek(0, 0)
            out.write(file_headers.rstrip('\r\n') + content[22:])
        print(f"XML Saved to: {file_out_path}")
        return file_out_path


if __name__ == "__main__":
    converter = voucherDataConverter("config.json", "2021-11-22_16-44-12.json")
    converter.ConvertFOLIOBatchVoucher()
    print(converter.getXMLString())
    converter.saveXML()
