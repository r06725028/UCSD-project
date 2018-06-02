# 資料庫
import sqlite3
# 執行參數
import argparse
import first_graph_generator
import second_graph_generator
import third_graph_generator
from datetime import datetime
# 文字顏色
from termcolor import colored
# 進度bar
from tqdm import tqdm


def parse():
  parser = argparse.ArgumentParser(description="UCSD GRAPH GENERATOR")
  parser.add_argument('--slm_db', default='data/ucsd_slm250.db', help='please input ucsd_slm path')
  parser.add_argument('--dunn_db', default='data/dunn.db', help='please input dunn path')
  parser.add_argument('--train_pg', action='store_true', help='whether train policy gradient')
  try:
    from argument import add_arguments
    parser = add_arguments(parser)
  except:
    pass
  
  args = parser.parse_args()
  return args


if __name__ == '__main__':
  args = parse()

  # 連線到兩個資料庫: [1] slm_250.db [2] dunn.db
  conn_ucsd_slm = sqlite3.connect(args.slm_db)
  conn_ucsd_slm.text_factory = str

  conn_dunn = sqlite3.connect(args.dunn_db)
  conn_dunn.text_factory = str

  # 1. 產生類別間彼此間的關係圖
  print('///////////////////////////////////////////////////////////')
  print('[-] First graph output path: graph/all_community_graph.html')
  first_graph_generator.generateAllCommunityGraph(conn_dunn, conn_ucsd_slm)
  print('[v] First graph')
  print('///////////////////////////////////////////////////////////')


  # 2. 產生類別內部節點的關係圖
  print('[-] Second graph output path: graph/group_[{}]_[{}|{}|{}].html'.format(\
    colored('Group id', 'red'),\
    colored('main', 'white'),\
    colored('table', 'white'),\
    colored('graph', 'white'),))

  sql = "SELECT DISTINCT(GID) FROM IN_GROUP"
  cursor = conn_dunn.execute(sql)
  for gids in tqdm(list(cursor)):
    second_graph_generator.generateCommunityInsideGraph(conn_dunn, conn_ucsd_slm, gids[0])

  print('[v] Second graph')
  print('///////////////////////////////////////////////////////////')

  # 3. 產生每個NODE的關係圖
  print('[-] Third graph output ptah: graph/[{}]_[{}|{}|{}|{}].html'.format(\
    colored('Resource id', 'red'),\
    colored('main', 'white'),\
    colored('table', 'white'),\
    colored('graph', 'white'),\
    colored('pmids', 'white'),))
  print('\t* Exceptions will be written in \'{}\''.format(colored('Exceptions_logs.txt', 'white')))

  # 將每個resource的id取出
  cursor = conn_ucsd_slm.execute('''SELECT DISTINCT ID FROM NODE''')
  target_list = list([row[0] for row in cursor])

  err = []
  with open('Exceptions_logs.txt', 'a') as f:
    f.write('--------------------{}--------------------\n'.format(str(datetime.now())))
  for pid in tqdm([x for x in target_list if x not in err]):
    try:
      # numberOfNodes的參數是用來篩選top N個的與master resource一同出現的resource
      third_graph_generator.generator(conn_ucsd_slm=conn_ucsd_slm, numberOfNodes=20).generateGraphById(pid)
    except Exception as e:
      with open('Exceptions_logs.txt', 'a') as f:
        # 格式：[node id]: [處裡此node id時發生的錯誤]
        f.write('[{}]{}\n'.format(pid, str(e)))
  print('[v] Third graph')
  print('//////////////////////////////////////////')
