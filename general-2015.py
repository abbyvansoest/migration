# dependencies: xlrd, pandas, networkx, matplotlib

import networkx as nx
import pandas as pd
import pagerank
import math
import numpy as np
import csv
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="migrate")

import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

non_cities = ['Outside Metro Area within U.S. or Puerto Rico', 
'Africa', 'Asia', 'Central America', 'Caribbean', 'Europe',
'U.S. Island Areas', 'Northern America', 'Oceania and At Sea', 
'South America']

G = nx.DiGraph()

x = pd.ExcelFile('data/metro-to-metro-2011-2015.xlsx')
print(x.sheet_names)

previous = 'Unnamed: 15'
current = 'Unnamed: 2'
count = 'Unnamed: 26'
cur_pop = 'Unnamed: 3'
prev_pop = 'Unnamed: 16'

thresh = 0
pop_thresh = 2000
migrate = []

visual_data = {}
all_migration = {}
cities_to_pops = {}


for state in x.sheet_names:
    df = x.parse(state)

    for index, row in df.iterrows():

        # skip first three rows: header rows
        if index < 3:
            continue
        # skip the last rows: footer rows
        if index >= 53724:
            break

        if row[previous] in non_cities or row[current] in non_cities:
            continue

        if int(row[count]) < thresh:
            continue

        migrate.append(row[count])
        G.add_edge(row[previous], row[current], weight=int(row[count]))

        if row[previous] not in all_migration:
            all_migration[row[previous]] = {}
            # if row[current] not
        all_migration[row[previous]][row[current]] = row[count]

        if row[current] not in cities_to_pops:
            cities_to_pops[row[current]] = row[cur_pop]
        if row[previous] not in cities_to_pops:
            cities_to_pops[row[previous]] = row[prev_pop]

print(len(G.nodes()))
print(len(G.edges()))

# plt.hist(migrate, range=(0, 1000), bins=200)
# plt.title('Distribution of Edge Weights of Migration Flow Graph')
# plt.xlabel('Edge Weight')
# plt.ylabel('Frequency')
# plt.savefig('figs/hist.png')

# print(np.var(migrate))
# print(np.mean(migrate))

def get_and_save_pr():
    pr = nx.pagerank(G, max_iter=1000)
    most_important = sorted([(value,key) for (key,value) in pr.items()], reverse=True)
    least_important = sorted([(value,key) for (key,value) in pr.items()])

    most_important_list = ['%s\t%f' % (k,v) for v,k in most_important]
    np.savetxt('results/most-important-list', most_important_list, fmt='%s')

    # save most_important as excel
    most_important_df = pd.DataFrame.from_items([('ranking', most_important)])
    most_important_df.to_excel("results/most_important.xlsx")
    print("----- Most Important -----")
    for i in range(10):
        print(most_important[i])
    print("----- Least Important -----")
    for i in range(10):
        print(least_important[i])

    print(sum(pr.values()))
    return pr

# pr = get_and_save_pr()

def get_and_save_edge_centrality():
    eb = nx.edge_betweenness_centrality(G)
    most_important = sorted([(value,key) for (key,value) in eb.items()], reverse=True)
    least_important = sorted([(value,key) for (key,value) in eb.items()])
    most_important_list = ['%s\t%f' % (k,v) for v,k in most_important]
    np.savetxt('results/edge-centrality-most-important-list', most_important_list, fmt='%s')

    print("----- Most Important -----")
    for i in range(10):
        print(most_important[i])
    print("----- Least Important -----")
    for i in range(10):
        print(least_important[i])

    return eb

# eb = get_and_save_edge_centrality()

def plot_pr_pop_correlation():
    xs = []
    ys = []
    for city,pr_city in pr.items():
        if city in non_cities:
            continue
        pop = cities_to_pops[city]
        xs.append(pr_city)
        ys.append(pop)
    print(len(xs))
    print(len(ys))
    plt.scatter(xs, ys)
    # add best fit line
    z = np.polyfit(xs, ys, 1)
    p = np.poly1d(z)
    xs = np.arange(min(xs),.025,.001)
    plt.plot(xs,p(xs),'r--')

    plt.xlim([min(xs)-.002, max(xs)+.002])
    # plt.ylim([min(ys), max(ys)])

    plt.xlabel('PageRank')
    plt.ylabel('Population')
    plt.title('Correlation between PageRank and Population')
    # plt.show()
    plt.savefig('figs/correlation-pr-pop.png')

# plot_pr_pop_correlation()

def get_clustering():
    cluster = nx.clustering(G)
    most_clustered = sorted([(value,key) for (key,value) in cluster.items()], reverse=True)
    least_clustered = sorted([(value,key) for (key,value) in cluster.items()])
    most_important_list = ['%s\t%f' % (k,v) for v,k in most_clustered]
    np.savetxt('results/node-clustering-most-important-list', most_important_list, fmt='%s')

    print("----- Most Clustered -----")
    for i in range(20):
        print(most_clustered[i])
    print("----- Least Clustered -----")
    for i in range(20):
        print(least_clustered[i])

    return cluster

get_clustering()

def get_reciprocity():
    recip = nx.reciprocity(G, nodes=G.nodes())
    most_recip = sorted([(value,key) for (key,value) in recip.items()], reverse=True)
    least_recip = sorted([(value,key) for (key,value) in recip.items()])
    most_recip_list = ['%s\t%f' % (k,v) for v,k in most_recip]
    np.savetxt('results/reciprocity', most_recip_list, fmt='%s')

    print("----- Most Reciprocical -----")
    for i in range(20):
        print(most_recip[i])
    print("----- Least Reciprocical -----")
    for i in range(20):
        print(least_recip[i])
get_reciprocity()

# table = []
# dest_table = []

cities = [city for city in cities_to_pops.keys() if city not in non_cities]
cities = sorted(cities)

# for city1 in cities:
#     vals = [city1]
#     dsts = []
#     for city2 in cities:
#         if city1 in all_migration:
#             if city2 in all_migration[city1]:
#                 vals.append(all_migration[city1][city2])
#                 if all_migration[city1][city2] > pop_thresh:
#                     dsts.append(city2)
#             else:
#                 vals.append(0)

#     table.append(vals)
#     dest_table.append([city1, '+'.join(dsts)])

# with open('big_table.tsv', 'w') as f:
#     header = ['Source'] + [city for city in cities]
#     writer = csv.writer(f, delimiter='\t')
#     f.write('\t'.join(header) + '\n')
#     writer.writerows(table)
# with open('dest_table-thresh%d.tsv'%pop_thresh, 'w') as f:
#     header = ['Source', 'Dests']
#     writer = csv.writer(f, delimiter='\t')
#     f.write('\t'.join(header) + '\n')
#     writer.writerows(dest_table)

# Load coordinates
coordinates = {}
coords = open('coordinates.txt','r') 
coords = csv.reader(coords, delimiter='\t')
coords = list(coords)
for coord in coords:
    # print(coord[0])
    coordinates[coord[0].strip()] = coord[1]

table = []
unique_id = 0
for city1 in cities:
    for city2 in cities:
        if city1 in all_migration and city2 in all_migration[city1]:
            if all_migration[city1][city2] > pop_thresh:
                table.append([unique_id, city1, coordinates[city1], city2, coordinates[city2], all_migration[city1][city2]])
                unique_id += 1

with open('pairwise-thresh%d.tsv'%pop_thresh, 'w') as f:
    header = ['ID', 'Source', 'SOURCE_coord', 'Dest', 'DEST_coord', 'count']
    writer = csv.writer(f, delimiter='\t')
    f.write('\t'.join(header) + '\n')
    writer.writerows(table)


