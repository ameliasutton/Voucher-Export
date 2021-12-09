import voucherBatcher
import json
from termcolor import colored

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
                          "f. Run a new batch\n\n"
                          "Press any other key to exit \n")
        print('\n' * 40)
        if selection == "a":
            vouchers = retriever.retrieveVoucher()
            if vouchers:
                print(json.dumps(vouchers, indent=4))
            input("\nPress Enter to return to Menu...")

        elif selection == "b":
            vouchers = retriever.retrieveVoucher()
            if vouchers:
                print("Saving Voucher Batch...")
                with open(retriever.batchEndDate[0:-5].replace(":", "-").replace("T", "_") + ".json", "w") as out:
                    out.write(json.dumps(vouchers, indent=4))
                print("Voucher Batch Saved.")
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

        else:
            print("\n"*40)
            exit()
