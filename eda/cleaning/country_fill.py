#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Alan Choon
"""

import pandas as pd
import pycountry
import phonenumbers
import os.path as path
from phonenumbers.phonenumberutil import (
region_code_for_country_code,
region_code_for_number,
)

def cleanwebscrape(data):
    df = pd.read_csv(data,encoding = "ISO-8859-1")
    
    df = df.fillna(" ")
    df['id'] = df.index.values
    df_rm = df[df["country"]==" "]
    
    df_rm['country']=df_rm['country'].apply(lambda x: " ".join(x.split()))
    df_rm['country']=df_rm['country'].apply(lambda x: x.lower())
    df_rm['address']=df_rm['address'].apply(lambda x: " ".join(x.split()))
    df_rm['address']=df_rm['address'].apply(lambda x: x.lower())
    def lookformultiplewords(x):
        if ('republic' in x) | ('state' in x) | ('federated' in x) | ('province' in x):
            return(x.split()[0])
        else:
            return(x)
        
    ctys = [country.name for country in pycountry.countries]
    ctys = [" ".join(x.split(",")) for x in ctys]
    ctys = [x.lower() for x in ctys]
    ctys = [lookformultiplewords(x) for x in ctys]
    
    def det_cty(df_col,ctys):
    #This function will detect if country is in address and fill it to column
        li = []
        for j in df_col:
            truefalse = False
            for i in range(len(ctys)):
                if ctys[i] in j:
                    li.append(ctys[i])
                    truefalse = True
                    break
            if truefalse == False:
                li.append(" ") 
        return(li)

    dnew = det_cty(df_rm['address'],ctys)
    df_rm['country'] = dnew
    
    df_rm['address']
    def num_parser(x):
        try:
            return(phonenumbers.parse(x))
        except:
            return(" ")
    
    df_rm['parsed'] = df_rm['contact_number'].apply(num_parser)
    
    def country_parser(y):
        try:
            return(pycountry.countries.get(alpha2=region_code_for_number(y)).name)
        except: 
            " "
    df_rm['cty_parsed'] = df_rm['parsed'].apply(country_parser)
    #'india' in df_rm['address'][30]

    lind = list(df_rm['country'][df_rm['country']==" "].index.values)
    df_rm['country'][lind] = df_rm['cty_parsed'][lind]
    df_rm[df_rm['country'].isnull()] = " "
    
    lind = list(df['country'][df['country']==" "].index.values)
    df['country'][lind] = df_rm['country'][lind]
    df['country']=df['country'].apply(lambda x: x.lower())
    return(df)

path =  path.abspath(path.join("../..","data/output/web_scraping/web_scrape_v3.csv"))

df = cleanwebscrape(path)

df['country'] = pd.np.where(df.country.str.contains("indo"), "indonesia",
                pd.np.where(df.country.str.contains("philipp|phillip"),"philippines",
                pd.np.where(df.country.str.contains("thai"),"thailand",
                pd.np.where(df.country.str.contains("cambo"),"cambodia",
                pd.np.where(df.country.str.contains("myanm|burma"),"myanmar",
                pd.np.where(df.country.str.contains("lao"),"laos",
                pd.np.where(df.country.str.contains("singa"),"singapore",
                pd.np.where(df.country.str.contains("malay"),"malaysia",
                pd.np.where(df.country.str.contains("brun"),"brunei",
                pd.np.where(df.country.str.contains("viet"),"vietnam",
                pd.np.where(df.country.str.contains("timo"),"timor leste",
                pd.np.where(df.country.str.contains("papa|guin"),"papau new guinea",
                df['country']))))))))))))




