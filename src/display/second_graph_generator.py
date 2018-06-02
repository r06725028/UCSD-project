import math
from tqdm import tqdm
from collections import OrderedDict
from formatter import toScrTitle, EMIValueAdjust, toJSLinks

# 輸出table中每個row的資料的html
def toMentionIdHtmlFormat(rid, name, mention):
  html = '\t<tr>\n\t\t<td><a class=\"external\" target=\"_blank\"\n\thref=\"https://scicrunch.org/browse/resources/'
  
  html += toScrTitle(rid) + '\">' + toScrTitle(rid) + '</td>'
  html += '\n\t\t<td align="center"><a class=\"external\" target=\"_blank\"\n\thref=\"' + str(rid) + '_main.html'
  html += '\">' + str(name) + '</td>'
  html += '\n\t\t<td align="center">' + str(mention) + '</td></tr>'

  return html

# '類別圖_main.html'的html格式(已固定)
def getMainHTML(gid):
  main_output = '<!DOCTYPE html>\n<html>\n<head>\n<title>'
  main_output += 'group_' + str(gid)
  main_output += '</title>\n</head>\n<frameset cols=\"65%,35%\">\n\t\t<frame src=\"'
  main_output = main_output + 'group_' + str(gid) + '_graph.html\">\n\t\t<frame src=\"'
  main_output = main_output + 'group_' + str(gid) + '_table.html\">\n'
  main_output = main_output + '</frameset>\n</html>'

  return main_output

# 調整d3.js的node大小
def nodeValueAdjust(value):
  return str(float(value) ** .3 / 3)

# 輸出符合d3.js node格式的javascript code
def toJSNodes(rid, value, name, group, separator=' '):
  if (group == 'nan'): group = 30 # NaN shows same color with 30 (other: gray)
  return "\t{\"name\": \"" + str(toScrTitle(rid)) + separator + str(name) + "\", \"group\": " + str(group) + ", \"value\": " + str(nodeValueAdjust(value)) + "},\n"

def generateCommunityInsideGraph(conn_dunn, conn_ucsd_slm, gid):
  nodeInfo = {}
  raw_rids = []

  # 選取在這個group內部有互相連結的resource
  sql = "SELECT r1, r2 AS res FROM IN_GROUP WHERE GID={} AND EMI > 0.0".format(gid)
  cursor = conn_dunn.execute(sql)

  # 得到此group的unique resource
  for r1, r2 in cursor:
    raw_rids += [r1, r2]  
  rids = list(set(raw_rids))

  # 得到這些unique resource各自被mention的次數
  tmp = ','.join([str(rid) for rid in rids])
  mention_counts = list(conn_ucsd_slm.execute('SELECT RID, COUNT(1) FROM MENTION WHERE RID IN ({}) GROUP BY RID'.format(tmp)))

  # 新增這些unique resource的資料：mention次數、name、group id
  for rid, count in mention_counts:
    # 取得resource的name
    sql = "SELECT NAME FROM NODE WHERE ID = ({})".format(rid)
    cursor = conn_ucsd_slm.execute(sql) 

    name_ls = list(cursor)
    name = name_ls[0][0] if(len(name_ls) > 0) else 'UNKNOWN'

    nodeInfo[rid] = {
      'count': count,
      'name': name,
      'group': gid
    }

  # 新增專屬'類別圖_table.html'的css樣式
  table_output = '<style>\
    table {\
        font-family: arial, sans-serif;\
        border-collapse: collapse;\
        width: 100%;\
    }\
    td, th {\
        border: 1px solid;\
        padding: 8px;\
    }\
    tr:nth-child(1) {\
        background-color: #cccccc;\
    }\
    tr:nth-child(even) {\
        background-color: #dddddd;\
    }\
    tr:hover{background-color:#f5f500}\
  </style>\
  </head>\
  <body>'
  # 新增專屬'類別圖_table.html'
  table_output += '<table>\n\t<tr>\n\t\t<th>RRID</th>'
  table_output += '\n\t\t<th>Resource name</th>\n\t\t<th>Mention count</th>\n\t</tr>\n'

  # 根據被mention次數來排序此group的resource
  sorted_rids = sorted(nodeInfo.keys(), key=lambda x: (nodeInfo[x]['count']), reverse=True)
  # 根據mention次數排序的resource來輸出表格
  for rid in sorted_rids:
    table_output += toMentionIdHtmlFormat(rid=rid, name=nodeInfo[rid]['name'], mention=nodeInfo[rid]['count'])
  
  # 新增專屬'類別圖_table.html'的javascript檔及html文字
  table_output += '</table></body></html>'
  with open('src/display/graph/group_{}_table.html'.format(gid), 'w') as f:
    f.write(table_output)

  # 新增'類別圖_main.html'，其中包含'類別圖_table.html'與'類別圖_graph.html'
  with open('src/display/graph/group_{}_main.html'.format(gid), 'w') as f:
    f.write(getMainHTML(gid))


  # 新增專屬'類別圖_graph.html'的javascript檔及html文字
  graph_part1 = open('src/display/data/html_text/graph_part1.txt', 'r').read()
  graph_part2 = "</script>\
  \n\
  \n<script src=\"secondGroupGraph.js\" charset=\"UTF-8\"></script>\
  \n</body>\
  \n</html>"
  open('src/display/data/html_text/graph_part2.txt', 'r').read()
  links = "\"links\":[\n"
  nodes = "\"nodes\":[\n"
  

  # 選取在這個group內部有互相連結的resource及其emi值
  sql = "SELECT r1, r2, EMI FROM IN_GROUP WHERE GID={} AND EMI > 0.0".format(gid)
  cursor = conn_dunn.execute(sql)

  # 根據mention次數排序的前40個resource來輸出graph
  filtered_rids = sorted_rids[:40]
  
  # 篩選根據mention次數排序的前40個resource的連結及其emi值
  raw_links = []
  for r1, r2, emi in cursor:
    if (r1 in filtered_rids) and (r2 in filtered_rids):
      raw_links.append((r1, r2, emi))

  # 降低連結數量：只取emi值由大至小排序的前40個連結
  filtered_links = sorted(raw_links, key=lambda x: x[2])[:40]
  # 根據這些去蕪存菁的連結，取得被連結的resource id
  filtered_rids = list(set(tup[0] for tup in filtered_links).union(set(tup[1] for tup in filtered_links)))

  for rid in filtered_rids:
    # 根據resource id選取name
    sql = "SELECT NAME FROM NODE WHERE ID = {}".format(rid)
    cursor = conn_ucsd_slm.execute(sql)
    # 將node加入nodes
    nodes += toJSNodes(rid=rid, name=next(cursor)[0],value=nodeInfo[rid]['count'], group=nodeInfo[rid]['group'], separator='@#$')
  # 將link加入links
  for src, desc, emi in filtered_links:
    links += toJSLinks(source=filtered_rids.index(src), target=filtered_rids.index(desc), value=EMIValueAdjust(value=emi, multi_num=50, pow_num=.75))
  
  # 補全javescript格式
  nodes = nodes[:-2] + "\n],\n"
  links = links[:-2] + "\n]}\n"

  # 這裏的宣告只是為了避免HTML有引用到master_id的報錯
  declare_var = 'var master_id = {};'.format(12907490812908412094)

  # 輸出html
  graph_outfile = open('src/display/graph/group_{}_graph.html'.format(gid), 'w+')
  graph_outfile.write(graph_part1 + nodes + links + declare_var + graph_part2)
