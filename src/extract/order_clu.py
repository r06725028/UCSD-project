import csv
import numpy as np
import pandas as pd
import sys, argparse, os

#設定資料路徑
parser = argparse.ArgumentParser(description='order_clu')
parser.add_argument('--r',default='250')
parser.add_argument('--data_path', default = 'src/extract/raw_tsv/')
parser.add_argument('--save_path', default = 'src/extract/process_data/')
parser.add_argument('--community_path', default = 'src/extract/180306/')
parser.add_argument('--result_path', default = 'src/extract/community_result/')



path = args.result_path+'./lda'+args.r+'_order/'
if not os.path.isdir(path):
	os.mkdir(path)

#找出r分出的群數
num_path = args.save_path+'clu_num_r.txt'
clu_num_r = {}

with open(num_path,'r') as f:
  for line in f:
    clu_num_r[line.split()[0].strip()] = int(line.split()[1].strip())

df_list = []
m_list = []

#計算每群的rid數量
for i in range(clu_num_r[args.r]):
	f = open(args.result_path+'lda'+args.r+'/'+str(i)+'.csv','r')
	comm_df = pd.read_csv(f,sep=',')

	m = len(comm_df)

	df_list.append(np.array(comm_df,dtype=object))
	m_list.append(m)

#存起每群的rid數量和其中的rid
lda_df = pd.DataFrame(columns=['m','comm_df'])
lda_df['m'] = np.array(m_list)
lda_df['comm_df'] = np.array(df_list,dtype=object)

#依照rid數量排序
lda_df = lda_df.sort_values(by='m',ascending=False)

#依照排序結果，依序輸出
for idx,series in enumerate(lda_df.iterrows()):
	comm_df = pd.DataFrame(series[1]['comm_df'],columns=['RRID','Resource Name','total_mention_count'])


	comm_df.to_csv(path+str(idx)+'.csv',sep=',',index=False)

