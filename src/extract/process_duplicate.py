import pandas as pd
from tqdm import tqdm
import sys, argparse, os 

#設定資料路徑
parser = argparse.ArgumentParser(description='process_duplicate')
parser.add_argument('--data_path', default = 'src/extract/raw_tsv/')
args = parser.parse_args()


#=========================================================
#處理duplicates：找出要被取代rid，以及決定最終要使用的rid和名稱
#input : resource-duplicates.tsv
#output : dict，其中key為要被取代的rid，value則是要使用的rid
#=========================================================
arr = []
df = pd.read_csv(args.data_path + 'resource-duplicates.tsv', sep='\t')
for a,b in zip(df['id1'], df['id2']):
  flag = True
  tmp = { a, b }
  if(arr == []): arr.append(tmp)
  for idx, singleSet in enumerate(arr):
    if(a in singleSet or b in singleSet):
      arr[idx] = singleSet.union(tmp)
      flag = False
      break
  if(flag): arr.append(tmp)

new_arr = [sorted(list(int(y.replace('SCR_', '')) for y in x)) for x in arr]


metaData = pd.read_csv(args.data_path + 'resource-metadata.tsv', sep='\t', encoding="ISO-8859-1")
all_rid2name = { rid: name for rid, name in zip(metaData['e_uid'], metaData['resource_name']) }

obj = {}
for dup in new_arr:
  nonexist_in_meta = True
  for v in dup:
    if(v in all_rid2name):
      nonexist_in_meta = False
      dup.remove(v)
      obj[v] = dup
      break
  if(nonexist_in_meta):
    with open('duplicate_error_file', 'w') as f:
      f.write(str(dup) + '\n')

slave2master = {}
for master in obj.keys():
  for slave in obj[master]:
    slave2master[slave] = master


#====================================================
#處理exclusion：找出需被移除的rid
#input : exclusion.tsv
#output : list，其中element為要被移除的rid
#====================================================
df = pd.read_csv(args.data_path + 'exclusion.tsv', sep='\t', header=None)
all_exclude_rid = []

for b in df[1]:
  tmp = b 
  tmp = int(tmp.replace('SCR_', ''))
  tmp = tmp if tmp not in slave2master else slave2master[tmp]
  if tmp not in all_exclude_rid: all_exclude_rid.append(tmp)
  
#====================================================
#替代mention資料中須被取代的rid，以及移除需被排除的rid
#input : dataframe
#output : dataframe
#====================================================

steps = 0

def mention_tsv_filter(source):
  # for other tsv file
  print('\n====================[ mention.tsv ]===================\n')
  global steps
  
  steps += 1
  tqdm.pandas(desc='[' + str(steps) + '] Remove Duplicate values')

  source['rid'] = source['rid'].progress_apply(lambda x: x if x not in slave2master else slave2master[x])

  steps += 1
  tqdm.pandas(desc='[' + str(steps) + '] Remove Exclude values')

  target = source[source.progress_apply(lambda x: (x['rid'] not in all_exclude_rid) and (str(x['id'])[0] in num_list), axis=1)]

  return target

#====================================================
#替代relationship資料中須被取代的rid，以及移除需被排除的rid
#input : dataframe
#output : dataframe
#====================================================
def relationship_tsv_filter(source):

  print('\n====================[ relationship.tsv ]===================\n')

  global steps
  target = source

  steps += 1
  tqdm.pandas(desc='[' + str(steps) + '] Remove Duplicate values')
  target['r1'] = target['r1'].progress_apply(lambda x: x if x not in slave2master else slave2master[x])
  target['r2'] = target['r2'].apply(lambda x: x if x not in slave2master else slave2master[x])

  steps += 1
  tqdm.pandas(desc='[' + str(steps) + '] Remove Exclude values')
  target = target[target.progress_apply(lambda x: x['r1'] not in all_exclude_rid, axis=1)]
  target = target[target.apply(lambda x: x['r2'] not in all_exclude_rid, axis=1)]
  target = target.query('r1 != r2')
 
  return target

#====================================================
#替代metadata資料中須被取代的rid，以及移除需被排除的rid
#input : dataframe
#output : dataframe
#====================================================

def meta_tsv_filter(source):
  # only for meta.tsv
  print('\n====================[ meta.tsv ]===================\n')

  global steps
  slaves = list(slave2master.keys())
  filters = slaves + all_exclude_rid

  steps += 1
  tqdm.pandas(desc='[' + str(steps) + '] Remove Duplicate & Exclude values')
  target = source[source.progress_apply(lambda x: x['e_uid'] not in filters, axis=1)]

  return target


