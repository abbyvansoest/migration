# dependencies: xlrd, pandas, networkx, matplotlib

import networkx as nx
import pandas as pd
import pagerank
import math

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

for state in x.sheet_names:
    df = x.parse(state)
    print(list(df))
    for index, row in df.iterrows():

        # skip first three rows: header rows
        if index < 3:
            continue
        # skip the last rows: footer rows
        if index >= 53724:
            break

        print(row[previous], row[current], row[count])

        if int(row[count]) < thresh:
            continue

        G.add_edge(row[previous], row[current], weight=int(row[count]))

print(len(G.nodes()))
print(len(G.edges()))

nx.write_gexf(G, "test.gexf")
nx.write_gpickle(G, "test.gpickle")

pr = nx.pagerank(G, max_iter=1000)
most_important = sorted([(value,key) for (key,value) in pr.items()], reverse=True)
least_important = sorted([(value,key) for (key,value) in pr.items()])

print("----- Most Important -----")
for i in range(50):
    print(most_important[i])
print("----- Least Important -----")
for i in range(50):
    print(least_important[i])


