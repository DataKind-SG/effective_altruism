from bs4 import BeautifulSoup
import pandas as pd
import requests

changemakers_indo = open('changemakers_indo.html')
soup = BeautifulSoup(changemakers_indo, 'html.parser')


result_list = []

for link in soup.find_all('a'):
    # r = requests.get(link.get('href'))
    link_str = link.get('href')
    if link_str is not None and 'entries' in link_str:
        record = {}
        record['name'] = link.text
        record['website'] = link_str
        record['country'] = 'Indonesia'

        # get each NGO page
        ngo_details_page = requests.get(link_str)
        ngo_dtl_soup = BeautifulSoup(ngo_details_page.content, 'html.parser')

        for ngo_dtl_divs in ngo_dtl_soup.find_all('div'):
            class_list = ngo_dtl_divs.get_attribute_list('class')
            if 'field-name-field-ce-url' in class_list:
                record['website'] = ngo_dtl_divs.text.strip()
                continue

            if 'user-info' in class_list:
                user_profile_str = ngo_dtl_divs.a.get_attribute_list('href')[0].strip()
                user_profile_page = requests.get('https://www.changemakers.com' + user_profile_str)
                user_profile_soup = BeautifulSoup(user_profile_page.content, 'html.parser')
                user_span_list = user_profile_soup.find_all('span')
                for each_span in user_span_list:
                    if 'views-field-name' in each_span.get_attribute_list('class'):
                        record['contact_person'] = each_span.find_all('span')[1].text
                continue

            if 'field-type-text-with-summary' in class_list:
                record['description'] = ngo_dtl_divs.p.text.strip().replace('’', "'")
                continue

            if 'field-name-field-ce-need' in class_list:
                record['problems'] = ngo_dtl_divs.text.strip().replace('’', "'")
                continue

            if 'field-name-field-ce-solution' in class_list:
                record['solutions'] = ngo_dtl_divs.text.strip().replace('’', "'")
                continue
            # print(link_str)



        result_list.append(record)


# columns = ['name',
# 'description',
# 'website',
# 'cause_area_',
# 'programme_types_',
# 'address',
# 'country',
# 'city_',
# 'contact_number',
# 'email_',
# 'contact_person']

result = pd.DataFrame(data=result_list)
result.to_csv("changemakers_indonesia1.csv")

# print(soup)