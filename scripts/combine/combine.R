library(data.table)

#List the directory which contains all the csv files
setwd("../..")
file_dir = "data/input/web_scraping/"

#Character vector of all acceptable column names
columns = c("name","description","website","cause_area","programme_types","address","country","city","contact_number")

#Read each file and check if the column names are all acceptable names and bind them together
data = rbindlist(lapply(list.files(file_dir), function(i){
  x=read.csv(paste(file_dir, "/", i, sep = ""), stringsAsFactors = F)
  
  if (all(colnames(x) %in% columns) == F) {
    print(i)
    print(setdiff(colnames(x), columns))
  } else {
    print(paste0("All columns are correct in:", i))
  }
  
  x$file = i
  x
}), fill = T)

#export data file
write.csv(data,"data/output/web_scraping/web_scrape_v1.csv", na="", row.names =F)
