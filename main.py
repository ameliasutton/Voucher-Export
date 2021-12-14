import voucherBatcher
import json
import FOLIO2JAGGAER

if __name__ == "__main__":
    print('\n' * 40)
    config_selection = input("\nPlease select a config file to use:\n\n"
                             "a. config.json \n"
                             "b. configUMass.json \n"
                             "c. Other File (you will be prompted for file\n\n"
                             "Press any other key to exit\n")
    config_name = ""
    if config_selection == "a":
        config_name = "config.json"
    elif config_selection == "b":
        config_name = "configUMass.json"
    elif config_selection == "c":
        config_name = input("\nInput Config File Name: ")
    else:
        print("\n" * 40)
        exit()

    retriever = voucherBatcher.VoucherBatchRetriever(config_name)
    while True:
        print('\n' * 40)
        print("Current Selected Batch Run Date: " + retriever.batchEndDate)
        selection = input("\nPlease select an action:\n\n"
                          "a. Print Selected Batch of Vouchers \n"
                          "b. Save Selected Batch of Vouchers \n"
                          "c. Select Next Batch \n"
                          "d. Select Previous Batch \n"
                          "e. Select Most Recently Run Batch\n"
                          "f. Run a new batch\n"
                          "g. Convert a Voucher JSON to a Jaggaer XML\n\n"
                          "Press any other key to exit \n")
        print('\n' * 40)
        if selection == "a":
            vouchers = retriever.retrieveVoucher()
            if vouchers:
                print(json.dumps(vouchers, indent=4))
            input("\nPress Enter to return to Menu...")

        elif selection == "b":
            retriever.saveVoucherJSON()
            input("\nPress Enter to return to Menu...")

        elif selection == "c":
            retriever.selectNextBatch()
            input("\nPress Enter to return to Menu...")

        elif selection == "d":
            retriever.selectPreviousBatch()
            input("\nPress Enter to return to Menu...")

        elif selection == "e":
            retriever.selectMostRecentBatch()
            input("\nPress Enter to return to Menu...")

        elif selection == "f":
            cont = input("Running a new batch will automatically select the most recent batch. Is that ok? (y/n) \n")
            if cont == "y":
                retriever.triggerBatch()
            input("\nPress Enter to return to Menu...")

        elif selection == "g":
            print("Not implemented yet! Sorry!\n")

            fileChoice = input("Select a json file to convert: \n\n"
                               "a. Most recently created\n"
                               "b. Type in a file name\n\n"
                               "Press any other key to return to Main Menu\n")
            if fileChoice == "a":
                converter = FOLIO2JAGGAER.json2xmlConverter(config_name)
                converter.ConvertFOLIOBatchVoucher()
                converter.saveXML()
            elif fileChoice == "b":
                converter = FOLIO2JAGGAER.json2xmlConverter(config_name, input("JSON File Name: "))
                converter.ConvertFOLIOBatchVoucher()
                converter.saveXML()
            else:
                print("Back")
            input("Press any key to return to Main Menu")
        else:
            print("\n"*40)
            exit()
