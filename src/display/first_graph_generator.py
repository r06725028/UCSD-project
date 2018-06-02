import math
import collections
from formatter import EMIValueAdjust, toJSLinks, nodeValueAdjust


def toJSNodes(gid, value, group, mention_rids):
  if (group == 'nan'): group = 30 # nan shows same color with 30 (other: grey)

  # 將前3頻繁出現的resource的name顯示在各group上
  name = '{0}.csv@#${1}'.format(gid, '\/'.join(mention_rids))

  return "\t{\"name\": \"" + str(name) + "\", \"group\": " + str(group) + ", \"value\": " + str(nodeValueAdjust(value)) + "},\n"

def generateAllCommunityGraph(conn_dunn, conn_ucsd_slm):
  nodeInfo = {}

  # 根據每個group，蒐集所有內部連結的resource
  sql = "SELECT GID, r1, r2 FROM IN_GROUP WHERE EMI > 0.0"
  cursor = conn_dunn.execute(sql)
  

  for gid, r1, r2 in cursor:
    # 若目前沒有此group的資料則初始化
    if gid not in nodeInfo.keys():
      nodeInfo[gid] = {}
      # 新增group id
      nodeInfo[gid]['group'] = gid
      # 將兩個有連結的resource新增進來
      nodeInfo[gid]['resourses'] = [r1, r2]
    else:
      # 將兩個有連結的resource新增進來
      nodeInfo[gid]['resourses'].append(r1)
      nodeInfo[gid]['resourses'].append(r2)


  for gid in nodeInfo.keys():
    s = set(nodeInfo[gid]['resourses'])
    # 此group有幾種resource
    nodeInfo[gid]['count'] = len(s)
    # 取此group前3頻繁出現的resource
    rids = [str(tup[0]) for tup in collections.Counter(nodeInfo[gid]['resourses']).most_common(3)]
    # 取得這些resource的name
    sql = "SELECT NAME FROM NODE WHERE ID in ({})".format(','.join(rids))
    cursor = conn_ucsd_slm.execute(sql)
    nodeInfo[gid]['mention'] = [x[0] for x in cursor]

    # 刪除用不到的key，釋放記憶體空間
    del nodeInfo[gid]['resourses']

  # 篩選內部resource>10個的group
  nodeInfo = { gid: nodeInfo[gid] for gid in nodeInfo.keys() if nodeInfo[gid]['count'] > 10 }
  
  # 根據這些篩選過的group尋找他們之間的連結強度
  sql = "SELECT * FROM TWO_GROUP"
  cursor = conn_dunn.execute(sql)
  relationSet = set( (g1, g2, emi) for g1, g2, emi in cursor \
    if (g1 in nodeInfo) and (g2 in nodeInfo))


  # 新增專屬'類別交互圖.html'的javascript檔及html文字
  graph_part1 = open('data/html_text/graph_part1.txt', 'r').read()
  graph_part2 = "</script>\
  \n\
  \n<script src=\"communityGraph.js\" charset=\"UTF-8\"></script>\
  \n</body>\
  \n</html>"
  open('data/html_text/graph_part2.txt', 'r').read()

  # 宣告d3.js的nodes和links
  links = "\"links\":[\n"
  nodes = "\"nodes\":[\n"


  gids = list(nodeInfo.keys())
  for gid in gids:
    # 篩選內部resource>10個的group
    if nodeInfo[gid]['count'] > 10:
      # 新增node進nodes
      nodes += toJSNodes(gid=gid, value=nodeInfo[gid]['count'], group=nodeInfo[gid]['group'], mention_rids=nodeInfo[gid]['mention'])
  
  for src, desc, emi in relationSet:
    # 新增link進links
    links += toJSLinks(source=gids.index(src), target=gids.index(desc), value=EMIValueAdjust(value=emi, multi_num=10))
  
  # 補全javescript格式
  nodes = nodes[:-2] + "\n],\n"
  links = links[:-2] + "\n]}\n"

  # 這裏的宣告只是為了避免HTML有引用到master_id的報錯
  declare_var = 'var master_id = {};'.format(19237894794712938127839)


  # 輸出html
  graph_outfile = open('graph/all_community_graph.html', 'w+')
  graph_outfile.write(graph_part1 + nodes + links + declare_var + graph_part2)

