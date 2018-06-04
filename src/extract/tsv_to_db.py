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
parser = argparse.ArgumentParser(description='to_db')
parser.add_argument('--mode',choices=['slm','lda'],default='slm')
parser.add_argument('--r',default='250')

parser.add_argument('--data_path', default = 'src/extract/raw_tsv/')
parser.add_argument('--save_path', default = 'src/extract/process_data/')
parser.add_argument('--community_path', default = 'src/extract/180306/')
parser.add_argument('--output_path', default = 'src/display/data/ucsd_slm250.db')

args = parser.parse_args()


#========================================================================================
#計算EMI值
#input: 如下圖
#                        Resource A
#            |          | Cited   | Not Cited  |
#  Resource B| Cited    | a       | b-a        | b
#            | Not Cited| c-a     | Total-b-c+a|
#            |          | c       | Total      |
#output: EMI值
#========================================================================================
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

t1 = time.time()
#######################################連結資料庫#######################################
engine = create_engine('sqlite:///'+args.output_path,encoding="utf8")
conn = engine.connect()


########################################新增table######################################
conn.execute('''CREATE TABLE IF NOT EXISTS MENTION (
	ID INT PRIMARY KEY NOT NULL, 
	RID INT NOT NULL, 
	MENTION_ID TEXT NOT NULL, 
	INPUT_SOURCE TEXT NOT NULL, 
	CONFIDENCE  INT NOT NULL, 
	SNIPPET TEXT NOT NULL,
	YEAR TEXT NOT NULL );''')
print("create mention ok")

conn.execute('''CREATE TABLE RELATIONSHIP (
	SOURCE INT NOT NULL, 
	TARGET INT NOT NULL, 
	VALUE REAL NOT NULL,
	EMI REAL NOT NULL,
	MENTION_ID TEXT );''')
print("create relationship ok")

conn.execute('''CREATE TABLE NODE (
	ID INT PRIMARY KEY NOT NULL, 
	MENTION INT NOT NULL, ONE_MENTION INT NOT NULL, 
	POINT_NINE_FIVE_MENTION INT NOT NULL, 
	POINT_EIGHT_MENTION INT NOT NULL, 
	POINT_TWO_MENTION INT NOT NULL, 
	NAME TEXT , ABBR TEXT , URL TEXT , COMMUNITIES INT);''')
print("create node ok")

#=========================================
# mention
#=========================================
#從tsv檔新增紀錄到db中
print("write mention start......")

men_df = pkl.load(open(args.save_path+'men_df.pkl','rb')) 
	
#寫入資料庫:加入原本的mention table/不把dataframe的id作為一欄（原本資料中即有）
men_df.to_sql('MENTION',conn,if_exists='append',index=False)

print("write mention ok!")

#===========================================
#  relation
#============================================
print("write relationship start......")

rel_df = pkl.load(open(args.save_path+'rel_df.pkl','rb')) 


#寫入資料庫:加入原本的mention table/不把dataframe的id作為一欄（原本資料中即有）
rel_df.to_sql('RELATIONSHIP',conn,if_exists='append',index=False)
print("write relationship ok!")

#==============================================
#   node
#==============================================
#讀tsv檔
print("write node start..")

csvfile = open(args.data_path+'resource-metadata.tsv', 'rb')
meta_df = meta_tsv_filter(pd.read_csv(csvfile, sep='\t', encoding='ISO-8859-1', low_memory=False,quoting=3))


#建立新的dataframe
node_df = pd.DataFrame(columns=['ID', 'MENTION', 'ONE_MENTION', 'POINT_NINE_FIVE_MENTION', 
									'POINT_EIGHT_MENTION', 'POINT_TWO_MENTION',
											'NAME', 'ABBR', 'URL','COMMUNITIES'])
#主鍵
rid_arr = meta_df['e_uid']#有些rid在mention中沒有！！！！

#各種存放計算次數的list
count_men_list = []
count_one_list = []
count_nine_list = []
count_eight_list = []
count_two_list = []
commun_list = []


#讀取communities
commun = OrderedDict()

path = args.community_path+args.mode+args.r+'/'#加上資料夾名稱

for dirPath, dirNames, fileNames in os.walk(path):#遍歷資料夾下每個txt檔
	for file in fileNames:
		commun_id = file[:len(file)-4]

		with open(path+file,'r') as f:
			for row in f:
				rfid = row.strip()#key type:str
				commun[rfid] = commun_id

#取出所有rid
men_list = men_df['RID'].tolist()
#計算每個rid出現次數
c_men = Counter(men_list)

for rid in tqdm(rid_arr,total=len(rid_arr),desc='count confidence & mention 次數'):
	#算mention次數
	num = c_men[rid]
	count_men_list.append(num)
	
	if num > 0 :
		temp1_df = men_df[men_df['RID']==rid]#公用的
		confid_list = temp1_df['CONFIDENCE'].tolist()
		c_conf = Counter(confid_list)
		
		#算信心指數1的次數
		num = c_conf[1]
		count_one_list.append(num)

		#算信心指數0.95的次數
		num = c_conf[0.95]
		count_nine_list.append(num)

		#算信心指數0.8的次數
		num = c_conf[0.8]
		count_eight_list.append(num)

		#算0信心指數0.2的次數
		num = c_conf[0.2]
		count_two_list.append(num)

	else:
		count_one_list.append(0)
		count_nine_list.append(0)
		count_eight_list.append(0)
		count_two_list.append(0)

	#查找communities
	if str(rid) in commun:
		num = commun[str(rid)]
		commun_list.append(num)
	else:
		commun_list.append(np.nan)#放入nan表示遺失值

#放入經計算後各欄位的值
#加入各個欄位
node_df['ID'] = rid_arr#加入ID列

node_df['MENTION'] = np.array(count_men_list)
	
node_df['ONE_MENTION'] = np.array(count_one_list)

node_df['POINT_NINE_FIVE_MENTION'] = np.array(count_nine_list)

node_df['POINT_EIGHT_MENTION'] = np.array(count_eight_list)

node_df['POINT_TWO_MENTION'] = np.array(count_two_list)

node_df['NAME'] = meta_df['resource_name']#加入name列
node_df['ABBR'] = meta_df['abbreviation']#加入abbr列
node_df['URL'] = meta_df['url']#加入URL列

node_df['COMMUNITIES'] = np.array(commun_list)

#print("node len before = ",len(node_df))
#tqdm.pandas(desc='Remove node not in men')
node_df = node_df[node_df.progress_apply(lambda x: (x['MENTION']>0),axis=1)]
#print("node len after = ",len(node_df))

with open (args.save_path+'meta_df.pkl','wb') as f:
        print('saving tmp files...')
        pkl.dump(meta_df,f)
#寫入資料庫:加入原本的mention table/不把dataframe的id作為一欄（原本資料中即有）
node_df.to_sql('NODE',conn,if_exists='append',index=False)
print("write node ok!")


##################################新增結束，關閉資料庫######################################
conn.detach()#conn.commit()
conn.close()







