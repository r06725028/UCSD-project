import pandas as pd
from tqdm import tqdm

arr = []
num_list = ['0','1','2','3','4','5','6','7','8','9']
# path = '../original_data/'
path = 'CoMen/tsvdata/'

df = pd.read_csv(path + 'resource-duplicates.tsv', sep='\t')
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

new_arr = [sorted(list(int(y.replace('SCR_', '')) for y in x), reverse=True) for x in arr]

all_rid = pd.read_csv(path + 'resource-metadata.tsv', sep='\t', encoding="ISO-8859-1")['e_uid']
obj = {}

for dup in new_arr:
  nonexist_in_meta = True
  for v in dup:
    if(v in all_rid):
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
# print(len(obj), len(slave2master))

df = pd.read_csv(path + 'exclusion.tsv', sep='\t', header=None)
all_exclude_rid = []
for a, b in zip(df[0], df[1]):
  tmp = b if a.isdigit() else a
  tmp = int(tmp.replace('SCR_', ''))
  tmp = tmp if tmp not in slave2master else slave2master[tmp]
  if tmp not in all_exclude_rid: all_exclude_rid.append(tmp)
# print(len(all_exclude_rid), all_exclude_rid)
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

  #target = source[source.progress_apply(lambda x: str(x['id'])[0] in num_list, axis=1)]


  # target = source.loc[~source['rid'].isin(all_exclude_rid)]
  return target

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

# tmp = pd.read_csv(path + 'resource-mentions-relationships.tsv', sep='\t')
# relationship_tsv_filter(tmp)

# tmp = pd.read_csv(path + 'resource-mentions.tsv', sep='\t')
# print(len(mention_tsv_filter(tmp)))

