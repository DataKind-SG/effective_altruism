## Function for geocoding use
## Specific for DataDive Event on 15th April 2018
## Returns the latitude and longitude of the address
## Builds upon geoChina package

library(plyr)
library(RJSONIO)
library(RCurl)
#library(jsonlite)
library(data.table)

# function for simple bing geocoding
# takes data and returns 2 columns, lat & lon
# required bing api key
bing_geocode <- function(data, BingMapsKey){
  require(RCurl)
  require(RJSONIO)
  for(i in 1:nrow(data)) {
    
    if(is.na(data$lat[i]) == F | is.na(data$address[i]) == T) {
      print(paste0("Skipping: ",i," as either lat long is filled or address is empty."))
      next
    }
    
    print(paste0("Processing: ",i))
    u <- URLencode(paste0("http://dev.virtualearth.net/REST/v1/Locations?q=", 
                          data$address, 
                          "&maxResults=1&key=", 
                          BingMapsKey))
    d <- getURL(u)
    j <- fromJSON(d,simplify = FALSE) 
    if (j$resourceSets[[1]]$estimatedTotal > 0) {
      lat <- j$resourceSets[[1]]$resources[[1]]$point$coordinates[[1]]
      lng <- j$resourceSets[[1]]$resources[[1]]$point$coordinates[[2]]
    }
    else {    
      lat <- lng <- NA
    }
    data$lon[i] <- lng
    data$lat[i] <- lat
  }
  return(data)
}  

# function for simple google geocoding
# takes data and returns 2 columns, lat & lon
# requires google API key
# can run without API key as well, simply remove "&key=" & api_key
google_geocode <- function(data, api_key){
  require(RCurl)
  require(RJSONIO)
  for(i in 1:nrow(data)) {
    
    if(is.na(data$lat[i]) == F | is.na(data$address[i]) == T) {
      print(paste0("Skipping: ",i," as either lat long is filled or address is empty."))
      next
    }
    
    print(paste0("Processing: ",i))
    u <- URLencode(paste0('https://maps.googleapis.com/maps/api/geocode/json',
                          "?address=",
                          data$address, 
                          "&sensor=false",
                          "&key=",
                          api_key))
    d <- getURL(u)
    j <- fromJSON(d,simplify = FALSE) 
    if (j$status=="OK") {
      lat <- j$results[[1]]$geometry$location$lat
      lng <- j$results[[1]]$geometry$location$lng
    }
    else {    
      lat <- lng <- NA
    }
    data$lon[i] <- lng
    data$lat[i] <- lat
  }
  return(data)
}  

# function to convert null and blanks to NA
NULLtoNA <- function(x){
  if (is.null(x)) return(NA)
  if (is.character(x) & length(x) == 0) return(NA)
  x
}

# geocode adapted from R GeoChina package
# simplified for current use case
geocode <- function(address, api = 'google', key = '', 
                    ocs = c('WGS-84', 'GCJ-02', 'BD-09'), 
                    output = c('latlng', 'latlngc', 'latlnga'), messaging = FALSE, 
                    time = 0){
  
  # check parameters
  stopifnot(is.character(address))
  api <- match.arg(api)
  stopifnot(is.character(key))
  output <- match.arg(output)
  ocs <- match.arg(ocs)
  stopifnot(is.logical(messaging))
  stopifnot(is.numeric(time))
  
  # vectorize for many addresses
  if (length(address) > 1) {
    s <- 'google restricts requests to 2500 requests a day.'
    if (length(address) > 2500) stop(s, call. = F)
    if (length(address) > 200 & messaging) message(paste('Reminder', s, sep = ' : '))

    return(ldply(address, function(add){
      Sys.sleep(time)
      geocode(add, api = api, key = key, ocs = ocs, output = output, messaging = messaging)
    }))
  }
  
  # location encoding
  address <- enc2utf8(address)
  api_url <- 'https://maps.googleapis.com/maps/api/geocode/json'
  
  # format url
  # https is only supported on Windows, when R is started with the --internet2 
  # command line option. without this option, or on Mac, you will get the error 
  # "unsupported URL scheme".
  url_string <- paste0(api_url, '?address=', address, '&sensor=false')
  # add API key to url string
  if (nchar(key) > 0) {
    url_string <- paste0(url_string, '&key=')
  }
  
  if (messaging) message(paste('calling ', url_string, ' ... ', sep = ''), appendLF = F)
  
  # geocode
  # addresses with "#" throws http 400 error
  # changed curl+JSON+readLines to getURL+JSON
  
  # con <- curl(URLencode(url_string))
  # gc <- fromJSON(paste(readLines(con, warn = FALSE), collapse = ''))
  
  con <- getURL(URLencode(url_string))
  gc <- fromJSON(con,simplify = FALSE) 
  if (messaging) message('done.')  
  # close(con)
  
  # did geocode fail?
  if (gc$status != 'OK') {
    warning(paste('geocode failed with status ', gc$status, ', location = "', 
                  address, '"', sep = ''), call. = FALSE)
    return(data.frame(lat = NA, lng = NA))  
  }
  
  # more than one location found?
  if (length(gc$results) > 1 && messaging) {
    Encoding(gc$results[[1]]$formatted_address) <- "UTF-8"
    message(paste('more than one location found for "', address, 
                  '", using address\n"', tolower(gc$results[[1]]$formatted_address), 
                  '"', sep = ''), appendLF = T)
  }
  
  gcdf <- with(gc$results[[1]], {
    data.frame(lat = NULLtoNA(geometry$location['lat']), 
               lng = NULLtoNA(geometry$location['lng']), 
               loctype = tolower(NULLtoNA(geometry$location_type)), 
               address = tolower(NULLtoNA(formatted_address)),
               row.names = NULL)})
  
  if (output == 'latlng') return(gcdf[c('lat', 'lng')])
  if (output == 'latlngc') return(gcdf[c('lat', 'lng', 'loctype')])
  if (output == 'latlnga') return(gcdf[!names(gcdf) %in% c('loctype')])
}

# function to run GeoChina's geocode on a dataframe
# takes in data and returns 2 columns, lat and lon
# requires google api key
geo_cn <- function(data, api_key) {
  
  for(i in 1:nrow(data)) {
    
    if(is.na(data$lat[i]) == F | is.na(data$address[i]) == T) {
      print(paste0("Skipping: ",i," as either lat long is filled or address is empty."))
      next
    }
    
    print(paste0("Processing: ",i))
    result <- suppressWarnings(geocode(data$address[i], 
                                       key = api_key, 
                                       output = "latlng"))
    if(!is.na(result[["lng"]])) {
      data$lon[i] <- as.numeric(result[[2]])
      data$lat[i] <- as.numeric(result[[1]])
    } else {
      data$lon[i] <- NA
      data$lat[i] <- NA
    } 
  }
  return(data)
}

setwd("../..")
file_dir = "data/output/web_scraping/web_scrape_cleaned_aft_google.csv"

dt = setDT(read.csv(file_dir, stringsAsFactors = F, na = ""))

# Pass through both google and bing, with google first.
dt_14001_to_14847 = bing_geocode(geo_cn(gc_dt[,.SD[14001:14847]],
                                   "AIzaSyB7XvDpglcVOsnKRIOi5xe0VbEytP9vn5w")
                            ,"AniHuFaiwVSw1cvFGvS3vaSQY3ff5Sx5LQdilxSdOYfsliJ4QC4uZGx7_Tdn1wLd")

gc_dt = rbindlist(list(dt_1_to_1000,
                       dt_1001_to_2000,
                       dt_2001_to_3000,
                       dt_3001_to_4000,
                       dt_4001_to_5000,
                       dt_5001_to_6000,
                       dt_6001_to_7000,
                       dt_7001_to_8000,
                       dt_8001_to_9000,
                       dt_9001_to_10000,
                       dt_10001_to_11000,
                       dt_11001_to_12000,
                       dt_12001_to_13000,
                       dt_13001_to_14000,
                       dt_14001_to_14847))
gc_dt[, key := .I]
write.csv(gc_dt, 
          "data/output/web_scraping/web_scrape_geocoded.csv",
          row.names = F,
          fileEncoding = "UTF-8")
# print(dt_1_to_55[,.(lat,lon)])

# bing = bing_geocode(dt[,.SD[1:5]],
#                     "AniHuFaiwVSw1cvFGvS3vaSQY3ff5Sx5LQdilxSdOYfsliJ4QC4uZGx7_Tdn1wLd")
# print(bing[,.(lat, lon)])
# 
# goog = google_geocode(dt[,.SD[1:5]],
#                       "AIzaSyB7XvDpglcVOsnKRIOi5xe0VbEytP9vn5w")
# print(goog[,.(lat, lon)])