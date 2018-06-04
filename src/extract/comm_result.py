#encoding='utf-8'
import sqlite3
import numpy as np
import pandas as pd
import csv
import os
from tqdm import tqdm
import sys, argparse, os

#設定資料路徑
parser = argparse.ArgumentParser(description='community_result')
parser.add_argument('--mode',choices=['slm','lda'],default='slm')
parser.add_argument('--r',default='250')

parser.add_argument('--db_path', default = 'src/display/slm250.db')
parser.add_argument('--data_path', default = 'src/extract/raw_tsv/')
parser.add_argument('--save_path', default = 'src/extract/process_data/')
parser.add_argument('--community_path', default = 'src/extract/180306/')
parser.add_argument('--result_path', default = 'src/extract/community_result/')

#讀分群數
clu_num = {}
with open(args.save_path+'clu_num_r.txt','r') as f:
	for line in f:
		line_list = line.strip().split()
		r_ = line_list[0].strip()
		num = int(line_list[1].strip())
		clu_num[r_] = num

#連結資料庫
conn = sqlite3.connect(args.db_path)
cur = conn.cursor()

try:
	#更新10557的name(Taiwan Biobank (Chinese)-->Taiwan biobank)
	cur.execute('''UPDATE NODE SET NAME = 'Taiwan biobank' WHERE ID = 10557  ;''')

	print('更新！！',cur.execute('''SELECT * FROM NODE WHERE ID = 10557  ;''').fetchall())
except:
	None

#新增資料夾
dirpath = args.result_path
if not os.path.isdir(dirpath):
	os.mkdir(dirpath)

if args.mode == 'slm':
	dirpath = dirpath+'slm'+args.r+'/'
else:
	dirpath = dirpath+'lda'+args.r+'/'

if not os.path.isdir(dirpath):
	os.mkdir(dirpath)

if args.mode == 'slm':
	for i in tqdm(range(clu_num[r]),desc='community result...'):
		#sql指令
		list_of_tuple = cur.execute('''SELECT ID, NAME, MENTION FROM NODE WHERE COMMUNITIES = ? ;''', (i,)).fetchall()
		#轉成dataframe
		clu_df = pd.DataFrame(list_of_tuple, columns=['RRID', 'Resource Name','total_mention_count'])
		#排序
		clu_df = clu_df.sort_values(by='total_mention_count',ascending=False)
		#轉成csv
		clu_df.to_csv(dirpath+str(i)+".csv", sep=',', index=False, header=True)
else:
	for i in tqdm(range(clu_num[r]),desc='community result...'):
		#sql指令
		list_of_tuple = cur.execute('''SELECT ID, NAME, MENTION FROM NODE WHERE COMMUNITIES = ? ;''', (i,)).fetchall()
		#轉成dataframe
		clu_df = pd.DataFrame(list_of_tuple, columns=['RRID', 'Resource Name','total_mention_count'])
		#排序
		clu_df = clu_df.sort_values(by='total_mention_count',ascending=False)
		#轉成csv
		clu_df.to_csv(dirpath+str(i)+".csv", sep=',', index=False, header=True)

cur.close()
conn.close()



