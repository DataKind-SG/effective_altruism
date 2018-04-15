from bs4 import BeautifulSoup
import pandas as pd
import requests
import math
import time
import random

source_csv = 'web_scrape_v2.csv'
target_csv = 'web_scrape_v2_aft_google.csv'


# source_csv = 'wikiwand_thailand.csv'
# target_csv = 'wikiwand_thailand1.csv'

result_file = pd.read_csv(source_csv,  encoding="latin-1")

if 'address_google' not in result_file.columns:
    result_file['address_google'] = ''

if 'contact_number_google' not in result_file.columns:
    result_file['contact_number_google'] = ''

if 'lat' not in result_file.columns:
    result_file['lat'] = ''

if 'long' not in result_file.columns:
    result_file['long'] = ''

address_counter = 0
tel_counter = 0
lat_long_counter = 0

for i in range(result_file.shape[0]):
    # if not isinstance(result_file.ix[i]['address'], str) and not isinstance(result_file.ix[i]['contact_number'], str):
    #     continue

    ngo_name = result_file['name'][i]

    print('processing:' + str(i) + '\t' + ngo_name)
    additional_search_words = ['', 'NGO']

    # time.sleep(random.random() * 3)

    found = False
    for each_add_search_word in additional_search_words:

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
                if each_span.text.replace(' ', '').replace('+', '').isdigit():
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
                result_file.set_value(i, 'long', lat_long_list[1])
                lat_long_counter+=1
                found = True

        if found:
            print('found!')
            break

    # save every 1000 records
    if i % 1000 == 0:
        result_file.to_csv(target_csv)

result_file.to_csv(target_csv)
print('address_counter:' + str(address_counter))
print('tel_counter:' + str(tel_counter))
print('lat_long_counter:' + str(lat_long_counter))
