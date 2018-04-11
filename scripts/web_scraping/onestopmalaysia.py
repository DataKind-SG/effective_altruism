import requests
from bs4 import BeautifulSoup
import pandas as pd

#Go into main website, retrieve all sub websites
source_path = "https://www.onestopmalaysia.com/directory/organisations/charity/"
page = requests.get(source_path)
page_content = page.content
soup = BeautifulSoup(page_content, 'html.parser')

websites_to_crawl = soup.find_all('div', class_='listing-summary')
website_list = []

for segment in websites_to_crawl:
    try:
        website_list.append(segment.find('a').attrs['href'])
    except:
        #catch errors
        print()

#for each sub website, retrieve all the important information and put them into a dataframe.
    
indexing = 0
df = pd.DataFrame()

for target_website in website_list:
    print(indexing)
    page = requests.get(target_website)
    page_content = page.content
    soup = BeautifulSoup(page_content, 'html.parser')
    #title = soup.find('div', id='listing').find('h2').get_text()
    #desc = soup.find('span',class_='listing-desc').get_text()
    df.set_value(indexing,'name',soup.find('div', id='listing').find('h2').get_text())
    df.set_value(indexing,'description',soup.find('span',class_='listing-desc').get_text())
    table_data = soup.find_all('dt')
    table_data2 = soup.find_all('dd')
    
    for i,data in enumerate(table_data):
        if (data.get_text() == "Address"):
            #print(table_data2[i].get_text())
            df.set_value(indexing, 'address' ,table_data2[i].get_text())
        if (data.get_text() == "Telephone"):
            #print(table_data2[i].get_text())
            df.set_value(indexing, 'telephone' ,table_data2[i].get_text())
        if (data.get_text() == "Website"):
            #print(table_data2[i].get_text())
            df.set_value(indexing, 'website' ,table_data2[i].get_text())

    indexing = indexing+1

df.to_csv("onestopmalaysia.csv",header=True,index=False)