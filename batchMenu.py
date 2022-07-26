import sys
import configMenu
import convertMenu
import tkinter as tk
from popupWindow import popupWindow


class batchMenu:

    def __init__(self, retriever, configName):
        self.configName = configName
        self.retriever = retriever
        self.batch_menu = tk.Tk()
        self.batch_menu.wm_title("FOLIO Voucher Export - Batch Menu")
        self.batch_menu.columnconfigure([0, 1, 2], minsize=200)
        self.batch_menu.rowconfigure([0, 1, 2, 3, 4, 5, 6, 7, 8], minsize=9)

        self.voucher_desc = tk.Label(master=self.batch_menu, text="Currently Selected Batch Ran:")
        self.voucher_desc.grid(row=0, column=0, columnspan=3)

        self.voucher_current = tk.Label(master=self.batch_menu,
                                        text=self.retriever.batchEndDate[0:-5].replace("T", " at "))
        self.voucher_current.grid(row=1, column=0, columnspan=3)

        self.status_desc = tk.Label(master=self.batch_menu, text="Currently Selected Batch Status:")
        self.status_desc.grid(row=2, column=1)

        self.voucher_status = tk.Label(master=self.batch_menu, text=self.retriever.getVoucherStatus())
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
        if self.retriever.selectNextBatch() == -1:
            popupWindow("No newer batch found.")
        self.voucher_current.config(text=self.retriever.batchEndDate[0:-5].replace("T", " at "))
        self.voucher_status.config(text=self.retriever.getVoucherStatus())

    def selectPrevious(self):
        if self.retriever.selectPreviousBatch() == -1:
            popupWindow("No older batch found.")
        self.voucher_current.config(text=self.retriever.batchEndDate[0:-5].replace("T", " at "))
        self.voucher_status.config(text=self.retriever.getVoucherStatus())

    def nextSuccessful(self):
        if self.retriever.selectNextSuccessful() == -1:
            popupWindow("No newer successful batch found.")
        self.voucher_current.config(text=self.retriever.batchEndDate[0:-5].replace("T", " at "))
        self.voucher_status.config(text=self.retriever.getVoucherStatus())

    def previousSuccessful(self):
        if self.retriever.selectPreviousSuccessful() == -1:
            popupWindow("No older successful batch found.")
        self.voucher_current.config(text=self.retriever.batchEndDate[0:-5].replace("T", " at "))
        self.voucher_status.config(text=self.retriever.getVoucherStatus())

    def runNew(self):
        response = self.retriever.triggerBatch()
        self.voucher_current.config(text=self.retriever.batchEndDate[0:-5].replace("T", " at "))
        self.voucher_status.config(text=self.retriever.getVoucherStatus())
        if response == {}:
            popupWindow(f"Batch Creation Failed, see log for details.")
        else:
            popupWindow("New Batch Created.")
            self.retriever.selectMostRecentBatch()

    def saveJson(self):
        if self.retriever.saveVoucherJSON() == 0:
            popupWindow("Voucher Saved as:\njsonBatchVouchers/" + self.retriever.batchGroup + "/"
                        + self.retriever.batchEndDate[0:-5].replace(":", "-").replace("T", "_") + ".json")
        else:
            popupWindow("Selected Batch was not successful, and does not have any associated vouchers.")

    def convert(self):
        self.batch_menu.destroy()
        convertMenu.convertMenu(self.configName, self.retriever)

    def reConfig(self):
        self.batch_menu.destroy()
        configMenu.configMenu()
