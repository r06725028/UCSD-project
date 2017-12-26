import sqlite3
import graph_generator
from joblib import Parallel, delayed
import multiprocessing
from tqdm import tqdm
from time import time
import datetime

if __name__ == '__main__':

    conn = sqlite3.connect('data/CoMentions.db')
    conn.text_factory = str

    linkValueLimit = 10
    numberOfNodes = 20

    cursor = conn.execute('''SELECT COUNT(*) FROM MENTION''')
    for row in cursor:
        totalMention = int(row[0])

    path = 'graph/'


    cursor = conn.execute('''SELECT ID FROM NODE''')
    target_list = [row[0] for row in cursor]

    try:
        # 13886 [#15702]
        startT = time()

        num_cores = multiprocessing.cpu_count()
        Parallel(n_jobs=num_cores)(delayed(graph_generator.generateGraphById)\
            (pid, path, linkValueLimit, numberOfNodes, totalMention) for pid in target_list) # 0 ~ 688

        endT = time()

        print('Total time cost: {}'.format(datetime.datetime.fromtimestamp(endT - startT).strftime('%M:%S')))
            
    except:
        with open('logs.txt', 'a') as f:
            f.write('[Error] pid: {}\n'.format(idx, pid))

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
