## Web Scrapping - 1. https://www.thengolist.com/volunteer-in-laos.html
library(rvest)
url<-read_html("https://www.thengolist.com/volunteer-in-laos.html")

#Get the elements needed to create the dataframe

name<-url%>%html_nodes(".wsite-content-title a")%>%html_text()
description<-url%>%html_nodes("span+ .paragraph")%>%html_text()
website<-substr(url%>%html_nodes("font a"),17,200)
website[4]<-paste("www.",website[4])
website[8]<-paste("www.",website[8])
website<-gsub("/.*","",website)
cause_area<-url%>%html_nodes(".wsite-content-title br+ font")%>%html_text()
cause_area<-gsub("/Laos.*","",cause_area)
df<-cbind(name,cause_area,description,website)
write.csv(df, file = "C:/Users/Pamela/Desktop/Data Dive/NGO_List_Laos.csv")








