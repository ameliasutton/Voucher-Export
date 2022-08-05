import json
import tkinter as tk
from popupWindow import popupWindow
import folio_api_aneslin as api
import requests


class loginMenu:
    def __init__(self, config, prompt=None):
        if not prompt:
            prompt = 'Please Input API Login Credentials:'
        # Read Config File
        self.configFileName = config
        try:
            with open(config, "r") as c:
                config = json.load(c)
                url = config["url"]
                tenant = config["tenant"]
                token = config["token"]
        except ValueError:
            print(f"| ERROR | Config file \"{config}\" not found")
            popupWindow(f"Config file \"{config}\" not found")

        # Create Requester
        try:
            self.requester = api.requestObject(url, tenant)
            self.requester.setToken(token)

            # Create Session
            headers = {'Content-Type': 'application/json',
                       'x-okapi-tenant': config["tenant"],
                       'x-okapi-token': self.requester.token,
                       'Accept': 'application/json'}
            self.session = requests.Session()
            self.session.headers = headers
        except Exception as e:
            print(f"| Warn | {e}")
            popupWindow(e)

        self.root = tk.Tk()
        self.root.rowconfigure([0, 1, 2, 3], minsize=10)
        self.root.columnconfigure([0, 1], minsize=10)

        self.prompt = tk.Label(master=self.root, text=prompt, font='TkDefaultFont 12 bold')
        self.prompt.grid(row=0, column=0, columnspan=2)

        self.userPrompt = tk.Label(master=self.root, text='Username: ', font='TkDefaultFont 10 bold')
        self.userPrompt.grid(row=1, column=0)

        self.userInput = tk.Entry(master=self.root)
        self.userInput.grid(row=1, column=1)

        self.passPrompt = tk.Label(master=self.root, text='Password: ', font='TkDefaultFont 10 bold')
        self.passPrompt.grid(row=2, column=0)

        self.passInput = tk.Entry(master=self.root, show='*')
        self.passInput.grid(row=2, column=1)

        self.submit = tk.Button(master=self.root, text='Submit', command=self.Submit)
        self.submit.grid(row=3, column=0, columnspan=2)

        self.root.mainloop()

    def Submit(self):
        username = self.userInput.get()
        password = self.passInput.get()
        try:
            self.requester.retrieveToken(username, password)
        except Exception as e:
            print(f"| Warn | {e}")
            popupWindow(e)

        with open(self.configFileName, 'r') as old_config:
            config = json.load(old_config)
        config['token'] = self.requester.token
        with open(self.configFileName, 'w') as new_config:
            new_config.write(json.dumps(config, indent=4))

        print('Login Successful. Token Updated in config')
        self.root.destroy()
        popupWindow('Login Successful.\nToken Updated in config')
