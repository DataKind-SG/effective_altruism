import requests
from bs4 import BeautifulSoup

# Get all pages into a page scrapping list
# landing_page = "https://ngo.mycitizen.net/"
# Note that main page list as shown in landing site is not updated with navigation buttons at the bottom. To test this, at the bottom,
# navigate to page 2 and back to page 1 (New page 1 list is not the same as Landing Site page listing). Also proven by different url links.
# Thus, method to obtain all updated comprehensive list is to apply a sorting filter ("Newest First") and start with all pages listed.

# Sorted page listings to obtain all pages of listing
sort_page_list=[]

# sorted_page_soup = BeautifulSoup(requests.get(sorted_page_url).text,"html.parser")
# To find all the urls found in the navigation buttons
# for i in sorted_page_soup.find_all("a",class_="sabai-btn sabai-btn-default sabai-btn-sm"):
#     print(i['href'])
# Output print of urls obtained
# https://ngo.mycitizen.net/directory?p=2&category=0&zoom=15&is_mile=0&directory_radius=0&view=list&sort=newest
# https://ngo.mycitizen.net/directory?p=2&category=0&zoom=15&is_mile=0&directory_radius=0&view=list&sort=newest
# https://ngo.mycitizen.net/directory?p=2&category=0&zoom=15&is_mile=0&directory_radius=0&view=list&sort=newest
       
# Note that the website is not updated correctly on Page 1 of Sorted Filter, as the navigation links at the bottom are all 
# linked to "p=2" in the url even for navigation buttons page 1,2,3 as shown above.
# Thus, manually key in page number to get compiled filtered pages to scrape.

for i in range(3):
    p = i+1
    sort_page_list.append("https://ngo.mycitizen.net/directory?p={}&category=0&zoom=15&is_mile=0&directory_radius=0&view=list&sort=newest".format(p))

print(sort_page_list)

####################

# From sorted page list, obtain all the individual organisation names and their urls for NGO Myanmar Directory listing
org_list= []
listing_url_list = []

for sort_page in sort_page_list:
    
    sort_page_url = requests.get(sort_page)
    
    sort_page_soup = BeautifulSoup(sort_page_url.text,"html.parser")
    
    for soup in sort_page_soup.find_all('div', class_='sabai-directory-title'):
        # Get Organisation Title
        org_list.append(soup.find('a',href=True)['title'])
        # Get Organisation listing page
        listing_url_list.append(soup.find('a',href=True)['href'])

############################
# Scrap data from listing_url_list

# Prepare all the required lists (Category, Address,)
category_list=[]
address_list = []
telephone_list=[]
mobile_list=[]
email_list = []
website_list = []
twitter_list = []
facebook_list =[]
description_list =[]
local_name_list = []
activities_list = []
regid_list = []
yof_list = []
further_web_list = []

for url in listing_url_list:
    url_soup = BeautifulSoup(requests.get(url).text,"html.parser")

    container = url_soup.find("div",{"id":"sabai-body"})
    
    # Category class of organisation
    cat_class = url_soup.find('div', class_="sabai-directory-category").find_all("a",href=True)

    if cat_class is None:
        category_list.append("NA")
    else:
        #cat_class_list[0].text to see first category. Note that each word has 1 white space in front.
        # concatenate all the categories into single string, but separated by "/"
        text = "/".join(i.text[1:] for i in cat_class) # eliminate initial white space
        category_list.append(text)

    # Address location information
    loc_add = url_soup.find('span',class_ = "sabai-googlemaps-address")
    if loc_add is None:
        address_list.append("NA")
    else:
        address_list.append(loc_add.text[1:])

    # find contact information
    # Telephone
    contact_telephone = container.find("div", class_="sabai-directory-contact-tel")
    if contact_telephone is None:
        telephone_list.append("NA")
    else:
        telephone_list.append(contact_telephone.find("a",href=True).text)

    # Mobile
    contact_mobile = container.find("div",class_="sabai-directory-contact-mobile")
    if contact_mobile is None:
        mobile_list.append("NA")
    else:
        mobile_list.append(contact_mobile.find("a",href=True).text)

    # Email
    contact_email = container.find("div", class_= "sabai-directory-contact-email")
    if contact_email is None:
        email_list.append("NA")
    else:
        email_list.append(contact_email.find("a",href=True).text)

    # Website
    contact_website = container.find("div",class_="sabai-directory-contact-website")
    if contact_website is None:
        website_list.append("NA")
    else:
        website_list.append(contact_website.find("a", href=True).text)

    # Twitter
    contact_twitter = container.find("a",class_="sabai-directory-social-twitter")
    if contact_twitter is None:
        twitter_list.append("NA")
    else:
        twitter_list.append(contact_twitter['href'])

    # Facebook
    contact_facebook = container.find("a",class_="sabai-directory-social-facebook")
    if contact_facebook is None:
        facebook_list.append("NA")
    else:
        facebook_list.append(contact_facebook['href'])

    # Description body
    body_text = container.find("div","sabai-directory-body")

    if body_text is None:
        description_list.append("NA")
    else:
        description_list.append(body_text.text)

    # name in local lang
    local_name = container.find("div","sabai-field-name-field-title-own")
    if local_name is None:
        local_name_list.append("NA")
    else:
        local_name_list.append(local_name.find("div","sabai-field-value").text)

    # activities
    activities= container.find("div","sabai-field-name-field-activities")
    if activities is None:
        activities_list.append("NA")
    else:
        activities_list.append(activities.text)

    # registration id
    regid = container.find("div","sabai-field-name-field-reg-id")
    if regid is None:
        regid_list.append("NA")
    else:
        regid_list.append(regid.find("div","sabai-field-value").text)

    # year of foundation
    yof = container.find("div","sabai-field-name-field-founded")
    if yof is None:
        yof_list.append("NA")
    else:
        # Remove comma and convert to int
        yof_list.append(int(yof.find("div","sabai-field-value").text.replace(",","")))

    # Further websites
    further_web = container.find("div","sabai-field-name-field-websites")
    #.find_all("a",href=True)
    if further_web is None:
        further_web_list.append("NA")
    else:
        # append all further websites links separated by " | "
        further_web_list.append(" | ".join(i['href'] for i in further_web.find_all("a",href=True)))

# Create Combined Contact List
contact_list=[]

for i in range(len(org_list)):
    contact_list.append("Tel: {}, Mob: {}".format(telephone_list[i],mobile_list[i]))
    

# Create Country list
country_list =[]

for i in address_list:
    
    # Myanmar
    if any(x in i.lower() for x in ["yangon","chin state","moulmein","ayeyarwady","bogale","mandalay","myanmar"]):
        country_list.append("Myanmar")
    
    # USA
    elif any(x in i.lower() for x in ["tulsa","usa"]):
        country_list.append("USA")
    
    # Thailand
    elif any(x in i.lower() for x in ["chiang mai", "mae sot","mae sariang","mae hong son", "bangkok","thailand"]):
        country_list.append("Thailand")
    
    # India
    elif any(x in i.lower() for x in ["new delhi","mizoram","west delhi","manipur","india"]):
        country_list.append("India")
    
    # Austria   
    elif any(x in i.lower() for x in ["vienna","austria"]):
        country_list.append("Austria")
    
    # Germany
    elif any(x in i.lower() for x in ["essen","germany"]):
        country_list.append("Germany")
    
    # Czech Republic
    elif any(x in i.lower() for x in ["prague","czech republic"]):
        country_list.append("Czech Republic")

# Create City list
city_list =[]
# Ordered list in x of city names (Exhaustive and must be updated when website has more listings)
x = ["Yangon","Chin State","Moulmein","Ayeyarwady","Bogale","Mandalay","Tulsa","Chiang Mai", "Mae Sot","Mae Sariang","Mae Hong Son", 
     "Bangkok","New Delhi","Mizoram","West Delhi","Manipur","Vienna","Essen","Prague"]

#for i in address_list:

for i in range(len(address_list)):
    # City names are searched in order of list in x
    for a in x:
        # Append city names if found
        if a.lower() in address_list[i].lower():
            city_list.append(a)
            break
        # if no city names found in address, use country instead
        if a == x[-1] and (a.lower() in address_list[i].lower()) != 1:
            city_list.append(country_list[i])


import pandas as pd

# all original variables
df0 = pd.DataFrame({"Organisation":org_list,
                   "NGO Listing Page":listing_url_list,
                   "Classified Category":category_list,
                   "Address":address_list,
                   "Telephone":telephone_list,
                   "Mobile":mobile_list,
                   "Email":email_list,
                   "Website":website_list,
                   "Twitter":twitter_list,
                   "Facebook":facebook_list,
                   "Description":description_list,
                   "Name in Myanmese":local_name_list,
                   "Activities":activities_list,
                   "Registration ID":regid_list,
                   "Year of Foundation":yof_list,
                   "Further Links": further_web_list
                  })

# Processed mined data for EA
df = pd.DataFrame({"organisation":org_list,
                   "description":description_list,
                   "website":website_list,
                   "cause_area":category_list,
                   "programme_types":activities_list,
                   "address":address_list,
                   "country":country_list,
                   "city":city_list,
                   "contact_number":contact_list,
                   "email":email_list
                  })

# Reordering data frames
df0 = df0[["Organisation","NGO Listing Page","Classified Category",
         "Registration ID","Year of Foundation","Address",
         "Telephone","Mobile","Email",
         "Website","Twitter","Facebook",
         "Description","Activities","Name in Myanmese","Further Links"]]

df = df[["organisation","description","website","cause_area","programme_types","address","contact_number","email"]]

# df.head(20)

# Some data cleaning on EA Data
# Description: Remove all "\n" characters
df['description']=df['description'].str.replace("\n","")
# Activities: Remove all entries beginning with "\nActivities\n"
df['programme_types']=df['programme_types'].str.replace("\nActivities\n","")
df['programme_types']=df['programme_types'].str.replace("\n\n"," ")
df['programme_types']=df['programme_types'].str.replace("\n"," ")

# Some data cleaning on All Data
# Description: Remove all "\n" characters
df0['Description']=df0['Description'].str.replace("\n","")
# Activities: Remove all entries beginning with "\nActivities\n"
df0['Activities']=df0['Activities'].str.replace("\nActivities\n","")
df0['Activities']=df0['Activities'].str.replace("\n\n","")
df0['Activities']=df0['Activities'].str.replace("\n","")

# Output to csv
df0.to_csv("myanmar_ngo_all_data.csv")
df.to_csv("myanmar_ngo_EA_data.csv")