# dependencies: xlrd, pandas, networkx, matplotlib

import networkx as nx
import pandas as pd
import pagerank
import math
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt

G = nx.DiGraph()

x = pd.ExcelFile('metro-to-metro-2011-2015.xlsx')
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

        migrate.append(row[count])
        G.add_edge(row[previous], row[current], weight=int(row[count]))

print(len(G.nodes()))
print(len(G.edges()))

plt.hist(migrate, range=(0, 10000), bins=200)
plt.show()
plt.save('hist.png')

nx.write_gexf(G, "test.gexf")
nx.write_gpickle(G, "test.gpickle")

pr = nx.pagerank(G, max_iter=1000)
most_important = sorted([(value,key) for (key,value) in pr.items()], reverse=True)
least_important = sorted([(value,key) for (key,value) in pr.items()])

# save most_important as a 
most_important_df = pd.DataFrame.from_items([('ranking', most_important)])
# most_important_df.to_excel("most_important.xlsx")

print("----- Most Important -----")
for i in range(50):
    print(most_important[i])
print("----- Least Important -----")
for i in range(50):
    print(least_important[i])

print(sum(pr.values()))


