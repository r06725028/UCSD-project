import sqlite3
import math
import collections

conn = sqlite3.connect('data/dunn.db')
conn.text_factory = str

# group_name = {
#   0: 'Disease',
#   1: 'Omics',
#   2: 'Pathway',
#   3: 'Neuroimg',
#   4: 'Ontology',
#   5: 'Institutes',
#   6: 'Mouse',
#   7: 'Mouse'
# }

def nodeValueAdjust(value):
  return str(math.sqrt(float(value)) / 5)

def EMIValueAdjust(value):
  return value * 10

def toJSNodes(gid, value, group, mention_rids):
  if (group == 'nan'): group = 30 # nan shows same color with 30(other: gray)

  name = '{0}.csv@#${1}'.format(gid, '\/'.join(mention_rids))
  return "\t{\"name\": \"" + str(name) + "\", \"group\": " + str(group) + ", \"value\": " + str(nodeValueAdjust(value)) + "},\n"

def toJSLinks(source, target, value):
  return "\t{\"source\": " + str(source) + ", \"target\": " + str(target) + ", \"value\": " + str(value) + "},\n"

def generateAllCommunityGraph():
  nodeInfo = {}

  sql = "SELECT GID, r1, r2 FROM IN_GROUP WHERE EMI > 0.0"
  cursor = conn.execute(sql)
  for gid, r1, r2 in cursor:
    if gid not in nodeInfo.keys():
      nodeInfo[gid] = {}
      nodeInfo[gid]['group'] = gid
      nodeInfo[gid]['resourses'] = [r1, r2]
    else:
      nodeInfo[gid]['resourses'].append(r1)
      nodeInfo[gid]['resourses'].append(r2)

  conn2 = sqlite3.connect('data/ucsd_slm250.db')
  conn2.text_factory = str
  

  for gid in nodeInfo.keys():
    s = set(nodeInfo[gid]['resourses'])
    nodeInfo[gid]['count'] = len(s)
    rids = [str(tup[0]) for tup in collections.Counter(nodeInfo[gid]['resourses']).most_common(3)]
    sql = "SELECT NAME FROM NODE WHERE ID in ({})".format(','.join(rids))
    cursor = conn2.execute(sql)
    nodeInfo[gid]['mention'] = [x[0] for x in cursor]

    del nodeInfo[gid]['resourses']

  nodeInfo = { gid: nodeInfo[gid] for gid in nodeInfo.keys() if nodeInfo[gid]['count'] > 10 }
  sql = "SELECT * FROM TWO_GROUP"
  cursor = conn.execute(sql)
  relationSet = set( (g1, g2, emi) for g1, g2, emi in cursor \
    if (g1 in nodeInfo) and (g2 in nodeInfo))




  graph_part1 = open('data/html_text/graph_part1.txt', 'r').read()
  graph_part2 = "</script>\
  \n\
  \n<script src=\"communityGraph.js\" charset=\"UTF-8\"></script>\
  \n</body>\
  \n</html>"
  open('data/html_text/graph_part2.txt', 'r').read()
  links = "\"links\":[\n"
  nodes = "\"nodes\":[\n"

  gids = list(nodeInfo.keys())

  for gid in gids:
    if nodeInfo[gid]['count'] > 10:
      nodes += toJSNodes(gid=gid, value=nodeInfo[gid]['count'], group=nodeInfo[gid]['group'], mention_rids=nodeInfo[gid]['mention'])
  
  for src, desc, emi in relationSet:
    links += toJSLinks(source=gids.index(src), target=gids.index(desc), value=EMIValueAdjust(emi))
    
  nodes = nodes[:-2] + "\n],\n"
  links = links[:-2] + "\n]}\n"

  declare_var = 'var master_id = {};'.format(19237894794712938127839)

  graph_outfile = open('graph/all_community_graph.html', 'w+')
  graph_outfile.write(graph_part1 + nodes + links + declare_var + graph_part2)

def generateSingleCommunityGraph():
  nodeInfo = {}
  sql = "SELECT GID, COUNT(1) FROM IN_GROUP GROUP BY GID"
  cursor = conn.execute(sql)
  for gid, count in cursor:
    name = group_name[gid] if gid in group_name.keys() else 'Others'
    nodeInfo[gid] = {
      'count': count,
      'name': name,
      'group': gid
    }

if __name__ == '__main__':
  generateAllCommunityGraph()
