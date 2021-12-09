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
            400: "Bad Request, e.g. malformed request body or query parameter. Details of the error (e.g. name of the "
                 "parameter or line/character number with malformed data) provided in the response.",
            401: "Not authorized to perform requested action",
            403: "Forbidden",
            404: "Not Found",
            408: "Request Timeout",
            500: "Internal server error, e.g. due to misconfiguration"

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

# verifies token is working, if not, prompts for new user/pass
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

    def singleGet(self, modURL, session):
        url = self.url + modURL
        returned = session.get(url)
        if returned.status_code in self.responseErrors.keys():
            sys.exit("Response Status Code: " + str(returned.status_code) + " " + str(self.responseErrors[returned.status_code]))
        return returned.json()

    def post(self, modURL, session, payload):
        headers = {'Content-Type': 'application/json',
                   'x-okapi-tenant': self.tenant,
                   'x-okapi-token': self.token}
        url = self.url + modURL
        returned = requests.post(url,headers=headers, data=json.dumps(payload))

        if returned.status_code in self.responseErrors.keys():
            print("\n\n" + returned.request + "\n\n")
            sys.exit(f"Response Status code: {str(returned.status_code)} "
                     f"{str(self.responseErrors[returned.status_code])}\n\n")

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
