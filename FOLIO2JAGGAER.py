import json
import xml.etree.ElementTree as xmlET
import os
import glob
from xml.dom import minidom


class json2xmlConverter:

    def __init__(self, config, jsonName=None, xmlName=None):
        try:
            with open(config, "r") as readFile:
                config = json.load(readFile)
                self.user = config["jaggaerIdentity"]
                self.secret = config["jaggaerSecret"]
                self.batchGroup = config["batchGroup"]
        except FileNotFoundError:
            exit(f"Config File \"{config}\" Not Found")
        self.JsonName = jsonName
        if jsonName:
            with open(f"jsonBatchVouchers/{self.batchGroup}/{jsonName}", "r") as jsonIn:
                self.selectedJson = json.load(jsonIn)
        else:
            self.retrieveMostRecentJSON()
        if xmlName:
            self.createdXML = xmlET.parse(xmlName)
            self.XMLstring = self.getXMLstring()
        else:
            self.createdXML = None
            self.XMLstring = None

    # locates most recently created json
    def retrieveMostRecentJSON(self):
        folder_path = os.getcwd() + "/jsonBatchVouchers/" + self.batchGroup
        file_type = '/*json'
        files = glob.glob(folder_path + file_type)
        try:
            max_file = max(files, key=os.path.getctime)
        except FileNotFoundError:
            exit(f"No json files found in {folder_path}")
        self.JsonName = max_file
        file_out = json.load(open(max_file, 'r'))
        self.selectedJson = file_out
        return self.selectedJson

    # Takes in a json dict
    def ConvertFOLIOBatchVoucher(self):
        if not self.selectedJson:
            print("No JSON file selected")
            return
        if self.selectedJson["batchGroup"] != self.batchGroup:
            exit("Batch Group in Voucher json does not match Batch Group in config.")
        print("test")

        xml_root = xmlET.Element("BuyerInvoiceOcrMessage")
        xml_root.attrib = {"version": "1.0"}

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
            invoice_line = xmlET.SubElement(xml_root, "BuyerInvoiceOrc")
            invoice_header = xmlET.SubElement(invoice_line, "BuyerInvoiceHeader")

            invoice_number = xmlET.SubElement(invoice_header, "SupplierInvoiceNumber")
            invoice_number.text = voucher["vendorInvoiceNo"]

            invoice_type = xmlET.SubElement(invoice_header, "InvoiceType")
            invoice_type.text = "Invoice"

            # Bill To Information (Under Invoice Header)
            bill_to = xmlET.SubElement(invoice_header, "BillTo")
            bill_to_address = xmlET.SubElement(bill_to, "Address")

            bill_to_address_code = xmlET.SubElement(bill_to_address, "AddressCode")
            bill_to_address_code.text = "TODO address code"
            bill_to_contact = xmlET.SubElement(bill_to_address, "ContactName")
            bill_to_contact.text = "TODO contact"
            bill_to_city = xmlET.SubElement(bill_to_address, "City")
            bill_to_city.text = "Amherst"
            bill_to_state = xmlET.SubElement(bill_to_address, "State")
            bill_to_state.text = "MA"
            bill_to_postal = xmlET.SubElement(bill_to_address, "PostalCode")
            bill_to_postal.text = "TODO postal code"
            bill_to_country = xmlET.SubElement(bill_to_address, "Country")
            bill_to_country.attrib = {"isoCountryCode": "US"}

            # Remit To Information (Under Invoice Header)
            remit_to = xmlET.SubElement(invoice_header, "RemitTo")
            remit_to_address = xmlET.SubElement(remit_to, "Address")

            remit_to_address_code = xmlET.SubElement(remit_to_address, "AddressCode")
            remit_to_address_code.text = "TODO address code"
            remit_to_contact = xmlET.SubElement(remit_to_address, "ContactName")
            remit_to_contact.text = "TODO contact"
            remit_to_city = xmlET.SubElement(remit_to_address, "City")
            remit_to_city.text = "TODO city"
            remit_to_state = xmlET.SubElement(remit_to_address, "State")
            remit_to_state.text = "TODO state"
            remit_to_postal = xmlET.SubElement(remit_to_address, "PostalCode")
            remit_to_postal.text = "TODO postal code"
            remit_to_country = xmlET.SubElement(remit_to_address, "Country")
            remit_to_country.attrib = {"isoCountryCode": "TODO Country Code"}

            # Ship To Information (Under Invoice Header)
            ship_to = xmlET.SubElement(invoice_header, "ShipTo")
            ship_to_address = xmlET.SubElement(ship_to, "Address")

            ship_to_address_code = xmlET.SubElement(ship_to_address, "AddressCode")
            ship_to_address_code.text = "TODO address code"
            ship_to_contact = xmlET.SubElement(ship_to_address, "ContactName")
            ship_to_contact.text = "TODO contact"
            ship_to_city = xmlET.SubElement(ship_to_address, "City")
            ship_to_city.text = "TODO city"
            ship_to_state = xmlET.SubElement(ship_to_address, "State")
            ship_to_state.text = "TODO state"
            ship_to_postal = xmlET.SubElement(ship_to_address, "PostalCode")
            ship_to_postal.text = "TODO postal code"
            ship_to_country = xmlET.SubElement(ship_to_address, "Country")
            ship_to_country.attrib = {"isoCountryCode": "TODO Country Code"}

            # Terms Information (Under Invoice Header)
            terms = xmlET.SubElement(invoice_header, "Terms")
            discount_amount = xmlET.SubElement(terms, "DiscountAmount")
            money = xmlET.SubElement(discount_amount, "Money")
            money.attrib = {"currency": "USD"}
            money.text = "0"

            # Due Date Information (Under Invoice Header)
            due_date = xmlET.SubElement(invoice_header, "DueDate")
            due_date.text = "TODO Due Date"

            # Grand Total Information (Under Invoice Header)
            grand_total = xmlET.SubElement(invoice_header, "GrantTotal")
            grand_total_money = xmlET.SubElement(grand_total, "Money")
            grand_total_money.attrib = {"currency": "USD"}
            grand_total_money.text = str(voucher["amount"])

            # Sub Total Information (Under Invoice Header)
            sub_total = xmlET.SubElement(invoice_header, "Subtotal")
            sub_total_money = xmlET.SubElement(sub_total, "Money")
            sub_total_money.attrib = {"currency": "USD"}
            sub_total_money.text = "TODO SubTotal"

            # Notes (Under Invoice Header)
            notes = xmlET.SubElement(invoice_header, "Notes")
            notes.text = "TODO: Notes"

            # Business Unit (Under Invoice Header)
            business_unit = xmlET.SubElement(invoice_header, "BusinessUnit")
            business_unit.attrib = {"internalName": "TODO internal name"}

            # Supplier (Under Invoice Header)
            supplier = xmlET.SubElement(invoice_header, "Supplier")
            supplier_contact = xmlET.SubElement(supplier, "ContactInfo")
            supplier_phone = xmlET.SubElement(supplier_contact, "Phone")
            supplier_phone_number = xmlET.SubElement(supplier_phone, "TelephoneNumber")
            supplier_phone_country = xmlET.SubElement(supplier_phone_number, "CountryCode")
            supplier_phone_country.text = "TODO: country code"
            supplier_phone_area = xmlET.SubElement(supplier_phone_number, "AreaCode")
            supplier_phone_area.text = "TODO: area code"
            supplier_phone_number_number = xmlET.SubElement(supplier_phone_number, "Number")
            supplier_phone_number_number.text = "TODO: Phone Number"

            # Shipping Charges Information (Under Invoice Header)
            shipping_charges = xmlET.SubElement(invoice_header, "ShippingCharges")
            shipping_charges_money = xmlET.SubElement(shipping_charges, "Money")
            shipping_charges_money.attrib = {"currency": "USD"}
            shipping_charges_money.text = "TODO: Shiping Charge"

            # Handling Charges Information (Under Invoice Header)
            handling_charges = xmlET.SubElement(invoice_header, "HandlingCharges")
            handling_charges_money = xmlET.SubElement(handling_charges, "Money")
            handling_charges_money.attrib = {"currency": "USD"}
            handling_charges_money.text = "TODO Money"

            # Tax 1 Information (Under Invoice Header)
            tax_1 = xmlET.SubElement(invoice_header, "Tax1")
            tax1_money = xmlET.SubElement(tax_1, "Money")
            tax1_money.attrib = {"currency": "USD"}
            tax1_money.text = "TODO Tax 1"

            # Tax 2 Information (Under Invoice Header)
            tax_2 = xmlET.SubElement(invoice_header, "Tax2")
            tax2_money = xmlET.SubElement(tax_2, "Money")
            tax2_money.attrib = {"currency": "USD"}
            tax2_money.text = "TODO Tax 2"

            # OCR Images (Under Invoice Header)
            ocr_images = xmlET.SubElement(invoice_header, "OCRImages")
            ocr_image = xmlET.SubElement(ocr_images, "OCRImage")
            ocr_image.attrib = {"id": "", "type": "URL"}
            ocr_image_url = xmlET.SubElement(ocr_image, "OCRImageURL")
            ocr_image_url.text = "TODO: URL"
            ocr_image_name = xmlET.SubElement(ocr_image, "OCRImageName")
            ocr_image_name.text = "TODO: Name"

            # Buyer Invoice Line Begins
            buyer_invoice_line = xmlET.SubElement(invoice_line, "BuyerInvoiceLine")
            buyer_invoice_line.attrib = {"lineNumber": "001"}

            # Item (Under Buyer Invoice Line)
            item = xmlET.SubElement(buyer_invoice_line, "Item")
            item_cat_no = xmlET.SubElement(item, "CatalogNumber")
            item_cat_no.text = "TODO CatNo"
            item_units = xmlET.SubElement(item, "UnitOfMeasure")
            item_units.text = "TODO Units"

            # Quantity (Under Buyer Invoice Line)
            quantity = xmlET.SubElement(buyer_invoice_line, "Quantity")
            quantity.text = "TODO quantity"

            # Unit Price (Under Buyer Invoice Line)
            unit_price = xmlET.SubElement(buyer_invoice_line, "UnitPrice")
            unit_price_money = xmlET.SubElement(unit_price, "Money")
            unit_price_money.attrib = {"currency": "USD"}
            unit_price_money.text = "TODO: Money"

            # Splittable Field Set Group Start (Under Buyer Invoice Line)
            split_set_group = xmlET.SubElement(buyer_invoice_line, "SplittableFieldSetGroup")

            # Split Field 1 (Campus) (Under Buyer Invoice Line)
            split_set_1 = xmlET.SubElement(split_set_group, "SplittableFieldIndexSet")
            split_set_1.attrib = {"distributiontype": "PercentOfPrice", "context": "Line"}
            split_index_1 = xmlET.SubElement(split_set_1, "SplittableFieldIndex")
            split_index_1.attrib = {"distributionbalue": "100", "splitindex": "0"}
            split_1_custom = xmlET.SubElement(split_index_1, "CustomFieldValue")
            split_1_custom.attrib = {"name": "Campus"}
            split_1_custom_val = xmlET.SubElement(split_1_custom, "Value")
            split_1_custom_val.text = "TODO: Campus Value"

            # Split Field 2 (Speedtype) (Under Buyer Invoice Line)
            split_set_2 = xmlET.SubElement(split_set_group, "SplittableFieldIndexSet")
            split_set_2.attrib = {"distributiontype": "PercentOfPrice", "context": "Line"}
            split_index_2 = xmlET.SubElement(split_set_2, "SplittableFieldIndex")
            split_index_2.attrib = {"distributionbalue": "100", "splitindex": "0"}
            split_2_custom = xmlET.SubElement(split_index_2, "CustomFieldValue")
            split_2_custom.attrib = {"name": "Speedtype"}
            split_2_custom_val = xmlET.SubElement(split_2_custom, "Value")
            split_2_custom_val.text = "TODO: Speedtype"

            # Split Field 3 (Fund) (Under Buyer Invoice Line)
            split_set_3 = xmlET.SubElement(split_set_group, "SplittableFieldIndexSet")
            split_set_3.attrib = {"distributiontype": "PercentOfPrice", "context": "Line"}
            split_index_3 = xmlET.SubElement(split_set_3, "SplittableFieldIndex")
            split_index_3.attrib = {"distributionbalue": "100", "splitindex": "0"}
            split_3_custom = xmlET.SubElement(split_index_3, "CustomFieldValue")
            split_3_custom.attrib = {"name": "Fund"}
            split_3_custom_val = xmlET.SubElement(split_3_custom, "Value")
            split_3_custom_val.text = "TODO: Fund Code"

            # Split Field 4 (Account) (Under Buyer Invoice Line)
            split_set_4 = xmlET.SubElement(split_set_group, "SplittableFieldIndexSet")
            split_set_4.attrib = {"distributiontype": "PercentOfPrice", "context": "Line"}
            split_index_4 = xmlET.SubElement(split_set_4, "SplittableFieldIndex")
            split_index_4.attrib = {"distributionbalue": "100", "splitindex": "0"}
            split_4_custom = xmlET.SubElement(split_index_4, "CustomFieldValue")
            split_4_custom.attrib = {"name": "Account"}
            split_4_custom_val = xmlET.SubElement(split_4_custom, "Value")
            split_4_custom_val.text = "TODO: Account Value"

            # Split Field 5 (Program) (Under Buyer Invoice Line)
            split_set_5 = xmlET.SubElement(split_set_group, "SplittableFieldIndexSet")
            split_set_5.attrib = {"distributiontype": "PercentOfPrice", "context": "Line"}
            split_index_5 = xmlET.SubElement(split_set_5, "SplittableFieldIndex")
            split_index_5.attrib = {"distributionbalue": "100", "splitindex": "0"}
            split_5_custom = xmlET.SubElement(split_index_5, "CustomFieldValue")
            split_5_custom.attrib = {"name": "Program"}
            split_5_custom_val = xmlET.SubElement(split_5_custom, "Value")
            split_5_custom_val.text = "TODO: Program Value"

            # Split Field 6 (Department) (Under Buyer Invoice Line)
            split_set_6 = xmlET.SubElement(split_set_group, "SplittableFieldIndexSet")
            split_set_6.attrib = {"distributiontype": "PercentOfPrice", "context": "Line"}
            split_index_6 = xmlET.SubElement(split_set_6, "SplittableFieldIndex")
            split_index_6.attrib = {"distributionbalue": "100", "splitindex": "0"}
            split_6_custom = xmlET.SubElement(split_index_6, "CustomFieldValue")
            split_6_custom.attrib = {"name": "Department"}
            split_6_custom_val = xmlET.SubElement(split_6_custom, "Value")
            split_6_custom_val.text = "TODO: Department Value"

        self.createdXML = xml_root
        return self.createdXML

    def getXMLstring(self, xml_root=None):
        if not xml_root:
            if not self.createdXML:
                print("No XML Created Yet")
                return
            else:
                xml_root = self.createdXML
        xml_string = minidom.parseString(xmlET.tostring(xml_root)).toprettyxml(indent="   ")
        return xml_string

    def saveXML(self, xml_string=None):
        if not xml_string:
            if not self.XMLstring:
                self.XMLstring = self.getXMLstring()
            xml_string = self.XMLstring

        file_out_path = f"xmlBatchVouchers\\{self.batchGroup}\\{self.JsonName[-24:-5]}.xml"
        print(file_out_path)
        with open(file_out_path, "w") as f:
            f.write(xml_string)

        with open(file_out_path, 'r+') as out:
            file_headers = "<?xml version=\"1.0\"?>\n<!DOCTYPE BuyerInvoiceOcrMessage SYSTEM\n" \
                           "\"https://integrations.sciquest.com/app_docs/dtd/buyerinvoice/BuyerInvoiceOCR.dtd\">"
            content = out.read()
            print(content[22:])
            out.seek(0, 0)
            out.write(file_headers.rstrip('\r\n') + content[22:])


if __name__ == "__main__":
    converter = json2xmlConverter("config.json", "2021-11-22_16-44-12.json")
    converter.ConvertFOLIOBatchVoucher()
    print(converter.getXMLstring())
    converter.saveXML()

