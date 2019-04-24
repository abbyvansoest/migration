import csv
import os, shutil
import random

scale = 1000

exp_name = 'none-from'

direct = '/Users/abbyvansoest/migration/dropout/'

files = []
for file in os.listdir(direct):
    f = direct + file
    if os.path.isdir(f) or file.startswith('.'):
        continue
    if file.find(exp_name) == -1:
        continue

    print(file)
    files.append(f)

files.append('results/most-important-list')
# copy coordinates files
# joined = open('all_drop_pr_data.txt','r')
dst = 'all_drop_pr_data.txt'
shutil.copyfile('coordinates.txt', dst)

for i,f in enumerate(files):
    joined = open(dst,'r')

    pr_file = open(f)

    if f == 'results/most-important-list':
        city = 'pr'
    else:
        idx = f.find(exp_name) + len(exp_name) + 1
        city = f[idx:idx+7].strip().replace('-', '')

    prev = csv.reader(joined, delimiter='\t')    
    pr_tsv = csv.reader(pr_file, delimiter='\t')

    prev_list=list(prev)
    pr_tsv_list=list(pr_tsv)

    final = []
    for t1 in prev_list:
        for t2 in pr_tsv_list:
           if t1[0].strip() == t2[0].strip():
            final.append(t1 + [float(t2[1])*scale])

    joined.close()
    pr_file.close()

    with open(dst, 'w') as f:
        header = prev_list[0] + ['pr_drop_%s'%city]
        f.write('\t'.join(header) + '\n')
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(final)
    
print(header)
