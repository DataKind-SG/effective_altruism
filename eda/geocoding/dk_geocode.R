## Function for geocoding use
## Specific for DataDive Event on 15th April 2018
## Returns the latitude and longitude of the address
## Builds upon geoChina package

dk_geocode <- function(data = NULL, api_key = NULL) {

    if(!require(geoChina)) {
        
        if(!require(devtools)) {
            
            install.packages("devtools")
            
        }
        
        devtools::install_github("caijun/geoChina")
        
    }
    
    library(geoChina)
    for(i in 1:nrow(data))
    {
        print(paste0("Record: ",i))
        result <- suppressWarnings(geocode(data$address[i], api = "google", key = api_key, output = "latlng"))
        
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