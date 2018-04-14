# EDA Task: Reverse geo-code location/country
### Intent/Purpose
Tag location using latitude and longitude values

### Author/s
Chris, Win, Vidya, Ka Ho, Syuen, Yoke Yong

### Usage
Tasks:
1. First clean web_scrape_v1 file:
- dedup by unique Addresses
- remove all records with missing values on Addresses field
2. Split file into 5 sets to distribute requests to 5 machines.
3. We tried 3 methods on our cleaned, distributed datasets to  

Method 1: Python Google Maps API
File: Addresses2 API.ipynb
1. Produced using Anaconda Python Jupyterlab notebook.
2. Packages used: pandas, numpy, requests, logging, time
3. Guidance was from here: https://www.shanelynn.ie/batch-geocoding-in-python-with-google-geocoding-api/

Results:
Encountered 2 main issues:
1. Hitting query limit for Google Maps API request (2500 requests per day) - successfully geocoded ~200 records out of ~1000 records dataset.
2. Many addresses had errors (invalid results or no results found). Will need to do more data cleaning to investigate why - some hunches include address is too specific that it is not listed on google maps, or special characters are used.

Method 2: GGmap package using R
File: geocode.R
1. Packages used: ggmap
Results: managed to successfully geocode ~50% of dataset of ~1000 records. No API key field to input but hit query limit after 3 runs.

Method 3: Google Sheets add on (Geocode by AwesomeTable)
1. Add dataset csv to Google Sheets.
2. Click on Add-ons>Get Add-ons>search for Geocode by AwesomeTable
3. Once install, click on Add-ons>Geocode by AwesomeTable>Start Geocoding.
4. Ensure that addresses field is input correctly in the tool.
5. Run Geocoding tool.

Results: encountered issue with hitting query limit- can consistently successfully geocode ~300 addresses out of ~1000 addresses dataset.

#### Docker Captains Meta Data:
Reproduced using: Place Docker Environment version used here:
e.g. quay.io/dksg/ea-jupyterlab:1.0.0
Reproduced By: name of docker captain
