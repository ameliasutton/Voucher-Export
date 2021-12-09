import requests
import json
import sys


class requestObject():
    def __init__(self, url, tenant, token=None):
        if url[-1] == '/':
            self.url = url
        else:
            self.url = url + '/'
        self.tenant = tenant
        self.token = token
        # TODO: Fill this dict with more possible errors
        self.responseErrors = {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            408: "Request Timeout",
            500: "Internal Server Record"

        }

    def retrieveToken(self, userName, Password):

        headers = {'Content-Type': 'application/json',
                   'x-okapi-tenant': self.tenant}
        payload = {"username": userName,
                   "password": Password}
        connection_url = self.url + "authn/login"
        login = requests.post(connection_url, headers=headers, data=json.dumps(payload))

        try:
            self.token = login.headers['x-okapi-token']

        except KeyError:
            print(login.text)
            sys.exit("Login Failed")

# Sets token if provided
    def setToken(self, t):
        self.token = t

# verifys token is working, if not, prompts for new user/pass
    def testToken(self):
        headers = {'Content-Type': 'application/json',
                   'x-okapi-tenant': self.tenant, 'x-okapi-token': self.token}
        connection_url = self.url + "batch-groups"
        test = requests.get(connection_url, headers=headers)
        if test.status_code == 401:
            print("Token Failed with status code: 401")
            print("Please input updated username and password...")
            self.retrieveToken(input("Username: "), input("Password: "))
        else:
            return

# repeats a get request and returns the combined results.
    def paging(self, modURL, inc, session, topLevel=None):
        url = self.url + modURL
        result = session.get(url).json()
        pages = result['totalRecords']
        for index, page in enumerate(range(0, pages+1, inc)):
            if topLevel:
                next_page = session.get(url, params={"offset":page}).json()[topLevel]
            else:
                next_page = session.get(url, params={"offset":page}).json()
            yield next_page

    def singleRequest(self, modURL, session, topLevel=None):
        url = self.url + modURL
        returned = session.get(url)
        if returned.status_code in self.responseErrors.keys():
            sys.exit("Response Status Code: " + str(returned.status_code) + " " + str(self.responseErrors[returned.status_code]))
        return returned.json()


if __name__ == '__main__':
    x = open("inputData.json", "r")
    credentials = json.load(x)
    tok = requestObject(credentials['url'], credentials['tenant'])
    tok.retrieveToken(credentials['username'], credentials['password'])
    head = {'Content-Type': 'application/json', 'x-okapi-tenant': credentials['tenant'],
            'x-okapi-token': tok.token, 'Accept': 'application/json'}
    s = requests.Session()
    s.headers = head
    s.params = {"limit": "100"}

    x = tok.paging('organizations-storage/organizations', 100, s, 'organizations')

    print(json.dumps(next(x), indent=4))
