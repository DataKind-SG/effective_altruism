import requests
import csv
from bs4 import BeautifulSoup

scraping_host = 'http://hacccambodia.org/'

def harvest():
    directory_path = 'ngo_directory.php'
    page_soup = get_soup(scraping_host + directory_path)
    num_pages = int(page_soup.find(class_='paginate').contents[-2].text)
    data = [
        ['name', 'description', 'website', 'cause_area', 'address', 'country', 'contact_number', 'email', 'contact_person']
    ]
    for i in range(1, num_pages + 1):
        page_url = scraping_host + directory_path + '?page=' + str(i)
        print('Retriving NGOs info from', page_url)
        indexed_page_soup = get_soup(page_url)
        data.extend([extract_ngo_data(tbody) for tbody in indexed_page_soup.find(id='back_member').find_all('tbody')])
    
    with open('hacccambodia.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
        
        
def get_soup(url):
    url_http_response = requests.get(url)
    return BeautifulSoup(url_http_response.text, 'html.parser')

def extract_ngo_data(ngo_info):
    ngo_path = ngo_info.find('a').get('href')
    ngo_page_http_soup = get_soup(scraping_host + ngo_path)
    ngo_info = ngo_page_http_soup.find(id='simple1Tab').find_all('tr')
    ngo_program = ngo_page_http_soup.find(id='simple2Tab').find_all('tr')
    return [extract_key('organization name', ngo_info),
           extract_key('main activities', ngo_program),
           extract_key('website', ngo_info),
           extract_key('program/project names', ngo_program),
           extract_key('address', ngo_info),
           'Cambodia',
           extract_key('telephone', ngo_info),
           extract_key('email', ngo_info),
           extract_key('key contact', ngo_info)]
        
def extract_key(key, rows):
    for row in rows:
        if key in row.find('th').get_text().lower():
            return row.find('td').get_text()
        
harvest()