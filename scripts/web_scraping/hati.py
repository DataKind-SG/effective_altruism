
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup as BS
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

import asyncio
import logging
import pandas as pd
import requests


# ## Setup / Helpers

# In[27]:


MAX_WORKERS = 40
LOG_COUNT_INTERVAL = 10
lock = Lock()
logger = logging.getLogger(__name__)
logger.setLevel(10)


# In[3]:


def get_soup(url):
    html = requests.get(url).text
    return BS(html, 'lxml')


# ## Categories

# In[4]:


def get_category_data():
    category_data = []
    soup = get_soup('http://www.hati.my/')
    
    for anchor in soup.select('.home-categories li a'):
        cause = anchor.text.strip()
        url = anchor.attrs['href']
        category_data.append([cause, url])
    
    return category_data


# ## Higher Level Entities

# In[5]:


def scrape_hl(url, hl_entities=None):
    if not hl_entities:
        hl_entities = []
        
    html = requests.get(url).text
    soup = BS(html, 'lxml')
    
    for title in soup.select('.title')[:15]:
        hl_entity_title = title.text
        anchor = title.select_one('a')
        if not anchor:
            continue
        href = anchor.attrs['href']
        
        hl_entities.append([hl_entity_title, href])
        
    next_btn = soup.select_one('.alignleft a')
    
    if next_btn:
        if next_btn.text == '« Older Entries':
            url = next_btn.attrs['href']
            print(url)
            return scrape_hl(url, hl_entities)
    
    return hl_entities


# In[6]:


hl_entities = []

def get_hl_entity_from_cat_data(cat_data):
    global hl_entities_final
    
    cause = cat_data[0]
    url = cat_data[1]
    
    cat_hl_entities = scrape_hl(url)
    
    lock.acquire()
    hl_entities.extend(cat_hl_entities)
    lock.release()


# In[7]:


with ThreadPoolExecutor(MAX_WORKERS) as executor:
    loop = asyncio.get_event_loop()
    futures = [
        loop.run_in_executor(
            executor,
            get_hl_entity_from_cat_data,
            cat_data
        ) for cat_data in get_category_data()
    ]


# In[8]:


def get_entry( hl_info ):
    entry_details = {}
    
    entry_details['name'] = hl_info[0]
    url = hl_info[1]
    
    soup = get_soup(url)
    
    cause_areas = [c.text.strip() for c in soup.select('.description')]
    entry_details['cause_area'] = '/'.join(cause_areas).replace(', ' ,'/')

    table_data = soup.select_one('.my_table_1')
    if table_data:
        for row in table_data.select('tr'):
            cells = row.find_all('td')
            cell_name = cells[0].text.strip()

            if cell_name == 'Email address':
                entry_details['email'] = cells[1].find('a').text
            if cell_name == 'Contact person':
                entry_details['contact_person'] = cells[1].text
            if cell_name == 'Website':
                entry_details['url'] = cells[1].find('a').attrs['href']
            if cell_name == 'Phone number':
                entry_details['contact_number'] = cells[1].text
            if cell_name == 'Address':
                entry_details['address'] = cells[1].text

        descrip_data = [item.text for item in soup.select('.entry p')]
        descrip_data = '\n'.join(descrip_data)
        entry_details['description'] = descrip_data

    return entry_details


# In[29]:


final = []
count = 0
def process_hl_entity(hl_entity):
    global final, count
    
    entry = get_entry(hl_entity)
    
    lock.acquire()
    final.append(entry)
    lock.release()
    
    count += 1
    if count % LOG_COUNT_INTERVAL == 0:
        print('{} charities processed'.format(count) )


# In[30]:


with ThreadPoolExecutor(MAX_WORKERS) as executor:
    loop = asyncio.get_event_loop()
    futures = [
        loop.run_in_executor(
            executor,
            process_hl_entity,
            hl_entity
        ) for hl_entity in hl_entities
    ]
    


# In[23]:


pd.DataFrame(final).drop_duplicates().to_csv('output.csv')

