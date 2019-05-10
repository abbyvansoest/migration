
# Analyze what happens to pagerank when different cities are removed.

# dependencies: xlrd, pandas, networkx, matplotlib

import networkx as nx
import pandas as pd
import pagerank
import math
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt

# instead of moving TO any of these cities, people have to move elsewhere.
# it is as if the cities and their populations do not exist.
individual_dropout_cities = ['Dallas-Fort Worth-Arlington, TX Metro Area', 
'New York-Newark-Jersey City, NY-NJ-PA Metro Area',
'Los Angeles-Long Beach-Anaheim, CA Metro Area',
'Washington-Arlington-Alexandria, DC-VA-MD-WV Metro Area', 
'Atlanta-Sandy Springs-Roswell, GA Metro Area',
'Houston-The Woodlands-Sugar Land, TX Metro Area',
'Chicago-Naperville-Elgin, IL-IN-WI Metro Area',
'Phoenix-Mesa-Scottsdale, AZ Metro Area',
'Seattle-Tacoma-Bellevue, WA Metro Area',
'Riverside-San Bernardino-Ontario, CA Metro Area',
'San Francisco-Oakland-Hayward, CA Metro Area']

x = pd.ExcelFile('data/metro-to-metro-2011-2015.xlsx')
print(x.sheet_names)

previous = 'Unnamed: 15'
current = 'Unnamed: 2'
count = 'Unnamed: 26'
current_pop = 'Unnamed: 3'

thresh = 0

def check_ok(index, row):
    # skip first three rows: header rows
    if index < 3:
        return False
    # skip the last rows: footer rows
    if index >= 53724:
        return False

    if int(row[count]) < thresh:
        return False

    if row[previous] == 'Outside Metro Area within U.S. or Puerto Rico':
        return False
    if row[current] == 'Outside Metro Area within U.S. or Puerto Rico':
        return False

    return True


source_to_dests = {}
populations = {}

for state in x.sheet_names:
    df = x.parse(state)

    for index, row in df.iterrows():

        if not check_ok(index, row):
            continue

        if row[previous] not in source_to_dests:
            source_to_dests[row[previous]] = {}
        if row[current] in source_to_dests[row[previous]]:
            print('ERROR')
        source_to_dests[row[previous]][row[current]] = row[count]

        if row[current] not in populations:
            populations[row[current]] = int(row[current_pop])
            print(row[current_pop])

total_migration_from = {}
# now need to normalize the count values for each source
for source in source_to_dests:
    tmf = 0
    for dest in source_to_dests[source]:
        pop = source_to_dests[source][dest]
        tmf += pop
    total_migration_from[source] = tmf

    check_sum = 0
    for dest in source_to_dests[source]:
        pop = source_to_dests[source][dest]
        source_to_dests[source][dest] = float(pop)/tmf
        check_sum += source_to_dests[source][dest]

# now need to remove a city from the pagerank.
# do not add any edges where current == city

# if current == city, instead add an edge for each of the other dests,
# proportionally based on source_to_dests weights
def dropout_graph(city, ignore_from=False):
    
    G = nx.DiGraph()
    print(city)

    for state in x.sheet_names:
        df = x.parse(state)

        for index, row in df.iterrows():
            if not check_ok(index, row):
                continue

            if ignore_from and row[previous] in city:
                continue

            # no migration inflience TO city
            if row[current] in city:
                population = int(row[count])
                for dest in source_to_dests[row[previous]]:
                    if dest in city:
                        continue
                    portion = int(population*source_to_dests[row[previous]][dest])
                    G.add_edge(row[previous], dest, weight=portion)
                    print('%s: %d' %(dest, portion))
            else:
                G.add_edge(row[previous], row[current], weight=int(row[count]))

    print(len(G.nodes()))
    print(len(G.edges()))

    # print([e for e in G.edges])
    edges = [e for e in G.edges() if city[0] == e[1]]
    print(edges)
    return G

    # nx.write_gexf(G, "dropout/%s.gexf" % city)
    # nx.write_gpickle(G, "dropout/%s.gpickle" % city)

for city in individual_dropout_cities:

    G = dropout_graph([city])

    pr = nx.pagerank(G, max_iter=1000)
    most_important = sorted([(value,key) for (key,value) in pr.items()], reverse=True)
    least_important = sorted([(value,key) for (key,value) in pr.items()])

    most_important_list = ['%s\t%f' % (k,v) for v,k in most_important]
    np.savetxt('dropout/ranked-migration-from-%s'% city.replace(' ', ''), most_important_list, fmt='%s')
    most_important_df = pd.DataFrame.from_items([('ranking', most_important)])
    most_important_df.to_excel("dropout/excel/ranked-migration-from-%s.xlsx" % city.replace(' ', ''))

    print(sum(pr.values()))

    G = dropout_graph([city], ignore_from=True)

    pr = nx.pagerank(G, max_iter=1000)
    most_important = sorted([(value,key) for (key,value) in pr.items()], reverse=True)
    least_important = sorted([(value,key) for (key,value) in pr.items()])

    most_important_list = ['%s\t%f' % (k,v) for v,k in most_important]
    np.savetxt('dropout/ranked-none-from-%s'% city.replace(' ', ''), most_important_list, fmt='%s')
    most_important_df = pd.DataFrame.from_items([('ranking', most_important)])
    most_important_df.to_excel("dropout/excel/ranked-none-from-%s.xlsx" % city.replace(' ', ''))

    print(sum(pr.values()))


pop_thresh = 200000
drop_group_cities = [city for (city,pop) in populations.items() if pop > pop_thresh]

G = dropout_graph(drop_group_cities)

pr = nx.pagerank(G, max_iter=1000)
most_important = sorted([(value,key) for (key,value) in pr.items()], reverse=True)
least_important = sorted([(value,key) for (key,value) in pr.items()])

most_important_list = ['%s\t%f' % (k,v) for v,k in most_important]
np.savetxt('dropout/ranked-migration-from-group', most_important_list, fmt='%s')

most_important_df = pd.DataFrame.from_items([('ranking', most_important)])
most_important_df.to_excel("dropout/excel/ranked-migration-from-group.xlsx")

print(sum(pr.values()))


G = dropout_graph(drop_group_cities, ignore_from=True)

pr = nx.pagerank(G, max_iter=1000)
most_important = sorted([(value,key) for (key,value) in pr.items()], reverse=True)
least_important = sorted([(value,key) for (key,value) in pr.items()])

most_important_list = ['%s\t%f' % (k,v) for v,k in most_important]
np.savetxt('dropout/ranked-none-from-group', most_important_list, fmt='%s')

most_important_df = pd.DataFrame.from_items([('ranking', most_important)])
most_important_df.to_excel("dropout/excel/ranked-none-from-group.xlsx")

print(sum(pr.values()))

