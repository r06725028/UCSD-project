#encoding='utf-8'
import time
import numpy as np
import pandas as pd
import csv
from tqdm import tqdm
from collections import OrderedDict #有序字典
from collections import Counter
import string 
import requests
import pickle as pkl
from process_duplicate import mention_tsv_filter, relationship_tsv_filter, meta_tsv_filter
import sys, argparse, os 

#設定資料路徑
parser = argparse.ArgumentParser(description='get_year')
parser.add_argument('--data_path', default = 'src/extract/raw_tsv/')
parser.add_argument('--save_path', default = 'src/extract/process_data/')

args = parser.parse_args()


#讀mention資料
csvfile = open(args.data_path+'resource-mentions.tsv', 'r',encoding='utf-8')
men_df = pd.read_csv(csvfile, delimiter='\t', low_memory=False)
men_df = mention_tsv_filter(pd.read_csv(csvfile, delimiter='\t', low_memory=False))

#========================================================================================
#用批次方式取得年份（一次最多1000筆，但太多筆會太大讓url太長造成error，900是試過每批次都安全的數字）
#input: dataframe(mention資料)
#output: pkl file(儲存dict，其中key是pmid，value是年份)
#========================================================================================

#儲存年份
year_list = []
pmid_to_year = {}

#批次處理
m = len(men_df)
b = 900#batch_size:太大會讓url太長!造成404 error!
q = int(m/b)#商
r = int(m%b)#餘

for i in tqdm(range(0,q),desc='get year'):
	#取出900筆，轉為字串
	batch_list = [str(int(x)) for x in men_df[0+b*i:b+b*i]['mentionid_int'].tolist()]
	pmid_str = ','.join(batch_list)

	#查詢年分
	response = requests.get("/".join(["https://icite.od.nih.gov/api","pubs?pmids="+pmid_str,]),)
	#print("response",response)#200:0k/414:url too long
	try:
		pub = response.json()
		#建立dict，方便之後查
		#注意：回傳順序和query順序不同，其中還會跳過找不到的pmid
		for _dict in pub['data']:
			if str(_dict['pmid']) not in pmid_to_year:
				pmid_to_year[str(_dict['pmid'])] = _dict['year']
	except:
		with open ("414_error,txt",'a') as f:#記下沒查詢到的
			f.write(str(0+b*i)+" "+str(b+b*i)+'\n')
	
	#整理查詢結果
	for x in batch_list:
		if x in pmid_to_year:
			year_list.append(pmid_to_year[x])
		else:
			year_list.append(np.nan)
			with open ('not_found.txt','a') as f:
				f.write(x+'\n')

#取出剩下的r筆，轉為字串
batch_list = [str(int(x)) for x in men_df[m-r:]['mentionid_int'].tolist()]
pmid_str = ','.join(batch_list)

#查詢年分
response = requests.get("/".join(["https://icite.od.nih.gov/api","pubs?pmids="+pmid_str,]),)
pub = response.json()

#建立dict，方便之後查
#注意：回傳順序和query順序不同，其中還會跳過找不到的pmid
for _dict in pub['data']:
	if str(_dict['pmid']) not in pmid_to_year:
		pmid_to_year[str(_dict['pmid'])] = _dict['year']

#整理查詢結果
for x in batch_list:
	if x in pmid_to_year:
		year_list.append(pmid_to_year[x])
	else:
		year_list.append(np.nan)
		with open ('not_found.txt','a') as f:
			f.write(x+'\n')
#把結果存起來
with open (args.save_path+'pmid_to_year.pkl','w') as f:
	pkl.dump(pmid_to_year,f)


	



