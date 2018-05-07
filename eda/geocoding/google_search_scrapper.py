#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
import math
import time
import random
import traceback
import os.path as path

source_csv = path.abspath(path.join("../..","data/output/web_scraping/web_scrape_cleaned.csv"))
target_csv = path.abspath(path.join("../..","data/output/web_scraping/web_scrape_cleaned_aft_google.csv"))

result_file = pd.read_csv(source_csv,  encoding="utf-8", na_values = " ")

if 'address_google' not in result_file.columns:
    result_file['address_google'] = ''

if 'contact_number_google' not in result_file.columns:
    result_file['contact_number_google'] = ''

if 'lat' not in result_file.columns:
    result_file['lat'] = ''

if 'lon' not in result_file.columns:
    result_file['lon'] = ''

address_counter = 0
tel_counter = 0
lat_long_counter = 0

for i in range(result_file.shape[0]):
    # if not isinstance(result_file.iloc[i]['address'], str) and not isinstance(result_file.iloc[i]['contact_number'], str):
    #     continue
    if pd.isnull(result_file['name'][i]) == True:
        print(str(i), 'skipped as name is blank')
        continue
    
    if pd.isnull(result_file['country'][i]) == True:
        ngo_name = str(result_file['name'][i]) 
    else:
        ngo_name = str(result_file['name'][i]) + str(" ") + str(result_file['country'][i])

    if not isinstance(ngo_name, str):
        continue

    print('processing:' + str(i) + '\t' + ngo_name)
    additional_search_words = ['', 'NGO']

    time.sleep(random.random() * 3)

    found = False
    for each_add_search_word in additional_search_words:

        error_ind = True
        while error_ind:
            try:
                search_result_page = requests.get('https://www.google.com/search?q=' + ngo_name.replace(' ', '%20') + '%20' + each_add_search_word)

                # in case google catch you, wait for 10 mins
                if 'CAPTCHA' in str(search_result_page.content):
                    print('caught by google. sleep for 10 mins')
                    time.sleep(600)
                    search_result_page = requests.get('https://www.google.com/search?q=' + ngo_name.replace(' ', '%20') + '%20' + each_add_search_word)

                search_result_soup = BeautifulSoup(search_result_page.content, 'html.parser')

                # search address
                a_list = search_result_soup.find_all('a')
                for each_a in a_list:
                    if 'LvEtkb' in each_a.get_attribute_list('class'):
                        addr_href = each_a.get('href')
                        address_str = addr_href[addr_href.find('addr') + 5:addr_href.find('&ved')].replace('+', ' ')
                        result_file.set_value(i, 'address_google', address_str)
                        found = True
                        address_counter+=1

                # search contact
                span_list = search_result_soup.find_all('span')
                for each_span in span_list:
                    if 'A1t5ne' in each_span.get_attribute_list('class'):
                        if 'Phone' in each_span.parent.span.text:
                            result_file.set_value(i, 'contact_number_google', each_span.text)
                            tel_counter+=1
                            found = True

                # search lat long
                div_list = search_result_soup.find_all('div')
                for each_div in div_list:
                    if 'R8KuR' in each_div.get_attribute_list('class'):
                        maps_href = each_div.a.get('href')
                        if maps_href.find('ll=') == -1:
                            continue
                        lat_long_list = maps_href[maps_href.find('ll=')+3:maps_href.find('&z')].split(',')
                        result_file.set_value(i, 'lat', lat_long_list[0])
                        result_file.set_value(i, 'lon', lat_long_list[1])
                        lat_long_counter+=1
                        found = True

                error_ind = False
            except Exception as e:
                error_ind = True
                #print(traceback.format_exc())
                traceback.print_exc()
                print('Exception caught! Sleeping for 15 mins')
                time.sleep(900)

        if found:
            print('found!')
            break

    # save every 1000 records
    if i % 1000 == 0:
        result_file.to_csv(target_csv, index = False, encoding = "utf-8")

result_file['address'] = result_file['address'].replace('Nan', np.NaN)

# set all address as google values
# set blank contact numbers as google contact numbers
# drop address_google, contact_num_google
result_file.loc[
        (result_file['address_google'].notnull()), 
        ['address']] = result_file['address_google']

result_file.loc[
        (result_file['contact_number'].isnull()),
        ['contact_number']] = result_file['contact_number_google']

result_file.drop(['location','address_google','contact_number_google'], axis = 1, inplace = True)

result_file.to_csv(target_csv, index = False, encoding = "utf-8")
print('address_counter:' + str(address_counter))
print('tel_counter:' + str(tel_counter))
print('lat_long_counter:' + str(lat_long_counter))
