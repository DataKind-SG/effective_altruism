from bs4 import BeautifulSoup
import urllib
import requests
import pandas as pd
import numpy as np
import re
#import urllib2
import time

#page = requests.get("http://www.wikiwand.com/en/List_of_non-governmental_organizations_in_Thailand#/overview")
#soup = BeautifulSoup(page.content, 'html.parser')
f = open('index.html')      # simplified for the example (no urllib)
soup = BeautifulSoup(f,'html.parser')
columns = ['name','description','website','cause_area','city']
results = {}

links = []
org_lists = []
name_list = []
#df = pd.DataFrame(columns = columns)
url_root = "http://db0nus869y26v.cloudfront.net"

sections = soup.find_all('section')
count = 0
for section in sections:
    print(count)
    #every cause area
    if 'article_content' in section.get_attribute_list('class'):
        links += section.get_attribute_list('id')
        #url_ext = ''.join(section.li.a.get_attribute_list('href'))
        #every section/cause area
        for link in links:
            if link in section.get_attribute_list('id'):
                #every organization
                for name in section.find_all('a'):
                    org_dict = {}
                    url_ext = ''.join(name.get_attribute_list('href'))
                    if 'wikipedia' in url_ext:
                    #     url_ext = ""
                        continue
                    if 'Citation_needed' in name.get_attribute_list("href"):
                        continue
                    url_ext = url_ext.replace("http://www.wikiwand.com", url_root)
                    org_dict['name'] = name.next_element
                    #org_dict['name'] = ''.join(name.contents)
                    print(org_dict['name'])
                    #org_dict['cause_area'] = section.span.text
                    url = url_ext
                    #org_dict['url'] = url
                    #org_lists.append(org_dict)
                    #Each organisation's page
                    page = requests.get(url)
                    page_soup = BeautifulSoup(page.content, 'html.parser')
                    org_sections = page_soup.find_all('section')
                    paragraph_list = []
                    description_list = []
                    for org_section in org_sections:
                        #Description
                        if 'article_content' in org_section.get_attribute_list('class'):
                            if 'overview' in org_section.get_attribute_list('id'):
                                for paragraph in org_section.find_all('p'):
                                    description_list.append(paragraph.text)
                                org_dict['description'] = ''.join(description_list)
                                #Website add later
                            # else:
                            #     for paragraph in org_section.find_all('p'):
                            #         paragraph_list.append(paragraph.text)
                            #         org_dict['programme_types'] = ''.join(paragraph_list)
                            for header in org_section.find_all('th'):
                                if 'Website' in header:
                                    if(len(header.parent.find_all('a')) != 0):
                                        web = header.parent.a.get_attribute_list('href')
                                        org_dict['website'] = ''.join(web)
                                if 'Location' in header:
                                    city = header.parent.li.text
                                    org_dict['city'] = ''.join(city)
                                if 'Purpose' in header:
                                    purpose = header.parent.td.text
                                    org_dict['cause_area'] = ''.join(purpose)
                    org_lists.append(org_dict)
                    count +=1
                    print(count)


df = pd.DataFrame(columns=columns, data=org_lists).fillna('')
df.to_csv("result.csv")
print("DONE")

# name
# description
# website
# cause_area
# programme_types
# address
# country
# city
# contact_number
# email
# contact_person