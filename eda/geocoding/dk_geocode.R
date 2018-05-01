## Function for geocoding use
## Specific for DataDive Event on 15th April 2018
## Returns the latitude and longitude of the address
## Builds upon geoChina package

library(plyr)
library(RJSONIO)
library(curl)
library(jsonlite)


# Code adapted from GeoChina package
NULLtoNA <- function(x){
  if (is.null(x)) return(NA)
  if (is.character(x) & length(x) == 0) return(NA)
  x
}

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
  url_string <- paste(api_url, '?address=', address, '&sensor=false', sep = '')
  # add API key to url string
  if (nchar(key) > 0) {
    url_string <- paste(url_string, '&key=', key, sep = '')
  }
  
  if (messaging) message(paste('calling ', url_string, ' ... ', sep = ''), appendLF = F)
  
  # geocode
  con <- curl(URLencode(url_string))
  gc <- fromJSON(paste(readLines(con, warn = FALSE), collapse = ''))
  if (messaging) message('done.')  
  close(con)
  
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

geo_cn <- function(data = NULL, api_key = NULL) {
  
  for(i in 1:nrow(data))
  {   print(paste0("Record: ",i))
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

gc = geo_cn(dt[,.SD[1:4]], 
                   "AIzaSyB7XvDpglcVOsnKRIOi5xe0VbEytP9vn5w")
print(gc[,.(lat, lon)])

# Test on simple bing geocoding

bing_geocode <- function(data, BingMapsKey){
  require(RCurl)
  require(RJSONIO)
  for(i in 1:nrow(data)) {
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

bing = bing_geocode(dt[,.SD[1:4]], 
                "AniHuFaiwVSw1cvFGvS3vaSQY3ff5Sx5LQdilxSdOYfsliJ4QC4uZGx7_Tdn1wLd")
print(bing[,.(lat, lon)])

# Test on simple google geocoding

google_geocode <- function(data, api_key){
  require(RCurl)
  require(RJSONIO)
  for(i in 1:nrow(data)) {

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

goog = google_geocode(dt[,.SD[1:4]],
                      "AIzaSyB7XvDpglcVOsnKRIOi5xe0VbEytP9vn5w")
print(goog[,.(lat, lon)])
