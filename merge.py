import csv
import os, shutil
import random

scale = 1000
expon = 2

top_x_ranked = 20

def run_merge(gender, exp_name):
    home = '/Users/abbyvansoest/migration/'
    direct = '/Users/abbyvansoest/migration/dropout/'
    if gender == 'male':
        direct = '/Users/abbyvansoest/migration/dropout-gender/01/'
    elif gender == 'female':
        direct = '/Users/abbyvansoest/migration/dropout-gender/02/'

    files = []
    for file in os.listdir(direct):
        f = direct + file
        if os.path.isdir(f) or file.startswith('.'):
            continue
        if file.find(exp_name) == -1:
            continue
        print(file)
        files.append(f)

    files.append(home + 'results/most-important-list')
    if gender == 'male':
        files.append(home + 'results/most-important-list-male')
    if gender == 'female':
        files.append(home + 'results/most-important-list-female')

    if gender != '':
        files.append(home + 'results/most-important-list-gender-global')

    dst = 'merged/all_drop_pr_data-%s-%s-top%d.txt' % (exp_name, gender, top_x_ranked)
    if top_x_ranked == -1:
        dst = 'merged/all_drop_pr_data-%s-%s.txt' % (exp_name, gender)
    shutil.copyfile('coordinates.txt', dst)

    for i,f in enumerate(files):
        joined = open(dst,'r')

        print(f)
        pr_file = open(f)

        if f == home+'results/most-important-list':
            city = 'pr'
        elif f == home+'results/most-important-list-gender-global':
            city = 'pr_global'
        elif f == home + 'results/most-important-list-male':
            city = 'pr_male'
        elif f == home + 'results/most-important-list-female':
            city = 'pr_female'
        else:
            idx = f.find(exp_name) + len(exp_name) + 1
            city = f[idx:idx+7].strip().replace('-', '')

        prev = csv.reader(joined, delimiter='\t')    
        pr_tsv = csv.reader(pr_file, delimiter='\t')

        prev_list=list(prev)
        pr_tsv_list=list(pr_tsv)

        final = []
        for idx, t1 in enumerate(prev_list):
            if idx == 0:
                # print(t1)
                continue
            matched = False
            for rank, t2 in enumerate(pr_tsv_list):
                if rank > top_x_ranked and top_x_ranked != -1:
                    break
                if t1[0].strip() == t2[0].strip():
                    final.append(t1 + [(float(t2[1])*scale)**expon])
                    matched = True
            if not matched: # what about unmatched cities?
                final.append(t1 + [0.0])

        joined.close()
        pr_file.close()

        # print(len(final))
        with open(dst, 'w') as f:
            new_title = '%s-%s'%(city, gender)
            if city == 'pr' or city == 'pr_female' or city == 'pr_male' or city == 'pr_global':
                new_title = city
            header = prev_list[0] + [city]
            f.write('\t'.join(header) + '\n')
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(final)
        
    print(header)

genders = ['', 'male', 'female']
exp_names = ['migration-from']
for gender in genders:
    for exp_name in exp_names:
        run_merge(gender, exp_name)




