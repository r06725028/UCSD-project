import math
import sqlite3
import time
import numpy as np
import pandas as pd
import csv
from tqdm import tqdm

t1 = time.time()
###############################global variable: 用來檢查用的##################################
num_list = ['0','1','2','3','4','5','6','7','8','9']
conf_list = [0.2,0.8,0.95,1.0]
steps = 0

path = 'CoMen/tsvdata/'
all_slave_rid = []
all_exclude_rid = []

#####################讀duplicates，建立slave2master，每個slave對應到一個master#################
df = pd.read_csv(path + 'resource-duplicates.tsv', sep='\t')
arr = []
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

all_slave_rid = list(slave2master.keys())

#################################讀exclusion，找出所有應移除的rid##################################
df = pd.read_csv(path + 'exclusion.tsv', sep='\t', header=None)
#all_exclude_rid = []
for a, b in zip(df[0], df[1]):
  tmp = b if a.isdigit() else a
  tmp = int(tmp.replace('SCR_', ''))
  tmp = tmp if tmp not in slave2master else slave2master[tmp]
  if tmp not in all_exclude_rid: all_exclude_rid.append(tmp)

###############################################連結資料庫#########################################
conn = sqlite3.connect('1226.db')
cur = conn.cursor()

####################################從資料庫中取出要檢查的data#####################################
#mention
men_list_of_tuple = cur.execute("select * from MENTION ").fetchall()
men_df = pd.DataFrame(men_list_of_tuple, columns=['ID', 'RID', 'MENTION_ID', 'INPUT_SOURCE', 'CONFIDENCE', 'SNIPPET'])

#node
node_list_of_tuple = cur.execute("select * from NODE ").fetchall()
node_df = pd.DataFrame(node_list_of_tuple, columns=['ID', 'MENTION', 'ONE_MENTION', 'POINT_NINE_FIVE_MENTION', 
	'POINT_EIGHT_MENTION', 'POINT_TWO_MENTION', 'NAME', 'ABBR', 'URL', 'COMMUNITIES'])

#relationship
rel_list_of_tuple = cur.execute("select * from RELATIONSHIP ").fetchall()
rel_df = pd.DataFrame(rel_list_of_tuple, columns=['SOURCE', 'TARGET', 'VALUE','EMI'])

######################################檢查MENTION######################################

print('\n====================[ mention ]===================\n')#跑約五分鐘

#steps += 1
#tqdm.pandas(desc='[' + str(steps) + '] mention check')

for index, row in tqdm(enumerate(men_df.iterrows()),total=len(men_df),desc='mention check'):#Iterate over DataFrame rows as (index, Series) pairs
	if row[1]['RID'] in all_slave_rid:#檢查duplicate
		with open("men_duplicate_error.txt",'a') as f:
			print("duplicate error in index : ",str(index)," / ID = ", str(row[1]['ID']))
			f.write("index : "+str(index)+" / ID = "+str(row[1]['ID'])+'\n')
	elif row[1]['RID'] in all_exclude_rid:#檢查exclude
		with open("men_exclude_error.txt",'a') as f:
			print("exclude error in index : ",str(index)," / ID = ", str(row[1]['ID']))
			f.write("index : "+str(index)+" / ID = "+str(row[1]['ID'])+'\n')
	else:
		#檢查id是否有非數字出現（原本的mention.tsv中有部分資料格式錯誤，會導致not null failed）
		for char in str(row[1]['ID']):
			if char not in num_list:
				with open("men_ID_error.txt",'a') as f:
					print("ID string error in index: ", str(index), " / ID = ", str(row[1]['ID']))
					f.write("index: "+str(index)+" / ID = "+str(row[1]['ID'])+'\n')
				break
		#檢查confidence是否有nan，即沒補成NULL（原本的mention.tsv中有部分資料遺失，會導致not null failed）
		if row[1]['CONFIDENCE'] not in conf_list:
			with open("men_confidence_error.txt",'a') as f:
				print("conf nan error in index: ", str(index)," / ID = ", str(row[1]['ID']))
				f.write("index: "+str(index)+" / ID = "+str(row[1]['ID'])+'\n')

print("men check ok")

######################################檢查relationship######################################
print('\n====================[ relationship ]===================\n')#跑約22分鐘
#steps += 1
#tqdm.pandas(desc='[' + str(steps) + '] relationship check')

for index, row in tqdm(enumerate(rel_df.iterrows()),total=len(rel_df),desc='relationship check'):
#Iterate over DataFrame rows as (index, Series) pairs:row[1]即是單列的series
	if row[1]['SOURCE']  in all_slave_rid:#檢查duplicate
		with open("rel_duplicate_error.txt",'a') as f:
			print("duplicate 'source' error in index : ",str(index)," / SOURCE = ", str(row[1]['SOURCE']))
			f.write("index : "+str(index)+" / SOURCE = "+str(row[1]['SOURCE'])+'\n')
	elif row[1]['TARGET'] in all_slave_rid:#檢查duplicate
		with open("rel_duplicate_error.txt",'a') as f:
			print("duplicate 'target' error in index : ",str(index)," / TARGET = ", str(row[1]['TARGET']))
			f.write("index : "+str(index)+" / TARGET = "+str(row[1]['TARGET'])+'\n')
	
	elif row[1]['SOURCE']  in all_exclude_rid:#檢查exclude
		with open("rel_exclude_error.txt",'a') as f:
			print("exclude 'source' error in index : ",str(index)," / SOURCE = ", str(row[1]['SOURCE']))
			f.write("index : "+str(index)+" / SOURCE = "+str(row[1]['SOURCE'])+'\n')
	elif row[1]['TARGET'] in all_exclude_rid:#檢查exclude
		with open("rel_exclude_error.txt",'a') as f:
			print("exclude 'target' error in index : ",str(index)," / TARGET = ", str(row[1]['TARGET']))
			f.write("index : "+str(index)+" / TARGET = "+str(row[1]['TARGET'])+'\n')
	
print("rel check ok")

###############################################檢查node#######################################
print('\n====================[ node ]===================\n')#跑約1分鐘
#steps += 1
#tqdm.pandas(desc='[' + str(steps) + '] node check')

for index, row in tqdm(enumerate(node_df.iterrows()),total=len(node_df),desc='node check'):#Iterate over DataFrame rows as (index, Series) pairs
	if row[1]['ID']  in all_slave_rid:#檢查duplicate
		with open("node_duplicate_error.txt",'a') as f:
			print("duplicate error in index : ",str(index)," / ID = ", str(row[1]['ID']))
			f.write("index : "+str(index)+" / ID = "+str(row[1]['ID'])+'\n')
	elif row[1]['ID'] in all_exclude_rid:#檢查exclude
		with open("node_exclude_error.txt",'a') as f:
			print("exclude error in index : ",str(index)," / ID = ", str(row[1]['ID']))
			f.write("index : "+str(index)+" / ID = "+str(row[1]['ID'])+'\n')
	else:
		#信心指數1的次數
		num_1 = row[1]['ONE_MENTION']#confid_list.count('1.0')
		#信心指數0.95的次數
		num_95 = row[1]['POINT_NINE_FIVE_MENTION']#confid_list.count('0.95')
		#信心指數0.8的次數
		num_8 = row[1]['POINT_EIGHT_MENTION']#confid_list.count('0.8')
		#信心指數0.2的次數
		num_2 = row[1]['POINT_TWO_MENTION']#confid_list.count('0.2')

		sum_mention = num_1+num_95+num_8+num_2#+num_null

		if row[1]['MENTION'] != sum_mention:#檢查menttion次數是否有算錯
			with open("node_count_mention_error.txt",'a') as f:
				print("count error in index: ",str(index), " MENTION = ", str(row[1]['MENTION']), " / sum_mention = ", str(sum_mention))
				f.write("index: ",str(index)+" MENTION = "+str(row[1]['MENTION'])+" / sum_mention = "+str(sum_mention)+'\n')

		if row[1]['COMMUNITIES'] == 'nan':#檢查是否有資源沒被分到群
			with open("node_community_error.txt",'a') as f:
				print("community error in index: ", str(index), " / ID = ", str(row[1]['ID']))
				f.write("index: "+str(index)+" / ID = "+str(row[1]['ID'])+'\n')

print("node check ok")

cur.close()
conn.close()	

t2 = time.time()

print("check db 時間 = ", t2-t1)#927.8324720859528




