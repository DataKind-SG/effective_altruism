import requests
from bs4 import BeautifulSoup

landing_page = "https://www.bali.com/charities-ngos.html"


landing_page_request = requests.get(landing_page)
landing_page_soup = BeautifulSoup(landing_page_request.text,"html.parser")

sorted_page_anchor = landing_page_soup.find("ul", attrs={"class":"pagination"} )

page_list=[]
page_href = []

for i in sorted_page_anchor.find_all("li"):
    page_list.append(i.text.replace("\n","")) # remove "\n" characters
    
for i in ["next","back"]:
    if i in page_list:
        page_list.remove(i)

page_urls_list = []

for i in page_list:
    page_urls_list.append("https://www.bali.com/charity_"+i+".html")

# print(page_urls_list)

listing_url_list = []

for url in page_urls_list:

    url_request = requests.get(url)

    url_request_soup = BeautifulSoup(url_request.text,"html.parser")
    
    a = url_request_soup.find_all("a",class_="btn btn-primary")
    
    for i in a:
        listing_url_list.append("https://www.bali.com"+i['href'])
# print(listing_url_list)	

# Prepare all the required lists 
org_list= []

telephone_list=[]
mobile_list=[]

city_list =[]
address_list = []

email_list = []
website_list = []

yof_list = []
programs_list=[]
description_list = []
cause_list=[]

twitter_list = []
facebook_list =[]
instagram_list=[]
googleplus_list=[]

country_list =[]

for i in listing_url_list:
    
    ngo_soup = BeautifulSoup(requests.get(i).text,"html.parser")
    
    # Organisation
    org_list.append(ngo_soup.find("h1", class_= "lh1em").text)
    
    # Find telephone and mobile numbers
    contact_box =[]
    telephone = []
    mobile =[]
        
    for i in ngo_soup.find_all("div",class_="col-md-4"):
        if len(i.find_all("p")) ==0:
            continue
        else:
            contact_box.append(i.find_all("p"))
    
    for i in contact_box[0]:
    
        if i.find_all("i"):
            
            for j in i.find_all("i"):
                
                if "fa-phone" in j["class"]:
                    telephone = j.next_sibling

                if "fa-mobile-phone" in j["class"]:
                    mobile = j.next_sibling
    
    if telephone:
        telephone_list.append(telephone.strip())
    else:
        telephone_list.append("NA")
    
    if mobile:
        mobile_list.append(mobile.strip())
    else:
        mobile_list.append("NA")
            
    # Find City and Address information
    city_and_add =  ngo_soup.find("div", class_="col-md-9").find("p").text.split("|")
    
    city = city_and_add[0]
    add = city_and_add[1]   
    
    for i in ["\t","\n"]:
        if i in city:
            city = str(city).replace(i,"")
        if i in add:
            add = str(add).replace(i,"")
    
    city=city.strip()
    add=add.strip()
    
    # if there is no address in city_and_add, find address details in contact_box[0]
    if len(add) == 0:
        
        for i in contact_box[0]:
            # use "Area:" to detect paragraph with address
            if "Area:" in i.text:
                add = i.text
    
                # Find everything after ":" in Area: XX\nxxx". Would come with \n to split
                add = add.split(": ")[1]
                add = add.split("\n",1)[1]
                
                if "\t" in add:
                    add = str(add).replace("\t"," ")
    
                if "\n" in add:
                    add = str(add).replace("\n","")
                
                add=add.strip()
    
    city_list.append(city)
    address_list.append(add)
    del city
    del add
    
    # find email and website
    email = []
    website = []
    email_and_web = []
    
    for i in contact_box[0]:
        if len(i.find_all("a",href=True)) ==0:
            continue
        else: 
            email_and_web.append(i.find_all("a",href=True))

    if email_and_web: # exists
        for i in email_and_web[0]:
            if "mailto:" in i['href']:
                email = i['href'].split("mailto:")[1]

    if len(email) ==0:
        email_list.append("NA")
    else: 
        email_list.append(email)
    
    if email_and_web: #exists
        for i in email_and_web[0]:
            if "http" in i['href']:
                website = i['href']
    
    if len(website) ==0:
        website_list.append("NA")
    else:
        website_list.append(website)
    
    del email
    del website
    
    # YOF, Programs, Cause 
    programs = []
    cause = []
    yof = []
    bullet_list = []
    
    for i in ngo_soup.find_all("div",class_="col-md-6"):
        bullet_list.append(i.find_all("span",class_="booking-item-feature-title"))
     
    # only care about 1st item in bullet_list
    for i in bullet_list[0]:
        if "Founding" in i.text:
            yof = i.text
        elif "Mission" in i.text:
            programs = i.text
        elif "Type of Yayasan" in i.text:
            cause = i.text
    
    for i in ["\t","\n"]:
        if i in yof:
            yof = str(yof).replace(i,"")
        if i in programs:
            programs = str(programs).replace(i,"")
        if i in cause:
            cause = str(cause).replace(i,"")
    
    if yof:
        yof_list.append(yof.split(": ")[1])
    else:
        yof_list.append("NA")
        
    if programs:    
        programs_list.append(programs.split(": ")[1])
    else:
        programs_list.append("NA")
        
    if cause:
        cause_list.append(cause.split(": ",1)[1])
    else:
        cause_list.append("NA")
       
    # Description
    description_list.append(ngo_soup.find("div",class_="col-md-12").find("p").text)
    
    # Facebook, Twitter, Instagram, Googleplus
    
    social_media_box = ngo_soup.find_all("div",class_="col-md-4")
       
    facebook=[]
    twitter = []
    googleplus=[]
    instagram=[]
    
    for i in social_media_box:
        if i.find_all("ul","list list-horizontal list-space"):
            
            for j in i.find_all("ul","list list-horizontal list-space"):

                if j.find_all("a",class_="fa-facebook"):
                    facebook = j.find("a",class_="fa-facebook")['href']
                if j.find_all("a",class_="fa-twitter"):
                    twitter = j.find("a",class_="fa-twitter")['href']
                if j.find("a", class_="fa-instagram"):    
                    instagram = j.find("a",class_="fa-instagram")['href']
                if j.find("a", class_="fa-google-plus"):    
                    googleplus = j.find("a",class_="fa-google-plus")['href']

    if facebook:
        facebook_list.append(facebook)
    else:
        facebook_list.append("NA")
        
    if twitter:
        twitter_list.append(twitter)
    else:
        twitter_list.append("NA")
        
    if instagram:
        instagram_list.append(instagram)
    else:
        instagram_list.append("NA")
        
    if googleplus:
        googleplus_list.append(googleplus)
    else:
        googleplus_list.append("NA")
        
    country_list.append("Indonesia")

# Contact list should be telephone first, if not available, then mobile number
contact_list =[]

for i in range(len(telephone_list)):
    if telephone_list[i] =="NA":
        contact_list.append(mobile_list[i])
    else:
        contact_list.append(telephone_list[i])

import pandas as pd

# all original variables
df0 = pd.DataFrame({"Organisation":org_list,
                    "NGO Listing Page":listing_url_list,
                    "Classified Category":cause_list,
                    "Address":address_list,
                    "Telephone":telephone_list,
                    "Mobile":mobile_list,
                    "Email":email_list,
                    "Website":website_list,
                    "Twitter":twitter_list,
                    "Facebook":facebook_list,
                    "GooglePlus":googleplus_list,
                    "Instagram":instagram_list,
                    "Description":description_list,
                    "Programs":programs_list,
                    "Year of Foundation":yof_list,
                    "Country":country_list
                   })

# Processed mined data for EA
df = pd.DataFrame({"organisation":org_list,
                   "description":description_list,
                   "website":website_list,
                   "cause_area":cause_list,
                   "programme_types":programs_list,
                   "address":address_list,
                   "country":country_list,
                   "city":city_list,
                   "contact_number":contact_list,
                   "email":email_list
                  })

df0 = df0[["Organisation",
                    "NGO Listing Page",
                    "Classified Category",
                    "Address",
                    "Telephone",
                    "Mobile",
                    "Email",
                    "Website",
                    "Twitter",
                    "Facebook",
                    "GooglePlus",
                    "Instagram",
                    "Description",
                    "Programs",
                    "Year of Foundation",
                    "Country"
                   ]]

df = df[["organisation",
                   "description",
                   "website",
                   "cause_area",
                   "programme_types",
                   "address",
                   "country",
                   "city",
                   "contact_number",
                   "email"
                  ]]

# Output to csv
df0.to_csv("bali_ngo_all_data.csv")
df.to_csv("bali_ngo_EA_data.csv")