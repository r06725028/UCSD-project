import sqlite3
import math
from tqdm import tqdm
from collections import OrderedDict

conn = sqlite3.connect('data/dunn.db')
conn.text_factory = str

group_name = {
  0: 'Disease',
  1: 'Omics',
  2: 'Pathway',
  3: 'Neuroimg',
  4: 'Ontology',
  5: 'Institutes',
  6: 'Mouse',
  7: 'Mouse'
}

def toScrTitle(id):
  name = 'SCR_'
  for i in range(0, 6 - len(str(id))):
    name += '0'
  return name + str(id)  

def toMentionIdHtmlFormat(rid, name, mention):
  html = '\t<tr>\n\t\t<td><a class=\"external\" target=\"_blank\"\n\thref=\"https://scicrunch.org/browse/resources/'
  
  html += toScrTitle(rid) + '\">' + toScrTitle(rid) + '</td>'
  html += '\n\t\t<td align="center"><a class=\"external\" target=\"_blank\"\n\thref=\"' + str(rid) + '_main.html'
  html += '\">' + str(name) + '</td>'
  html += '\n\t\t<td align="center">' + str(mention) + '</td></tr>'

  return html

def getMainHTML(gid):

  main_output = '<!DOCTYPE html>\n<html>\n<head>\n<title>'
  main_output += 'group_' + str(gid)
  main_output += '</title>\n</head>\n<frameset cols=\"65%,35%\">\n\t\t<frame src=\"'
  main_output = main_output + 'group_' + str(gid) + '_graph.html\">\n\t\t<frame src=\"'
  main_output = main_output + 'group_' + str(gid) + '_table.html\">\n'
  main_output = main_output + '</frameset>\n</html>'

  return main_output

def nodeValueAdjust(value):
  return str(float(value) ** .3 / 3)

def EMIValueAdjust(value):
  return (value * 50) ** .75

def toJSNodes(rid, name, value, group):
  if (group == 'nan'): group = 30 # nan shows same color with 30(other: gray)
  name = name.replace("\"", "\\\"")
  return "\t{\"name\": \"" + str(toScrTitle(rid)) + '@#$' + name + "\", \"group\": " + str(group) + ", \"value\": " + str(nodeValueAdjust(value)) + "},\n"

def toJSLinks(source, target, value):
  return "\t{\"source\": " + str(source) + ", \"target\": " + str(target) + ", \"value\": " + str(value) + "},\n"

def generateCommunityInsideGraph(gid):
  nodeInfo = {}
  raw_rids = []

  sql = "SELECT r1, r2 AS res FROM IN_GROUP WHERE GID={} AND EMI > 0.0".format(gid)
  cursor = conn.execute(sql)

  for r1, r2 in cursor:
    raw_rids += [r1, r2]
  
  rids = list(set(raw_rids))

  conn2 = sqlite3.connect('data/ucsd_slm250.db')
  conn2.text_factory = str

  kkk = ','.join([str(rid) for rid in rids])
  mention_counts = list(conn2.execute('SELECT RID, COUNT(1) FROM MENTION WHERE RID IN ({}) GROUP BY RID'.format(kkk)))
  for rid, count in mention_counts:
    sql = "SELECT NAME FROM NODE WHERE ID = ({})".format(rid)
    cursor = conn2.execute(sql) 

    name_ls = list(cursor)
    name = name_ls[0][0] if(len(name_ls) > 0) else 'UNKNOWN'

    nodeInfo[rid] = {
      'count': count,
      'name': name,
      'group': gid
    }

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
  table_output += '<table>\n\t<tr>\n\t\t<th>RRID</th>'
  table_output += '\n\t\t<th>Resource name</th>\n\t\t<th>Mention count</th>\n\t</tr>\n'

  sorted_rids = sorted(nodeInfo.keys(), key=lambda x: (nodeInfo[x]['count']), reverse=True)

  for rid in sorted_rids:
    table_output += toMentionIdHtmlFormat(rid=rid, name=nodeInfo[rid]['name'], mention=nodeInfo[rid]['count'])
  
  table_output += '</table></body></html>'
  with open('graph/group_{}_table.html'.format(gid), 'w') as f:
    f.write(table_output)

  with open('graph/group_{}_main.html'.format(gid), 'w') as f:
    f.write(getMainHTML(gid))


  graph_part1 = open('data/html_text/graph_part1.txt', 'r').read()
  graph_part2 = "</script>\
  \n\
  \n<script src=\"secondGroupGraph.js\" charset=\"UTF-8\"></script>\
  \n</body>\
  \n</html>"
  open('data/html_text/graph_part2.txt', 'r').read()
  links = "\"links\":[\n"
  nodes = "\"nodes\":[\n"
  

  conn2 = sqlite3.connect('data/ucsd_slm250.db')
  conn2.text_factory = str

  sql = "SELECT r1, r2, EMI FROM IN_GROUP WHERE GID={} AND EMI > 0.0".format(gid)
  cursor = conn.execute(sql)

  filtered_rids = sorted_rids[:40]
  raw_links = []
  for r1, r2, emi in cursor:
    if (r1 in filtered_rids) and (r2 in filtered_rids):
      raw_links.append((r1, r2, emi))

  filtered_links = sorted(raw_links, key=lambda x: x[2])[:40]
  filtered_rids = list(set(tup[0] for tup in filtered_links).union(set(tup[1] for tup in filtered_links)))

  for rid in filtered_rids:
    sql = "SELECT NAME FROM NODE WHERE ID = {}".format(rid)
    cursor = conn2.execute(sql)
    nodes += toJSNodes(rid=rid, name=next(cursor)[0],value=nodeInfo[rid]['count'], group=nodeInfo[rid]['group'])

  for src, desc, emi in filtered_links:
    links += toJSLinks(source=filtered_rids.index(src), target=filtered_rids.index(desc), value=EMIValueAdjust(emi))
    
  nodes = nodes[:-2] + "\n],\n"
  links = links[:-2] + "\n]}\n"

  declare_var = 'var master_id = {};'.format(12907490812908412094)

  graph_outfile = open('graph/group_{}_graph.html'.format(gid), 'w+')
  graph_outfile.write(graph_part1 + nodes + links + declare_var + graph_part2)

if __name__ == '__main__':
  sql = "SELECT DISTINCT(GID) FROM IN_GROUP"
  cursor = conn.execute(sql)
  for gids in tqdm(list(cursor)):
    generateCommunityInsideGraph(gids[0])

