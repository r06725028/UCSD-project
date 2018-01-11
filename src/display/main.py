import sqlite3
from graph_generator import generator
from joblib import Parallel, delayed
import multiprocessing
from tqdm import tqdm
from time import time
import datetime

if __name__ == '__main__':

    conn = sqlite3.connect('data/CoMentions.db')
    conn.text_factory = str

    cursor = conn.execute('''SELECT DISTINCT RID FROM MENTION''')
    target_list = list([row[0] for row in cursor])

    # generator(numberOfNodes=20).generateGraphById(14)

    
    # 13886 [#15702]
    startT = time()
    # err = [7247, 14216]
    err = []
    for pid in tqdm([x for x in target_list if x not in err]):
        try:
            generator(numberOfNodes=20).generateGraphById(pid)
        except Exception as e:
            print(str(e))
            with open('logs.txt', 'a') as f:
                f.write('{}\n'.format(str(e)))
# num_cores = multiprocessing.cpu_count()
# Parallel(n_jobs=num_cores)(delayed(\
#     generator(numberOfNodes=20).generateGraphById)(pid)
#         for pid in target_list) # 0 ~ 688

    endT = time()

    print('Total time cost: {}'.format(datetime.datetime.fromtimestamp(endT - startT).strftime('%M:%S')))
            

    # All graphs

    # id_list = []
    # cursor = conn.execute('''SELECT ID FROM NODE''')
    # for row in cursor:
    #     id_list.append(row[0])

    # for id in id_list:
    #     try:
    #         graph_generator.generateGraphById(int(id), path, linkValueLimit, numberOfNodes, totalMention)
    #     except:
    #         print 'id error:' + str(id)
