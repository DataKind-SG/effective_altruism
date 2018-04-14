from bs4 import BeautifulSoup
import pandas as pd
import requests

source_csv = 'changemakers_indonesia_bef_google.csv'
target_csv = 'changemakers_indonesia.csv'

result_file = pd.read_csv(source_csv)

if 'address' not in result_file.columns:
    result_file['address'] = ''

if 'contact_number' not in result_file.columns:
    result_file['contact_number'] = ''

address_counter = 0
tel_counter = 0
for i in range(result_file['name'].shape[0]):
    print('processing:' + str(i))
    ngo_name = result_file['name'][i]
    search_result_page = requests.get('https://www.google.com/search?q=' + ngo_name.replace(' ', '%20'))
    search_result_soup = BeautifulSoup(search_result_page.content, 'html.parser')
    a_list = search_result_soup.find_all('a')

    for each_a in a_list:
        if 'LvEtkb' in each_a.get_attribute_list('class'):
            addr_href = each_a.get('href')
            address_str = addr_href[addr_href.find('addr') + 5:addr_href.find('&ved')].replace('+', ' ')
            result_file.set_value(i, 'address', address_str)
            address_counter+=1

    span_list = search_result_soup.find_all('span')
    for each_span in span_list:
        if 'A1t5ne' in each_span.get_attribute_list('class'):
            # indonesia specific
            if '+62' in each_span.text:
                result_file.set_value(i, 'contact_number', each_span.text)
                tel_counter+=1

print('address_counter:' + str(address_counter) + ' tel_counter:' + str(tel_counter))

result_file.to_csv(target_csv)