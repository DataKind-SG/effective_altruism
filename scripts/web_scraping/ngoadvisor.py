import re
import requests
import csv
from bs4 import BeautifulSoup

def harvest():
    session = requests.Session()
    scraping_url = 'https://www.ngoadvisor.net/all-certified/'

    session.head(scraping_url)

    ngo_certified_list_html = session.post(
        url = 'https://www.ngoadvisor.net/wp-admin/admin-ajax.php',
        data = {
            'action': 'loadallcertified'
        },
        headers = {
            'Referer': scraping_url
        }
    )

    page_soup = BeautifulSoup(ngo_certified_list_html.text, 'html.parser')

    ngo_page_urls = [link.get('href') for link in page_soup.find_all('a', 'ngo')]

    data = [
        ['name', 'description', 'website', 'cause_area', 'country', 'city', 'email', 'contact_person']
    ]
    data.extend([extract_info(url) for url in ngo_page_urls])
    
    with open('ngoadvisor.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
        
def extract_info(url):
    ngo_data = []
    ngo_html_response = requests.get(url)
    ngo_html_soup = BeautifulSoup(ngo_html_response.text, 'html.parser')

    ngo_data.append(extract_name(ngo_html_soup))
    ngo_data.append(extract_description(ngo_html_soup))

    static_details = ngo_html_soup.find(id='staticdetails').find_all('p')
    ngo_data.append(extract_website(static_details))

    ngo_data.append(','.join(extract_cause_area(ngo_html_soup)))

    location = extract_location(static_details)
    if len(location) > 1:
        city = location[0].strip()
        country = location[1].strip()
    else:
        location_split_by_comma = location[0].split(',')
        if len(location_split_by_comma) > 1:
            city = location_split_by_comma[0].strip()
            country = location_split_by_comma[1].strip()
        else:
            city = None
            country = location[0].strip()
    ngo_data.append(city)
    ngo_data.append(country)

    contact = extract_contact(static_details)
    if contact is not None:
        ngo_data.append(','.join(re.findall(r'[\w\.-]+@[\w\.-]+', contact)))
        ngo_data.append(contact)
    return ngo_data

def extract_name(soup):
    return soup.find(id='name').get_text()

def extract_description(soup):
    rows = soup.find_all('div', class_='row bordered-top')
    for row in rows:
        extracted_row_text = [div.get_text() for div in row.find_all('div')]
        if extracted_row_text[0].strip() == 'Mission':
            return extracted_row_text[1].strip()

def extract_cause_area(soup):
    return [span.get_text().strip() for span in soup.find(id='benefices').find_all('span', class_='sector')]

def extract_website(paragraphs):
    for p in paragraphs:
        if p.find('strong').get_text().strip() == 'Official Website':
            return p.find('a').get('href')
        
def extract_location(paragraphs):
    for p in paragraphs:
        if p.find('strong').get_text().strip() == 'Country where headquartered':
            return p.text.replace('Country where headquartered', '').strip().split('|')
        
def extract_contact(paragraphs):
    for p in paragraphs:
        if p.find('strong').get_text().strip() == 'Primary contact and general inquiries':
            return p.text.replace('Primary contact and general inquiries', '').strip()

harvest()