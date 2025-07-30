# -*- coding: utf-8 -*-
"""
Created on Tue Jul 29 15:47:05 2025

@author: prakasp2
"""

import glassdoor_scraping as gs
# import pandas as pd   # You can leave this commented out unless you use it later.

df = gs.get_job('Data Scientist', 'united states', 1000)
print(df)