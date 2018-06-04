from collections import OrderedDict #有序字典
import os
import re
import string
import math
#自然語言處理套件
import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

import time
import numpy as np
import pandas as pd
import csv
from tqdm import tqdm
from collections import OrderedDict #有序字典
from collections import Counter
import pickle as pkl

import lda

import sys, argparse, os
#設定資料路徑
parser = argparse.ArgumentParser(description='lda_clu')
parser.add_argument('--r',default='250')
parser.add_argument('--data_path', default = 'src/extract/raw_tsv/')
parser.add_argument('--save_path', default = 'src/extract/process_data/')
parser.add_argument('--community_path', default = 'src/extract/180306/')


args = parser.parse_args()
################################## 切詞處理##############################
def extractterm(text):#移除空字串、含有數字的字串:回傳list
    linelist = []
    tokenlist = []
    mystemmer = PorterStemmer()
    stop = set(stopwords.words('english'))#英文的stop word清單

    linelist = re.split('[\s|,|.]',text)
    
    m = len(linelist)
    for i in range (m):
        if linelist[i].strip().replace(" ",""):#檢查元素是否為空
           for c in string.punctuation :#去除字串中的標點符號
               linelist[i] = linelist[i].replace(c,"")
           linelist[i] = mystemmer.stem(linelist[i].strip().lower())#轉為小寫並作stem 
           if linelist[i] not in stop and linelist[i].isalpha():#移除stopword和有非字母出現的詞
              if linelist[i]:#檢查是否為空
                 tokenlist.insert(i,linelist[i])
    return tokenlist     

#########################################取出參與分群的rid們########################################
def input_matrix(all_rid_list):
    #取出rid的description，並做切詞
    rid_desc = {}
    all_trem_list = []
    meta_df = pkl.load(open(args.save_path+'meta_df.pkl','rb'))

    need_rid = []

    for index, row in tqdm(enumerate(meta_df.iterrows()),total=len(meta_df),desc='取出description&切詞'):
      rid = row[1]['e_uid']

      if rid in all_rid_list:
        desc = row[1]['description']
        need_rid.append(rid)

        try:
          token_list = extractterm(desc)
          rid_desc[rid] = token_list
          all_trem_list += token_list
        except:
          #有的rid沒有description，就設為空字串
          rid_desc[rid] = ''
        
    #所有出現過的字
    all_trem_list = list(set(all_trem_list))
    term_num = len(all_trem_list)
    print("總字數=",term_num)

    #建立起索引對應
    term_index = {}
    for index,term in tqdm(enumerate(all_trem_list),desc='建立起term的索引對應'):
      term_index[term] = index
    
    #計算tf
    all_rid_tf = []#等等要轉成array
    for rid in tqdm(rid_desc,total=len(rid_desc.keys()),desc='計算tf的list'):
      rid_tf = rid_tf = [0]*term_num
      
      if not(rid_desc[rid] == ''):
        tf_counter = Counter(rid_desc[rid])

        for token in tf_counter.keys():
          index = term_index[token]
          rid_tf[index] = tf_counter[token]

      all_rid_tf.append(np.array(rid_tf))

    #轉成array
    lda_input = np.array(all_rid_tf)
    print("all_rid_tf shape=",lda_input.shape)
    
    with open(args.save_path+'lda_input.pkl','wb') as f:
      pkl.dump(lda_input,f)
    with open(args.save_path+'need_rid.pkl','wb') as f:
      pkl.dump(need_rid,f)

    return lda_input,need_rid


#各r分出的群數
num_path = args.save_path+'clu_num_r.txt'
clu_num_r = {}

with open(num_path,'r') as f:
  for line in f:
    clu_num_r[line.split()[0].strip()] = int(line.split()[1].strip())

#取出需要的rid
#讀csv檔，轉成df的格式
rel_df = pkl.load(open(args.save_path+'rel_df.pkl','rb'))

#兩個list相加後移除重複並從小到大排序
sou_list = rel_df['SOURCE'].tolist()
tar_list = rel_df['TARGET'].tolist()
all_rid_list = sorted(list(set(sou_list+tar_list)))
print("len of all_rid_list = ",len(all_rid_list))

#用以判斷是否為第一次跑lda分群，如已跑過，直接使用之前處理好的檔案
"""
try:
  lda_input = pkl.load(open(args.save_path+'lda_input.pkl','rb'))
  need_rid = pkl.load(open(args.save_path+'need_rid.pkl','rb'))
except:
  lda_input,need_rid = input_matrix(all_rid_list)
"""
lda_input,need_rid = input_matrix(all_rid_list)

top_num = clu_num_r[args.r]
#跑lda
model = lda.LDA(n_topics=top_num, n_iter=500, random_state=1)
model.fit(lda_input)

#取出rid-topic
rid_topic = model.doc_topic_

#新增資料夾
dir_path = args.community_path
if not os.path.isdir(dir_path):
  os.mkdir(dir_path)
  
#新增資料夾
dir_path = args.community_path+'lda'+args.r+'/'
if not os.path.isdir(dir_path):
  os.mkdir(dir_path)

#開始分群
for i in range(len(need_rid)):
  rid_clu = rid_topic[i].argmax()
  with open (dir_path+str(rid_clu)+'.txt','a') as f:
    f.write(str(need_rid[i])+'\n')

