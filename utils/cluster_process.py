import sqlite3
import numpy as np
import pandas as pd
import csv
from collections import Counter

#########################################取出參與分群的rid們########################################
#連結資料庫
conn = sqlite3.connect('rel_3.db')
cur = conn.cursor()
#取出relationship的資料
rel_list_of_tuple = cur.execute("select SOURCE,TARGET from RELATIONSHIP ").fetchall()
rel_df = pd.DataFrame(rel_list_of_tuple, columns=['SOURCE', 'TARGET'])
#兩個list相加後移除重複並從小到大排序
sou_list = rel_df['SOURCE'].tolist()
tar_list = rel_df['TARGET'].tolist()
all_rid_list = sorted(list(set(sou_list+tar_list)))
print("len of all_rid_list = ",len(all_rid_list))
#關閉連結
cur.close()
conn.close()
##########################################找出各rid分群結果##########################################
#讀分群結果
#====================================================================================================
#注意: 我們的rid是跳著的，但即使只給2,3,9的資料，他分群還是會去分0~9的結果，而沒有資料的0,1,4~8就都會自己一群
#====================================================================================================
#取出所有node的分群結果，包含有在all_rid_list和不在all_rid_list中的
all_cluster_list = []
with open("output.txt",'r') as f:
	for line in f:
		all_cluster_list.append(line.strip())
print("len of all_cluster_list = ",len(all_cluster_list))

#只取出在all_rid_list中的分群結果
rid_to_clu_dict = {}
for rid in all_rid_list:
	rid_to_clu_dict[rid] = all_cluster_list[rid]#分群的結果是按給的rid去分的，所以直接用rid即可，不用+1

#找出自己一群的(有在rid中的條件下)
rid_cluster_list = rid_to_clu_dict.values()#包含重複
only_one_list = []
c = Counter(rid_cluster_list)#計算各群出現次數(即有幾個rid被分為此群)
for key in c:
	if c[key] == 1:
		only_one_list.append(key)

#取出所有rid對應到的分群的編號
rid_cluster_list = list(set(rid_cluster_list))#不包含重複  
print("len rid_cluster_list = ",len(rid_cluster_list))

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
		#clu_to_rid_dict = [r for r,c in rid_to_clu_dict.items() if c == clu] 
	else:
		for rid in rid_to_clu_dict:
			if rid_to_clu_dict[rid] == clu:
				only_one_dict[rid] = clu
				break
		#rid = [r for r,c in rid_to_clu_dict.items() if c == clu] 
		#only_one_dict[rid[0]] = clu
print("分成 ",len(clu_to_rid_dict)," 群")
print("自己一群的有 ",len(only_one_dict)," 群")

#輸出txt檔
for key in clu_to_rid_dict:
	path = "./171224/"+str(key)+".txt"
	with open(path,'w',encoding='utf-8') as f:
		for rid in clu_to_rid_dict[key]:
			f.write(str(rid)+"\n")

path = "only_one_cluster.csv"
with open(path,'w',encoding='utf-8') as f:
	f_writer = csv.writer(f)
	header = ['rid', 'cluster_no']
	f_writer.writerow(header)
	for rid in only_one_dict:
		data = [rid, only_one_dict[rid]]
		f_writer.writerow(data)

path = "cluster_num.txt" 
with open(path,'w',encoding='utf-8') as f:
	for key in sorted(c.keys()):#沒有按順序輸出!!!!!!!!!!!!!!!!!!!!!!!!!!!
		f.write("第"+str(key)+"群 : "+str(c[key])+"\n")
	










