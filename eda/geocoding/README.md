# EDA Task: Reverse geo-code location/country
### Intent/Purpose
Tag location using latitude and longitude values

### Author/s
Chris, Win, Vidya, Ka Ho, Syuen, Yoke Yong

### Usage
Scripts:
Geocode.R
Addresses2 API.ipynb

Steps:

Step One: Run geocode.R.
Packages to install: ggmap
Output:
1. Unique on all addresses in address field.
2. Addition of ID column.
3. Split datasets into 5 datasets of approx ~1000 records each. (addresses1, addresses2, addresses3, addresses4, addresses5).
4. Output file latlona dataset with longitude and latitude tagged in additional columns.

Step Two: Run Addresses2 API.ipynb
Packages to install: pandas, numpy, requests, logging, time
Output:
1. Hit query limit after ~200 records geocoded - code will remain running to retry request every 30 minutes until stopped.
2. Output file output.csv generated with additional fields [accuracy, formatted_address,	google_place_id,input_string,	latitude,	longitude,	number_of_results,	postcode,	status,	type] after every 100 records geocoded.

Step Three: Add addresses3, addresses4, addresses5 csv to Google Sheets.

Step Four: Click on Add-ons>Get Add-ons>search for Geocode by AwesomeTable

Step Five: Once install, click on Add-ons>Geocode by AwesomeTable>Start Geocoding.

Step Six: Ensure that addresses field is input correctly in the tool.

Step Seven: Run Geocoding tool.
Output: Hit query limit after ~300 records geocoded.

#### Docker Captains Meta Data:
Reproduced using: Place Docker Environment version used here:
e.g. quay.io/dksg/ea-jupyterlab:1.0.0
Reproduced By: name of docker captain
