#encoding='utf-8'
import math
import sqlite3
import time
import os
import numpy as np
import pandas as pd
import csv
from tqdm import tqdm
from collections import OrderedDict #有序字典
from collections import Counter
import string 
from sqlalchemy import create_engine 
import requests
import pickle as pkl

import sys, argparse, os

from process_duplicate import mention_tsv_filter, relationship_tsv_filter, meta_tsv_filter


#設定資料路徑
parser = argparse.ArgumentParser(description='for_slms')
parser.add_argument('--data_path', default = 'src/extract/raw_tsv/')
parser.add_argument('--save_path', default = 'src/extract/process_data/')

args = parser.parse_args()

def getEMIValue(a, b, c, total):
	if int(a) > int(b) or int(a) > int(c):
		return 0
	else:
		a = float(a)
		b = float(b)
		c = float(c)
		total = float(total)

		pA = float(c / total)
		pnA = float(1 - pA)
		pB = float(b / total)
		pnB = float(1 - pB)
		pAB = float(a / total)
		pnAB = float((b - a) / total)
		pAnB = float((c - a) / total)
		pnAnB = float((total - b - c + a) / total)

		part1 = float(pAB * math.log(float(pAB / float(pA * pB)), 2))

		if(a != c):
			part2 = float(pAnB * math.log(float(pAnB / float(pA * pnB)), 2))
		else:
			part2 = 0

		part3 = float(pnAnB * math.log(float(pnAnB / float(pnA * pnB)), 2))

		if(a != b):
			part4 = float(pnAB * math.log(float(pnAB / float(pnA * pB)), 2))
		else:
			part4 = 0

		return (part1 + part2 + part3 + part4)

def EMIValueAdjust(value):
	return 5 * value * math.pow(10, 5)


#=========================================
# mention
#=========================================
#quoting=3用來設定對於括號的處理，避免“”“被用作註解，使得部分資料未被讀取到
csvfile = open(args.data_path+'resource-mentions.tsv', 'r')
men_df = mention_tsv_filter(pd.read_csv(csvfile, delimiter='\t', low_memory=False,quoting=3))


#移除重複項（因為經過duplicate替代後會有重複項出現）
print("men len before 移除重複項 = ",len(men_df))
men_df = men_df.drop_duplicates(['rid','mentionid'])
print("men len after 移除重複項 = ",len(men_df))

#只取confidence > 0.5   OR   rating = good
print("men len before 過濾 = ",len(men_df))
tqdm.pandas(desc='過濾掉信心低的')
men_df = men_df[men_df.progress_apply(lambda x: ((x['confidence']>0.5) or (x['rating']=='good')),axis=1)]
print("men len after 過濾 = ",len(men_df))

#加上年份
year_list = []
pmid_to_year = pkl.load(open(args.save_path+'pmid_to_year.pkl','rb'))
print('有年份的pmid = ',len(pmid_to_year))

for pmid in tqdm(men_df['mentionid_int'],total=len(men_df),desc='get year'):
	try:
		pmid = str(int(pmid))
		if pmid in pmid_to_year:
			year_list.append(pmid_to_year[pmid])
		else:
			year_list.append('NULL')
	except:
		year_list.append('NULL')

#整理欄位
#刪除column
men_df = men_df.drop(['uid','rating','timestamp','vote_sum','mentionid_int'],axis=1)

men_df.columns.values[0] = 'ID'
men_df.columns.values[1] = 'RID'
men_df.columns.values[2] = 'MENTION_ID'
men_df.columns.values[3] = 'INPUT_SOURCE'
men_df.columns.values[4] = 'CONFIDENCE'
men_df.columns.values[5] = 'SNIPPET'

#增加年份欄位
men_df['YEAR'] = np.array(year_list)

#處理遺失值
men_df = men_df.fillna({'SNIPPET':'NULL'})

with open (save_path+'men_df.pkl','wb') as f:
	pkl.dump(men_df,f)

#===========================================
#  relation
#============================================
csvfile = open(args.data_path+'resource-mentions-relationships.tsv', 'r',encoding='utf-8')
rel_df = relationship_tsv_filter(pd.read_csv(csvfile, delimiter='\t',quoting=3))

#移除count_hc=0
print("rel len before 移除count_hc=0 : ",len(rel_df))
tqdm.pandas(desc='過濾掉信心低的')
rel_df = rel_df[rel_df.progress_apply(lambda x: (x['count_hc']>0),axis=1)]
print("rel len after 移除count_hc=0 : ",len(rel_df))

#檢查是否r1>r2，不是的話就交換順序，方便之後移除重複項
#（因為經過duplicate替代後，可能出現r1>r2的情況）
for index, row in tqdm(enumerate(rel_df.iterrows()),total=len(rel_df),desc='檢查r1>r2'):
	a = row[1]['r1'] 
	b = row[1]['r2']
	
	if a > b :
		tamp = row[1]['r2']
		row[1]['r2'] = row[1]['r1']
		row[1]['r1'] = tamp
		bool_ = True


#重新排序，由小排到大
rel_df = rel_df.sort_values(by=['r1','r2'])

#移除重複項
print("rel len before 移除重複項 = ",len(rel_df))
rel_df = rel_df.drop_duplicates(['r1','r2','comentions_hc'])#預設留先出現的
print("rel len after 移除重複項 = ",len(rel_df))


#用pmid當key，找出每篇論文提到的rid有哪些
#再依此去重建出resource-mentions-relationships
#避免再有重複項出現
rel_dict = OrderedDict()
for index, row in tqdm(enumerate(rel_df.iterrows()),total=len(rel_df),desc='用pmid當key'):
	r1 = row[1]['r1'] 
	r2 = row[1]['r2']
	val = row[1]['count_hc']
	c_str = row[1]['comentions_hc']

	if c_str !=  '':#不為空字串
		c_list = c_str.split(',')

		if (r1,r2) not in rel_dict:
			rel_dict[(r1,r2)] = [val,c_list]
		else:
			for pmid in c_list:
				if pmid not in rel_dict[(r1,r2)][1]:
					rel_dict[(r1,r2)][0]+=1 
					rel_dict[(r1,r2)][1].append(pmid)

#新建df
new_rel_df = pd.DataFrame(columns=['SOURCE','TARGET', 'VALUE','EMI','MENTION_ID'])

r1r2_list = list(rel_dict.keys())
#print('檢查排序: ',r1r2_list[0])

sor_list = []
tar_list = []
val_list = []
EMI_list = []
menid_list = []

#算EMI用
men_list = men_df['RID'].tolist()
c_men = Counter(men_list)

total = len(men_list)

for (sor,tar) in r1r2_list:
	sor_list.append(sor)
	tar_list.append(tar)

	a = rel_dict[(sor,tar)][0] 
	b = c_men[tar]
	c = c_men[sor]
	EMI = EMIValueAdjust(getEMIValue(a, b, c, total))
	EMI_list.append(abs(EMI))

	val_list.append(a)
	menid_list.append(np.array(','.join(rel_dict[(sor,tar)][1])))

#增加欄位
new_rel_df['SOURCE'] = np.array(sor_list)
new_rel_df['TARGET'] = np.array(tar_list)
new_rel_df['VALUE'] = np.array(val_list)
new_rel_df['EMI'] = np.array(EMI_list)
new_rel_df['MENTION_ID'] = np.array(menid_list)


with open (args.save_path+'rel_df.pkl','wb') as f:
	pkl.dump(new_rel_df,f)

#輸出跑slm的tsv檔
#轉換type
tqdm.pandas(desc='EMI to INT')
new_rel_df['EMI'] = new_rel_df['EMI'].progress_apply(lambda x: int(x*math.pow(10,12)))#轉成int格式
new_rel_df = new_rel_df.drop (['VALUE','MENTION_ID'],axis=1)#刪除column

#轉成tsv檔，用來跑SLM用的
new_rel_df.to_csv(args.save_path+'slm_input.csv', sep='\t', index=False, header=None)#必須沒有標頭，用\t分隔才可以







