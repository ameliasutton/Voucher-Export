import requests
import json
import sys
from datetime import datetime
import logging

class requestObject:
    def __init__(self, url, tenant, user=None, password=None):
        if url[-1] == '/':
            self.url = url
        else:
            self.url = url + '/'
        self.tenant = tenant
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json', 'x-okapi-tenant': self.tenant, 'Accept': "application/json"})
        if user and password:
            self.retrieveToken(user, password)


# makes post call to authn/login to request a fresh token
    def retrieveToken(self, user, password):
        payload = json.dumps({"username": user,
                   "password": password})
        headers = {'Content-Type': 'application/json', 'x-okapi-tenant': self.tenant}
        connection_url = self.url + "authn/login-with-expiry"
        login = self.session.post(connection_url, data=payload, headers=headers, timeout=10)
        if login.status_code >= 400:
            raise Exception(f'Login Failed, {login.status_code}: {login.reason}')
        return 0
        
    def checkTokenExpiry(self):
        logging.info("Checking Token Expiry...")
        for cookie in self.session.cookies:
            if cookie.name == 'folioAccessToken':
                if (datetime.fromtimestamp(cookie.expires)-datetime.now()).total_seconds() <= 65 :
                    logging.info("Token needs to be refreshed...")
                    self.refreshToken()
                else:
                    logging.info("Token still valid!")
        return 0
    
    def refreshToken(self):
        url = self.url + "authn/refresh"
        login = self.session.post(url, timeout=10)
        if login.status_code == 201:
            logging.info("Token Refreshed!")

# repeats a get request and returns the combined results.
    def paging(self, modURL, inc, topLevel=None):
        url = self.url + modURL
        result = self.session.get(url).json()
        pages = result['totalRecords']
        for page in range(0, pages+1, inc):
            if topLevel:
                next_page = self.session.get(url, params={"offset":page}).json()[topLevel]
            else:
                next_page = self.session.get(url, params={"offset":page}).json()
            yield next_page

    def singleGet(self, modURL):
        self.checkTokenExpiry()
        url = self.url + modURL
        returned = self.session.get(url, timeout=10)
        if returned.status_code >= 300:
            raise Exception(f"Response Status Code: {str(returned.status_code)} {str(returned.reason)}")
        return returned.json()

    def post(self, modURL, payload):
        url = self.url + modURL
        logging.info(url)
        self.checkTokenExpiry()
        returned = self.session.post(url, data=json.dumps(payload))
        return self.checkResponse(returned)

    def put(self, modURL, payload):
        url = self.url + modURL
        logging.info(url)
        self.checkTokenExpiry()
        returned = self.session.put(url, data=json.dumps(payload))
        return self.checkResponse(returned)

    def checkResponse(self, returned):
        if returned.status_code >= 300:
            requestbody = json.loads(returned.request.body)
            logging.info(f"Request Body:\n{json.dumps(requestbody, indent=4)}")
            logging.info(f"Response Status code: {str(returned.status_code)}{str(returned.reason)}")
            return {"error": True}

        logging.info(f"Response:\n{json.dumps(returned.json(), indent=4)}")
        return returned.json()
