import pandas as pd
from shutil import copyfile

path = '../src/extract/CoMen/exclusion.tsv'

df = pd.read_csv('../sample_file/utils_exclusion_append_input.csv', header=None)

df[1] = ['SCR_' + '{0:06d}'.format(x) for x in df[1]]

print('Backup path: [ ' + path + '_backup')
copyfile(path, path + '_backup')

with open(path, 'a') as f:
	for x, y, z in zip(df[0], df[1], df[2]):
		newline = '\t'.join(str(v) for v in [x,y,z]) + '\n'
		f.write(newline)
