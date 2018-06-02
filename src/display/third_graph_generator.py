import collections
from time import time
import datetime
import math
import numpy as np
from formatter import toJSNodes, toJSLinks, toScrTitle, toTargetIdHtmlFormat, toMentionIdHtmlFormat, toPMIDFormat, EMIValueAdjust


# 報錯物件
class TestFailed(Exception):
  def __init__(self, m):
    self.message = m
  def __str__(self):
    return self.message

class generator:
  def __init__(self, conn_ucsd_slm, CoMentionThreshold=10.0, numberOfNodes=20, PATH='graph/'):
    self.PATH = PATH
    self.CoMentionThreshold = CoMentionThreshold
    self.numberOfNodes = numberOfNodes
    self.top20RelationRid = []
    self.conn = conn_ucsd_slm

  # 取出所有master resource連結的節點以及emi的值
  def getLinkedRelation(self):
    emiDict = dict()
    coMentionDict = dict()

    # VALUE為兩個resource共同出現的次數
    cursor = self.conn.execute('''SELECT SOURCE, TARGET, VALUE, EMI FROM RELATIONSHIP\
      WHERE SOURCE = ? OR TARGET = ? ORDER BY VALUE DESC LIMIT 30''',\
      (int(self.master_rid), int(self.master_rid),))

    for src, desc, v, emi in cursor:
      rid = src if desc == self.master_rid else desc
      # emiDict物件，負責某個resource與master resource連結的emi數值
      emiDict[rid] = emi
      # coMentionDict物件，負責某個resource與master resource存共同出現的次數
      coMentionDict[rid] = v

    return emiDict, coMentionDict

  # 根據coMention物件，根據裡頭每一個resource與master resource共同出現的次數由高至低排序取出前20(numberOfNodes)個resource
  def getTop20RID(self, coMentionDict):
    totalSortedVal = sorted(coMentionDict.items(), key=lambda kv: kv[1], reverse=True)

    res = []
    for rid, val in totalSortedVal:
      res.append(rid)
    res = res[:self.numberOfNodes]

    return res

  def constructNodeInfo(self):
    nodeInfo = {}

    # 取出前20個與master resource共同出現次數最多的resource id
    rids = [str(rid) for rid in self.top20RelationRid]

    # 得到這些resource的資訊
    sql = "SELECT * FROM NODE WHERE ID IN ({});".format(','.join(rids))
    cursor = self.conn.execute(sql)

    # 把這些資訊加入nodeInfo物件
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

    # 如果與master resource連結的resource沒有出現在ucsd_slm資料庫，則報錯
    if(len(rids) != len(nodeInfo.keys())):
      diff = set([int(x) for x in rids]) - set(nodeInfo.keys())
      for rid in diff:
        raise(TestFailed('{} no data in nodeInfo(links)'.format(rid)))

    return nodeInfo
  
  # 建立包含所有resource連結的物件
  def appendMutualRelation(self, nodeInfo):
    # 取得前20個頻繁共同出現的partners resoruce id
    rids = [str(rid) for rid in self.top20RelationRid]
    # 根據上述resource id所得到的連結資訊
    cursor = self.conn.execute("SELECT SOURCE, TARGET, VALUE, EMI FROM RELATIONSHIP WHERE SOURCE IN ({})".format(','.join(rids)))
    # 篩選連結：
    # 1. 與master resource的共同出現次數高過threshold
    # 2. 這些resource存在於nodeInfo物件
    # 3. 連結的resource其中之一為master resource
    res = set( (src, desc, emi) for src, desc, coMentionCount, emi in cursor\
      if (src in nodeInfo) and (desc in nodeInfo) and\
      (coMentionCount > self.CoMentionThreshold or src == self.master_rid or desc == self.master_rid))

    return res

  # 根據resource id輸出diversity
  def getDiversity(self, rid):
    # 計算entropy
    def calDiversity(community):
      # 所有的group裡頭的數量的總和
      total = len(community);

      entropy = 0
      for count in community.values():
        if count != 0:
          entropy -= (count / total) * math.log(count / total);
      return entropy;
    
    # 找出前40個與resource最多共同出現次數的resource
    sql = 'SELECT TARGET, VALUE AS res FROM RELATIONSHIP WHERE SOURCE={}\
            UNION\
           SELECT SOURCE, VALUE AS res FROM RELATIONSHIP WHERE TARGET={}\
            ORDER BY VALUE DESC LIMIT 40'.format(rid, rid)
    cursor = self.conn.execute(sql)
    comention_rids = [str(pair[0]) for pair in cursor]

    # 根據這些共同出現的resources算他們出現的community種類數量(不包含nan)
    sql = 'SELECT COMMUNITIES, COUNT(*) FROM NODE WHERE ID IN ({}) AND\
      COMMUNITIES != \'nan\' GROUP BY COMMUNITIES'.format(','.join(comention_rids))
    cursor = self.conn.execute(sql)

    # 格式：{ group id: 數量 }
    community = { str(i): 0 for i in range(82) }
    for key, val in cursor:
      community[key] = val
    entropy = calDiversity(community)

    return entropy

  # 'resource_graph.html'的html格式(已固定)
  def WriteGraphHTML(self, nodeInfo, relationSet):
    # graph.html加上html的元素
    graph_part1 = open('data/html_text/graph_part1.txt', 'r').read()
    graph_part2 = open('data/html_text/graph_part2.txt', 'r').read()
    links = "\"links\":[\n"
    nodes = "\"nodes\":[\n"

    # 根據每個resource id，將它加入d3.js的nodes
    rids = list(nodeInfo.keys())
    for rid in rids:
      nodes += toJSNodes(rid=rid, value=nodeInfo[rid]['total_mention'], name=nodeInfo[rid]['name'], group=nodeInfo[rid]['group'])
    
    # 根據已經建立好的物件，將它加入d3.js的links
    for src, desc, emi in relationSet:
      links += toJSLinks(source=rids.index(src), target=rids.index(desc), value=EMIValueAdjust(emi))
    
    # 補全javescript格式
    nodes = nodes[:-2] + "\n],\n"
    links = links[:-2] + "\n]}\n"

    # 宣告javascript會用到的master_id，使用於網頁特效

    # 輸出resource_graph.html
    declare_var = 'var master_id = {};'.format(self.master_rid)
    graph_outfile = open(self.PATH + str(self.master_rid) + '_graph.html', 'w+')
    graph_outfile.write(graph_part1 + nodes + links + declare_var + graph_part2)

  # 'resource_pmid.html'的html格式(已固定)
  def WritePMIDHTML(self, nodeInfo):
    pmids_part1 = open('data/html_text/pmids_part1.txt', 'r').read()
    pmids_part2 = open('data/html_text/pmids_part2.txt', 'r').read()
    pmids_part3 = open('data/html_text/pmids_part3.txt', 'r').read()

    pmids_outfile = open(self.PATH + str(self.master_rid) + '_pmids.html', 'w+')
    pmids_output = '<!DOCTYPE html>\n<html>\n<head>\n<title>PubMed IDs '
    # 加上src title
    pmids_output += toScrTitle(self.master_rid)
    # 加上pmid的部分html內容
    pmids_output += pmids_part1
    pmids_output += toScrTitle(self.master_rid)
    pmids_output += ' ' + nodeInfo[self.master_rid]['name']
    pmids_output += pmids_part2

    # 根據此resource id，得到所有提到此resource的pmid以及其相關資料
    cursor = self.conn.execute('''SELECT * FROM MENTION WHERE RID = ?;''', (str(self.master_rid),))

    for pmidInfo in cursor:
      _, rid, mention_id, input_source, confidence, snippet, year = pmidInfo
      pmids_output += toPMIDFormat(rid, mention_id, input_source, confidence, snippet)

    pmids_output += pmids_part3

    pmids_outfile.write(pmids_output)
    pmids_outfile.close()

  # 'resource_table.html'的html格式(已固定)
  def WriteTableHTML(self, nodeInfo, pmidTotalCoMention, diversity, emiDict, coMentionDict):
    # 將table.html共同會出現的html內容寫入
    infile_table_part1 = open('data/html_text/table_part1.txt', 'r')
    infile_table_part2 = open('data/html_text/table_part2.txt', 'r')
    infile_table_part3 = open('data/html_text/table_part3.txt', 'r')
    table_part1 = infile_table_part1.read()
    table_part2 = infile_table_part2.read()
    table_part3 = infile_table_part3.read()
    table_outfile = open(self.PATH + str(self.master_rid) + '_table.html', 'w+')

    table_output = '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">\n<html>\t<head>\n<title>'
    table_output = table_output + toScrTitle(self.master_rid) + ' Table</title>'

    # 根據resource id將物件資訊取出
    try:
      mention = nodeInfo[self.master_rid]['total_mention']
      one_mention = nodeInfo[self.master_rid]['one_mention']
      point_nine_five_mention = nodeInfo[self.master_rid]['nine_five_mention']
      point_eight_mention = nodeInfo[self.master_rid]['eight_mention']
      point_two_mention = nodeInfo[self.master_rid]['two_mention']
      name = nodeInfo[self.master_rid]['name']
      abbr = nodeInfo[self.master_rid]['abbr']
      url = nodeInfo[self.master_rid]['url']
    except:
      # 如果取出來的資料有少上面任何一種，就跳出錯誤
      raise (TestFailed('{} no data in nodeInfo(master_rid)'.format(self.master_rid)))

    # 將master_resource的資訊加入table
    table_output += table_part1
    table_output += name
    table_output += '</font></h3>\n<h2>'
    table_output += 'RRID:' + toScrTitle(self.master_rid)
    table_output += table_part2
    table_output += toTargetIdHtmlFormat(self.master_rid, url, name, pmidTotalCoMention, diversity ,mention)

    img_icon = '<a href="#legend"><img src="question-mark-icon.png" alt="?" style="width:24px;height:24px;"></a>'

    table_output +=\
    '<div><table>\n\t<tr>\n\t\t<th>RRID</th>' +\
    '\n\t\t<th>Resource name</th>\n\t\t<th>Top 20 partners' + img_icon + \
    '</th>\n\t\t<th>Co-mention strength' + img_icon + \
    '</th>\n\t\t<th>Co-mention count' + img_icon + \
    '</th>\n\t\t<th>Total mentions' + img_icon + \
    '</th>\n\t</tr>\n'

    tableRows = []
    '''
    nodeInfo格式：{
      rid[1]: {
        resource information 
      },
      rid[2]: {
        resource information 
      },
      ...
    }
    '''
    # 根據所有相鄰的node，一個resource的資料(resource id, url, name, emi, 跟其他top20共同出現的總次數, 出現的總次數)為一列加入table中
    for rid in nodeInfo:
      if (rid == self.master_rid): continue
      mention = nodeInfo[rid]['total_mention']
      name = nodeInfo[rid]['name']
      url = nodeInfo[rid]['url']
      emi = emiDict[rid]
      numOfCoMention = coMentionDict[rid]

      tableRows.append((rid, url, name, emi, numOfCoMention, mention))

    # 將table中的列按照emi數值有高至低排序
    for row in sorted(tableRows, key=lambda row: row[3], reverse=True):
      (id, url, name, coMention, EMI, mention) = row
      # 取得提到master resource的所有pmid
      cursor = self.conn.execute('''SELECT MENTION_ID FROM MENTION WHERE RID = ? OR RID = ? GROUP BY MENTION_ID HAVING COUNT(*) > 1;''', (str(id), str(self.master_rid)))
      mids = [mid[0].replace('PMID:', '') for mid in cursor]
      table_output += toMentionIdHtmlFormat(id, url, name, coMention, EMI, mention, mids)

    table_output += table_part3
    table_outfile.write(table_output)
    table_outfile.close()

  # 'resource_main.html'的html格式(已固定)
  def WriteMainHTML(self):
    main_outfile = open(self.PATH + str(self.master_rid) + '_main.html', 'w+')
    main_output = '<!DOCTYPE html>\n<html>\n<head>\n<title>'
    main_output += toScrTitle(self.master_rid)
    main_output += '</title>\n</head>\n<frameset cols=\"65%,35%\">\n\t\t<frame src=\"'
    main_output = main_output + str(self.master_rid) + '_graph.html\">\n\t\t<frame src=\"'
    main_output = main_output + str(self.master_rid) + '_table.html\">\n'
    main_output = main_output + '</frameset>\n</html>'

    main_outfile.write(main_output)
    main_outfile.close()

  def generateGraphById(self, master_rid):
    self.master_rid = master_rid

    # 建立emi以及coMention的物件
    emiDict, coMentionDict = self.getLinkedRelation()

    # 取得前20個頻繁共同出現的partners resoruce id
    self.top20RelationRid = self.getTop20RID(coMentionDict)
    # 取得與前20個頻繁共同出現的partners，此resource id與這些partner們共同出現的總次數
    totalCoMentionPartners = np.sum([coMentionDict[rid] for rid in self.top20RelationRid])

    # 將此resource id資訊加入top20RelationRid
    self.top20RelationRid.insert(0, str(self.master_rid))

    # 建立包含每個resource的物件
    nodeInfo = self.constructNodeInfo()
    # 建立包含所有resource連結的物件
    relationSet = self.appendMutualRelation(nodeInfo)

    # 輸出resource_graph.html
    self.WriteGraphHTML(nodeInfo=nodeInfo, relationSet=relationSet)
    # 輸出resource_table.html
    self.WriteTableHTML(nodeInfo=nodeInfo, pmidTotalCoMention=totalCoMentionPartners,
      diversity=self.getDiversity(self.master_rid), emiDict=emiDict, coMentionDict=coMentionDict)
    # 輸出resource_pmid.html
    self.WritePMIDHTML(nodeInfo=nodeInfo)
    # 輸出resource_main.html
    self.WriteMainHTML()
