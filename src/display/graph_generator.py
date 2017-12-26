#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import sqlite3
import time

def generateGraphById(id, path, linkValueLimit, numberOfNodes, totalMention):
    
    # 連結資料庫
    conn = sqlite3.connect('data/CoMentions.db')
    # 控制對於TEXT數據類型，何種對象將會返回
    # 預設為unicode，若想要返回bytestrings，設置為str
    conn.text_factory = str

    # ===========================================#
    # generate id_graph.html
    # ===========================================#

    infile_graph_part1 = open('data/html_text/graph_part1.txt', 'r')
    infile_graph_part2 = open('data/html_text/graph_part2.txt', 'r')
    graph_part1 = infile_graph_part1.read()
    graph_part2 = infile_graph_part2.read()

    print "Generate graph. id = " + str(id)
    links = "\"links\":[\n"
    nodes = "\"nodes\":[\n"


    # list of nodes that linked to node (id)
    linkNodeList = set()
    # Find all nodes linked by node(id) in linkNodeList
    cursor = conn.execute('''SELECT TARGET FROM RELATIONSHIP WHERE SOURCE = ?;''', (int(id),))
    for row in cursor:
        linkNodeList.add(row[0])

    cursor = conn.execute('''SELECT SOURCE FROM RELATIONSHIP WHERE TARGET = ?;''', (int(id),))
    for row in cursor:
        linkNodeList.add(row[0])

    linkNodeList = list(linkNodeList)



    # Need to split to chunks since list limit in SQL is 1000
    tempNodeList = []
    tempRelationshipList = []
    nodeList = []
    max_sql = 998

    for i in range(0, (len(linkNodeList) / max_sql + 1)):
        tempNodeForSingleSqlList = []
        max = max_sql * (i + 1)
        if max > len(linkNodeList):
            max = len(linkNodeList)

        # Find top-k co-mention nodes in linkNodeList
        AboveNodeList = []
        BelowNodeList = []
        for node_id in linkNodeList[i*max_sql:max]:
            if int(node_id) > id:
                AboveNodeList.append(node_id)
            elif int(node_id) < id:
                BelowNodeList.append(node_id)

        AboveNodeList.append(id)
        sql = "SELECT * FROM    RELATIONSHIP    WHERE   TARGET  IN  ({seq}) AND SOURCE = {id}".format(
            seq=','.join(['?'] * (len(AboveNodeList)-1)), id='?')
        cursor.execute(sql, AboveNodeList)
        for row in cursor:
            tempRelationshipList.append(row)

        BelowNodeList.append(id)
        sql = "SELECT * FROM    RELATIONSHIP    WHERE   SOURCE  IN  ({seq}) AND TARGET = {id}".format(
            seq=','.join(['?'] * (len(BelowNodeList) - 1)), id='?')
        cursor.execute(sql, BelowNodeList)
        for row in cursor:
            tempRelationshipList.append([row[1], row[0], row[2]])

    # Find top-k co-mention nodes
    tempRelationshipList.sort(key=lambda tup: (tup[2]), reverse=True)

    for i in range(0, numberOfNodes * 2):
        if len(tempRelationshipList) > i:
            cursor.execute("SELECT * FROM NODE WHERE ID = ?;", (int(tempRelationshipList[i][1]),))
            for row in cursor:
                nodeList.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], tempRelationshipList[i][2], row[9]])
                break

    # 優先序： 在這段關係中的COUNT數 > 在資料庫裡的MENTION次數
    nodeList.sort(key=lambda tup: (tup[1]), reverse=True)
    nodeList.sort(key=lambda tup: (tup[8]), reverse=True)

    tempNodeList = []
    for i in range(0, numberOfNodes):
        if len(nodeList) > i:
            tempNodeList.append(nodeList[i])
            nodes = nodes + toJSNodes(nodeList[i][0], nodeList[i][1], nodeList[i][6], nodeList[i][9])

    nodeList = tempNodeList

    '''
        NODE: { 
            Id, #[0]
            Mention, #[1]
            1_mention, #[2]
            0.95_mention, #[3]
            0.8_mention, #[4]
            0.2_mention, #[5]
            Name, #[6]
            Abbr, #[7]
            Url, #[8]
            Community #[9]
        }
    '''
    cursor = conn.execute('''SELECT * FROM NODE WHERE ID = ?;''', (int(id),))
    for row in cursor:
        nodes = nodes + toJSNodes(row[0], row[1], row[6], row[9])
        nodeList.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[1]])

    nodeIdList = []
    for node in nodeList:
        nodeIdList.append(node[0])

    # RELATIONSHIP: { Source, Target, Value }
    sql = "SELECT * FROM RELATIONSHIP WHERE SOURCE IN ({seq})".format(
        seq=','.join(['?'] * len(nodeIdList)))
    cursor.execute(sql, nodeIdList)
    tempLinkList = cursor.fetchall()

    EMI_list = []
    for link in tempLinkList:
        if link[0] in nodeIdList and link[1] in nodeIdList:
            if (int(link[2]) >= linkValueLimit) or (str(link[0]) == str(id) or str(link[1]) == str(id)):
                # ========= Original value =========
                # links = links + toJSLinks(toLinkPosition(link[0], nodeIdList), toLinkPosition(link[1], nodeIdList), link[2])
                # =========== EMI value ============
                cursor = conn.execute('''SELECT * FROM NODE WHERE ID = ?;''', (int(link[0]),))
                for row in cursor:
                    valueA = row[1]
                    break
                cursor = conn.execute('''SELECT * FROM NODE WHERE ID = ?;''', (int(link[1]),))
                for row in cursor:
                    valueB = row[1]
                    break

                EMI = EMIValueAdjust(getEMIValue(link[2], valueA, valueB, totalMention))
                if EMI != 0:
                    EMI_list.append([link[0], link[1], link[2], EMI])
                    links = links + toJSLinks(toLinkPosition(link[0], nodeIdList), toLinkPosition(link[1], nodeIdList), EMI)
                else:
                    print link[0], valueA, link[1], valueB, link[2]
                    raise EnvironmentError('Error: EMI value calculation.')

    nodes = nodes[:-2]
    links = links[:-2]
    nodes += "\n],\n"
    links += "\n]"

    # print "Generate graph. id = " + str(id) + " finished."
    graph_outfile = open(path + str(id) + '_graph.html', 'w+')
    graph_outfile.write(graph_part1 + nodes + links + graph_part2)
    graph_outfile.close()
    infile_graph_part1.close()
    infile_graph_part2.close()

    # ===========================================#
    # generate id_table.html
    # ===========================================#

    infile_table_part1 = open('data/html_text/table_part1.txt', 'r')
    infile_table_part2 = open('data/html_text/table_part2.txt', 'r')
    infile_table_part3 = open('data/html_text/table_part3.txt', 'r')
    table_part1 = infile_table_part1.read()
    table_part2 = infile_table_part2.read()
    table_part3 = infile_table_part3.read()
    table_outfile = open(path + str(id) + '_table.html', 'w+')

    table_output = '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">\n<html>\t<head>\n<title>'
    table_output = table_output + toScrTitle(id) + ' Table</title>'
    table_output += table_part1
    table_output += toScrTitle(id)
    table_output += '</h1>\n<h2>'

    cursor = conn.execute('''SELECT * FROM NODE WHERE ID = ?;''', (int(id),))
    for row in cursor:
        mention = row[1]
        one_mention = row[2]
        point_nine_five_mention = row[3]
        point_eight_mention = row[4]
        point_two_mention = row[5]
        name = row[6]
        url = row[7]
        numOfCoMention = len(tempRelationshipList)
        table_output += name
        table_output += table_part2
        table_output += toTargetIdHtmlFormat(id, url, name, numOfCoMention, mention, one_mention, point_nine_five_mention, point_eight_mention, point_two_mention)
        break

    sql = "SELECT * FROM NODE WHERE ID IN ({seq})".format(
        seq=','.join(['?'] * len(nodeIdList)))
    cursor.execute(sql, nodeIdList)
    tableNodeList = cursor.fetchall()

    table_output = table_output + '<div><table>\n\t<tr>\n\t\t<th>RRID</th>'
    table_output = table_output + '\n\t\t<th>Resource name</th>\n\t\t<th>Co-mention network</th>\n\t\t<th>Co-mention count</th>'
    table_output = table_output + '\n\t\t<th>Mutual Info</th>\n\t\t<th>Total mentions</th>\n\t</tr>\n'

    if len(nodeList) < numberOfNodes:
        max = len(nodeList)
    else:
        max = numberOfNodes
    for i in range(0, max):
        cursor = conn.execute('''SELECT * FROM NODE WHERE ID = ?;''', (int(nodeList[i][0]),))
        for row in cursor:
            valueA = row[1]
            break

        # =========== EMI value ============
        for item in EMI_list:
            if (str(item[0]) == str(nodeList[i][0]) and str(item[1]) == str(id)) or (str(item[0]) == str(id) and str(item[1]) == str(nodeList[i][0])):
                coMention = item[2]
                EMI = "{0:.4f}".format(item[3])
                table_output = table_output + toMentionIdHtmlFormat(nodeList[i][0], nodeList[i][7], nodeList[i][6], coMention, EMI, nodeList[i][1])
                break


    table_output += table_part3
    table_outfile.write(table_output)
    table_outfile.close()

    # ===========================================#
    # generate id_pmids.html
    # ===========================================#

    infile_pmids_part1 = open('data/html_text/pmids_part1.txt', 'r')
    infile_pmids_part2 = open('data/html_text/pmids_part2.txt', 'r')
    infile_pmids_part3 = open('data/html_text/pmids_part3.txt', 'r')
    pmids_part1 = infile_pmids_part1.read()
    pmids_part2 = infile_pmids_part2.read()
    pmids_part3 = infile_pmids_part3.read()

    pmids_outfile = open(path + str(id) + '_pmids.html', 'w+')
    pmids_output = '<!DOCTYPE html>\n<html>\n<head>\n<title>PubMed IDs '
    pmids_output += toScrTitle(id)
    pmids_output += pmids_part1
    pmids_output += toScrTitle(id)
    pmids_output += pmids_part2

    cursor = conn.execute('''SELECT * FROM MENTION WHERE RID = ?;''', (int(id),))
    for row in cursor:
        rid = row[1]
        mention_id = row[2]
        input_source = row[3]
        confidence = row[4]
        snippet = unicode(str(row[5]), "utf-8")

        pmids_output += toPMIDFormat(rid, mention_id, input_source, confidence, snippet)

    pmids_output += pmids_part3

    pmids_outfile.write(pmids_output)
    pmids_outfile.close()

    # ===========================================#
    # generate id_main.html
    # ===========================================#

    main_outfile = open(path + str(id) + '_main.html', 'w+')
    main_output = '<!DOCTYPE html>\n<html>\n<head>\n<title>'
    main_output += toScrTitle(id)
    main_output += '</title>\n</head>\n<frameset cols=\"65%,35%\">\n\t\t<frame src=\"'
    main_output = main_output + str(id) + '_graph.html\">\n\t\t<frame src=\"'
    main_output = main_output + str(id) + '_table.html\">\n'
    main_output = main_output + '</frameset>\n</html>'

    main_outfile.write(main_output)
    main_outfile.close()

    conn.commit()
    conn.close()

def toScrTitle(id):
    name = 'SCR_'
    for i in range(0, 6 - len(str(id))):
        name += '0'
    return name + str(id)


def toTargetIdHtmlFormat(id, url, name, numCoMentionPartners, mention, point_one_mention, point_nine_five_mention, point_eight_mention, point_two_mention):
    html = '\t<tr>\n\t\t<td><a class=\"external\" target=\"_blank\"\n\thref=\"https://scicrunch.org/browse/resources/'
    html = html + toScrTitle(id) + '\">' + toScrTitle(id) + '</td>'
    
    len_url = 0 if url is None else len(url)
    if(len_url < 5):
        html = html + '\n\t\t<td><a class=\"external\" target=\"_blank\"\n\thref=\"' + 'https://www.fake_url_' + str(id) + '.com\">' + name + '</a></td>'
    else:
        html = html + '\n\t\t<td><a class=\"external\" target=\"_blank\"\n\thref=\"' + url + '\">' + name + '</a></td>'

    html = html + '\n\t\t<td align="right">' + str(numCoMentionPartners) + '</td>'
    html = html + '\n\t\t<td align="right">' + str(mention) + '</td>'
    html = html + '\n\t\t<td align="right">' + str(point_one_mention) + '</td>'
    html = html + '\n\t\t<td align="right">' + str(point_nine_five_mention) + '</td>'
    html = html + '\n\t\t<td align="right">' + str(point_eight_mention) + '</td>'
    html = html + '\n\t\t<td align="right">' + str(point_two_mention) + '</td>'
    html = html + '\n\t</tr>\n</table>'

    html = html + '<p>Click <a class=\"external\" target=\"_blank\" href=\"' + str(id) + '_pmids.html\"><b>here</b></a>'
    html = html + ' for a list of PubMed IDs where the mentions were identified.</p>'
    # html = html + '<h3>Top 20 co-mention partners:</h3>'
    html = html + '<h3>Top 20 co-mention partners: <a class="external" target="_blank" href="help.html"><font color="red">[Help]</font></a></h3>'
    return html


def toMentionIdHtmlFormat(id, url, name, coMention, EMI, mention):
    html = '\t<tr>\n\t\t<td><a class=\"external\" target=\"_blank\"\n\thref=\"https://scicrunch.org/browse/resources/'
    html = html + toScrTitle(id) + '\">' + toScrTitle(id) + '</td>'
    html = html + '\n\t\t<td><a class=\"external\" target=\"_blank\"\n\thref=\"' + str(url) + '\">' + str(name) + '</a></td>'
    html = html + '\n\t\t<td align="center">' + '<a class=\"external\" target=\"_blank\" href=\"' + str(
        id) + '_main.html\">Go</a>' + '</td>'
    html = html + '\n\t\t<td align="right">' + str(int(coMention)) + '</td>'
    html = html + '\n\t\t<td align="right">' + str(EMI) + '</td>'
    html = html + '\n\t\t<td align="right">' + str(mention) + '</td>'
    return html


def toJSLinks(source, target, value):
    return "\t{\"source\": " + str(source) + ", \"target\": " + str(target) + ", \"value\": " + str(value) + "},\n"



def toJSNodes(name, value, abbr, group):
    return "\t{\"name\": \"" + str(toScrTitle(name)) + " " + str(abbr) + "\", \"group\": " + str(group) + ", \"value\": " + str(
        nodeValueAdjust(value)) + "},\n"


def getEMIValue(a, b, c, total):
    #                        Resource A
    #            |          | Cited   | Not Cited  |
    #  Resource B| Cited    | a       | b-a        | b
    #            | Not Cited| c-a     | Total-b-c+a|
    #            |          | c       | Total      |

    if int(a) > int(b) or int(a) > int(c):
        return 0
    else:
        a = float(a)
        b = float(b)
        c = float(c)
        total = float(total)

        pA = float(c / total)
        pnA = float(1 - pA)
        pB = float(b / total)
        pnB = float(1 - pB)
        pAB = float(a / total)
        pnAB = float((b - a) / total)
        pAnB = float((c - a) / total)
        pnAnB = float((total - b - c + a) / total)


        part1 = float(pAB * math.log(float(pAB / float(pA * pB)), 2))

        if(a != c):
            part2 = float(pAnB * math.log(float(pAnB / float(pA * pnB)), 2))
        else:
            part2 = 0

        part3 = float(pnAnB * math.log(float(pnAnB / float(pnA * pnB)), 2))

        if(a != b):
            part4 = float(pnAB * math.log(float(pnAB / float(pnA * pB)), 2))
        else:
            part4 = 0

        return (part1 + part2 + part3 + part4)

def EMIValueAdjust(value):

    return 5 * value * math.pow(10, 5)

def toPMIDFormat(rid, mention_id, input_source, confidence, snippet):

    content = '\t<tr height=21 style=\'height:16.0pt\'>\n\t\t<td height=21 align=right style=\'height:16.0pt\'>'
    content += str(rid)
    content += '\t</td>\n\t\t<td><a class=\"external\" target=\"_blank\"href=\"https://www.ncbi.nlm.nih.gov/pubmed/'
    content += str(mention_id)[5:]
    content += '\">'
    content += str(mention_id)
    content += '</a></td>\n\t\t<td>'
    content += str(input_source)
    content += '</td>\n\t\t<td align=right>'
    content += str(confidence)
    content += '</td>\n\t\t<td colspan=92 style=\'mso-ignore:colspan\'>'

    snippet = unicode.encode(snippet, 'utf-8')

    if str(snippet).strip('\n') == 'NULL':
        content += ' '
    else:
        content += str(snippet)
    content += '</td>\n\t</tr>'
    return content


def nodeValueAdjust(value):

    return str(math.sqrt(float(value)) / 10)
    # return str((1 + math.log(int(value)))/10)

def toLinkPosition(id, linkPositionList):
    for i in range(0, len(linkPositionList)):
        if int(linkPositionList[i]) == int(id):
            return i
    raise ValueError('Error: Link Position.')
