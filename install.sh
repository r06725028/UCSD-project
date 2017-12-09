#!/bin/bash

mkdir src/extract/CoMen/tsvdata/
echo 'Download file for db construction...'
curl -o src/extract/CoMen/tsvdata/resource-mentions.tsv ftp://140.112.107.148/resource-mentions.tsv
curl -o src/extract/CoMen/tsvdata/resource-metadata.tsv ftp://140.112.107.148/resource-metadata.tsv
curl -o src/extract/CoMen/tsvdata/resource-mentions-relationships.tsv ftp://140.112.107.148/resource-mentions-relationships.tsv
curl -o src/extract/CoMen/tsvdata/resource-duplicates.tsv ftp://140.112.107.148/resource-duplicates.tsv
curl -o src/extract/CoMen/tsvdata/exclusion.tsv ftp://140.112.107.148/exclusion.tsv
curl -o src/display/CoMentions.db ftp://140.112.107.148/CoMentions.db
echo 'Download complete.'
