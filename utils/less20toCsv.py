import sqlite3
a=open('../src/display/less20.txt').read()
a=a.split('\n')[:-1]
b=[x.split(' ') for x in a]
# x[-1] is relation counts
conn = sqlite3.connect('../src/display/data/CoMentions.db')
conn.text_factory = str

c=[]
for x in b:
	rid=int(x[0])
	relation_count=int(x[-1])
	if(relation_count>0): continue
	cursor = conn.execute('''SELECT NAME FROM NODE WHERE ID=? LIMIT 1''', (rid,))
	query = list(cursor)
	if(len(query)==0): continue
	n = query[0][0]
	c.append('SCR_{0:06d},{1}'.format(rid, n))
print(c)
d='\n'.join(c)
x=open('../src/display/mentioned_but_no_relationship_with_others.txt', 'w')
x.write(d)
x.close()