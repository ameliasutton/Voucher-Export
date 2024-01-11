import json
import tkinter as tk
from popupWindow import popupWindow
import folio_api_aneslin as api
import batchMenu
from voucherBatcher import VoucherBatchRetriever
import logging


class loginMenu:
    def __init__(self, config, prompt=None):
        if not prompt:
            prompt = 'Please Input API Login Credentials:'
        # Read Config File
        self.config_name = config
        try:
            with open(config, "r") as c:
                config = json.load(c)
                url = config["url"]
                tenant = config["tenant"]
                defaultUsername = config["defaultUsername"]
        except Exception as e:
            raise(e)


        # Create Requester
        try:
            self.requester = api.requestObject(url, tenant)
        except Exception as e:
            logging.exception(e)
            popupWindow(e)

        self.root = tk.Tk()
        self.root.rowconfigure([0, 1, 2, 3], minsize=10)
        self.root.columnconfigure([0, 1], minsize=10)

        self.prompt = tk.Label(master=self.root, text=prompt, font='TkDefaultFont 12 bold')
        self.prompt.grid(row=0, column=0, columnspan=2)

        self.userPrompt = tk.Label(master=self.root, text='Username: ', font='TkDefaultFont 10 bold')
        self.userPrompt.grid(row=1, column=0)

        self.userInput = tk.Entry(master=self.root)
        self.userInput.insert(0, defaultUsername)
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
            retriever = VoucherBatchRetriever(self.config_name, self.requester)
        except Exception as e:
            logging.exception(e)
            popupWindow(e)
            return -1
        if retriever.selectMostRecentBatch() == -1:
            if retriever.triggerBatch() == -1:
                logging.warning("No existing batches found, and batch creation failed.")
                popupWindow("No existing batches and batch creation failed.")
        else:
            logging.info(retriever.getVoucherStatus())
        logging.info('Login Successful. Token Updated in config')
        self.root.destroy()
        batchMenu.batchMenu(retriever, self.config_name)
