import sqlite3
import graph_generator

if __name__ == '__main__':

    conn = sqlite3.connect('data/CoMentions.db')
    conn.text_factory = str

    linkValueLimit = 10
    numberOfNodes = 20

    cursor = conn.execute('''SELECT COUNT(*) FROM MENTION''')
    for row in cursor:
        totalMention = int(row[0])

    path = 'graph/'


    # Single graph

    graph_generator.generateGraphById(1847, path, linkValueLimit, numberOfNodes, totalMention)

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