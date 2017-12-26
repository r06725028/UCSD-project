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


    cursor = conn.execute('''SELECT ID FROM NODE''')
    # i = (id)
    # i[0] = id
    target_list = [i[0] for i in cursor]

    # Single graph
    try:
        for pid in target_list:
            graph_generator.generateGraphById(pid, path, linkValueLimit, numberOfNodes, totalMention)
    except:
        print('error')

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