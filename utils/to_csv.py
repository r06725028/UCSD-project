import sqlite3
import numpy as np
import pandas as pd
import csv
import math
from process_duplicate import mention_tsv_filter, relationship_tsv_filter, meta_tsv_filter
from tqdm import tqdm



conn = sqlite3.connect('rel_3.db')
cur = conn.cursor()

#================跑分群用的csv====================#
#relationship
rel_list_of_tuple = cur.execute("select SOURCE,TARGET,EMI from RELATIONSHIP ").fetchall()
rel_df = pd.DataFrame(rel_list_of_tuple, columns=['SOURCE', 'TARGET','EMI'])

tqdm.pandas(desc='EMI to INT')
rel_df['EMI'] = rel_df['EMI'].progress_apply(lambda x: int(x*math.pow(10,12)))#轉成int格式

rel_df.to_csv("input.csv", sep='\t', index=False, header=None)#必須沒有標頭，用\t分隔才可以


cur.close()
conn.close()
