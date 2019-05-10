# dependencies: xlrd, pandas, networkx, matplotlib

import networkx as nx
import pandas as pd
import pagerank
import math
import numpy as np
import csv

import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt

G_male = nx.DiGraph()
G_female = nx.DiGraph()
G_global = nx.DiGraph()

x = pd.ExcelFile('data/metro-to-metro-by-sex-2011-2015.xlsx')
print(x.sheet_names)

gender = 'Unnamed: 2'
previous = 'Unnamed: 16'
current = 'Unnamed: 3'
count = 'Unnamed: 27'

male = '01'
female = '02'

thresh = 0
weights_male = []
weights_female = []

for state in x.sheet_names:
    df = x.parse(state)
    for index, row in df.iterrows():

        # skip first three rows: header rows
        if index < 3:
            continue
        # skip the last rows: footer rows
        if index >= 47520:
            break

        # ignore migrating populations less than thresh.
        if int(row[count]) < thresh:
            continue

        if row[previous] == 'Outside Metro Area within U.S. or Puerto Rico':
            continue
        if row[current] == 'Outside Metro Area within U.S. or Puerto Rico':
            continue

        weights_male.append(row[count])
        weights_female.append(row[count])

        if row[gender] == male:
            G_male.add_edge(row[previous], row[current], weight=int(row[count]))
        elif row[gender] == female:
            G_female.add_edge(row[previous], row[current], weight=int(row[count]))

        G_global.add_edge(row[previous], row[current], weight=int(row[count]))

# Plot histogram for male/female edge weights
plt.hist(weights_male, range=(0, 1000), bins=200)
plt.title('Distribution of Edge Weights of Migration Flow Graph: Male')
plt.xlabel('Edge Weight')
plt.ylabel('Frequency')
plt.savefig('figs/male-hist.png')

# Plot histogram for male/female edge weights
plt.hist(weights_female, range=(0, 1000), bins=200)
plt.title('Distribution of Edge Weights of Migration Flow Graph: Female')
plt.xlabel('Edge Weight')
plt.ylabel('Frequency')
plt.savefig('figs/female-hist.png')

# nx.write_gexf(G_male, "results/male.gexf")
# nx.write_gpickle(G_male, "results/male.gpickle")
# nx.write_gexf(G_female, "results/female.gexf")
# nx.write_gpickle(G_female, "results/female.gpickle")

pr_male = nx.pagerank(G_male, max_iter=1000)
most_important_male = sorted([(value,key) for (key,value) in pr_male.items()], reverse=True)

most_important_list = ['%s\t%f' % (k,v) for v,k in most_important_male]
np.savetxt('results/most-important-list-male', most_important_list, fmt='%s')

most_important_df_male = pd.DataFrame.from_items(
    [('ranking', most_important_male)])
most_important_df_male.to_excel("results/most_important-male.xlsx")
print(sum(pr_male.values()))

pr_fem = nx.pagerank(G_female, max_iter=1000)
most_important_female = sorted([(value,key) for (key,value) in pr_fem.items()], reverse=True)

most_important_list = ['%s\t%f' % (k,v) for v,k in most_important_female]
np.savetxt('results/most-important-list-female', most_important_list, fmt='%s')

most_important_df_female = pd.DataFrame.from_items([('ranking', most_important_female)])
most_important_df_female.to_excel("results/most_important-female.xlsx")
print(sum(pr_fem.values()))

pr_global = nx.pagerank(G_global, max_iter=1000)
most_important = sorted([(value,key) for (key,value) in pr_global.items()], reverse=True)

most_important_list = ['%s\t%f' % (k,v) for v,k in most_important]
np.savetxt('results/most-important-list-gender-global', most_important_list, fmt='%s')

most_important_df = pd.DataFrame.from_items([('ranking', most_important)])
most_important_df.to_excel("results/most_important-gender-global.xlsx")
print(sum(pr_fem.values()))

# get sorted list of cities by max distance in rank
# fem_locs = []
# for v,loc in most_important_female:
#     fem_locs.append(loc)
# male_locs = []
# for v,loc in most_important_male:
#     male_locs.append(loc)

# idx_diffs = dict()
# for idx_male, loc in enumerate(male_locs):
#     idx_fem = fem_locs.index(loc)
#     idx_diffs[loc] = idx_male - idx_fem
# w = csv.writer(open("results/max-dist-sex-idx.csv", "w"))
# for key, val in idx_diffs.items():
#     w.writerow([key, val])

# # Get sorted list of cities by max PR score distance
# pr_diffs = dict()
# for loc, val_male in pr_male.items(): # 
#     val_fem = pr_fem[loc]
#     pr_diffs[loc] = abs(float(val_fem) - float(val_male))
# w = csv.writer(open("results/max-dist-sex-pr.csv", "w"))
# for key, val in pr_diffs.items():
#     w.writerow([key, val])





