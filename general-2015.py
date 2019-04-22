# dependencies: xlrd, pandas, networkx, matplotlib

import networkx as nx
import pandas as pd
import pagerank
import math
import numpy as np
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="migrate")

import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt

others = ['Outside Metro Area within U.S. or Puerto Rico', 
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
        if row[previous] not in others:
            loc = row[previous].replace('Metro Area', '')
            loc = loc.split(',')
            cities = loc[0].split('-')
            states = loc[1].split('-')

            print(cities[0] + ' ' + states[0])
            location = geolocator.geocode(cities[0] + ' ' + states[0])
            print(location.latitude, location.longitude)

        migrate.append(row[count])
        G.add_edge(row[previous], row[current], weight=int(row[count]))

print(len(G.nodes()))
print(len(G.edges()))

plt.hist(migrate, range=(0, 1000), bins=200)
plt.title('Distribution of Edge Weights of Migration Flow Graph')
plt.xlabel('Edge Weight')
plt.ylabel('Frequency')
plt.savefig('figs/hist.png')

print(np.var(migrate))
print(np.mean(migrate))

nx.write_gexf(G, "results/test.gexf")
nx.write_gpickle(G, "results/test.gpickle")

pr = nx.pagerank(G, max_iter=1000)
most_important = sorted([(value,key) for (key,value) in pr.items()], reverse=True)
least_important = sorted([(value,key) for (key,value) in pr.items()])

# save most_important as a 
most_important_df = pd.DataFrame.from_items([('ranking', most_important)])
most_important_df.to_excel("results/most_important.xlsx")

print("----- Most Important -----")
for i in range(50):
    print(most_important[i])
print("----- Least Important -----")
for i in range(50):
    print(least_important[i])

print(sum(pr.values()))


