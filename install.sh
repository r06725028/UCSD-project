#!/bin/bash

FILE_PATH='ftp://140.112.107.148/UCSD/'

mkdir src/extract/CoMen/
mkdir src/extract/CoMen/tsvdata/
echo 'Download file for db construction...'
curl -o src/extract/CoMen/tsvdata/resource-mentions.tsv ${FILE_PATH}resource-mentions.tsv
curl -o src/extract/CoMen/tsvdata/resource-metadata.tsv ${FILE_PATH}resource-metadata.tsv
curl -o src/extract/CoMen/tsvdata/resource-mentions-relationships.tsv ${FILE_PATH}resource-mentions-relationships.tsv
curl -o src/extract/CoMen/tsvdata/resource-duplicates.tsv ${FILE_PATH}resource-duplicates.tsv
curl -o src/extract/CoMen/tsvdata/exclusion.tsv ${FILE_PATH}exclusion.tsv
curl -o src/display/CoMentions.db ${FILE_PATH}CoMentions.db
echo 'Download complete.'
