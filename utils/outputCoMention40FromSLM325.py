from tqdm import tqdm
from joblib import Parallel, delayed
import multiprocessing
import sqlite3
import math
import pandas as pd

def main(rid):
  conn = sqlite3.connect('data_sucks_slm325.db')
  conn.text_factory = str
  # Get their top 40 highest frequency co-mention resource partners
  sql = 'SELECT TARGET, VALUE AS res FROM RELATIONSHIP WHERE SOURCE={}\
          UNION\
         SELECT SOURCE, VALUE AS res FROM RELATIONSHIP WHERE TARGET={}\
         ORDER BY VALUE DESC LIMIT 40'.format(rid, rid)
  cursor = conn.execute(sql)
  comention_rids = [str(pair[0]) for pair in cursor]
  
  sql = 'SELECT COMMUNITIES, COUNT(*) FROM NODE WHERE ID IN ({}) AND COMMUNITIES != \'nan\' GROUP BY COMMUNITIES'.format(','.join(comention_rids))
  cursor = conn.execute(sql)
  countRes = { str(x[0]): x[1] for x in cursor }

  community = { str(i): 0 for i in range(82) }
  for key in countRes.keys():
    community[key] += countRes[key]
  entropy = diversity(community)

  # Get these partner's SLM r=3.25 community assignment
  sql = 'SELECT NODE.NAME, TEMP.COUNT\
         FROM NODE\
         LEFT JOIN\
         (SELECT RID ,COUNT(*) AS COUNT FROM MENTION WHERE MENTION.RID={}) TEMP\
         ON TEMP.RID = NODE.ID WHERE NODE.ID={} LIMIT 1'.format(rid, rid)
  rName, rMention = next(conn.execute(sql))

  stringLine = '{}\t{}\t'.format(rid, rName)
  for key in sorted(community.keys(), key=lambda x: int(x)):
    stringLine += '{}\t'.format(community[key])
  stringLine += '{}\t{}\t{}\n'.format(entropy, rMention, entropy * rMention)
  with open('result_slm325(1).tsv', 'a') as f:
    f.write(stringLine)

def diversity(community):
  # total of com
  total = len(community);
  # print ( # of mentions of resource + tab );munity(i), for all i
  entropy = 0
  for count in community.values():
    if count != 0:
      entropy -= (count / total) * math.log(count / total);
  return entropy;

if __name__ == '__main__':
  conn = sqlite3.connect('data_sucks_slm325.db')
  conn.text_factory = str
  cursor = conn.execute('''SELECT DISTINCT ID FROM NODE''')
  all_rids = [ridPair[0] for ridPair in cursor]

  with open('result_slm325(1).tsv', 'w') as f:
    f.write('Resource_ID\tResource_Name\t')
    for i in range(82):
      f.write('community({})\t'.format(i))
    f.write('diversity\tmention\tmultiple/n\n')

  num_cores = multiprocessing.cpu_count()
  Parallel(n_jobs=num_cores)(delayed(main)(rid) for rid in tqdm(all_rids)) # 0 ~ 688

  tmp = pd.read_csv('result_slm325(1).tsv', sep='\t')
  tmp = tmp.sort_values('Resource_ID')
  tmp.to_csv('final_slm325.tsv', sep='\t', index=False) 
