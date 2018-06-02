#!/bin/sh
pip3 install argparse==1.1 termcolor==1.1.0 tqdm==4.19.4 sqlalchemy==1.1.9 pickle==4.0 numpy==1.13.3 requests==2.18.4 lda==1.0.5 nltk==3.0.3 
echo '[-] .tsv files downloading'
curl -o src/extract/raw_tsv/resource-duplicates.tsv ftp://140.112.107.150/UCSD/resource-duplicates.tsv
curl -o src/extract/raw_tsv/resource-mentions-relationships.tsv ftp://140.112.107.150/UCSD/resource-mentions-relationships.tsv
curl -o src/extract/raw_tsv/resource-mentions.tsv ftp://140.112.107.150/UCSD/resource-mentions.tsv
curl -o src/extract/raw_tsv/resource-metadata.tsv ftp://140.112.107.150/UCSD/resource-metadata.tsv
curl -o src/extract/raw_tsv/exclusion.tsv ftp://140.112.107.150/UCSD/exclusion.tsv
echo '[v] downloaded.'

echo '[-] generating slm db'
python3 src/extract/tsv_to_db.py
echo '[v] slm db generated'

echo '[-] generating dunn db'
python3 src/extract/dunn.py
echo '[v] dunn db generated.'

python3 src/display/main.py
