## Works on the geocoding portion of the project


## Sets the working Directory, 
## user need to define the workdirectory in setwd(workdirectory) eg. setwd("C:/Documents and Settings/Data")


setwd("C:/Documents and Settings/Data")
webdata <- read.csv("./data/output/web_scraping/web_scrape_v1.csv", header = TRUE, stringsAsFactors = FALSE)


# Check for duplicates


webdata <- webdata[order(webdata$name, decreasing = FALSE),]
webdata_u <- unique(webdata)


lookup_names <- data.frame(organizations = unique(webdata_u$name))


lookup_names$ID <- seq(from = 1, to = nrow(lookup_names), by = 1)


webdata_u$ID <- lookup_names$ID[match(webdata_u$name, lookup_names$organizations)]


webdata_u <- webdata_u[order(webdata_u$name, decreasing = FALSE),]


orgonly <- subset(webdata_u, select = c("ID", "country", "address", "city"))
orgonly_u <- unique(orgonly)


orgonly_add <- orgonly_u[orgonly_u$address!="",]


addresses <- unique(orgonly_add)


addresses1 <- addresses[1:1224,]
addresses2 <- addresses[1225:2449,]
addresses3 <- addresses[2450:3674,]
addresses4 <- addresses[3675:4899,]
addresses5 <- addresses[4900:nrow(addresses),]


write.csv(addresses1, "./addresses1.csv", row.names = FALSE)
write.csv(addresses2, "./addresses2.csv", row.names = FALSE) 
write.csv(addresses3, "./addresses3.csv", row.names = FALSE) 
write.csv(addresses4, "./addresses4.csv", row.names = FALSE) 
write.csv(addresses5, "./addresses5.csv", row.names = FALSE) 


#Addresses1 only


address1only <- unique(subset(addresses1, select = c("ID", "address")))


#Data cleaning steps


address1only$address <- gsub("\xa0", "", address1only$address)
address1only$address <- gsub("\\<", "", address1only$address)
address1only$address <- gsub("\\>", "", address1only$address)
address1only$address <- gsub("\n", " ", address1only$address)
address1only$address <- gsub("\xfc\xbe\x8c\xa3\xa4\xbc", "", address1only$address)


library(ggmap)


for(i in 1:nrow(address1only))
{
  # Print("Working...")
  result <- suppressWarnings(geocode(address1only$address[i], output = "latlona", source = "google"))
  
  if(!is.na(result[["lon"]])) {
    
    address1only$lon[i] <- as.numeric(result[1])
    address1only$lat[i] <- as.numeric(result[2])
    address1only$geoaddress[i] <- result$address
    
  } else {
    
    address1only$lon[i] <- NA
    address1only$lat[i] <- NA
    address1only$geoaddress[i] <- NA
    
  }
  
}


test <- address1only[582,]
result <- suppressWarnings(geocode(test$address, output = "latlona", source = "google"))