library(data.table)
library(readr)

#List the directory which contains all the csv files
setwd("../..")
file_dir = "data/input/web_scraping/"

#Character vector of all acceptable column names
columns = c("name","description","website","cause_area","programme_types","address","country","city","contact_number","email")

#Read each file and check if the column names are all acceptable names and bind them together
data = rbindlist(lapply(list.files(file_dir), function(i){
  x=read_csv(paste(file_dir, "/", i, sep = ""))
  
  if (all(colnames(x) %in% columns) == F) {
    print(i)
    print(setdiff(colnames(x), columns))
  } else {
    print(paste0("All columns are correct in:", i))
  }
  
  x$file = i
  x
}), fill = T)

colnames(data) = make.names(colnames(data))
data[,c("X1","Unnamed..0","X12","X10","X11","X13","X5","X6","X7") := NULL]

#export data file
fwrite(data,"data/output/web_scraping/web_scrape_v3.csv", row.names =F)
