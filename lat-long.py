# dependencies: xlrd, pandas, networkx, matplotlib

import networkx as nx
import pandas as pd
import pagerank
import math
import numpy as np
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="lat-long-migration")

import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt

non_cities = ['Outside Metro Area within U.S. or Puerto Rico', 
'Africa', 'Asia', 'Central America', 'Caribbean', 'Europe',
'U.S. Island Areas', 'Northern America', 'Oceania and At Sea', 
'South America']

G = nx.DiGraph()

x = pd.ExcelFile('data/metro-to-metro-2011-2015.xlsx')
# x = pd.ExcelFile('county-to-county-2012-2016-ins-outs-nets-gross.xlsx')
print(x.sheet_names)

previous = 'Unnamed: 15'
current = 'Unnamed: 2'
count = 'Unnamed: 26'

thresh = 0
migrate = []

lat_long_dict = {'Location': ('Latitude', 'Longitude')}

for state in x.sheet_names:
    df = x.parse(state)

    for index, row in df.iterrows():

        # skip first three rows: header rows
        if index < 3:
            continue
        # skip the last rows: footer rows
        if index >= 53724:
            break

        if int(row[count]) < thresh:
            continue

        if row[count]==83445:
            print(row[previous])
            print(row[current])

        # Get lat/long of cities.
        if row[previous] not in non_cities and row[previous] not in lat_long_dict:
            loc = row[previous].replace('Metro Area', '').split(',')
            cities = loc[0].split('-')
            states = loc[1].split('-')
            base_loc = cities[0] + ' ' + states[0]
            print(base_loc)
            location = geolocator.geocode(base_loc)
            print(location.latitude, location.longitude)

            # if row[previous] in lat_long_dict:
            #     print(lat_long_dict[row[previous]] == (location.latitude, location.longitude))
            lat_long_dict[row[previous]] = (location.latitude, location.longitude)

        if index % 10 == 0:
            # save lat and long
            df = pd.DataFrame.from_dict(lat_long_dict, orient="index")
            df.to_csv("lat-long.csv")






