# FOLIO Voucher Export

Simple program with a few functions:
* Trigger Batch Voucher Exports in FOLIO
* Download Batched Vouchers in JSON format
* Convert JSON formatted Batched Vouchers into the XML format required for import into Jaggaer
* Post converted XML files to a BuyWays endpoint

## Requirements


* Python 3.x
* json
* requests
* datetime
* sys
* xml
* os
* glob
* tkinter
* pandas



## Installation Instructions

* Create json config file in the following format:
>{  
> "url": "some FOLIO url",  
    "tenant": "some FOLIO x-okapi-tenant",  
    "jaggaerIdentity": "some jaggaer identity",  
    "jaggaerSecret": "some jaggaer password",  
    "buyWaysURL": "BuyWays URL",
    "token": "FOLIO token",
    "batchStartDate": "Date in the form: YYYY-MM-DDTHH:MM:SS.000*",  
    "batchEndDate": "Date in the form: YYYY-MM-DDTHH:MM:SS.000*",  
    "batchGroup": "Voucher Batch Group for export",
    "chartfield": "Chartfield File"
>
> }
* Create folders **jsonBatchVouchers**, **xmlBatchVouchers**, **voucherIdentifiers**, and **postResults** with subfolders for
  the names of each Batch Group you plan to export files from inside your working directory.
  
## Usage Instructions:

* Run main.py using the command line 
  
* Using the menu, input a config file name or select the default option: "Default config.json" 
* Using the selection buttons navigate to the voucher batch export that you would like to save. Alternatively select "Run New Batch Export" to create a new export
* Select "Save Selected Batch (json)"
* To convert files to XML and post the results to BuyWays select "convert Saved Batches to XML" then select one of the following:
    * **"Convert Most Recently Created File"** - Converts the most recently created json export file from the selected batch group and converts it to the BuyWays XML format
    * **"Convert Most Recently Created File and post XML to BuyWays"** - As above but also posts the created file to the BuyWays url provided in the config
    * **Input a file name into the text field and select "Convert"** - Converts the provided JSON file to XML
    * **Input a file name into the text field and select "Convert and Post"** - Converts the provided JSON file to XML and posts the results to the BuyWays url as above 

## Notes

* The Program's log is saved to voucher_export_log.log this log only shows information for the most recent running of the program.
* JSON Files are saved to 'jsonBatchVouchers/[Batch Group Name]'
* XML Files are saved to 'xmlBatchVouchers/[Batch Group Name]'
* Voucher Identifier files are saved to 'voucherIdentifiers/[Batch Group Name]'
* Post Results are saved to 'postResults/[Batch Group Name]'

## Contributors

* Aaron Neslin
* Amelia Sutton


## Version History
* 0.5
  * Filled XML Output Data.
  * Added Invoice Date Data to the export
* 0.2
	* Implemented GUI
	* Added Logging for better bug tracking.

* 0.1
    * Initial Release
    
## Known Issues

## Planned Features
* Revamp of back-end to improve simplicity for maintenance

