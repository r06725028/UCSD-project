import pandas as pd
from tqdm import tqdm

FIELDS = ['Resource_Name', 'Description', 'Synonyms', 'Keywords']
KEYWORDS = ['university', 'department', 'college', 'univ', 'dept']
SHOWCOLS = ['rid', 'Resource_Name', 'Description', 'Supercategory', 'Additional_Resource_Types', 'type', 'frequency']

def calCounts(content):
  totalCount = 0
  for k in KEYWORDS:
    totalCount += str(content).lower().count(k)
  return totalCount

def dfFilter(df):
  pat = '|'.join(KEYWORDS)
  res = pd.DataFrame()
  freq = {}

  for field in tqdm(FIELDS):
    # generate new mask based on the keywords(case insensitive)
    col = df[field]
    newMask = col.str.contains(pat, case=False)
    for idx, d in enumerate(col):
      num = calCounts(d)
      freq[idx] = num if idx not in freq else freq[idx] + num
    res = newMask if res.empty else res | newMask
  return res, freq

if __name__ == '__main__':
  df = pd.read_csv('../sample_file/utils_exclusion_choice_input.tsv',sep='\t', header=0)
  mask, freq = dfFilter(df)

  df['frequency'] = df.apply(lambda x: freq[x.name], axis=1)
  processed_df = df[mask].sort_values(['frequency'], ascending=[False]).filter(items=SHOWCOLS)
  processed_df.to_csv(path_or_buf='output.csv', encoding='utf-8', index=False)
  print(processed_df)
  
  print('Ouput Path: ' + './output.csv')
