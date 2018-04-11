#DataJam
#Scraping from Give2Asia

from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
from bs4 import BeautifulSoup
import requests
import csv

countries = ["Indonesia", "Philippines", "Vietnam", "Thailand", "Myanmar", "Malaysia", "Cambodia", "Laos", "Singapore", "Timor Leste"]
causes = ["Arts & Culture",
"Civil Society",
"Education", 
"Environment", 
"Health", 
"Infrastructure", 
"Livelihood", 
"Media", 
"Social Services",
"Women & Girls"]
browser = webdriver.Firefox()

url = 'http://search.give2asia.org/give2asiasearch/'

with open('charities.csv', 'w') as csvfile:
    thewriter = csv.writer(csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for country in countries:
        for cause in causes:
            browser.get(url)

            element = browser.find_elements_by_class_name("SumoSelect")
            element[0].find_element_by_tag_name("p").click()

            elements = element[0].find_elements_by_tag_name("li")

            for option in elements:
                if option.get_attribute("data-val")==country:
                    print("Value is: %s" % option.get_attribute("data-val"))
                    option.click()
                    break

            element[0].find_element_by_tag_name("p").click()

            element[1].find_element_by_tag_name("p").click()

            elements1 = element[1].find_elements_by_tag_name("li")
            
            for option1 in elements1:
                if option1.get_attribute("data-val")==cause:
                    print("Value is: %s" % option1.get_attribute("data-val"))
                    option1.click()
                    break

            element[1].find_element_by_tag_name("p").click()

            browser.execute_script("startSearch();return false")

            time.sleep(4)

            charits = browser.find_element_by_id("logo_list_id")

            soup = BeautifulSoup(charits.get_attribute('innerHTML'), "lxml")
            mydivs = soup.find_all("div", {"class": "col-xs-6 col-md-4"})

            print("Country: %s; Cause: %s." % (country, cause))

            for t in mydivs:
                r  = requests.get(t.find("a").get("href"))

                data = r.text

                soup2 = BeautifulSoup(data, "lxml")
                #Name, cause, location, website
            
                if(len(soup2.find_all("strong"))>2):
                    if(soup2.find_all("strong")[2].parent.find("a")!=None):
                        if((soup2.find_all("strong")[2].parent.find("a").get("href")+"")[0:4]=="http"):
                            thewriter.writerow([t.text.strip()+"", cause+"", country+"", soup2.find_all("strong")[2].parent.find("a").get("href")+""])
                        else:
                            thewriter.writerow([t.text.strip(), cause, country, ""])
                    else:
                        thewriter.writerow([t.text.strip(), cause, country, ""])
                else:
                    thewriter.writerow([t.text.strip(), cause, country, ""])

    #print(init_page_soup)