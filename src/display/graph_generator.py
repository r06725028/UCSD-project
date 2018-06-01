import sqlite3
import collections
from time import time
import datetime
import math
import numpy as np
from formatter import toJSNodes, toJSLinks, toScrTitle, toTargetIdHtmlFormat, toMentionIdHtmlFormat, toPMIDFormat, EMIValueAdjust

# conn = sqlite3.connect('data/CoMentions.db')
conn = sqlite3.connect('data/ucsd_slm250.db')
conn.text_factory = str

class TestFailed(Exception):
  def __init__(self, m):
    self.message = m
  def __str__(self):
    return self.message

class generator:
  def __init__(self, CoMentionThreshold=10.0, numberOfNodes=20, PATH='graph/'):
    self.PATH = PATH
    self.CoMentionThreshold = CoMentionThreshold
    self.numberOfNodes = numberOfNodes
    self.top20RelationRid = []

  def getLinkedRelation(self):
    emiDict = dict()
    coMentionDict = dict()
    cursor = conn.execute('''SELECT SOURCE, TARGET, VALUE, EMI FROM RELATIONSHIP WHERE SOURCE = ? OR TARGET = ? ORDER BY VALUE DESC LIMIT 30''', (int(self.pmid), int(self.pmid),))

    for src, desc, v, emi in cursor:
      rid = src if desc == self.pmid else desc
      emiDict[rid] = emi
      coMentionDict[rid] = v

    return emiDict, coMentionDict

  def getTop20RID(self, coMentionDict):
    totalSortedVal = sorted(coMentionDict.items(), key=lambda kv: kv[1], reverse=True)

    res = []
    for rid, val in totalSortedVal:
      res.append(rid)
    res = res[:self.numberOfNodes]


    return res

  def constructNodeInfo(self):
    nodeInfo = {}
    rids = [str(rid) for rid in self.top20RelationRid]
    sql = "SELECT * FROM NODE WHERE ID IN ({});".format(','.join(rids))
    cursor = conn.execute(sql)
    for rid, total_mention, one_mention, nine_five_mention, eight_mention, two_mention, name, abbr, url, group in cursor:
      nodeInfo[rid] = {
        'total_mention': total_mention,
        'one_mention': one_mention,
        'nine_five_mention': nine_five_mention,
        'eight_mention': eight_mention,
        'two_mention': two_mention,
        'name': name,
        'abbr': abbr,
        'url': url,
        'group': group
      }

    if(len(rids) != len(nodeInfo.keys())):
      diff = set([int(x) for x in rids]) - set(nodeInfo.keys())
      for rid in diff:
        raise(TestFailed('{} no data in nodeInfo(links)'.format(rid)))

    return nodeInfo

  def appendMutualRelation(self, nodeInfo):
    rids = [str(rid) for rid in self.top20RelationRid]
    cursor = conn.execute("SELECT SOURCE, TARGET, VALUE, EMI FROM RELATIONSHIP WHERE SOURCE IN ({})".format(','.join(rids)))
    res = set( (src, desc, emi) for src, desc, coMentionCount, emi in cursor \
      if (src in nodeInfo) and (desc in nodeInfo) and (coMentionCount > self.CoMentionThreshold or src == self.pmid or desc == self.pmid))

    return res

  def getDiversity(self, rid):
    def calDiversity(community):
      # total of com
      total = len(community);
      # print ( # of mentions of resource + tab );munity(i), for all i
      entropy = 0
      for count in community.values():
        if count != 0:
          entropy -= (count / total) * math.log(count / total);
      return entropy;
    
    sql = 'SELECT TARGET, VALUE AS res FROM RELATIONSHIP WHERE SOURCE={}\
          UNION\
         SELECT SOURCE, VALUE AS res FROM RELATIONSHIP WHERE TARGET={}\
         ORDER BY VALUE DESC LIMIT 40'.format(rid, rid)
    cursor = conn.execute(sql)
    comention_rids = [str(pair[0]) for pair in cursor]

    sql = 'SELECT COMMUNITIES, COUNT(*) FROM NODE WHERE ID IN ({}) AND COMMUNITIES != \'nan\' GROUP BY COMMUNITIES'.format(','.join(comention_rids))
    cursor = conn.execute(sql)
    countRes = { str(x[0]): x[1] for x in cursor }

    community = { str(i): 0 for i in range(82) }
    for key in countRes.keys():
      community[key] += countRes[key]
    entropy = calDiversity(community)

    return entropy

  def WriteGraphHTML(self, nodeInfo, relationSet):
    graph_part1 = open('data/html_text/graph_part1.txt', 'r').read()
    graph_part2 = open('data/html_text/graph_part2.txt', 'r').read()
    links = "\"links\":[\n"
    nodes = "\"nodes\":[\n"


    rids = list(nodeInfo.keys())

    for rid in rids:
      nodes += toJSNodes(rid=rid, value=nodeInfo[rid]['total_mention'], name=nodeInfo[rid]['name'], group=nodeInfo[rid]['group'])
    
    for src, desc, emi in relationSet:
      links += toJSLinks(source=rids.index(src), target=rids.index(desc), value=EMIValueAdjust(emi))
      
    nodes = nodes[:-2] + "\n],\n"
    links = links[:-2] + "\n]}\n"

    declare_var = 'var master_id = {};'.format(self.pmid)
    graph_outfile = open(self.PATH + str(self.pmid) + '_graph.html', 'w+')
    graph_outfile.write(graph_part1 + nodes + links + declare_var + graph_part2)

  def WritePMIDHTML(self, nodeInfo):
    # ===========================================#
    # generate id_pmids.html
    # ===========================================#
    pmids_part1 = open('data/html_text/pmids_part1.txt', 'r').read()
    pmids_part2 = open('data/html_text/pmids_part2.txt', 'r').read()
    pmids_part3 = open('data/html_text/pmids_part3.txt', 'r').read()

    pmids_outfile = open(self.PATH + str(self.pmid) + '_pmids.html', 'w+')
    pmids_output = '<!DOCTYPE html>\n<html>\n<head>\n<title>PubMed IDs '
    pmids_output += toScrTitle(self.pmid)
    pmids_output += pmids_part1
    pmids_output += toScrTitle(self.pmid)
    pmids_output += ' ' + nodeInfo[self.pmid]['name']
    pmids_output += pmids_part2

    cursor = conn.execute('''SELECT * FROM MENTION WHERE RID = ?;''', (str(self.pmid),))

    for pmidInfo in cursor:
      _, rid, mention_id, input_source, confidence, snippet, year = pmidInfo
      pmids_output += toPMIDFormat(rid, mention_id, input_source, confidence, snippet)

    pmids_output += pmids_part3

    pmids_outfile.write(pmids_output)
    pmids_outfile.close()

  def WriteTableHTML(self, nodeInfo, pmidTotalCoMention, diversity, emiDict, coMentionDict):
    # ===========================================#
    # generate id_table.html
    # ===========================================#
    infile_table_part1 = open('data/html_text/table_part1.txt', 'r')
    infile_table_part2 = open('data/html_text/table_part2.txt', 'r')
    infile_table_part3 = open('data/html_text/table_part3.txt', 'r')
    table_part1 = infile_table_part1.read()
    table_part2 = infile_table_part2.read()
    table_part3 = infile_table_part3.read()
    table_outfile = open(self.PATH + str(self.pmid) + '_table.html', 'w+')

    table_output = '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">\n<html>\t<head>\n<title>'
    table_output = table_output + toScrTitle(self.pmid) + ' Table</title>'

    try:
      mention = nodeInfo[self.pmid]['total_mention']
      one_mention = nodeInfo[self.pmid]['one_mention']
      point_nine_five_mention = nodeInfo[self.pmid]['nine_five_mention']
      point_eight_mention = nodeInfo[self.pmid]['eight_mention']
      point_two_mention = nodeInfo[self.pmid]['two_mention']
      name = nodeInfo[self.pmid]['name']
      abbr = nodeInfo[self.pmid]['abbr']
      url = nodeInfo[self.pmid]['url']
    except:
      raise (TestFailed('{} no data in nodeInfo(pmid)'.format(self.pmid)))

    table_output += table_part1
    table_output += name
    table_output += '</font></h3>\n<h2>'
    table_output += 'RRID:' + toScrTitle(self.pmid)
    table_output += table_part2
    table_output += toTargetIdHtmlFormat(self.pmid, url, name, pmidTotalCoMention, diversity ,mention)

    img_icon = '<a href="#legend"><img src="question-mark-icon.png" alt="?" style="width:24px;height:24px;"></a>'

    table_output = table_output + '<div><table>\n\t<tr>\n\t\t<th>RRID</th>'
    table_output = table_output + '\n\t\t<th>Resource name</th>\n\t\t<th>Top 20 partners'+img_icon+'</th>\n\t\t<th>Co-mention strength'+img_icon+'</th>'
    table_output = table_output + '\n\t\t<th>Co-mention count'+img_icon+'</th>\n\t\t<th>Total mentions'+img_icon+'</th>\n\t</tr>\n'

    tableRows = []
    # nodeInfo = { rid: { resource information } }
    for rid in nodeInfo:
      if (rid == self.pmid): continue
      mention = nodeInfo[rid]['total_mention']
      name = nodeInfo[rid]['name']
      url = nodeInfo[rid]['url']
      emi = emiDict[rid]
      numOfCoMention = coMentionDict[rid]

      tableRows.append((rid, url, name, emi, numOfCoMention, mention))

    # sorted by emi value
    for row in sorted(tableRows, key=lambda row: row[3], reverse=True):
      (id, url, name, coMention, EMI, mention) = row
      cursor = conn.execute('''SELECT MENTION_ID FROM MENTION WHERE RID = ? OR RID = ? GROUP BY MENTION_ID HAVING COUNT(*) > 1;''', (str(id), str(self.pmid)))
      mids = [mid[0].replace('PMID:', '') for mid in cursor]
      table_output += toMentionIdHtmlFormat(id, url, name, coMention, EMI, mention, mids)

    table_output += table_part3
    table_outfile.write(table_output)
    table_outfile.close()

  def WriteMainHTML(self):
    # ===========================================#
    # generate id_main.html
    # ===========================================#

    main_outfile = open(self.PATH + str(self.pmid) + '_main.html', 'w+')
    main_output = '<!DOCTYPE html>\n<html>\n<head>\n<title>'
    main_output += toScrTitle(self.pmid)
    main_output += '</title>\n</head>\n<frameset cols=\"65%,35%\">\n\t\t<frame src=\"'
    main_output = main_output + str(self.pmid) + '_graph.html\">\n\t\t<frame src=\"'
    main_output = main_output + str(self.pmid) + '_table.html\">\n'
    main_output = main_output + '</frameset>\n</html>'

    main_outfile.write(main_output)
    main_outfile.close()


  def generateGraphById(self, pmid):
    self.pmid = pmid

    startT = time()
    emiDict, coMentionDict = self.getLinkedRelation()

    if len(coMentionDict) < 20:
      with open('less20.txt', 'a') as f:
        f.write('{} less than 20 relations(pmid\'s coMention): {}\n'.format(pmid, len(coMentionDict)))
    self.top20RelationRid = self.getTop20RID(coMentionDict) # 20個
    pmidTotalCoMention = np.sum([coMentionDict[rid] for rid in self.top20RelationRid])
    self.top20RelationRid.insert(0, str(self.pmid))# 21個
    nodeInfo = self.constructNodeInfo() # 19個!!! 有些出現在relationship，但沒有出現在Node中
    relationSet = self.appendMutualRelation(nodeInfo) # nodeInfo是為了篩掉那些出現在relationship，但沒有出現在Node中
    self.WriteGraphHTML(nodeInfo=nodeInfo, relationSet=relationSet)
    self.WriteTableHTML(nodeInfo=nodeInfo, pmidTotalCoMention=pmidTotalCoMention, diversity=self.getDiversity(self.pmid), emiDict=emiDict, coMentionDict=coMentionDict)

    print(datetime.datetime.fromtimestamp(time() - startT).strftime('%M:%S'))

    self.WritePMIDHTML(nodeInfo=nodeInfo)
    self.WriteMainHTML()
if __name__ == '__main__':
  generator().generateGraphById(66)
