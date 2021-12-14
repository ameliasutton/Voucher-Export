
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
  
* Run main.py using the command line 
  
* Using the menu, select the voucher batch that you want to export, or create a new one, then convert those files.


## Contributors


* Aaron Neslin
* Amelia Sutton


## Version History

* 0.1
    * Initial Release
    
## Known Issues
* XML converter fills output files with mostly placeholder data
## Planned Features
* Improved UI - potentially using [Gooey](https://github.com/chriskiehl/Gooey)
* Replace placeholder data in xml with actual data

