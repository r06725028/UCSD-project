import pandas as pd
import numpy as np
import csv
from tqdm import tqdm
from collections import OrderedDict #有序字典
import time
import os
import matplotlib.pyplot as plt
import numpy as np
import string 
import sys
import sqlite3
from sqlalchemy import create_engine 
import pickle as pkl

import sys, argparse, os

#設定資料路徑
parser = argparse.ArgumentParser(description='dunn_db')
parser.add_argument('mode',choice=['slm','lda'])
parser.add_argument('r')
parser.add_argument('--data_path', default = './raw_tsv/')
parser.add_argument('--save_path', default = './process_data/')
parser.add_argument('--community_path', default = './180306/')
parser.add_argument('--output_path', default = '../display/dunn.db')

#建立資料庫
conn = sqlite3.connect(args.dunn_path)
cur = conn.cursor()

#建立資料庫欄位
cur.execute('''CREATE TABLE  TWO_GROUP (
		G1 INT  NOT NULL, 
		G2 INT NOT NULL,  
		EMI REAL NOT NULL );''')
print("create TWO_GROUP ok")

cur.execute('''CREATE TABLE IN_GROUP (
		GID INT NOT NULL, 
		r1 INT  NOT NULL,
		r2 INT NOT NULL,
		EMI REAL NOT NULL );''')
print("create IN_GROUP ok")

#讀分群結果
def read_comm(mode,r):
	#讀community
	if mode == 'slm':
		comm_path = community_path+'slm'+r+'/'
	else:
		comm_path = community_path+'/lda'+r+'/'

	comm = OrderedDict()
	for dirPath, dirNames, fileNames in os.walk(comm_path):#遍歷資料夾下每個txt檔
		for file in fileNames:
			comm_id = file[:len(file)-4]
			comm[comm_id] = []
			with open(comm_path+file,'r') as f:
				for row in f:
					rid = row.strip()
					comm[comm_id].append(rid)
	return comm

#計算群之間的距離
def two_clu_dis(i,j,clui_list,cluj_list,rel_test_df,conn):
	#計算兩群所有rid可組成的pair數
	pair_num = (len(clui_list)*len(cluj_list))/float(2)
	
	emi_sum = 0
	#找出和第一群的rid有co-mention的所有rid
	for ridi in tqdm(clui_list,desc='for two_clu_dis ridiiii...'):
		ridi_df_t = rel_test_df[rel_test_df['TARGET'] == int(ridi)]
		ridi_df_s = rel_test_df[rel_test_df['SOURCE'] == int(ridi)]
		
		for ridj in tqdm(cluj_list,desc='for two_clu_dis ridjjj...'):
			emi = 0
			if int(ridj) in ridi_df_t['SOURCE'].tolist():
				emi = ridi_df_t[ridi_df_t['SOURCE'] == int(ridj)]['EMI'].tolist()[0]
			elif int(ridj) in ridi_df_s['TARGET'].tolist():
				emi = ridi_df_s[ridi_df_s['TARGET'] == int(ridj)]['EMI'].tolist()[0]
			else:
				None

			emi_sum += emi
	emi_avg = float(emi_sum)/ pair_num

	cur.execute("INSERT INTO TWO_GROUP VALUES (?,?,?) ",(i,j,emi_avg))


#計算群內的距離
def in_clu_dis(k,rid_list,rel_test_df,conn):
	m = len(rid_list)
	
	for i in tqdm(range(m),desc='for in_clu_dis iii...'): 
		rid_df_t = rel_test_df[rel_test_df['TARGET'] == int(rid_list[i])]
		rid_df_s = rel_test_df[rel_test_df['SOURCE'] == int(rid_list[i])]
		
		for j in tqdm(range(m),desc='for in_clu_dis jjj...'):
			emi = 0

			if i < j:
				if int(rid_list[j]) in rid_df_t['SOURCE'].tolist():
					emi = rid_df_t[rid_df_t['SOURCE'] == int(rid_list[j])]['EMI'].tolist()[0]
				elif int(rid_list[j]) in rid_df_s['TARGET'].tolist():
					emi = rid_df_s[rid_df_s['TARGET'] == int(rid_list[j])]['EMI'].tolist()[0]
				else:
					None
				cur.execute("INSERT INTO IN_GROUP VALUES (?,?,?,?)",(k,rid_list[i],rid_list[j],emi))

###################################################################################
t1 = time.time()

#讀csv檔，轉為df
men_df = pkl.load(open('men_df.pkl', 'rb'))

#取出有用到的rid
men_id = men_df['RID'].tolist()
uni_id = sorted(list(set(men_id)))
rid_num_t = len(uni_id)

rel_df = pkl.load(open('rel_df.pkl','rb'))

comm = read_comm(mode,r)

clu_list = list(comm.keys())
m = len(clu_list)

for j in tqdm(range(m),desc='count in_clu_dis...'):
	ridj_list = comm[clu_list[j]]
	in_clu_dis(j,ridj_list,rel_df,conn)
	
	for k in tqdm(range(m),desc='count two_clu_dis...'):
		if j < k:
			ridk_list = comm[clu_list[k]]
			two_clu_dis(j,k,ridj_list,ridk_list,rel_df,conn)


conn.commit()
conn.close()
			
t2 = time.time()

print("時間 ＝ ",t2-t1)


