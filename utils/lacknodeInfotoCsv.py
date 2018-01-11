import sqlite3
a=open('../src/display/logs.txt').read()
a=a.split('\n')[:-1]

b=[x.split(' ') for x in a]
# x[-1] is relation counts
conn = sqlite3.connect('../src/display/data/CoMentions.db')
conn.text_factory = str

c=[]
for x in b:
	rid=int(x[0])
	# cursor = conn.execute('''SELECT NAME FROM NODE WHERE ID=? LIMIT 1''', (rid,))
	# query = list(cursor)
	# if(len(query)==0): continue
	# n = query[0][0]
	c.append('SCR_{0:06d}'.format(rid))
	print(c)
print(c)
d='\n'.join(c)
x=open('../src/display/no_data_in_NODE_table.txt', 'w')
x.write(d)
x.close()