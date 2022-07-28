import sys
import tkinter as tk
import batchMenu
from popupWindow import popupWindow
from postToBuyWays import postToBuyWays
from voucherDataConverter import voucherDataConverter


class convertMenu:

    def __init__(self, configName, requester):
        print("Initializing Convert Menu...")
        self.requester = requester
        self.configName = configName
        self.convert_menu = tk.Tk()
        self.convert_menu.wm_title("FOLIO Voucher Export - Conversion Menu")
        self.convert_menu.columnconfigure([0, 1, 2], minsize=100)
        self.convert_menu.rowconfigure([0, 1, 2, 3, 4, 5], minsize=5)

        self.convert_prompt = tk.Label(master=self.convert_menu, text="Please select an option for conversion"
                                                                      "\n(The created file will be posted to BuyWays)"
                                                                      "\n\n Convert Most Recent File:")
        self.convert_prompt.grid(row=0, column=0, columnspan=3)

        self.most_recent = tk.Button(master=self.convert_menu, text="Convert Most Recently Created File",
                                     command=self.mostRecent)
        self.most_recent.grid(row=1, column=0)

        self.most_recent_post = tk.Button(master=self.convert_menu,
                                          text='Convert Most Recently Created File\nand Post XML to BuyWays',
                                          command=self.mostRecentPost)
        self.most_recent_post.grid(row=1, column=1, columnspan=2)

        self.spacer = tk.Label(master=self.convert_menu, text='\nOr select a specific file to convert:')
        self.spacer.grid(row=2, column=0, columnspan=3)

        self.input_prompt = tk.Label(master=self.convert_menu, text="Input File Name")
        self.input_prompt.grid(row=3, column=0)

        self.input_box = tk.Entry(master=self.convert_menu)
        self.input_box.grid(row=3, column=1, columnspan=2)

        self.input_submit = tk.Button(master=self.convert_menu, text="Convert", command=self.convertCustom)
        self.input_submit.grid(row=4, column=0)

        self.input_submit_post = tk.Button(master=self.convert_menu,
                                           text='Convert and Post',
                                           command=self.convertCustomPost)
        self.input_submit_post.grid(row=4, column=1, columnspan=2)

        self.batch_return = tk.Button(master=self.convert_menu, text="Return to Batch Selection",
                                      command=self.batchReturn)
        self.batch_return.grid(row=5, column=0, columnspan=3)

        self.menu_bar = tk.Menu(master=self.convert_menu)
        self.menu_file = tk.Menu(master=self.menu_bar, tearoff=0)
        self.menu_file.add_command(label="Exit", command=sys.exit)
        self.menu_bar.add_cascade(label="File", menu=self.menu_file)
        self.convert_menu.config(menu=self.menu_bar)
        print("Convert Menu Initialized!")

    def postXML(self, xml_file_name):
        try:
            postToBuyWays(self.configName, xml_file_name)
        except Exception as e:
            print(f"| Warn | {e}")
            popupWindow(e)
            return
        popupWindow('File Converted and Posted Successfully.')

    def mostRecent(self):
        try:
            converter = voucherDataConverter(self.configName)
            converter.retrieveMostRecentJSON()
            converter.ConvertFOLIOBatchVoucher()
            converter.saveXML()
            converter.saveVoucherIdentifiers()
        except Exception as e:
            print(f"| Warn | {e}")
            popupWindow(e)
            return
        popupWindow("File Converted Successfully.")

    def mostRecentPost(self):
        try:
            converter = voucherDataConverter(self.configName)
            converter.retrieveMostRecentJSON()
            converter.ConvertFOLIOBatchVoucher()
            xml_file_name = converter.saveXML()
            converter.saveVoucherIdentifiers()
        except Exception as e:
            print(f"| Warn | {e}")
            popupWindow(e)
            return
        self.postXML(xml_file_name)

    def convertCustom(self):
        if self.input_box.get() == '':
            print('| Warn | File Name must not be empty')
            popupWindow('File Name Cannot be empty')
        try:
            converter = voucherDataConverter(self.configName, self.input_box.get())
            converter.ConvertFOLIOBatchVoucher()
            converter.saveXML()
            converter.saveVoucherIdentifiers()
        except Exception as e:
            print(f"| Warn | {e}")
            popupWindow(e)
            return
        popupWindow("File Converted Successfully.")

    def convertCustomPost(self):
        if self.input_box.get() == '':
            print('| Warn | File Name must not be empty')
            popupWindow('File Name Cannot be empty')
        try:
            converter = voucherDataConverter(self.configName, self.input_box.get())
            converter.ConvertFOLIOBatchVoucher()
            converter.saveVoucherIdentifiers()
            xml_file_name = converter.saveXML()
        except Exception as e:
            print(f"| Warn | {e}")
            popupWindow(e)
            return
        self.postXML(xml_file_name)

    def batchReturn(self):
        self.convert_menu.destroy()
        batchMenu.batchMenu(self.requester, self.configName)