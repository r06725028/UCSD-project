import sqlite3
import numpy as np
import pandas as pd
import csv
from collections import Counter
import os
from tqdm import tqdm
import time
import pickle as pkl

import sys, argparse, os

from process_duplicate import mention_tsv_filter, relationship_tsv_filter, meta_tsv_filter


#設定資料路徑
parser = argparse.ArgumentParser(description='slm_clu')
parser.add_argument('--r', default='250')
parser.add_argument('--data_path', default = 'src/extract/raw_tsv/')
parser.add_argument('--save_path', default = 'src/extract/process_data/')
parser.add_argument('--community_path', default = 'src/extract/180306/')
parser.add_argument('--slm_path', default = 'src/extract/slm_output/')


args = parser.parse_args()

#########################################取出參與分群的rid們########################################
#讀csv檔，轉成df的格式
rel_df = pkl.load(open(args.save_path+'rel_df.pkl','rb'))

#兩個list相加後移除重複並從小到大排序
sou_list = rel_df['SOURCE'].tolist()
tar_list = rel_df['TARGET'].tolist()
all_rid_list = sorted(list(set(sou_list+tar_list)))
print("len of all_rid_list = ",len(all_rid_list))

##########################################找出各rid分群結果##########################################
#讀分群結果
all_cluster_list = []
op_path = args.slm_path+'slm_output'+args.r+'.txt'
with open(op_path,'r') as f:
	for line in f:
		all_cluster_list.append(line.strip())
print(" len of all_cluster_list = ",len(all_cluster_list))

#只取出在all_rid_list中的分群結果
rid_to_clu_dict = {}
for rid in all_rid_list:
	rid_to_clu_dict[rid] = all_cluster_list[rid]

#找出自己一群的(有在rid中的條件下)
rid_cluster_list = rid_to_clu_dict.values()#包含重複
only_one_list = []
c = Counter(rid_cluster_list)#計算各群出現次數(即有幾個rid被分為此群)
for key in c:
	if c[key] == 1:
		only_one_list.append(key)

#取出所有rid對應到的分群的編號
rid_cluster_list = list(set(rid_cluster_list))#不包含重複  
print(" len rid_cluster_list = ",len(rid_cluster_list))

##########################################找出各群的rid###########################################
clu_to_rid_dict = {}
only_one_dict = {}

#依序找出各群包含的rid
for clu in rid_cluster_list:
	if clu not in only_one_list:
		rid_list = []
		for rid in rid_to_clu_dict:
			if rid_to_clu_dict[rid] == clu:
				rid_list.append(rid)
		clu_to_rid_dict[clu] = rid_list 
	else:
		for rid in rid_to_clu_dict:
			if rid_to_clu_dict[rid] == clu:
				only_one_dict[rid] = clu
				break
print("分成 ",len(clu_to_rid_dict)," 群")
print(" 自己一群的有 ",len(only_one_dict)," 群")

with open (args.save_path+"clu_num_r.txt",'a') as f:
	f.write(args.r+" "+str(len(clu_to_rid_dict)+len(only_one_dict))+'\n')

#新增資料夾
if not os.path.isdir(args.community_path):
	os.mkdir(args.community_path)

dir_path = args.community_path+'slm'+args.r+'/'
if not os.path.isdir(dir_path):
	os.mkdir(dir_path)

#輸出txt檔
for key in clu_to_rid_dict:
	clu_path = dir_path+str(key)+".txt"
	with open(clu_path,'w',encoding='utf-8') as f:
		for rid in clu_to_rid_dict[key]:
			f.write(str(rid)+"\n")

if len(only_one_dict)>0:
	m = len(clu_to_rid_dict)
	n = len(clu_to_rid_dict)+len(only_one_dict)
	for rid in only_one_dict:
		clu_path = dir_path+str(m)+".txt"
		with open(clu_path,'w',encoding='utf-8') as f:
			f.write(str(rid)+"\n")
		m+=1

	oo_path = dir_path+"only_one_cluster.csv"
	with open(oo_path,'w',encoding='utf-8') as f:
		f_writer = csv.writer(f)
		header = ['rid', 'cluster_no']
		f_writer.writerow(header)
		for rid in only_one_dict:
			data = [rid, only_one_dict[rid]]
			f_writer.writerow(data)
	





