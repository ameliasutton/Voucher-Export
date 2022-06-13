import folio_api_aneslin
import json
import requests
from loginMenu import loginMenu
from popupWindow import popupWindow


def addInvoiceDates(filename, configName):
    try:
        with open(configName, 'r') as config:
            config = json.load(config)
            requester = folio_api_aneslin.requestObject(config['url'], config['tenant'], config['token'])
            if requester.testToken() == -1:
                loginMenu(configName, 'Login Failed, please input new credentials')
    except Exception as e:
        raise e
    session = requests.Session()
    headers = {'Content-Type': 'application/json',
               'x-okapi-tenant': config["tenant"],
               'x-okapi-token': requester.token,
               'Accept': 'application/json'}
    session.headers = headers
    session.params = {"limit": "1000"}
    with open(filename, 'r') as json_in:
        json_data = json.load(json_in)
    for i, voucher in enumerate(json_data['batchedVouchers']):
        identifier = voucher['voucherNumber']
        try:
            response = requester.singleGet(f"invoice/invoices?query=voucherNumber="
                                            f"\"{str(identifier)}\"", session)
            json_data['batchedVouchers'][i]["invoiceDate"] = response['invoices'][0]['invoiceDate']
        except Exception as e:
            print(e)

    with open(filename, 'w') as json_out:
        json_out.write(json.dumps(json_data, indent=4))


