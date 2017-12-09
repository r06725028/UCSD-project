import math
import sqlite3
import time
import os
import numpy as np
import pandas as pd
import csv
from collections import OrderedDict #有序字典
import string 
from process_duplicate import mention_tsv_filter, relationship_tsv_filter, meta_tsv_filter

#############################################
#連結資料庫
conn = sqlite3.connect('newdb.db')
"""
conn.execute('''CREATE TABLE NODE (
	ID INT PRIMARY KEY NOT NULL, 
	MENTION INT NOT NULL, ONE_MENTION INT NOT NULL, 
	POINT_NINE_FIVE_MENTION INT NOT NULL, 
	POINT_EIGHT_MENTION INT NOT NULL, 
	POINT_TWO_MENTION INT NOT NULL, 
	NAME TEXT, ABBR TEXT, URL TEXT, COMMUNITIES INT);''')
print("create node ok")
"""
##########################################
#讀tsv檔
print("write node start..")
csvfile = open('./CoMen/tsvdata/resource-metadata.tsv', 'rb')
meta_df = meta_tsv_filter(pd.read_csv(csvfile, sep='\t', encoding='ISO-8859-1', low_memory=False))

csvfile = open('./CoMen/tsvdata/resource-mentions.tsv', 'r')
men_df = mention_tsv_filter(pd.read_csv(csvfile, delimiter='\t', low_memory=False))

###########################################
#建立新的dataframe
node_df = pd.DataFrame(columns=['ID', 'MENTION', 'ONE_MENTION', 'POINT_NINE_FIVE_MENTION', 
									'POINT_EIGHT_MENTION', 'POINT_TWO_MENTION',
											'NAME', 'ABBR', 'URL', 'COMMUNITIES'])
#主鍵
rid_arr = meta_df['e_uid']#有些rid在mention中沒有！！！！
men_list = men_df['rid'].tolist()#所有被提到的rid(包含重複)
#rid_arr = np.array(list(set(men_list)))#移除重複後當作主鍵(會有nan!!!!why??????)
#rid_arr = rid_arr[~np.isnan(rid_arr)]#移除nan(rid type = float!)
print("rid len: ", len(rid_arr))#15360(meta的)13016(men)13006(remove nan)12836(學長的)

#各種存放計算次數的list
count_men_list = []
count_one_list = []
count_nine_list = []
count_eight_list = []
count_two_list = []
commun_list = []

#讀取communities
commun = OrderedDict()
path = os.getcwd()+"/20171019/"#加上資料夾名稱
for dirPath, dirNames, fileNames in os.walk(path):#遍歷資料夾下每個txt檔
	for file in fileNames:#print (f)#印出"1.txt"
		commun_id = file[:len(file)-4]

		with open(path+file,'r') as f:
			next(f)#略過第一行標頭
			for row in f:
				row = row.split()
				rfid = row[0].strip()#key type:str
				commun[rfid] = commun_id
#print("commun.keys()[0] ", list(commun.keys())[0])#6472 correct

for rid in rid_arr:
	#算mention次數
	num = men_list.count(rid)
	count_men_list.append(num)
	
	temp1_df = men_df[men_df['rid']==rid]#公用的!!!!!!!!!!!!
	confid_list = temp1_df['confidence'].tolist()
	
	#算信心指數1的次數
	#temp_1_df = temp_df[temp_df['confidence']==1]
	#num = len(temp_1_df.index)
	num = confid_list.count(1)
	count_one_list.append(num)

	#算信心指數0.95的次數
	num = confid_list.count(0.95)
	count_nine_list.append(num)


	#算信心指數0.8的次數
	num = confid_list.count(0.8)
	count_eight_list.append(num)

	#算0信心指數0.2的次數
	num = confid_list.count(0.2)
	count_two_list.append(num)

	#查找communities
	if str(rid) in commun:
		num = commun[str(rid)]
		commun_list.append(num)
	else:
		commun_list.append(np.nan)

#放入經計算後各欄位的值
#加入各個欄位
node_df['ID'] = rid_arr#加入ID列

node_df['MENTION'] = np.array(count_men_list)
print("mention ok")
	
node_df['ONE_MENTION'] = np.array(count_one_list)
print("one_mention ok")

node_df['POINT_NINE_FIVE_MENTION'] = np.array(count_nine_list)
print("0.95_mention ok")

node_df['POINT_EIGHT_MENTION'] = np.array(count_eight_list)
print("0.8_mention ok")

node_df['POINT_TWO_MENTION'] = np.array(count_two_list)
print("0.2_mention ok")

node_df['NAME'] = meta_df['resource_name']#加入name列
node_df['ABBR'] = meta_df['abbreviation']#加入abbr列
node_df['URL'] = meta_df['url']#加入URL列

node_df['COMMUNITIES'] = np.array(commun_list)
print("commun ok")

#寫入資料庫:加入原本的mention table/不把dataframe的id作為一欄（原本資料中即有）
node_df.to_sql('NODE',conn,if_exists='append',index=False)
print("write ok!")

conn.commit()
conn.close()


"""
#整理欄位：刪除和重新命名
meta_df = meta_df.drop(['descripition','see_full_record_url','see_full_record','alternative_ids','original_id','canonical_id'],axis=1)#刪除column
men_df = men_df.drop(['id','uid','mentionid','rating','timestamp','mentionid_int','input_source','vote_sum','snippet'],axis=1)
"""



