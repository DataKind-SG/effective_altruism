## Works on the geocoding portion of the project
## Sets the working Directory

library(dplyr)

setwd("/Users/yong/Documents/DataKind/EffectiveAltruism/workspace")

webdata <- read.csv("./web_scrape_v1.csv", header = TRUE, stringsAsFactors = FALSE)

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

#Extract the ones with geocode

filled <- subset(address1only, !is.na(address1only$lon))
null <- subset(address1only, is.na(address1only$lon))

#Using this package to overcome the problem of not being able to use API key.
require(geoChina)

#Running for Singapore Addresses first

null_u <- unique(subset(null, select = c("ID", "address")))

for (i in 1:nrow(null_u)) {
    
    add_split <- strsplit(null_u$address[i], split = " ")[[1]]
    null_u$last[i] <- add_split[length(add_split)]

}

null_u$singapore <- ifelse(grepl("singapore", tolower(null_u$address)), null_u$last, NA)
singaporeonly <- subset(null_u, !is.na(null_u$singapore))
singaporeonly[singaporeonly$ID == 112, "singapore"] <- "208263"
singaporeonly[singaporeonly$ID == 806, "singapore"] <- "130005"
singaporeonly[singaporeonly$ID == 2694, "singapore"][1] <- "308436"
singaporeonly[singaporeonly$ID == 3021, "singapore"][1] <- "479220"

singaporeonly <- singaporeonly %>% select("ID", "singapore") %>% rename(address = singapore)

for(i in 1:nrow(singaporeonly))
{
    print(paste0("Record: ",i))
    result <- suppressWarnings(geocode(singaporeonly$address[i], api = "google", key = "AIzaSyA8D34dA5zNbpvb_QIWHTSjmzgh-PCl-CU", output = "latlng"))
    
    if(!is.na(result[["lng"]])) {
        
        singaporeonly$lon[i] <- as.numeric(result[[2]])
        singaporeonly$lat[i] <- as.numeric(result[[1]])

    } else {
        
        singaporeonly$lon[i] <- NA
        singaporeonly$lat[i] <- NA

    }
    
}

null_u <- null_u %>% select("ID", "address")
null_u$lon <- singaporeonly$lon[match(null_u$ID, singaporeonly$ID)]
null_u$lat <- singaporeonly$lat[match(null_u$ID, singaporeonly$ID)]

filled2 <- null_u[!is.na(null_u$lon),]
null2 <- null_u[is.na(null_u$lon),]

clean <- rbind.data.frame(filled %>% select("ID", "address", "lon", "lat"), filled2)

# Geocoding for foreign addresses. Some singaporean addresses can't be matched. These
# addresses are to be given up.

null2 <- null2 %>% select("ID", "address")
null2$address <- gsub("\\.", "", null2$address)
null2$address <- gsub("\\,", "", null2$address)
null2$address <- gsub("\\/", "", null2$address)
null2$address <- gsub("B-[0-9]*", "", null2$address)
null2$address <- gsub("J-[0-9]*", "", null2$address)
##null2$address <- gsub("\bNo\b", "", null2$address, perl = TRUE)
##null2$address <- gsub("\bst\b", "", null2$address, perl = TRUE)
##null2$address <- gsub("\bnd\b", "", null2$address, perl = TRUE)

# test

test <- "Malviya Nagar New Delhi 110017 INDIA"
test_result <- geocode(test, api = "google", key = "AIzaSyA8D34dA5zNbpvb_QIWHTSjmzgh-PCl-CU", output = "latlng")

## Tagging of v2 and v3 diff data files

v2 <- read.csv("./web_scrape_v2_diff.csv", header = T, stringsAsFactors = FALSE)
v3 <- read.csv("./web_scrape_v2_v3_diff.csv", header = T, stringsAsFactors = FALSE)

# Creates the missing columns in v3 and arranges the columns in v3
missingcolumns <- colnames(v2)[!colnames(v2)%in%colnames(v3)]
for (i in missingcolumns) {
    
    print(paste0("Processing: ",i))
    v3[i] <- NA
    
}
v3 <- v3[c(colnames(v2))]

# Cleans up the address field of v3, as mostly are empty

v3$address <- ifelse(is.na(v3$address)&v3$city!="", v3$city, ifelse(is.na(v3$address)&v3$country!="", v3$country, NA))

# Combines v2 and v3 together
newdata <- rbind(v2, v3)
newdata_u <- unique(newdata)

# Checks for duplicate organizations in this new data. Takes out duplicate organizations,
# and do the ID coding for the new organizations

newdata_u$ID <- lookup_names$ID[match(newdata_u$name, lookup_names$organizations)]
neworgs <- newdata_u %>% select("ID", "name") %>% filter(is.na(ID)) %>%
    distinct() %>% rename(organizations = name)

# Carry out the ID-ing of the new organizations

neworgs <- neworgs[order(neworgs$organizations, decreasing=FALSE),]
neworgs_c <- neworgs[!neworgs$organizations%in%lookup_names$organizations,]
neworgs_c$ID <- seq(from = max(lookup_names$ID)+1, to = max(lookup_names$ID)+1+nrow(neworgs_c)-1, by = 1)

lookup_names <- lookup_names[c(colnames(neworgs_c))]

# Combine up the unique ID table for organization keys
master_lookup <- rbind(lookup_names, neworgs_c)
write.csv(master_lookup, "./master_lookup.csv", row.names = FALSE)

# Attaches the ID to the new data from web scraping

newdata_u$ID <- master_lookup$ID[match(newdata_u$name, master_lookup$organizations)]

# Forms the master list for geocoding

new_geodata <- newdata_u %>% select("ID", "country", "address", "city") %>% distinct()

# Do the cleaning up for Singapore first

singaporeonly2 <- subset(new_geodata, tolower(new_geodata$country) == "singapore")
others_new <- subset(new_geodata, tolower(new_geodata$country) != "singapore")

singaporeonly2 <- unique(subset(singaporeonly2, select = c("ID", "address")))

for (i in 1:nrow(singaporeonly2)) {
    
    add_split <- strsplit(singaporeonly2$address[i], split = " ")[[1]]
    singaporeonly2$last[i] <- add_split[length(add_split)]
    
}

singaporeonly2 <- singaporeonly2 %>% select("ID", "last") %>% rename(address = last)
others_new$address <- ifelse((others_new$address == ""|others_new$address == "Nan")&others_new$city!="", others_new$city,
                             ifelse((others_new$address == ""|others_new$address == "Nan")&others_new$country!="", others_new$country, others_new$address))

others_clean <- subset(others_new, !is.na(others_new$address))
others_clean2 <- subset(others_clean, others_clean$address!="")
others_clean3 <- subset(others_clean2, others_clean2$address!="Nan")

others_clean3 <- unique(others_clean3)
others_clean3$address <- gsub("#", "", others_clean3$address)
# Getting rid of ID 13002

others_clean3 <- subset(others_clean3, !ID %in% c("13002", "12958", "3941", "7760"))
others_clean3$address[others_clean3$ID==12907] <- others_clean3$city[others_clean3$ID==12907]
others_clean3$address <- trimws(others_clean3$address)

source("./dk_geocode.R")
singaporeonly2 <- dk_geocode(data = singaporeonly2, api_key = "AIzaSyBMW1G2PjuDTk8JZitAOTfeXGz0e-LvdJo")
others_clean3 <- dk_geocode(data = others_clean3, api_key = "AIzaSyA8MUQdXbNhaa7hVDazdQmtCUg0AieozV4")

new_singapore_clean <- subset(singaporeonly2, !is.na(singaporeonly2$lon)) %>% select("ID", "lat", "lon")
new_others_clean <- subset(others_clean3, !is.na(others_clean3$lon)) %>% select("ID", "lat", "lon")

newdata_geocoded <- unique(rbind(new_singapore_clean, new_others_clean))
write.csv(newdata_geocoded, "./newdata_geocoded.csv", row.names = FALSE)

# Combines the unique dataset for use in the dashboard

missingcolumns <- colnames(webdata_u)[!colnames(webdata_u)%in%colnames(newdata_u)]
for (i in missingcolumns) {
    
    print(paste0("Processing: ",i))
    newdata_u[i] <- NA
    
}
newdata_u <- newdata_u[c(colnames(webdata_u))]

webdata_final <- unique(rbind(webdata_u, newdata_u))
write.csv(webdata_final, "./webdata_final.csv", row.names = FALSE)
