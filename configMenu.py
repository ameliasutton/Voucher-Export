import sys
import loginMenu
import batchMenu
import tkinter as tk
from popupWindow import popupWindow
from voucherBatcher import VoucherBatchRetriever


class configMenu:
    def __init__(self):
        self.config_menu = tk.Tk()
        self.config_menu.wm_title("FOLIO Voucher Export - Config Menu")
        self.config_menu.columnconfigure([0, 1], minsize=100)
        self.config_menu.rowconfigure([0, 1, 2], minsize=4)

        self.config_prompt = tk.Label(master=self.config_menu, text="Please select a config file to use:\n")
        self.config_prompt.grid(row=0, column=0, columnspan=3)

        self.default_prompt = tk.Label(master=self.config_menu, text="Select Default Config:")
        self.default_prompt.grid(row=1, column=0)
        self.default_button = tk.Button(master=self.config_menu, text="   Default config.json    ",
                                        command=self.defaultLaunch)
        self.default_button.grid(row=1, column=1)

        self.config_input_prompt = tk.Label(master=self.config_menu, text="Input File Name:         ")
        self.config_input_prompt.grid(row=2, column=0)
        self.config_input_box = tk.Entry(master=self.config_menu, text="configUMass.json")
        self.config_input_box.grid(row=2, column=1)
        self.config_input_submit = tk.Button(master=self.config_menu, text="Submit",
                                             command=self.customLaunch).grid(row=2, column=2)

        self.config_menu_bar = tk.Menu(master=self.config_menu)
        self.config_file = tk.Menu(master=self.config_menu_bar, tearoff=0)
        self.config_file.add_command(label="Exit", command=sys.exit)
        self.config_menu_bar.add_cascade(label="File", menu=self.config_file)
        self.config_menu.config(menu=self.config_menu_bar)

        self.config_menu.mainloop()

    def defaultLaunch(self):
        config_name = "config.json"
        try:
            retriever = VoucherBatchRetriever(config_name)
            if retriever.selectMostRecentBatch() == -1:
                if retriever.triggerBatch() == -1:
                    popupWindow("No existing batches and batch creation failed.")
            self.config_menu.destroy()
            batchMenu.batchMenu(retriever, config_name)
        except Exception as e:
            if e.args[0] == 'Token rejected, new login credentials required':
                loginMenu.loginMenu(config_name, e.args[0])
            else:
                popupWindow(e)
                raise e

    def customLaunch(self):
        config_name = self.config_input_box.get()
        try:
            retriever = VoucherBatchRetriever(config_name)
            if retriever.selectMostRecentBatch() == -1:
                retriever.triggerBatch()
            self.config_menu.destroy()
            batchMenu.batchMenu(retriever, config_name)
        except Exception as e:
            if e.args[0] == 'Token rejected, new login credentials required':
                loginMenu.loginMenu(config_name, e.args[0])
            else:
                popupWindow(e)
