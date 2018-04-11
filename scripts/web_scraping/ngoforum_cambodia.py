#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 19:47:25 2018

@author: thiru
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
import inspect

headers = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36' }
BASE_URL = "https://www.ngoforum.org.kh"
TABLE_URL = 'https://www.ngoforum.org.kh/local-ngos/'
a_tag_counter = 0
table_counter = 0
errors = []
#==============================================================================
#                              Helper functions
#==============================================================================

# NOTE: inspect.stack()[0][3] is a shortcut to get name of current function

def obtain_soup(url):
    ob = requests.get(url,headers=headers).text
    soup = BeautifulSoup(ob, 'html.parser')
    return soup

def get_contact_person(individual_page):
    global a_tag_counter,table_counter
    func_name = inspect.stack()[0][3]
    name_tag = individual_page.find('p',{'class':'contact-position'})
    if not name_tag:
        handle_error(func_name,table_counter,a_tag_counter)
        return
    return name_tag.text

def get_email_add(individual_page):
    global a_tag_counter,table_counter
    func_name = inspect.stack()[0][3]
    email_tag = individual_page.find('span',{"class":'contact-emailto'})
    if not email_tag:
        handle_error(func_name,table_counter,a_tag_counter)
        return
    return email_tag.a.text

def get_address(individual_page):
    global a_tag_counter,table_counter
    address_tag = individual_page.find('address')
    func_name = inspect.stack()[0][3]
    if not address_tag:
        handle_error(func_name,table_counter,a_tag_counter)
        return
    return address_tag.text.strip().rstrip()

def get_phone(individual_page):
    global a_tag_counter,table_counter
    func_name = inspect.stack()[0][3]
    phone_tag = individual_page.find('span',{"class":"contact-telephone"})
    if not phone_tag:
        return handle_error(func_name,table_counter,a_tag_counter)
    return phone_tag.text.strip().rstrip()

def get_country(individual_page):
    return 'Cambodia'

def get_website(individual_page):
    global a_tag_counter,table_counter
    func_name = inspect.stack()[0][3]
    web_tag = individual_page.find('span',{"class":"contact-webpage"})
    if not web_tag:
        return handle_error(func_name,table_counter,a_tag_counter)
    return web_tag.a.text.strip().rstrip()

# Doesnt exist as of 7/2/17
def get_description(individual_page):
    return

# Doesnt exist as of 7/2/17
def get_cause_area(individual_page):
    return

# Doesnt exist as of 7/2/17
def get_programme_types(individual_page):
    return

# Doesnt exist as of 7/2/17
def get_city(individual_page):
    return

def handle_error(func_name,table_counter,a_tag_counter):
    print("{} - not found for table {} tag {}".format(func_name,table_counter,a_tag_counter))
    errors.append([table_counter,a_tag_counter,inspect.stack()[0][3]])
    return
#==============================================================================
#                                   main
#==============================================================================

# get the main table
soup = obtain_soup(TABLE_URL)
tbody = soup.find_all("tbody")

results = [["name","description","website","cause_area","programme_types",\
           "address","country","city","contact_number","email","contact_person"]]

for table in tbody:
    a_tags = table.find_all('a')
    for a_tag in a_tags:
        url = a_tag.get('href')
        proper_url = BASE_URL + url
        individual_page = obtain_soup(proper_url)

        name = a_tag.text.rstrip().strip()
        description = get_description(individual_page)
        website = get_website(individual_page)
        cause_area = get_cause_area(individual_page)
        programme_types = get_programme_types(individual_page)
        address = get_address(individual_page)
        country = get_country(individual_page)
        city = get_city(individual_page)
        phone_number = get_phone(individual_page)
        email = get_email_add(individual_page)
        contact_person = get_contact_person(individual_page)

        results.append([name,description,website,cause_area,programme_types,\
                        address,country,city,phone_number,email,contact_person])

        a_tag_counter += 1

    a_tag_counter = 0 #reset it
    table_counter += 1

df = pd.DataFrame(results)
df.to_csv("ngoforum_cambodia.csv",index=False)



