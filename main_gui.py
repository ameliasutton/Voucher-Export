import voucherBatcher
import FOLIO2JAGGAER
import tkinter as tk
import sys
from logger import logger


class popupWindow:
    def __init__(self, text):
        self.popup = tk.Tk()
        self.popup.wm_title("Popup Notice")
        self.popup.columnconfigure(0, minsize=100)
        self.popup.rowconfigure([0, 1], minsize=2)

        self.text_label = tk.Label(master=self.popup, text=text)
        self.text_label.grid(row=0, column=0)
        self.close_button = tk.Button(master=self.popup, text="OK", command=self.close)
        self.close_button.grid(row=1, column=0)

        self.popup.mainloop()

    def close(self):
        self.popup.destroy()


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

        self.config_menu.bind("<Return>", self.return_pressed)

        self.config_menu.mainloop()

    def return_pressed(self, event):
        self.customLaunch()

    def defaultLaunch(self):
        global retriever
        global configName
        configName = "config.json"
        try:
            retriever = voucherBatcher.VoucherBatchRetriever(configName)
        except Exception as e:
            popupWindow(e)
        if retriever.selectMostRecentBatch() == -1:
            retriever.triggerBatch()
        self.config_menu.destroy()
        batchMenu()

    def customLaunch(self, event=None):
        global retriever
        global configName
        configName = self.config_input_box.get()
        try:
            retriever = voucherBatcher.VoucherBatchRetriever(configName)
        except Exception as e:
            popupWindow("Config File Not Found.\nPlease Check File Name\nand try again")
            raise e

        if retriever.selectMostRecentBatch() == -1:
            retriever.triggerBatch()
        self.config_menu.destroy()
        batchMenu()


class batchMenu:

    def __init__(self):
        self.batch_menu = tk.Tk()
        self.batch_menu.wm_title("FOLIO Voucher Export - Batch Menu")
        self.batch_menu.columnconfigure([0, 1, 2], minsize=200)
        self.batch_menu.rowconfigure([0, 1, 2, 3, 4, 5, 6, 7, 8], minsize=9)

        self.voucher_desc = tk.Label(master=self.batch_menu, text="Currently Selected Batch Ran:")
        self.voucher_desc.grid(row=0, column=0, columnspan=3)

        self.voucher_current = tk.Label(master=self.batch_menu, text=retriever.batchEndDate[0:-5].replace("T", " at "))
        self.voucher_current.grid(row=1, column=0, columnspan=3)

        self.status_desc = tk.Label(master=self.batch_menu, text="Currently Selected Batch Status:")
        self.status_desc.grid(row=2, column=1)

        self.voucher_status = tk.Label(master=self.batch_menu, text=retriever.getVoucherStatus())
        self.voucher_status.grid(row=3, column=1)

        self.select_next = tk.Button(master=self.batch_menu, text="Select Next", command=self.selectNext)
        self.select_next.grid(row=1, column=2, rowspan=2)

        self.select_next_successful = tk.Button(master=self.batch_menu, text="Select Next Successful",
                                                command=self.nextSuccessful)
        self.select_next_successful.grid(row=3, column=2, rowspan=2)

        self.select_previous = tk.Button(master=self.batch_menu, text="Select Previous", command=self.selectPrevious)
        self.select_previous.grid(row=1, column=0, rowspan=2)

        self.select_previous_successful = tk.Button(master=self.batch_menu, text="Select Previous Successful",
                                               command=self.previousSuccessful)
        self.select_previous_successful.grid(row=3, column=0, rowspan=2)

        self.create_new = tk.Button(master=self.batch_menu, text="Run New Batch Export", command=self.runNew)
        self.create_new.grid(row=6, column=0, rowspan=2)

        self.save_json = tk.Button(master=self.batch_menu, text="Save Selected Batch (json)", command=self.saveJson)
        self.save_json.grid(row=6, column=1, rowspan=2)

        self.convert_button = tk.Button(master=self.batch_menu, text="Convert Saved Batches to XML",
                                        command=self.convert)
        self.convert_button.grid(row=6, column=2, rowspan=2)

        self.main_menu_bar = tk.Menu(master=self.batch_menu)
        self.file_menu = tk.Menu(master=self.main_menu_bar, tearoff=0)
        self.file_menu.add_command(label="Reselect Config", command=self.reConfig)
        self.file_menu.add_command(label="Exit", command=sys.exit)
        self.main_menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.batch_menu.config(menu=self.main_menu_bar)

    def selectNext(self):
        if retriever.selectNextBatch() == -1:
            popupWindow("No newer batch found.")
        self.voucher_current.config(text=retriever.batchEndDate[0:-5].replace("T", " at "))
        self.voucher_status.config(text=retriever.getVoucherStatus())

    def selectPrevious(self):
        if retriever.selectPreviousBatch() == -1:
            popupWindow("No older batch found.")
        self.voucher_current.config(text=retriever.batchEndDate[0:-5].replace("T", " at "))
        self.voucher_status.config(text=retriever.getVoucherStatus())

    def nextSuccessful(self):
        if retriever.selectNextSuccessful() == -1:
            popupWindow("No newer successful batch found.")
        self.voucher_current.config(text=retriever.batchEndDate[0:-5].replace("T", " at "))
        self.voucher_status.config(text=retriever.getVoucherStatus())

    def previousSuccessful(self):
        if retriever.selectPreviousSuccessful() == -1:
            popupWindow("No older successful batch found.")
        self.voucher_current.config(text=retriever.batchEndDate[0:-5].replace("T", " at "))
        self.voucher_status.config(text=retriever.getVoucherStatus())

    def runNew(self):
        response = retriever.triggerBatch()
        self.voucher_current.config(text=retriever.batchEndDate[0:-5].replace("T", " at "))
        self.voucher_status.config(text=retriever.getVoucherStatus())
        if response == {}:
            popupWindow(f"Batch Creation Failed, see log for details.")
        else:
            popupWindow("New Batch Created.")
            retriever.selectMostRecentBatch()

    def saveJson(self):
        if retriever.saveVoucherJSON() == 0:
            popupWindow("Voucher Saved as:\njsonBatchVouchers/" + retriever.batchGroup + "/"
                        + retriever.batchEndDate[0:-5].replace(":", "-").replace("T", "_") + ".json")
        else:
            popupWindow("Selected Batch was not successful, and does not have any associated vouchers.")

    def convert(self):
        self.batch_menu.destroy()
        convertMenu()

    def reConfig(self):
        self.batch_menu.destroy()
        configMenu()


class convertMenu:

    def __init__(self):
        self.convert_menu = tk.Tk()
        self.convert_menu.wm_title("FOLIO Voucher Export - Conversion Menu")
        self.convert_menu.columnconfigure([0, 1, 2], minsize=100)
        self.convert_menu.rowconfigure([0, 1, 2, 3], minsize=5)

        self.convert_prompt = tk.Label(master=self.convert_menu, text="Please select a json voucher batch to convert: ")
        self.convert_prompt.grid(row=0, column=0, columnspan=3)

        self.most_recent = tk.Button(master=self.convert_menu, text="Convert Most Recently Created File", command=self.mostRecent)
        self.most_recent.grid(row=1, column=0, columnspan=3)

        self.input_prompt = tk.Label(master=self.convert_menu, text="Input File Name")
        self.input_prompt.grid(row=2, column=0)

        self.input_box = tk.Entry(master=self.convert_menu)
        self.input_box.grid(row=2, column=1)

        self.input_submit = tk.Button(master=self.convert_menu, text="Submit", command=self.convertCustom)
        self.input_submit.grid(row=2, column=2)

        self.batch_return = tk.Button(master=self.convert_menu, text="Return to Batch Selection",
                                      command=self.batchReturn)
        self.batch_return.grid(row=3, column=1)

        self.menu_bar = tk.Menu(master=self.convert_menu)
        self.menu_file = tk.Menu(master=self.menu_bar, tearoff=0)
        self.menu_file.add_command(label="Exit", command=sys.exit)
        self.menu_bar.add_cascade(label="File", menu=self.menu_file)
        self.convert_menu.config(menu=self.menu_bar)

    def mostRecent(self):
        try:
            converter = FOLIO2JAGGAER.voucherDataConverter(configName)
            converter.retrieveMostRecentJSON()
            converter.ConvertFOLIOBatchVoucher()
            converter.saveXML()
        except Exception as e:
            print(e)
            popupWindow(e)
            return
        popupWindow("File Converted Successfully")

    def convertCustom(self):
        converter = FOLIO2JAGGAER.voucherDataConverter(configName, self.input_box.get())
        try:
            converter.ConvertFOLIOBatchVoucher()
            converter.saveXML()
        except Exception as e:
            print(e)
            popupWindow(e)
            return
        popupWindow("File Converted Successfully")

    def batchReturn(self):
        self.convert_menu.destroy()
        batchMenu()


if __name__ == "__main__":
    # TODO: allow log to be generated without swallowing the login prompt
    logger = logger("voucher_export_log")
    print("Launching...")
    configMenu()


