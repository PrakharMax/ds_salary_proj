# -*- coding: utf-8 -*-
"""
Created on Fri Aug  1 14:33:25 2025

@author: prakasp2
"""

import pandas as pd
df=pd.read_csv('glassdoor_jobs_fixed(700+ records).csv')

#salary parsing, remove nan
#remove empty nan
#show the states in the dictionary

df=df[df['salary'].notna()]

df['salary']=df['salary'].str.split('(').str[0]
df['hourly'] = df['salary'].str.lower().str.contains('per', na=False)
df['hourly']=df['hourly'].apply(lambda x : 1 if x else 0)
df['salary']=df['salary'].str.lower().str.split('p').str[0]
df['salary']=df['salary'].str.replace(r'[kK]','000',regex=True).str.replace('$','')
df['min_sal']=df['salary'].str.split('-').str[0]
df['max_sal']=df['salary'].str.split('-').str[1]
df['max_sal'] = df.apply(lambda row: row['min_sal'] if pd.isna(row['max_sal']) else row['max_sal'], axis=1)
df['min_sal']=pd.to_numeric(df['min_sal'])
df['max_sal']=pd.to_numeric(df['max_sal'])
df['avg_salary'] = (df['min_sal'] + df['max_sal']) / 2
print(df.info())