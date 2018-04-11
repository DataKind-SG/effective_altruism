
# coding: utf-8

# In[30]:


from bs4 import BeautifulSoup
import requests
import pandas as pd


# In[9]:


url = "https://www.viet.net/community/nonprofit"
r = requests.get(url)


# In[28]:


soup = BeautifulSoup(r.text, "html.parser")

links = []
for link in soup.find_all('a'):
    l = link.get('href')
    if l != None:
        if "http" in l:
            links.append(l)


# In[31]:


df = pd.DataFrame(links, columns=["website"])
df.to_csv('viet_list.csv', index=False)

