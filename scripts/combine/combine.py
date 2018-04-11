#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 22:20:09 2018

@author: kelvin
"""

import pandas as pd
import glob
import os.path as path
import ntpath

csv_path =  path.abspath(path.join("../..","data/input/web_scraping"))
all_files = glob.glob(os.path.join(csv_path, "*.csv"))

df = pd.DataFrame()

#it seems some files have different encoding, messing up some data
for file_ in all_files:
    data = pd.read_csv(file_encoding='latin-1')
    data['file'] = ntpath.basename(file_)
    df = pd.concat([df, data])

export_path = path.abspath(path.join("../..","data/output/web_scraping/web_scrape_v1.csv"))
df.to_csv(export_path, index = False, encoding = "utf-8")
