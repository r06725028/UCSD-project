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

from process_duplicate import mention_tsv_filter, relationship_tsv_filter, meta_tsv_filter

num_list = ['0','1','2','3','4','5','6','7','8','9']
conf_list = [0.2,0.8,0.95,1.0]

#############################################秋中學長的函數#################################
def getEMIValue(a, b, c, total):
    #                        Resource A
    #            |          | Cited   | Not Cited  |
    #  Resource B| Cited    | a       | b-a        | b
    #            | Not Cited| c-a     | Total-b-c+a|
    #            |          | c       | Total      |
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
#conn = sqlite3.connect('1226_null.db')
engine = create_engine('sqlite:///1226_none.db',encoding="utf8")
conn = engine.connect()
########################################新增table######################################
conn.execute('''CREATE TABLE IF NOT EXISTS MENTION (
	ID INT PRIMARY KEY NOT NULL, 
	RID INT NOT NULL, MENTION_ID TEXT NOT NULL, 
	INPUT_SOURCE TEXT NOT NULL, 
	CONFIDENCE  INT NOT NULL, 
	SNIPPET TEXT );''')
print("create mention ok")

conn.execute('''CREATE TABLE RELATIONSHIP (
	SOURCE INT NOT NULL, 
	TARGET INT NOT NULL, 
	VALUE REAL NOT NULL,
	EMI REAL NOT NULL);''')
print("create relationship ok")

conn.execute('''CREATE TABLE NODE (
	ID INT PRIMARY KEY NOT NULL, 
	MENTION INT NOT NULL, ONE_MENTION INT NOT NULL, 
	POINT_NINE_FIVE_MENTION INT NOT NULL, 
	POINT_EIGHT_MENTION INT NOT NULL, 
	POINT_TWO_MENTION INT NOT NULL, 
	NAME TEXT , ABBR TEXT , URL TEXT , COMMUNITIES INT);''')
print("create node ok")

######################################mention###########################################
#從tsv檔新增紀錄到db中
print("write mention start......")
#2635021

csvfile = open('./CoMen/tsvdata/resource-mentions.tsv', 'r',encoding='utf-8')
men_df = mention_tsv_filter(pd.read_csv(csvfile, delimiter='\t', low_memory=False))

#整理欄位：刪除和重新命名
men_df = men_df.drop(['uid','rating','timestamp','mentionid_int','vote_sum'],axis=1)#刪除column

men_df.columns.values[0] = 'ID'
men_df.columns.values[1] = 'RID'
men_df.columns.values[2] = 'MENTION_ID'
men_df.columns.values[3] = 'INPUT_SOURCE'
men_df.columns.values[4] = 'CONFIDENCE'
men_df.columns.values[5] = 'SNIPPET'

#把空的confidence填上0.2，所以此欄是INT
men_df = men_df.fillna({"CONFIDENCE":0.2}) 
#men_df = men_df.fillna({'SNIPPET':'NULL'})
#寫入資料庫:加入原本的mention table/不把dataframe的id作為一欄（原本資料中即有）
men_df.to_sql('MENTION',conn,if_exists='append',index=False)
print("write mention ok!")

#####################################relation#############################################
print("write relationship start......")
#tsv檔總資料數3310177
csvfile = open('./CoMen/tsvdata/resource-mentions-relationships.tsv', 'r',encoding='utf-8')
rel_df = relationship_tsv_filter(pd.read_csv(csvfile, delimiter='\t'))

#整理欄位：刪除和重新命名
rel_df = rel_df.drop(['id','comentions','count_hc','comentions_hc'],axis=1)#刪除column

rel_df.columns.values[0] = 'SOURCE'
rel_df.columns.values[1] = 'TARGET'
rel_df.columns.values[2] = 'VALUE'

#算EMI
EMI_list = []

men_list = men_df['RID'].tolist()
c_men = Counter(men_list)
total = len(men_list)

print("======================算EMI開始============================")
#source_list = []#rel_df['SOURCE'].tolist()#et
#target_list = []#rel_df['TARGET'].tolist()#ec
total_list = []
for index, row in tqdm(enumerate(rel_df.iterrows()),total=len(rel_df),desc='count EMI'):
    a = row[1]['VALUE'] 
    b = c_men[row[1]['TARGET']]
    c = c_men[row[1]['SOURCE']]
    EMI = EMIValueAdjust(getEMIValue(a, b, c, total))
    EMI_list.append(EMI)

#增加欄位
rel_df['EMI'] = np.array(EMI_list)

#寫入資料庫:加入原本的mention table/不把dataframe的id作為一欄（原本資料中即有）
rel_df.to_sql('RELATIONSHIP',conn,if_exists='append',index=False)
print("write relationship ok!")

#######################################node#############################################
#讀tsv檔
#t1 = time.time()
print("write node start..")
csvfile = open('./CoMen/tsvdata/resource-metadata.tsv', 'rb')
meta_df = meta_tsv_filter(pd.read_csv(csvfile, sep='\t', encoding='ISO-8859-1', low_memory=False))
#csvfile = open('./CoMen/tsvdata/resource-mentions.tsv', 'r')
#men_df = mention_tsv_filter(pd.read_csv(csvfile, delimiter='\t', low_memory=False))

#建立新的dataframe
node_df = pd.DataFrame(columns=['ID', 'MENTION', 'ONE_MENTION', 'POINT_NINE_FIVE_MENTION', 
									'POINT_EIGHT_MENTION', 'POINT_TWO_MENTION',
											'NAME', 'ABBR', 'URL', 'COMMUNITIES'])
#主鍵
rid_arr = meta_df['e_uid']#有些rid在mention中沒有！！！！
#men_list = men_df['RID'].tolist()#所有被提到的rid(包含重複)
#c_men = Counter(men_list)
#print("rid len: ", len(rid_arr))#15360(meta的)13016(men)13006(remove nan)12836(學長的)

#各種存放計算次數的list
count_men_list = []
count_one_list = []
count_nine_list = []
count_eight_list = []
count_two_list = []
commun_list = []

#讀取communities
commun = OrderedDict()
path = "./171224/"#加上資料夾名稱
for dirPath, dirNames, fileNames in os.walk(path):#遍歷資料夾下每個txt檔
	for file in fileNames:#print (f)#印出"1.txt"
		commun_id = file[:len(file)-4]

		with open(path+file,'r') as f:
			#next(f)#略過第一行標頭
			for row in f:
				#row = row.split()
				rfid = row.strip()#key type:str
				commun[rfid] = commun_id
#print("commun ", commun)
#print("commun.keys()[0] ", list(commun.keys())[0])#6472 correct

for rid in tqdm(rid_arr,total=len(rid_arr),desc='count confidence & mention 次數'):
	#算mention次數
	num = c_men[rid]#men_list.count(rid)
	count_men_list.append(num)
	
	temp1_df = men_df[men_df['RID']==rid]#公用的!!!!!!!!!!!!
	confid_list = temp1_df['CONFIDENCE'].tolist()
	c_conf = Counter(confid_list)
	
	#算信心指數1的次數
	num = c_conf[1]#confid_list.count(1)
	count_one_list.append(num)

	#算信心指數0.95的次數
	num = c_conf[0.95]#confid_list.count(0.95)
	count_nine_list.append(num)

	#算信心指數0.8的次數
	num = c_conf[0.8]#confid_list.count(0.8)
	count_eight_list.append(num)

	#算0信心指數0.2的次數
	num = c_conf[0.2]#confid_list.count(0.2)
	count_two_list.append(num)

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
#print("mention ok")
	
node_df['ONE_MENTION'] = np.array(count_one_list)
#print("one_mention ok")

node_df['POINT_NINE_FIVE_MENTION'] = np.array(count_nine_list)
#print("0.95_mention ok")

node_df['POINT_EIGHT_MENTION'] = np.array(count_eight_list)
#print("0.8_mention ok")

node_df['POINT_TWO_MENTION'] = np.array(count_two_list)
#print("0.2_mention ok")

node_df['NAME'] = meta_df['resource_name']#加入name列
node_df['ABBR'] = meta_df['abbreviation']#加入abbr列
node_df['URL'] = meta_df['url']#加入URL列

node_df['COMMUNITIES'] = np.array(commun_list)
#print("commun ok")
#node_df = node_df.fillna({'NAME':'NULL','ABBR':'NULL','URL':'NULL','COMMUNITIES':'NULL'})


#寫入資料庫:加入原本的mention table/不把dataframe的id作為一欄（原本資料中即有）
node_df.to_sql('NODE',conn,if_exists='append',index=False)
print("write node ok!")

##################################新增結束，關閉資料庫######################################
conn.detach()#conn.commit()
conn.close()

t2 = time.time()
print("時間 = ",t2-t1)#486.86046838760376(1226)



