
# coding: utf-8

# In[7]:


from selenium import webdriver
import pandas as pd


# In[2]:


option = webdriver.ChromeOptions()
option.add_argument("--incognito")

# Download the chromedriver and put in the pathway to the chromedriver
chromedriver_path = r'C:\Users\User\Desktop\DataDive\201804 Effective Altru\chromedriver.exe'
browser = webdriver.Chrome(executable_path = chromedriver_path, chrome_options = option)

# Open the website
url = r"http://www.networkforgood.org/topics/international/"
browser.get(url)


# In[3]:


# Extracting the list of organization with valid website links
# Invalid website links are ignored
org_names_elements = browser.find_elements_by_xpath("//*[starts-with(@href, '/topics/')]")
org_names= [x.text for x in org_names_elements]


# In[4]:


# Extracting all the tags with "li"
descr_elements = browser.find_elements_by_tag_name("li")
descr= [x.text for x in descr_elements]

# Extracting the org descriptions
org_descr = []
for y in org_names:
    matching = [x for x in descr if y in x]
    org_descr.extend(matching)
    
 # Removing the org names
for i in range(len(org_descr)):
    org_descr[i] = org_descr[i].split(" — ")[1]


# In[5]:


# Extracting the list of organization with valid website links
# Invalid website links are ignored
links_elements = browser.find_elements_by_xpath("//*[starts-with(@href, '/topics/')]")
links = [x.get_attribute("href") for x in links_elements]


# In[11]:


cols = ["name","description","website"]
data = [org_names, org_descr, links]
csv_file = pd.DataFrame(columns = cols)
num = len(links)

for i in range(num):
    for j in range(len(cols)):
        csv_file.loc[i, cols[j]] = data[j][i]


# In[18]:


file_name = "Network for Good.csv"
csv_file.to_csv("Network for Good.csv", index = False)

