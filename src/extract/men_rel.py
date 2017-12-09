import math
import sqlite3
import time
import numpy as np
import pandas as pd
import csv
from process_duplicate import mention_tsv_filter, relationship_tsv_filter, meta_tsv_filter

######################################
#連結資料庫
conn = sqlite3.connect('newdb.db')
"""
#新增table
conn.execute('''CREATE TABLE MENTION (
	ID INT PRIMARY KEY NOT NULL, 
	RID INT , MENTION_ID TEXT , 
	INPUT_SOURCE TEXT , 
	CONFIDENCE TEXT , 
	SNIPPET TEXT);''')
print("create mention ok")

conn.execute('''CREATE TABLE RELATIONSHIP (
	SOURCE INT , 
	TARGET INT , 
	VALUE REAL );''')
print("create relationship ok")
"""


######################################mention!!!!!!!!!!!
#從tsv檔新增紀錄到db中
print("write mention start..")
csvfile = open('./CoMen/tsvdata/resource-mentions.tsv', 'r')
men_df = mention_tsv_filter(pd.read_csv(csvfile, delimiter='\t', low_memory=False))

#整理欄位：刪除和重新命名
men_df = men_df.drop(['uid','rating','timestamp','mentionid_int','vote_sum'],axis=1)#刪除column

men_df.columns.values[0] = 'ID'
men_df.columns.values[1] = 'RID'
men_df.columns.values[2] = 'MENTION_ID'
men_df.columns.values[3] = 'INPUT_SOURCE'
men_df.columns.values[4] = 'CONFIDENCE'
men_df.columns.values[5] = 'SNIPPET'

#寫入資料庫:加入原本的mention table/不把dataframe的id作為一欄（原本資料中即有）
men_df.to_sql('MENTION',conn,if_exists='append',index=False)
print("write ok!")

#####################################relation
print("write relationship start..")
csvfile = open('./CoMen/tsvdata/resource-mentions-relationships.tsv', 'r')
rel_df = relationship_tsv_filter(pd.read_csv(csvfile, delimiter='\t'))

#整理欄位：刪除和重新命名
rel_df = rel_df.drop(['id','comentions','count_hc','comentions_hc'],axis=1)#刪除column

rel_df.columns.values[0] = 'SOURCE'
rel_df.columns.values[1] = 'TARGET'
rel_df.columns.values[2] = 'VALUE'

#寫入資料庫:加入原本的mention table/不把dataframe的id作為一欄（原本資料中即有）
rel_df.to_sql('RELATIONSHIP',conn,if_exists='append',index=False)
print("write ok!")

####################################node

#df.loc[row_indexer,column_indexer]



conn.commit()
conn.close()



