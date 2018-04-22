reqPackages <- c("shiny", "data.table", "RCurl", "jsonlite", "fields", "stringdist", "shinythemes", "bit64")

loadPackages <- function(requiredPackages){
  for (i in 1:length(requiredPackages)) {
    if (!(requiredPackages[i] %in% rownames(installed.packages()))) {
      install.packages(requiredPackages[i])
    } else {
      update.packages(oldPkgs = requiredPackages[i], checkBuilt = T, ask = F)
    }
    suppressMessages(library(requiredPackages[i], character.only = T))
  }
}

loadPackages(reqPackages)

options(shiny.maxRequestSize = 100*1024^2)

server <- function(input, output, session) {
  
  ######################
  ### Load Libraries ###
  ######################
  
  suppressMessages(require(data.table))
  suppressMessages(require(RCurl))
  suppressMessages(require(jsonlite))
  suppressMessages(require(fields))
  
  ##########################################################
  ### Functions/Tables for Geocoding & Reverse Geocoding ###
  ##########################################################
  
  languageTable <- reactive({
    data.table(language = c("Arabic", "Bulgarian", "Bengali", "Catalan", "Czech", "Danish", "German", "Greek", "English", "English (Australian)", "English (Great Britain)", "Spanish", "Basque", "Basque", "Farsi", "Finnish", "Filipino", "French", "Galician", "Gujarati", "Hindi", "Croatian", "Hungarian", "Indonesian", "Italian", "Hebrew", "Japanese", "Kannada", "Korean", "Lithuanian", "Latvian", "Malayalam", "Marathi", "Dutch", "Norwegian", "Polish", "Portuguese", "Portuguese (Brazil)", "Portuguese (Portugal)", "Romanian", "Russian", "Slovak", "Slovenian", "Serbian", "Swedish", "Tamil", "Telugu", "Thai", "Tagalog", "Turkish", "Ukrainian", "Vietnamese", "Chinese (Simplified)", "Chinese (Traditional)"), 
               code = c("ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "en-AU", "en-GB", "es", "eu", "eu", "fa", "fi", "fil", "fr", "gl", "gu", "hi", "hr", "hu", "id", "it", "iw", "ja", "kn", "ko", "lt", "lv", "ml", "mr", "nl", "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te", "th", "tl", "tr", "uk", "vi", "zh-CN", "zh-TW"), 
               stringsAsFactors = F)
  })
  
  geocoderTable <- reactive({
    c("Google", "Bing")
  })
  
  urlGeocode <- function(address, return.call = "json", language = "en", geocoder = c("Google", "Bing"), authentication_key = NULL) {
    if (geocoder == "Google") {
      root <- "http://maps.google.com/maps/api/geocode/"
      u <- paste0(root, return.call, "?address=", address, "&language=", language)
    }
    if (geocoder == "Bing") {
      if (is.null(authentication_key)) stop('"authentication_key" cannot be NULL if Bing is set as the geocoder')
      root <- "http://dev.virtualearth.net/REST/v1/Locations"
      u <- paste0(root, "?q=", address, "&maxResults=0&c=", language, "&key=", authentication_key)
    }
    return(URLencode(u))
  }
  
  geocodeGoogleFormat <- function(address, flattenJSON) {
    
    flattenJSON$results$address_components[[1]]$types <- sapply(flattenJSON$results$address_components[[1]]$types, function(x) unlist(strsplit(x, split = ", "))[1])
    
    input_address <- address
    google_formatted_address <- flattenJSON$results$formatted_address[1]
    google_location_type <- flattenJSON$results$geometry$location_type[1]
    google_latitude <- flattenJSON$results$geometry$location$lat[1]
    google_longitude <- flattenJSON$results$geometry$location$lng[1]
    
    google_street_address <- ifelse("street_address" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "street_address"], "")
    google_route <- ifelse("route" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "route"], "")
    google_intersection <- ifelse("intersection" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "intersection"], "")
    google_country <- ifelse("country" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "country"], "")
    google_administrative_area_level_1 <- ifelse("administrative_area_level_1" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "administrative_area_level_1"], "")
    google_administrative_area_level_2 <- ifelse("administrative_area_level_2" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "administrative_area_level_2"], "")
    google_administrative_area_level_3 <- ifelse("administrative_area_level_3" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "administrative_area_level_3"], "")
    google_administrative_area_level_4 <- ifelse("administrative_area_level_4" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "administrative_area_level_4"], "")
    google_administrative_area_level_5 <- ifelse("administrative_area_level_5" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "administrative_area_level_5"], "")
    google_locality <- ifelse("locality" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "locality"], "")
    google_neighborhood <- ifelse("neighborhood" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "neighborhood"], "")
    google_premise <- ifelse("premise" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "premise"], "")
    google_subpremise <- ifelse("subpremise" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "subpremise"], "")
    google_postal_code <- ifelse("postal_code" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "postal_code"], "")
    google_street_number <- ifelse("street_number" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "street_number"], "")
    
    return(data.frame(input_address = input_address, 
                      google_formatted_address = google_formatted_address, 
                      google_location_type = google_location_type, 
                      google_latitude = google_latitude, 
                      google_longitude = google_longitude, 
                      google_street_address = google_street_address, 
                      google_route = google_route, 
                      google_intersection = google_intersection, 
                      google_country = google_country, 
                      google_administrative_area_level_1 = google_administrative_area_level_1, 
                      google_administrative_area_level_2 = google_administrative_area_level_2, 
                      google_administrative_area_level_3 = google_administrative_area_level_3, 
                      google_administrative_area_level_4 = google_administrative_area_level_4, 
                      google_administrative_area_level_5 = google_administrative_area_level_5, 
                      google_locality = google_locality, 
                      google_neighborhood = google_neighborhood, 
                      google_premise = google_premise, 
                      google_postal_code = google_postal_code, 
                      google_street_number = google_street_number, 
                      stringsAsFactors = F))
  }
  
  
  geocodeBingFormat <- function(address, flattenJSON) {
    
    input_address <- address
    bing_formatted_address <- flattenJSON$resourceSets$resources[[1]]$address$formattedAddress[1]
    bing_location_type <- flattenJSON$resourceSets$resources[[1]]$geocodePoints[[1]]$calculationMethod[1]
    bing_match_code <- flattenJSON$resourceSets$resources[[1]]$matchCodes[[1]][1]
    bing_confidence <- flattenJSON$resourceSets$resources[[1]]$confidence[1]
    bing_latitude <- flattenJSON$resourceSets$resources[[1]]$geocodePoints[[1]]$coordinates[[1]][1]
    bing_longitude <- flattenJSON$resourceSets$resources[[1]]$geocodePoints[[1]]$coordinates[[1]][2]
    
    bing_addressLine <- ifelse("addressLine" %in% names(flattenJSON$resourceSets$resources[[1]]$address), flattenJSON$resourceSets$resources[[1]]$address$addressLine[1], "")
    bing_locality <- ifelse("locality" %in% names(flattenJSON$resourceSets$resources[[1]]$address), flattenJSON$resourceSets$resources[[1]]$address$locality[1], "")
    bing_neighborhood <- ifelse("neighborhood" %in% names(flattenJSON$resourceSets$resources[[1]]$address), flattenJSON$resourceSets$resources[[1]]$address$neighborhood[1], "")
    bing_adminDistrict <- ifelse("adminDistrict" %in% names(flattenJSON$resourceSets$resources[[1]]$address), flattenJSON$resourceSets$resources[[1]]$address$adminDistrict[1], "")
    bing_adminDistrict2 <- ifelse("adminDistrict2" %in% names(flattenJSON$resourceSets$resources[[1]]$address), flattenJSON$resourceSets$resources[[1]]$address$adminDistrict2[1], "")
    bing_postalCode <- ifelse("postalCode" %in% names(flattenJSON$resourceSets$resources[[1]]$address), flattenJSON$resourceSets$resources[[1]]$address$postalCode[1], "")
    bing_countryRegion <- ifelse("countryRegion" %in% names(flattenJSON$resourceSets$resources[[1]]$address), flattenJSON$resourceSets$resources[[1]]$address$countryRegion[1], "")
    bing_countryRegionIso2 <- ifelse("countryRegionIso2" %in% names(flattenJSON$resourceSets$resources[[1]]$address), flattenJSON$resourceSets$resources[[1]]$address$countryRegionIso2[1], "")
    
    return(data.frame(input_address = input_address, 
                      bing_formatted_address = bing_formatted_address, 
                      bing_location_type = bing_location_type, 
                      bing_match_code = bing_match_code, 
                      bing_confidence = bing_confidence, 
                      bing_latitude = bing_latitude, 
                      bing_longitude = bing_longitude, 
                      bing_addressLine = bing_addressLine,
                      bing_locality = bing_locality, 
                      bing_neighborhood = bing_neighborhood, 
                      bing_adminDistrict = bing_adminDistrict, 
                      bing_adminDistrict2 = bing_adminDistrict2, 
                      bing_postalCode = bing_postalCode, 
                      bing_countryRegion = bing_countryRegion, 
                      bing_countryRegionIso2 = bing_countryRegionIso2, 
                      stringsAsFactors = F))
  }
  
  
  geocode <- function(address, language = "en", geocoder = c("Google", "Bing"), authentication_key = NULL, max.counter = 20) {
    
    counter <- 0
    urlSearch <- urlGeocode(address, return.call = "json", language = language, geocoder = geocoder, authentication_key = authentication_key)
    origJSON <- getURL(urlSearch)
    Sys.sleep(0.2)
    flattenJSON <- fromJSON(origJSON, flatten = FALSE)
    
    while (counter < max.counter) {
      if (geocoder == "Google") {
        if(flattenJSON$status=="OK") {
          return (geocodeGoogleFormat(address, flattenJSON))
        }
      }
      if (geocoder == "Bing") {
        if(flattenJSON$resourceSets$estimatedTotal>0) {
          return (geocodeBingFormat(address, flattenJSON))
        }
      }
      counter <- counter + 1
    }
    return (NULL)
  }
  
  geocode_Pipe <- function(street_df, city_df, language = "en", geocoder = c("Google", "Bing"), authentication_key = NULL, max.counter = 20) {
    
    output_df_list <- list()
    
    withProgress(message = "Geocoding in Progress...", value = 0, {
      
      n <- nrow(street_df)
      
      for (i in 1:n) {
        
      address <- paste(c(street_df[i, ], city_df[i, ]), collapse = ", ")
      
      # if(verbose) cat("Geocoding store ", i, " of ", nrow(address_df), " stores...\n")
      geocodeOutput <- geocode(address, language = language, geocoder = geocoder, authentication_key = authentication_key, max.counter = max.counter)
      
      if (geocoder == "Google") {
        if (is.null(geocodeOutput)) 
          geocodeOutput <- data.frame(input_address = address, 
                                      google_formatted_address = "No location found.", 
                                      google_location_type = "", 
                                      google_latitude = "", 
                                      google_longitude = "", 
                                      google_street_address = "", 
                                      google_route = "", 
                                      google_intersection = "", 
                                      google_country = "", 
                                      google_administrative_area_level_1 = "", 
                                      google_administrative_area_level_2 = "", 
                                      google_administrative_area_level_3 = "", 
                                      google_administrative_area_level_4 = "", 
                                      google_administrative_area_level_5 = "", 
                                      google_locality = "", 
                                      google_neighborhood = "", 
                                      google_premise = "", 
                                      google_postal_code = "", 
                                      google_street_number = "", 
                                      stringsAsFactors = F)
        
        if (geocodeOutput$google_locality == "") {
          address <- paste(city_df[i, ], collapse = ", ")
          geocodeOutput <- geocode(address, language = language, geocoder = geocoder, authentication_key = authentication_key, max.counter = max.counter)
        }
        
        if (is.null(geocodeOutput)) 
          geocodeOutput <- data.frame(input_address = address, 
                                      google_formatted_address = "No location found.", 
                                      google_location_type = "", 
                                      google_latitude = "", 
                                      google_longitude = "", 
                                      google_street_address = "", 
                                      google_route = "", 
                                      google_intersection = "", 
                                      google_country = "", 
                                      google_administrative_area_level_1 = "", 
                                      google_administrative_area_level_2 = "", 
                                      google_administrative_area_level_3 = "", 
                                      google_administrative_area_level_4 = "", 
                                      google_administrative_area_level_5 = "", 
                                      google_locality = "", 
                                      google_neighborhood = "", 
                                      google_premise = "", 
                                      google_postal_code = "", 
                                      google_street_number = "", 
                                      stringsAsFactors = F)
      }
      
      if (geocoder == "Bing") {
        if (is.null(geocodeOutput)) 
          geocodeOutput <- data.frame(input_address = address, 
                                      bing_formatted_address = "No location found", 
                                      bing_location_type = "", 
                                      bing_match_code = "", 
                                      bing_confidence = "", 
                                      bing_latitude = "", 
                                      bing_longitude = "", 
                                      bing_addressLine = "",
                                      bing_locality = "", 
                                      bing_neighborhood = "", 
                                      bing_adminDistrict = "", 
                                      bing_adminDistrict2 = "", 
                                      bing_postalCode = "", 
                                      bing_countryRegion = "", 
                                      bing_countryRegionIso2 = "", 
                                      stringsAsFactors = F)
        
        if (geocodeOutput$bing_locality == "") {
          address <- paste(city_df[i, ], collapse = ", ")
          geocodeOutput <- geocode(address, language = language, geocoder = geocoder, authentication_key = authentication_key, max.counter = max.counter)
        }
        
        if (is.null(geocodeOutput)) 
          geocodeOutput <- data.frame(input_address = address, 
                                      bing_formatted_address = "No location found", 
                                      bing_location_type = "", 
                                      bing_match_code = "", 
                                      bing_confidence = "", 
                                      bing_latitude = "", 
                                      bing_longitude = "", 
                                      bing_addressLine = "",
                                      bing_locality = "", 
                                      bing_neighborhood = "", 
                                      bing_adminDistrict = "", 
                                      bing_adminDistrict2 = "", 
                                      bing_postalCode = "", 
                                      bing_countryRegion = "", 
                                      bing_countryRegionIso2 = "", 
                                      stringsAsFactors = F)
      }
      # if(verbose) cat("Input Address: ", address, "\n", "Output Address: ", geocodeOutput$google_formatted_address, "\n")
      output_df_list[[i]] <- geocodeOutput
      
      incProgress(1/n, detail = paste0("Geocoding store ", i, " of ", nrow(street_df), " stores..."))
    }
    })
    output_df <- do.call(rbind, output_df_list)
    return (output_df)
  }
  
  urlReverse <- function(latlng, return.call = "json", language = "en", geocoder = c("Google", "Bing"), authentication_key = NULL) {
    
    if (geocoder == "Google") {
      root <- "http://maps.google.com/maps/api/geocode/"
      u <- paste0(root, return.call, "?latlng=", latlng, "&language=", language)
    }
    if (geocoder == "Bing") {
      if (is.null(authentication_key)) stop('"authentication_key" cannot be NULL if Bing is set as the geocoder')
      root <- "http://dev.virtualearth.net/REST/v1/Locations/"
      u <- paste0(root, latlng, "?maxResults=0&c=", language, "&key=", authentication_key)
    }
    return(URLencode(u))
  }
  
  reverseGoogleFormat <- function(latlng, flattenJSON) {
    
    flattenJSON$results$address_components[[1]]$types <- sapply(flattenJSON$results$address_components[[1]]$types, function(x) unlist(strsplit(x, split = ", "))[1])
    
    input_latlng <- latlng
    google_formatted_address <- flattenJSON$results$formatted_address[1]
    google_location_type <- flattenJSON$results$geometry$location_type[1]
    google_latitude <- flattenJSON$results$geometry$location$lat[1]
    google_longitude <- flattenJSON$results$geometry$location$lng[1]
    
    google_street_address <- ifelse("street_address" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "street_address"], "")
    google_route <- ifelse("route" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "route"], "")
    google_intersection <- ifelse("intersection" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "intersection"], "")
    google_country <- ifelse("country" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "country"], "")
    google_administrative_area_level_1 <- ifelse("administrative_area_level_1" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "administrative_area_level_1"], "")
    google_administrative_area_level_2 <- ifelse("administrative_area_level_2" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "administrative_area_level_2"], "")
    google_administrative_area_level_3 <- ifelse("administrative_area_level_3" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "administrative_area_level_3"], "")
    google_administrative_area_level_4 <- ifelse("administrative_area_level_4" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "administrative_area_level_4"], "")
    google_administrative_area_level_5 <- ifelse("administrative_area_level_5" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "administrative_area_level_5"], "")
    google_locality <- ifelse("locality" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "locality"], "")
    google_neighborhood <- ifelse("neighborhood" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "neighborhood"], "")
    google_premise <- ifelse("premise" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "premise"], "")
    google_subpremise <- ifelse("subpremise" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "subpremise"], "")
    google_postal_code <- ifelse("postal_code" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "postal_code"], "")
    google_street_number <- ifelse("street_number" %in% flattenJSON$results$address_components[[1]]$types, flattenJSON$results$address_components[[1]]$long_name[flattenJSON$results$address_components[[1]]$type == "street_number"], "")
    
    return(data.frame(input_latlng = input_latlng, 
                      google_formatted_address = google_formatted_address, 
                      google_location_type = google_location_type, 
                      google_latitude = google_latitude, 
                      google_longitude = google_longitude, 
                      google_street_address = google_street_address, 
                      google_route = google_route, 
                      google_intersection = google_intersection, 
                      google_country = google_country, 
                      google_administrative_area_level_1 = google_administrative_area_level_1, 
                      google_administrative_area_level_2 = google_administrative_area_level_2, 
                      google_administrative_area_level_3 = google_administrative_area_level_3, 
                      google_administrative_area_level_4 = google_administrative_area_level_4, 
                      google_administrative_area_level_5 = google_administrative_area_level_5, 
                      google_locality = google_locality, 
                      google_neighborhood = google_neighborhood, 
                      google_premise = google_premise, 
                      google_postal_code = google_postal_code, 
                      google_street_number = google_street_number, 
                      stringsAsFactors = F))
  }
  
  
  reverseBingFormat <- function(latlng, flattenJSON) {
    
    input_latlng <- latlng
    bing_formatted_address <- flattenJSON$resourceSets$resources[[1]]$address$formattedAddress[1]
    bing_location_type <- flattenJSON$resourceSets$resources[[1]]$geocodePoints[[1]]$calculationMethod[1]
    bing_match_code <- flattenJSON$resourceSets$resources[[1]]$matchCodes[[1]][1]
    bing_confidence <- flattenJSON$resourceSets$resources[[1]]$confidence[1]
    bing_latitude <- flattenJSON$resourceSets$resources[[1]]$geocodePoints[[1]]$coordinates[[1]][1]
    bing_longitude <- flattenJSON$resourceSets$resources[[1]]$geocodePoints[[1]]$coordinates[[1]][2]
    
    bing_addressLine <- ifelse("addressLine" %in% names(flattenJSON$resourceSets$resources[[1]]$address), flattenJSON$resourceSets$resources[[1]]$address$addressLine[1], "")
    bing_locality <- ifelse("locality" %in% names(flattenJSON$resourceSets$resources[[1]]$address), flattenJSON$resourceSets$resources[[1]]$address$locality[1], "")
    bing_neighborhood <- ifelse("neighborhood" %in% names(flattenJSON$resourceSets$resources[[1]]$address), flattenJSON$resourceSets$resources[[1]]$address$neighborhood[1], "")
    bing_adminDistrict <- ifelse("adminDistrict" %in% names(flattenJSON$resourceSets$resources[[1]]$address), flattenJSON$resourceSets$resources[[1]]$address$adminDistrict[1], "")
    bing_adminDistrict2 <- ifelse("adminDistrict2" %in% names(flattenJSON$resourceSets$resources[[1]]$address), flattenJSON$resourceSets$resources[[1]]$address$adminDistrict2[1], "")
    bing_postalCode <- ifelse("postalCode" %in% names(flattenJSON$resourceSets$resources[[1]]$address), flattenJSON$resourceSets$resources[[1]]$address$postalCode[1], "")
    bing_countryRegion <- ifelse("countryRegion" %in% names(flattenJSON$resourceSets$resources[[1]]$address), flattenJSON$resourceSets$resources[[1]]$address$countryRegion[1], "")
    bing_countryRegionIso2 <- ifelse("countryRegionIso2" %in% names(flattenJSON$resourceSets$resources[[1]]$address), flattenJSON$resourceSets$resources[[1]]$address$countryRegionIso2[1], "")
    
    return(data.frame(input_latlng = input_latlng, 
                      bing_formatted_address = bing_formatted_address, 
                      bing_location_type = bing_location_type, 
                      bing_match_code = bing_match_code, 
                      bing_confidence = bing_confidence, 
                      bing_latitude = bing_latitude, 
                      bing_longitude = bing_longitude, 
                      bing_addressLine = bing_addressLine,
                      bing_locality = bing_locality, 
                      bing_neighborhood = bing_neighborhood, 
                      bing_adminDistrict = bing_adminDistrict, 
                      bing_adminDistrict2 = bing_adminDistrict2, 
                      bing_postalCode = bing_postalCode, 
                      bing_countryRegion = bing_countryRegion, 
                      bing_countryRegionIso2 = bing_countryRegionIso2, 
                      stringsAsFactors = F))
  }
  
  
  reverse <- function(latlng, language = "en", geocoder = c("Google", "Bing"), authentication_key = NULL, max.counter = 20) {
    
    counter <- 0
    urlSearch <- urlReverse(latlng, return.call = "json", language = language, geocoder = geocoder, authentication_key = authentication_key)
    origJSON <- getURL(urlSearch)
    Sys.sleep(0.2)
    flattenJSON <- fromJSON(origJSON, flatten = FALSE)
    
    while (counter < max.counter) {
      if (geocoder == "Google") {
        if(flattenJSON$status=="OK") {
          return (reverseGoogleFormat(latlng, flattenJSON))
        }
      }
      if (geocoder == "Bing") {
        if(flattenJSON$resourceSets$estimatedTotal>0) {
          return (reverseBingFormat(latlng, flattenJSON))
        }
      }
      counter <- counter + 1
    }
    return (NULL)
  }
  
  reverse_Pipe <- function(latlng_df, language = "en", geocoder = c("Google", "Bing"), authentication_key = NULL, max.counter = 20) {
    
    output_df_list <- list()
    
    withProgress(message = "Geocoding in Progress...", value = 0, {
    n <- nrow(latlng_df)
    
    for (i in 1:n) {
      
      latlng <- paste(latlng_df[i, ], collapse = ",")
      # if(verbose) cat("Geocoding store ", i, " of ", nrow(address_df), " stores...\n")
      reverseOutput <- reverse(latlng, language = language, geocoder = geocoder, authentication_key = authentication_key, max.counter = max.counter)
      
      if (geocoder == "Google") {
        if (is.null(reverseOutput)) 
          reverseOutput <- data.frame(input_latlng = latlng, 
                                      google_formatted_address = "No location found.", 
                                      google_location_type = "", 
                                      google_latitude = "", 
                                      google_longitude = "", 
                                      google_street_address = "", 
                                      google_route = "", 
                                      google_intersection = "", 
                                      google_country = "", 
                                      google_administrative_area_level_1 = "", 
                                      google_administrative_area_level_2 = "", 
                                      google_administrative_area_level_3 = "", 
                                      google_administrative_area_level_4 = "", 
                                      google_administrative_area_level_5 = "", 
                                      google_locality = "", 
                                      google_neighborhood = "", 
                                      google_premise = "", 
                                      google_postal_code = "", 
                                      google_street_number = "", 
                                      stringsAsFactors = F)
      }
      
      if (geocoder == "Bing") {
        if (is.null(reverseOutput)) 
          reverseOutput <- data.frame(input_latlng = latlng, 
                                      bing_formatted_address = "No location found", 
                                      bing_location_type = "", 
                                      bing_match_code = "", 
                                      bing_confidence = "", 
                                      bing_latitude = "", 
                                      bing_longitude = "", 
                                      bing_addressLine = "",
                                      bing_locality = "", 
                                      bing_neighborhood = "", 
                                      bing_adminDistrict = "", 
                                      bing_adminDistrict2 = "", 
                                      bing_postalCode = "", 
                                      bing_countryRegion = "", 
                                      bing_countryRegionIso2 = "", 
                                      stringsAsFactors = F)
      }
      # if(verbose) cat("Input Address: ", address, "\n", "Output Address: ", geocodeOutput$google_formatted_address, "\n")
      output_df_list[[i]] <- reverseOutput
      
      incProgress(1/n, detail = paste0("Geocoding store ", i, " of ", nrow(latlng_df), " stores..."))
    }
    })
    output_df <- do.call(rbind, output_df_list)
    return (output_df)
  }
  
  writeUtf8 <- function(x, file) {
    con <- file(file, "wb")
    writeBin(charToRaw(paste(paste(names(x), collapse='\t'), '\r\n', sep='')), con, endian="little")
    apply(x, 1, function(a) {
      b <- paste(paste(a, collapse='\t'), '\r\n', sep='')
      writeBin(charToRaw(b), con, endian="little")
    })
    close(con)
  }
  
  
  ##################################
  ### Fixed Tables/Functions UIs ###
  ##################################
  
  SeparatorReference <- reactive({
    return (data.table(sepInput = c("tab", "comma", "semicolon", "pipe"), separator = c("\t", ",", ";", "|")))
  })
  
  ##############################################
  ### Conditional UIs for "Geocoding" module ###
  ##############################################
  
  output$geocode_FileSepSelect_UI <- renderUI({
    if (is.null(input$geocode_File)) return(NULL)
    return (radioButtons(inputId = "geocode_FileSep", label = "Indicate Separator for Input File: ", choices = c("tab", "comma", "semicolon", "pipe")))
  })
  
  output$geocode_FileUpload_UI <- renderUI({
    if (is.null(input$geocode_File)) return(NULL)
    return (actionButton(inputId = "geocode_FileUpload", label = "Upload Input File"))
  })
  
  geocode_DT <- eventReactive(input$geocode_FileUpload, {
    geocode_sep <- SeparatorReference()[sepInput == input$geocode_FileSep, separator]
    geocode_DTreturn <- fread(input$geocode_File$datapath, sep = geocode_sep, header = T, verbose = F, showProgress = F, stringsAsFactors = F, encoding = "UTF-8", strip.white = TRUE)
    geocode_DTreturn[, RowNumber:= 1:nrow(geocode_DTreturn)]
    setcolorder(geocode_DTreturn, c("RowNumber", names(geocode_DTreturn)[-which(names(geocode_DTreturn) == "RowNumber")]))
    return (geocode_DTreturn)
  })
  
  output$geocode_DTShow_UI <- renderUI({
    if (is.null(geocode_DT())) return(NULL)
    return (actionButton(inputId = "geocode_DTShow", label = "Show Input File"))
  })
  
  output$geocode_Street_UI <- renderUI({
    if (is.null(geocode_DT())) return(NULL)
    return (selectizeInput(inputId = "geocode_Street", label = "Address Line Fields to be used for Geocoding (in the order used in Postal Address) E.g., street name, house number.  Please exclude floor/unit number and building names.", choices = names(geocode_DT())[-1], multiple = T))
  })
  
  output$geocode_City_UI <- renderUI({
    if (is.null(input$geocode_Street)) return(NULL)
    return (selectizeInput(inputId = "geocode_City", label = "Locality Fields to be used for Geocoding (in the order used in Postal Address) E.g., city, province, country.", choices = names(geocode_DT())[-c(1, which(names(geocode_DT()) %in% input$geocode_Street))], multiple = T))
  })
  
  output$geocode_QualityMissing_UI <- renderUI({
    if (is.null(input$geocode_City)) return(NULL)
    return (textInput(inputId = "geocode_QualityMissing", label = "Please enter text labels (without quotation marks) indicating missing values.  Multiple entries should be separated with a pipe '|'."))
  })
  
  output$geocode_QualityCheck_UI <- renderUI({
    if (is.null(input$geocode_City)) return(NULL)
    return (actionButton(inputId = "geocode_QualityCheck", label = "Check Percentage of Address Fields with Missing Data"))
  })
  
  geocode_DTQuality <- reactiveValues(dt = NULL)
  observeEvent(input$geocode_QualityCheck, {
    geocode_missingIndicator <- toupper(c("", unlist(strsplit(input$geocode_QualityMissing, split = "[|]"))))
    geocode_Headers <- c(input$geocode_Street, input$geocode_City)
    geocode_DT <- geocode_DT()
    geocode_DTsubsetList <- geocode_DT[, lapply(.SD, function(x) (is.na(x) | toupper(x) %in% geocode_missingIndicator)), .SDcols = c("RowNumber", geocode_Headers)]
    geocode_DTPercent <- geocode_DT[, lapply(.SD, function(x) paste0(round(sum(is.na(x) | x %in% geocode_missingIndicator)/nrow(geocode_DT) * 100, 4), "%")), .SDcols = geocode_Headers]
    geocode_DTPoorData <- geocode_DT[apply(geocode_DTsubsetList, 1, function(x) ifelse(max(x) == 1, T, F))]
    geocode_DTQuality$dt <- list(geocode_DTPercent = geocode_DTPercent, geocode_DTPoorData = geocode_DTPoorData)
  })
  
  output$geocode_PoorPercentageShow_UI <- renderUI({
    if (is.null(geocode_DTQuality$dt)) return(NULL)
    return (actionButton(inputId = "geocode_PoorPercentageShow", label = "Show Percentage of Poor Quality Data By Address Fields"))
  })
  
  output$geocode_PoorDataShow_UI <- renderUI({
    if (is.null(geocode_DTQuality$dt)) return(NULL)
    return (actionButton(inputId = "geocode_PoorDataShow", label = "Show all Poor Quality Data"))
  })
  
  output$geocode_PoorDTDownload <- downloadHandler(
    # downloadHandler() takes two arguments, both functions.
    # The content function is passed a filename as an argument, and
    #   it should write out data to that filename.
    filename = function() paste0(substr(input$geocode_File, start = 1, stop = nchar(input$geocode_File) - 4), "_Geocode_PoorQualityData.txt"),
    
    # This function should write data to a file given to it by
    # the argument 'file'.
    content = function(file) {
      # Write to a file specified by the 'file' argument
      writeUtf8(geocode_DTQuality$dt$geocode_DTPoorData, file)
    }
  )
  
  output$geocode_Warning <- renderText({
    if (is.null(geocode_DTQuality$dt) | is.null(input$geocode_City)) return(NULL)
    if (max(as.numeric(gsub("%", "", geocode_DTQuality$dt$geocode_DTPercent))) > 0)
      return("Warning: There are missing entries in the address fields to be used for Geocoding.")
    return(NULL)
  })
  
  output$geocode_Language_UI <- renderUI({
    if (is.null(geocode_DTQuality$dt) | is.null(input$geocode_City)) return(NULL)
    return (selectizeInput(inputId = "geocode_Language", label = "Select the language encoding for Geocoded returns.", choices = languageTable()$language, selected = "English"))
  })
  
  output$geocode_Start_UI <- renderUI({
    if (is.null(geocode_DTQuality$dt) | is.null(input$geocode_City)) return(NULL)
    return (sliderInput(inputId = "geocode_Start", label = "Select the starting row number for Geocoding.", min = 1, max = nrow(geocode_DT()), value = 1, step = 1, round = T))
  })
  
  output$geocode_End_UI <- renderUI({
    if (is.null(input$geocode_Start) | is.null(input$geocode_City)) return(NULL)
    return (sliderInput(inputId = "geocode_End", label = "Select the ending row number for Geocoding. (Recommended number of addresses to Geocode is 1500)", min = input$geocode_Start, max = nrow(geocode_DT()), value = input$geocode_Start, step = 1, round = T))
  })
  
  output$geocode_Num <- renderText({
    if (is.null(input$geocode_End) | is.null(input$geocode_City)) return(NULL)
     return (paste0("You have selected ", input$geocode_End - input$geocode_Start + 1, " address(es) for Geocoding."))
  })
  
  output$geocode_NumWarning <- renderText({
    if (is.null(input$geocode_End) | is.null(input$geocode_City)) return(NULL)
    if (input$geocode_End - input$geocode_Start + 1 > 2500)
      return (paste0("You have selected more than 2500 addresses (daily limit for Google free API). Are you sure you want to continue?"))
    if (input$geocode_End - input$geocode_Start + 1 > 1500)
      return (paste0("You have selected more than the recommended number of addresses (1500). Are you sure you want to continue?"))
    return (paste0("Are you sure you want to continue?"))
  })
  
  output$geocode_Geocoder_UI <- renderUI({
    if (is.null(input$geocode_End) | is.null(input$geocode_City)) return(NULL)
    return (selectizeInput(inputId = "geocode_Geocoder", label = "Please select the Geocoder to be used", choices = geocoderTable(), selected = "Google"))
  })
  
  output$geocode_Key_UI <- renderUI({
    if (is.null(input$geocode_Geocoder)) return(NULL)
    if (input$geocode_Geocoder == "Google") return(NULL)
    return (textInput(inputId = "geocode_Key", label = "Please enter your API Key", value = ""))
  })
  
  output$geocode_Begin_UI <- renderUI({
    if (is.null(input$geocode_End) | is.null(input$geocode_City)) return(NULL)
    return (actionButton(inputId = "geocode_Begin", label = "Begin Geocoding"))
  })
  
  geocode_output <- reactiveValues(output = NULL, summary = NULL)
  observeEvent(input$geocode_Begin, {
    geocode_language <- languageTable()[language == input$geocode_Language, .(code)]
    geocode_Headers <- c(input$geocode_Street, input$geocode_City)
    geocode_input_df_all_cols <- geocode_DT()[input$geocode_Start:input$geocode_End, ]
    geocode_input_df <- data.frame(geocode_input_df_all_cols[, copy(.SD), .SDcols = c("RowNumber", geocode_Headers)])
    geocode_input_df_street <- subset(geocode_input_df, select = input$geocode_Street)
    geocode_input_df_city <- subset(geocode_input_df, select = input$geocode_City)
    if (input$geocode_Geocoder == "Google") {
      geocode_Key <- NULL
    } else {
      geocode_Key <- input$geocode_Key
    }
    geocode_output_df <- geocode_Pipe(geocode_input_df_street, geocode_input_df_city, language = geocode_language, geocoder = input$geocode_Geocoder, authentication_key = geocode_Key, max.counter = 20)
    geocode_output$output_display <- data.frame(geocode_input_df, geocode_output_df)
    geocode_output$output <- data.frame(geocode_input_df_all_cols, geocode_output_df)
    if (input$geocode_Geocoder == "Google") {
      geocode_output$summary <- data.frame(table(geocode_output$output$google_location_type))
      names(geocode_output$summary) <- c("google_location_type", "Frequency")
    }
    if (input$geocode_Geocoder == "Bing") {
      geocode_output$summary <- data.frame(table(geocode_output$output$bing_match_code))
      names(geocode_output$summary) <- c("bing_match_code", "Frequency")
    }
    geocode_output$summary$Percentage <- paste0(round(geocode_output$summary$Frequency / (input$geocode_End - input$geocode_Start + 1) * 100, 1), "%") 
  })
  
  output$geocode_OutputShow_UI <- renderUI({
    if (is.null(geocode_output$output)) return(NULL)
    return (actionButton(inputId = "geocode_OutputShow", label = "Show Geocoded Output"))
  })
  
  output$geocode_SummaryShow_UI <- renderUI({
    if (is.null(geocode_output$summary)) return(NULL)
    return (actionButton(inputId = "geocode_SummaryShow", label = "Show Geocoded Summary"))
  })
  
  output$geocode_FileDownload <- downloadHandler(
    # downloadHandler() takes two arguments, both functions.
    # The content function is passed a filename as an argument, and
    #   it should write out data to that filename.
    filename = function() paste0(substr(input$geocode_File, start = 1, stop = nchar(input$geocode_File) - 4), "_", input$geocode_Start, "-", input$geocode_End, "_Geocoded.txt"),
    
    # This function should write data to a file given to it by
    # the argument 'file'.
    content = function(file) {
      # Write to a file specified by the 'file' argument
      writeUtf8(geocode_output$output, file)
    }
  )
  
  geocode_Show <- reactiveValues(file = NULL)
  observeEvent(input$geocode_DTShow, {
    geocode_Show$file <- "DT"
  })
  observeEvent(input$geocode_PoorPercentageShow, {
    geocode_Show$file <- "PoorPercentage"
  })
  observeEvent(input$geocode_PoorDataShow, {
    geocode_Show$file <- "PoorData"
  })
  observeEvent(input$geocode_OutputShow, {
    geocode_Show$file <- "Output"
  })
  observeEvent(input$geocode_SummaryShow, {
    geocode_Show$file <- "Summary"
  })
  output$geocode_Show <- renderDataTable({
    if (is.null(geocode_Show$file)) return(NULL)
    if (geocode_Show$file == "DT") return(geocode_DT())
    if (geocode_Show$file == "PoorPercentage") return(geocode_DTQuality$dt$geocode_DTPercent)
    if (geocode_Show$file == "PoorData") return(geocode_DTQuality$dt$geocode_DTPoorData)
    if (geocode_Show$file == "Output") return(geocode_output$output_display)
    if (geocode_Show$file == "Summary") return(geocode_output$summary)
  })
  
  
  ######################################################
  ### Conditional UIs for "Reverse-Geocoding" module ###
  ######################################################
  
  output$reverse_FileSepSelect_UI <- renderUI({
    if (is.null(input$reverse_File)) return(NULL)
    return (radioButtons(inputId = "reverse_FileSep", label = "Indicate Separator for Input File: ", choices = c("tab", "comma", "semicolon", "pipe")))
  })
  
  output$reverse_FileUpload_UI <- renderUI({
    if (is.null(input$reverse_File)) return(NULL)
    return (actionButton(inputId = "reverse_FileUpload", label = "Upload Input File"))
  })
  
  reverse_DT <- eventReactive(input$reverse_FileUpload, {
    reverse_sep <- SeparatorReference()[sepInput == input$reverse_FileSep, separator]
    reverse_DTreturn <- fread(input$reverse_File$datapath, sep = reverse_sep, header = T, verbose = F, showProgress = F, stringsAsFactors = F, encoding = "UTF-8", strip.white = TRUE)
    reverse_DTreturn[, RowNumber:= 1:nrow(reverse_DTreturn)]
    setcolorder(reverse_DTreturn, c("RowNumber", names(reverse_DTreturn)[-which(names(reverse_DTreturn) == "RowNumber")]))
    return (reverse_DTreturn)
  })
  
  output$reverse_DTShow_UI <- renderUI({
    if (is.null(reverse_DT())) return(NULL)
    return (actionButton(inputId = "reverse_DTShow", label = "Show Input File"))
  })
  
  output$reverse_Fields_UI <- renderUI({
    if (is.null(reverse_DT())) return(NULL)
    return (selectizeInput(inputId = "reverse_Fields", label = "Lat-Long columns for Reverse-Geocoding (Latitude first, followed by Longitude)", choices = names(reverse_DT())[-1], multiple = T))
  })
  
  output$reverse_QualityMissing_UI <- renderUI({
    if (is.null(input$reverse_Fields)) return(NULL)
    return (textInput(inputId = "reverse_QualityMissing", label = "Please enter text labels (without quotation marks) indicating missing values.  Multiple entries should be separated with a pipe '|'."))
  })
  
  output$reverse_QualityCheck_UI <- renderUI({
    if (is.null(input$reverse_Fields)) return(NULL)
    return (actionButton(inputId = "reverse_QualityCheck", label = "Check Percentage of Entries with Missing Lat-Long Data"))
  })
  
  reverse_DTQuality <- reactiveValues(dt = NULL)
  observeEvent(input$reverse_QualityCheck, {
    reverse_missingIndicator <- toupper(c("", unlist(strsplit(input$reverse_QualityMissing, split = "[|]"))))
    reverse_Headers <- input$reverse_Fields
    reverse_DT <- reverse_DT()
    reverse_DTsubsetList <- reverse_DT[, lapply(.SD, function(x) (is.na(x) | toupper(x) %in% reverse_missingIndicator)), .SDcols = c("RowNumber", reverse_Headers)]
    reverse_DTPercent <- reverse_DT[, lapply(.SD, function(x) paste0(round(sum(is.na(x) | x %in% reverse_missingIndicator)/nrow(reverse_DT) * 100, 4), "%")), .SDcols = reverse_Headers]
    reverse_DTPoorData <- reverse_DT[apply(reverse_DTsubsetList, 1, function(x) ifelse(max(x) == 1, T, F))]
    reverse_DTQuality$dt <- list(reverse_DTPercent = reverse_DTPercent, reverse_DTPoorData = reverse_DTPoorData)
  })
  
  output$reverse_PoorPercentageShow_UI <- renderUI({
    if (is.null(reverse_DTQuality$dt)) return(NULL)
    return (actionButton(inputId = "reverse_PoorPercentageShow", label = "Show Percentage of Entries with Missing Lat-Long Data"))
  })
  
  output$reverse_PoorDataShow_UI <- renderUI({
    if (is.null(reverse_DTQuality$dt)) return(NULL)
    return (actionButton(inputId = "reverse_PoorDataShow", label = "Show all Entries with Missing Lat-Long Data"))
  })
  
  output$reverse_PoorDTDownload <- downloadHandler(
    # downloadHandler() takes two arguments, both functions.
    # The content function is passed a filename as an argument, and
    #   it should write out data to that filename.
    filename = function() paste0(substr(input$reverse_File, start = 1, stop = nchar(input$reverse_File) - 4), "_reverse_PoorQualityData.txt"),
    
    # This function should write data to a file given to it by
    # the argument 'file'.
    content = function(file) {
      # Write to a file specified by the 'file' argument
      writeUtf8(reverse_DTQuality$dt$reverse_DTPoorData, file)
    }
  )
  
  output$reverse_Warning <- renderText({
    if (is.null(reverse_DTQuality$dt) | is.null(input$reverse_Fields)) return(NULL)
    if (max(as.numeric(gsub("%", "", reverse_DTQuality$dt$reverse_DTPercent))) > 0)
      return("Warning: There are missing entries in the address fields to be used for Reverse-Geocoding.")
    return(NULL)
  })
  
  output$reverse_Language_UI <- renderUI({
    if (is.null(reverse_DTQuality$dt) | is.null(input$reverse_Fields)) return(NULL)
    return (selectizeInput(inputId = "reverse_Language", label = "Select the language encoding for Reverse-Geocoded returns.", choices = languageTable()$language, selected = "English"))
  })
  
  output$reverse_Start_UI <- renderUI({
    if (is.null(reverse_DTQuality$dt) | is.null(input$reverse_Fields)) return(NULL)
    return (sliderInput(inputId = "reverse_Start", label = "Select the starting row number for Reverse-Geocoding.", min = 1, max = nrow(reverse_DT()), value = 1, step = 1, round = T))
  })
  
  output$reverse_End_UI <- renderUI({
    if (is.null(input$reverse_Start) | is.null(input$reverse_Fields)) return(NULL)
    return (sliderInput(inputId = "reverse_End", label = "Select the ending row number for Reverse-Geocoding. (Recommended number of addresses to Geocode is 1500)", min = input$reverse_Start, max = nrow(reverse_DT()), value = input$reverse_Start, step = 1, round = T))
  })
  
  output$reverse_Num <- renderText({
    if (is.null(input$reverse_End) | is.null(input$reverse_Fields)) return(NULL)
    return (paste0("You have selected ", input$reverse_End - input$reverse_Start + 1, " address(es) for Reverse-Geocoding."))
  })
  
  output$reverse_NumWarning <- renderText({
    if (is.null(input$reverse_End) | is.null(input$reverse_Fields)) return(NULL)
    if (input$reverse_End - input$reverse_Start + 1 > 2500)
      return (paste0("You have selected more than 2500 addresses (daily limit for Google free API). Are you sure you want to continue?"))
    if (input$reverse_End - input$reverse_Start + 1 > 1500)
      return (paste0("You have selected more than the recommended number of addresses (1500). Are you sure you want to continue?"))
    return (paste0("Are you sure you want to continue?"))
  })
  
    output$reverse_Geocoder_UI <- renderUI({
    if (is.null(input$reverse_End) | is.null(input$reverse_Fields)) return(NULL)
    return (selectizeInput(inputId = "reverse_Geocoder", label = "Please select the Geocoder to be used", choices = geocoderTable(), selected = "Google"))
  })
  
  output$reverse_Key_UI <- renderUI({
    if (is.null(input$reverse_Geocoder)) return(NULL)
    if (input$reverse_Geocoder == "Google") return(NULL)
    return (textInput(inputId = "reverse_Key", label = "Please enter your API Key", value = ""))
  })
  
  
  output$reverse_Begin_UI <- renderUI({
    if (is.null(input$reverse_End) | is.null(input$reverse_Fields)) return(NULL)
    return (actionButton(inputId = "reverse_Begin", label = "Begin Reverse-Geocoding"))
  })
#   
#   reverse_output <- reactiveValues(output = NULL, summary = NULL)
#   observeEvent(input$reverse_Begin, {
#     reverse_language <- languageTable()[language == input$reverse_Language, .(code)]
#     reverse_Headers <- input$reverse_Fields
#     reverse_input_df <- data.frame(reverse_DT()[input$reverse_Start:input$reverse_End, copy(.SD), .SDcols = c("RowNumber", reverse_Headers)])
#     reverse_output_df <- geocodePipe(reverse_input_df[, -1], language = reverse_language, max.counter = 5)
#     reverse_output$output <- data.frame(reverse_input_df, reverse_output_df)
#     reverse_output$summary <- data.frame(table(reverse_output$output$google_location_type))
#     names(reverse_output$summary) <- c("google_location_type", "Frequency")
#     reverse_output$summary$Percentage <- paste0(round(reverse_output$summary$Frequency / (input$reverse_End - input$reverse_Start + 1) * 100, 1), "%")
#   })
  
  reverse_output <- reactiveValues(output = NULL, summary = NULL)
  observeEvent(input$reverse_Begin, {
    reverse_language <- languageTable()[language == input$reverse_Language, .(code)]
    reverse_Headers <- input$reverse_Fields
    reverse_input_df_all_cols <- reverse_DT()[input$reverse_Start:input$reverse_End, ]
    reverse_input_df <- data.frame(reverse_input_df_all_cols[, copy(.SD), .SDcols = c("RowNumber", reverse_Headers)])
    if (input$reverse_Geocoder == "Google") {
      reverse_Key <- NULL
    } else {
      reverse_Key <- input$reverse_Key
    }
    reverse_output_df <- reverse_Pipe(reverse_input_df[, -1], language = reverse_language, geocoder = input$reverse_Geocoder, authentication_key = reverse_Key, max.counter = 20)
    reverse_output$output_display <- data.frame(reverse_input_df, reverse_output_df)
    reverse_output$output <- data.frame(reverse_input_df_all_cols, reverse_output_df)
    if (input$reverse_Geocoder == "Google") {
      reverse_output$summary <- data.frame(table(reverse_output$output$google_location_type))
      names(reverse_output$summary) <- c("google_location_type", "Frequency")
    }
    if (input$reverse_Geocoder == "Bing") {
      reverse_output$summary <- data.frame(table(reverse_output$output$bing_match_code))
      names(reverse_output$summary) <- c("bing_match_code", "Frequency")
    }
    reverse_output$summary$Percentage <- paste0(round(reverse_output$summary$Frequency / (input$reverse_End - input$reverse_Start + 1) * 100, 1), "%") 
  })
  
  output$reverse_OutputShow_UI <- renderUI({
    if (is.null(reverse_output$output)) return(NULL)
    return (actionButton(inputId = "reverse_OutputShow", label = "Show Reverse-Geocoded Output"))
  })
  
  output$reverse_SummaryShow_UI <- renderUI({
    if (is.null(reverse_output$summary)) return(NULL)
    return (actionButton(inputId = "reverse_SummaryShow", label = "Show Reverse-Geocoded Summary"))
  })
  
  output$reverse_FileDownload <- downloadHandler(
    # downloadHandler() takes two arguments, both functions.
    # The content function is passed a filename as an argument, and
    #   it should write out data to that filename.
    filename = function() paste0(substr(input$reverse_File, start = 1, stop = nchar(input$reverse_File) - 4), "_", input$reverse_Start, "-", input$reverse_End, "_Reversed_Geocoded.txt"),
    
    # This function should write data to a file given to it by
    # the argument 'file'.
    content = function(file) {
      # Write to a file specified by the 'file' argument
      writeUtf8(reverse_output$output, file)
    }
  )
  
  reverse_Show <- reactiveValues(file = NULL)
  observeEvent(input$reverse_DTShow, {
    reverse_Show$file <- "DT"
  })
  observeEvent(input$reverse_PoorPercentageShow, {
    reverse_Show$file <- "PoorPercentage"
  })
  observeEvent(input$reverse_PoorDataShow, {
    reverse_Show$file <- "PoorData"
  })
  observeEvent(input$reverse_OutputShow, {
    reverse_Show$file <- "Output"
  })
  observeEvent(input$reverse_SummaryShow, {
    reverse_Show$file <- "Summary"
  })
  output$reverse_Show <- renderDataTable({
    if (is.null(reverse_Show$file)) return(NULL)
    if (reverse_Show$file == "DT") return(reverse_DT())
    if (reverse_Show$file == "PoorPercentage") return(reverse_DTQuality$dt$reverse_DTPercent)
    if (reverse_Show$file == "PoorData") return(reverse_DTQuality$dt$reverse_DTPoorData)
    if (reverse_Show$file == "Output") return(reverse_output$output_display)
    if (reverse_Show$file == "Summary") return(reverse_output$summary)
  })
  
  
  #########################################################################################
  ### Conditional UIs for "Compare Geocoded Data with Available GPS Coordinates" module ###
  #########################################################################################

  output$compare_FileSepSelect_UI <- renderUI({
    if (is.null(input$compare_File)) return(NULL)
    return (radioButtons(inputId = "compare_FileSep", label = "Indicate Separator for Input File: ", choices = c("tab", "comma", "semicolon", "pipe")))
  })
  
  output$compare_FileUpload_UI <- renderUI({
    if (is.null(input$compare_File)) return(NULL)
    return (actionButton(inputId = "compare_FileUpload", label = "Upload Input File"))
  })
  
  compare_DT <- eventReactive(input$compare_FileUpload, {
    compare_sep <- SeparatorReference()[sepInput == input$compare_FileSep, separator]
    compare_DTreturn <- fread(input$compare_File$datapath, sep = compare_sep, header = T, verbose = F, showProgress = F, stringsAsFactors = F, encoding = "UTF-8", strip.white = TRUE)
    compare_DTreturn[, RowNumber:= 1:nrow(compare_DTreturn)]
    setcolorder(compare_DTreturn, c("RowNumber", names(compare_DTreturn)[-which(names(compare_DTreturn) == "RowNumber")]))
    return (compare_DTreturn)
  })
  
  output$compare_DTShow_UI <- renderUI({
    if (is.null(compare_DT())) return(NULL)
    return (actionButton(inputId = "compare_DTShow", label = "Show Input File"))
  })
  
  output$compare_LatLong1Fields_UI <- renderUI({
    if (is.null(compare_DT())) return(NULL)
    return (selectizeInput(inputId = "compare_LatLong1Fields", label = "Set 1 of Lat-Long Fields to be used for Comparison (Latitude first, followed by Longitude)", choices = names(compare_DT())[-1], multiple = T))
  })
  
  output$compare_LatLong2Fields_UI <- renderUI({
    if (is.null(input$compare_LatLong1Fields)) return(NULL)
    return (selectizeInput(inputId = "compare_LatLong2Fields", label = "Set 2 of Lat-Long Fields to be used for Comparison (Latitude first, followed by Longitude)", choices = names(compare_DT())[-c(1, which(names(compare_DT()) %in% input$compare_LatLong1Fields))], multiple = T))
  })
  
  output$compare_Begin_UI <- renderUI({
    if (is.null(input$compare_LatLong2Fields)) return(NULL)
    return (actionButton(inputId = "compare_Begin", label = "Compute Distance between Pairs of Lat-Long (km)"))
  })
  
  compare_output <- reactiveValues(dt = NULL, summary = NULL)
  observeEvent(input$compare_Begin, {
    compare_LatLong1_df <- data.frame(compare_DT()[, copy(.SD), .SDcols = input$compare_LatLong1Fields])
    compare_LatLong2_df <- data.frame(compare_DT()[, copy(.SD), .SDcols = input$compare_LatLong2Fields])
    dist <- rdist.earth.vec(compare_LatLong1_df[, c(2, 1)], compare_LatLong2_df[, c(2, 1)], miles = F)
    compare_output$dt <- data.frame(compare_DT(), dist)
    compare_output$summary <- data.frame(Measure = names(summary(dist)), Value = as.numeric(summary(dist)))
  })
  
  output$compare_FileDownload <- downloadHandler(
    # downloadHandler() takes two arguments, both functions.
    # The content function is passed a filename as an argument, and
    #   it should write out data to that filename.
    filename = function() paste0(substr(input$compare_File, start = 1, stop = nchar(input$compare_File) - 4), "_", input$compare_Start, "-", input$compare_End, "_CompareGPS.txt"),
    
    # This function should write data to a file given to it by
    # the argument 'file'.
    content = function(file) {
      # Write to a file specified by the 'file' argument
      writeUtf8(compare_output$dt, file)
    }
  )
  
  output$compare_SummaryShow_UI <- renderUI({
    if (is.null(compare_output$dt)) return(NULL)
    return (actionButton(inputId = "compare_SummaryShow", label = "Show Summary File"))
  })
  
  compare_Show <- reactiveValues(file = NULL)
  observeEvent(input$compare_DTShow, {
    compare_Show$file <- "DT"
  })
  observeEvent(input$compare_SummaryShow, {
    compare_Show$file <- "Summary"
  })
  output$compare_DTShow <- renderDataTable({
    if (is.null(compare_Show$file)) return(NULL)
    if (compare_Show$file == "DT") return(compare_DT())
    if (compare_Show$file == "Summary") return(compare_output$summary)
  })
  
  
}

ui <- fluidPage(theme = shinytheme("spacelab"), 
  
  headerPanel("Geocoding Application"), 
  
  sidebarPanel(
    
    #########################################
    ### Conditional panel for "Geocoding" ###
    #########################################
    conditionalPanel(
      condition = "input.tabs==1", 
      
      # Upload Dictionary File
      fileInput(inputId = "geocode_File", label = "File for Geocoding (.txt/.csv). Note: Max Size = 100 Mb", 
                accept=c("text/csv", ".csv", ".txt")), 
      uiOutput("geocode_FileSepSelect_UI"), 
      uiOutput("geocode_FileUpload_UI"), 
      uiOutput("geocode_DTShow_UI"), 
      br(), 
      
      # Fields to be Used for Geocoding
      uiOutput("geocode_Street_UI"), 
      uiOutput("geocode_City_UI"), 
      
      # Address Check
      uiOutput("geocode_QualityMissing_UI"), 
      uiOutput("geocode_QualityCheck_UI"), 
      br(), 
      uiOutput("geocode_PoorPercentageShow_UI"), 
      uiOutput("geocode_PoorDataShow_UI"), 
      br(), 
      conditionalPanel(
        condition = "input.geocode_QualityCheck == true",
        downloadButton("geocode_PoorDTDownload", "Download Data with Poor Quality Address Fields")
      ), 
      
      br(), 
      
      # Geocode Data
      h4(textOutput("geocode_Warning"), style = "color:red"), 
      br(), 
      uiOutput("geocode_Language_UI"), 
      uiOutput("geocode_Start_UI"), 
      uiOutput("geocode_End_UI"), 
      br(), 
      h5(textOutput("geocode_Num")), 
      br(), 
      uiOutput("geocode_Geocoder_UI"), 
      uiOutput("geocode_Key_UI"), 
      br(), 
      h4(textOutput("geocode_NumWarning"), style = "color:red"), 
      uiOutput("geocode_Begin_UI"), 
      uiOutput("geocode_OutputShow_UI"), 
      uiOutput("geocode_SummaryShow_UI"), 
      br(), 
      conditionalPanel(
        condition = "input.geocode_Begin == true",
        downloadButton("geocode_FileDownload", "Download Geocoded Data")
      )
    )
    , 
    
    
    #################################################
    ### Conditional panel for "Reverse Geocoding" ###
    #################################################
    
    conditionalPanel(
      condition = "input.tabs==2", 
      
      # Upload Dictionary File
      fileInput(inputId = "reverse_File", label = "File for Reverse-Geocoding (.txt/.csv). Note: Max Size = 100 Mb", 
                accept=c("text/csv", ".csv", ".txt")), 
      uiOutput("reverse_FileSepSelect_UI"), 
      uiOutput("reverse_FileUpload_UI"), 
      uiOutput("reverse_DTShow_UI"), 
      br(), 
      
      # Fields to be Used for Geocoding
      uiOutput("reverse_Fields_UI"), 
      
      # Address Check
      uiOutput("reverse_QualityMissing_UI"), 
      uiOutput("reverse_QualityCheck_UI"), 
      br(), 
      uiOutput("reverse_PoorPercentageShow_UI"), 
      uiOutput("reverse_PoorDataShow_UI"), 
      br(), 
      conditionalPanel(
        condition = "input.reverse_QualityCheck == true",
        downloadButton("reverse_PoorDTDownload", "Download Entries with Missing Lat-Long Data")
      ), 
      
      br(), 
      
      # Geocode Data
      h4(textOutput("reverse_Warning"), style = "color:red"), 
      br(), 
      uiOutput("reverse_Language_UI"), 
      uiOutput("reverse_Start_UI"), 
      uiOutput("reverse_End_UI"), 
      br(), 
      h5(textOutput("reverse_Num")), 
      br(), 
      uiOutput("reverse_Geocoder_UI"), 
      uiOutput("reverse_Key_UI"), 
      br(), 
      h4(textOutput("reverse_NumWarning"), style = "color:red"), 
      uiOutput("reverse_Begin_UI"), 
      uiOutput("reverse_OutputShow_UI"), 
      uiOutput("reverse_SummaryShow_UI"), 
      br(), 
      conditionalPanel(
        condition = "input.reverse_Begin == true",
        downloadButton("reverse_FileDownload", "Download Reversed-Geocoded Data")
      )
    )
    , 
    
    
    ####################################################################################
    ### Conditional panel for "Compare Geocoded Data with Available GPS Coordinates" ###
    ####################################################################################
    conditionalPanel(
      condition = "input.tabs==3", 
      
      # Upload Dictionary File
      fileInput(inputId = "compare_File", label = "File Input with two sets of GPS Coordinates (.txt/.csv). Note: Max Size = 100 Mb", 
                accept=c("text/csv", ".csv", ".txt")), 
      uiOutput("compare_FileSepSelect_UI"), 
      uiOutput("compare_FileUpload_UI"), 
      uiOutput("compare_DTShow_UI"), 
      br(), 
      
      # Fields to be Used for Comparison
      uiOutput("compare_LatLong1Fields_UI"), 
      uiOutput("compare_LatLong2Fields_UI"), 
      br(), 
      
      # Distance Computation
      uiOutput("compare_Begin_UI"), 
      uiOutput("compare_SummaryShow_UI"), 
      br(),
      conditionalPanel(
        condition = "input.compare_Begin == true",
        downloadButton("compare_FileDownload", "Download Compared Data")
      )
    )

#     # Conditional panel for "Store Matching"
#     conditionalPanel(condition = "input.tabs==4", 
#                      fileInput(inputId = "dictionary", label = "Base/Dictionary File", 
#                                accept=c('text/csv', 'text/comma-separated-values,text/plain')), 
#                      fileInput(inputId = "lookup", label = "Lookup File", 
#                                accept=c('text/csv', 'text/comma-separated-values,text/plain')), 
#                      checkboxInput(inputId = "matchingFields", label = "Fields to be used for Store Matching", value = F), 
#                      actionButton(inputId = "storeMatching", label = "Start Store Matching")
#     )
  )
  ,
  mainPanel(
    tabsetPanel(id = "tabs", 
                tabPanel(title = "Geocoding using Address String", value = 1, dataTableOutput("geocode_Show"))
                , tabPanel(title  = "Reverse-Geocoding using Available GPS Coordinates", value = 2, dataTableOutput("reverse_Show"))
                , tabPanel(title  = "Compare Geocoded Data with Existing GPS Coordinates", value = 3, dataTableOutput("compare_DTShow"))
                # , tabPanel(title  = "Store-Matching", value = 4)
    )
  )
)

shinyApp(ui = ui, server = server)