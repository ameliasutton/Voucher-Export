
# FOLIO Voucher Export

Simple program with a few functions:
* Trigger Batch Voucher Exports in FOLIO
* Download Batched Vouchers in JSON format
* Convert JSON formatted Batched Vouchers into the XML format required for import into Jaggaer

## Requirements


* Python 3.x
* json
* requests
* datetime
* sys
* xml
* os
* glob


## Instructions

* Create json config file in the following format:
>{  
    "url": "some FOLIO url",  
    "tenant": "some FOLIO x-okapi-tenant",  
    "jaggaerIdentity": "some jaggaer identity",  
    "jaggaerSecret": "some jaggaer password",  
    "token": "FOLIO token",
    "batchStartDate": "Date in the form: YYYY-MM-DDTHH:MM:SS.000*",  
    "batchEndDate": "Date in the form: YYYY-MM-DDTHH:MM:SS.000*",  
    "batchGroup": "Voucher Batch Group for export"  
}
* Create folders **jsonBatchVouchers** and **xmlBatchVouchers** with subfolders for
  the names of each Batch Group you plan to export files from inside your working directory.
  
* Run main_gui.py using the command line 
  
* Using the menu, input a config file name or select the default option: "Default config.json" 
* Using the selection buttons navigate to the voucher batch export that you would like to save. Alternatively select "Run New Batch Export" to create a new export
* Select "Save Selected Batch (json)"
* Select "convert Saved Batches to XML" and either input a file name, or select: "Convert Most Recently Created File"


## Contributors


* Aaron Neslin
* Amelia Sutton


## Version History
* 0.2
	* Implemented GUI
	* Added Logging for better bug tracking.

* 0.1
    * Initial Release
    
## Known Issues
* XML converter fills output files with mostly placeholder data
## Planned Features
* Improved UI - potentially using [Gooey](https://github.com/chriskiehl/Gooey)
* Replace placeholder data in xml with actual data

