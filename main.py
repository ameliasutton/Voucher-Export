import voucherBatcher
import json

if __name__ == "__main__":
    configName = "configUMass.json"
    retriever = voucherBatcher.VoucherBatchRetriever(configName)
    while True:
        print('\n' * 40)
        print("Current Selected Batch Run Date: " + retriever.batchEndDate)
        selection = input("\nPlease select an action:\n\n"
                          "a. Print Selected Batch of Vouchers \n"
                          "b. Save Selected Batch of Vouchers \n"
                          "c. Select Next Batch \n"
                          "d. Select Previous Batch \n"
                          "e. Select Most Recently Run Batch"
                          "Press and other key to exit \n")
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
            print("Option Not Implemented Yet")
        else:
            exit()
