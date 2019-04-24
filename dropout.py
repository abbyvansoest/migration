
# want to analyze what happens to pagerank when different cities are removed.

# 1) Outside Metro Area within U.S. or Puerto Rico
# 2) Dallas-Fort Worth-Arlington, TX Metro Area
# 3) New York-Newark-Jersey City, NY-NJ-PA Metro Area
# 4) Los Angeles-Long Beach-Anaheim, CA Metro Area
# 5) Washington-Arlington-Alexandria, DC-VA-MD-WV Metro Area
# 6) Atlanta-Sandy Springs-Roswell, GA Metro Area
# 7) Houston-The Woodlands-Sugar Land, TX Metro Area
# 8) Chicago-Naperville-Elgin, IL-IN-WI Metro Area
# 9) Phoenix-Mesa-Scottsdale, AZ Metro Area
# 10) Seattle-Tacoma-Bellevue, WA Metro Area
# 11) Riverside-San Bernardino-Ontario, CA Metro Area
# 12) San Francisco-Oakland-Hayward, CA Metro Area

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
dropout_cities = ['Outside Metro Area within U.S. or Puerto Rico',
'Dallas-Fort Worth-Arlington, TX Metro Area', 
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

thresh = 0

source_to_dests = {}

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

        if row[previous] not in source_to_dests:
            source_to_dests[row[previous]] = {}
        if row[current] in source_to_dests[row[previous]]:
            print('ERROR')
        source_to_dests[row[previous]][row[current]] = row[count]

total_migration_from = {}
# now need to normalize the count values for each source
for source in source_to_dests:
    tmf = 0
    for dest in source_to_dests[source]:
        pop = source_to_dests[source][dest]
        tmf += pop
    # print(tmf)
    total_migration_from[source] = tmf

    check_sum = 0
    for dest in source_to_dests[source]:
        pop = source_to_dests[source][dest]
        source_to_dests[source][dest] = float(pop)/tmf
        check_sum += source_to_dests[source][dest]
    # print(round(check_sum, 3))

# now need to remove a city from the pagerank.
# do not add any edges where current == city or where source == city

# if current == city, instead add an edge for each of the other dests,
# proportionally based on source_to_dests weights

for city in dropout_cities:

    G = nx.DiGraph()
    print(city)

    for state in x.sheet_names:
        df = x.parse(state)

        for index, row in df.iterrows():

            # print(index)
            # print(row)
            # print(previous)
            # print(current)

            # skip first three rows: header rows
            if index < 3:
                continue
            # skip the last rows: footer rows
            if index >= 53724:
                break

            if int(row[count]) < thresh:
                continue

            if row[previous] == 'Outside Metro Area within U.S. or Puerto Rico':
                continue
            if row[current] == 'Outside Metro Area within U.S. or Puerto Rico':
                continue

            # no migration influence FROM city
            # if row[previous] == city:
            #     continue

            # no migration inflience TO city
            if row[current] == city:
                population = int(row[count])
                for dest in source_to_dests[row[previous]]:
                    portion = int(population*source_to_dests[row[previous]][dest])
                    G.add_edge(row[previous], dest, weight=portion)
                    print('%s: %d' %(dest, portion))
            else:
                G.add_edge(row[previous], row[current], weight=int(row[count]))

    print(len(G.nodes()))
    print(len(G.edges()))

    # nx.write_gexf(G, "dropout/%s.gexf" % city)
    # nx.write_gpickle(G, "dropout/%s.gpickle" % city)

    pr = nx.pagerank(G, max_iter=1000)
    most_important = sorted([(value,key) for (key,value) in pr.items()], reverse=True)
    least_important = sorted([(value,key) for (key,value) in pr.items()])

    most_important_list = [k for v,k in most_important]
    np.savetxt('dropout/ranked-migration-from-%s'% city.replace(' ', ''), most_important_list, fmt='%s')

    # save most_important as a 
    most_important_df = pd.DataFrame.from_items([('ranking', most_important)])
    most_important_df.to_excel("dropout/ranked-migration-from-%s.xlsx" % city.replace(' ', ''))

    print("----- Most Important -----")
    for i in range(12):
        print(most_important[i])
    print("----- Least Important -----")
    for i in range(12):
        print(least_important[i])

    print(sum(pr.values()))