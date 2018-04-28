# EDA Task: Reverse geo-code location/country
### Intent/Purpose
Tag location using latitude and longitude values

### Author/s
Chris, Win, Vidya, Ka Ho, Syuen, Yoke Yong
Brandon, Pam, Donna, Alan, Christian

### Usage
Scripts:
1. cleaning and combining.R (Author: Yoke Yong)
2. If using R, use R script dk_geocode.R
3. If using python, use geocode_api v2.ipynb

Part 1. cleaning and combining.R (Author: Yoke Yong)
Expected output:
1. Gets unique raw dataset from 3 webscraping files (web_scraping_v1, web_scraping_v2, web_scraping_v3).
2. Cleans Singapore addresses such that only postal codes are left.
3. Cleans some foreign (non-Singapore) addresses.
4. Outputs geocoding for data generated on Saturday (archived as addresses1).

Part 2. dk_geocode.R script (Author: Yoke Yong)
Requirements:
- install.packages(“curl”)
- install.packages(“devtools”)
- install.packages(“geoChina”): https://github.com/caijun/geoChina
- apikey: Please get a key from Google GeoCoding API. Search for Google Maps API on Google Search, and select Google GeoCoding API from the api picker. You will have to create a new project and generate the key. Copy the key. If you miss copying the key, please log on to Google API console.
- This function will auto install devtools and geoChina if not installed in R.
1. Ensure input datafile contains following:
- As long as the data has an address (column name “address”) and api key from Google Maps, you can use the function dk_geocode within the script with the data.
- For record sake, you will want to create an ID for each address, such that you can tie it back to the main dataset that the address comes from.
- The data passed into the function must be in a data frame format.
- This function is dependent on the geocode function in geoChina, which takes in the address string and api key.
2. Expected output:
- The function attaches the longitude and latitude to the data you pass it into.

Part 3. Geocode_api v2.ipynb script (Author: Brandon, Syuen)
Packages to install: pandas, requests, logging, time
1. Get Google Maps API key.
2. Run script.
3. Key in inputs:
- key in filepath of specific file
- if file is not country specific, key in "General"
- if file is country specific, key in "Country"
- key in API key
3. Expected output:
- Geocoded [country if entered].csv file with geocoded addresses. Output file will not be generated until all records have been geocoded.
- once hit API query limit (2,500 requests per day), code will stop running and wait for 30 minutes before continuing.

Archived scripts:
1. Addresses2 API.ipynb - used for generating geocoded addresses. Revised to geocode_api v2.ipynb
2. geocode.R - used for generating initial geocoded addresses. Revised to dk_geocode.R.

#### Docker Captains Meta Data:
Reproduced using: Place Docker Environment version used here:
e.g. quay.io/dksg/ea-jupyterlab:1.0.0
Reproduced By: name of docker captain
