#!/bin/sh

#附註：「原始tsv檔」是指exclusion、resource-duplicates、resource-mentions-relationships、
#     resource-mentions、resource-metadata這五個檔案

pip3 install argparse==1.1 termcolor==1.1.0 tqdm==4.19.4 sqlalchemy==1.1.9 numpy==1.13.3 requests==2.18.4 lda==1.0.5 nltk==3.0.3

printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' -
PS3=$'\n''Choose a way(1/2/3) to get all raw files below: '$'\n''  * resource-duplicates.tsv'$'\n''  * esource-mentions-relationships.tsv'$'\n''  * resource-mentions.tsv'$'\n''  * resource-metadata.tsv'$'\n''  * exclusion.tsv'$'\n''> '
options=("Download From NTU server" "From an url (should be valid url address)" "No worries (already have)")
select opt in "${options[@]}"
do
	case $opt in
		"Download From NTU server")
			echo '[-] .tsv files downloading'
			curl -o src/extract/raw_tsv/resource-duplicates.tsv ftp://140.112.107.150/UCSD/resource-duplicates.tsv
			curl -o src/extract/raw_tsv/resource-mentions-relationships.tsv ftp://140.112.107.150/UCSD/resource-mentions-relationships.tsv
			curl -o src/extract/raw_tsv/resource-mentions.tsv ftp://140.112.107.150/UCSD/resource-mentions.tsv
			curl -o src/extract/raw_tsv/resource-metadata.tsv ftp://140.112.107.150/UCSD/resource-metadata.tsv
			curl -o src/extract/raw_tsv/exclusion.tsv ftp://140.112.107.150/UCSD/exclusion.tsv
			echo '[v] downloaded.'
			break
			;;
		"From an url (valid url address)")
			read -p "Enter url location containing all .tsv files (Ex: ftp://140.112.107.150/UCSD): " SOMEWHERE
			echo '[-] .tsv files downloading'
			curl -o src/extract/raw_tsv/resource-duplicates.tsv $SOMEWHERE/resource-duplicates.tsv
			curl -o src/extract/raw_tsv/resource-mentions-relationships.tsv $SOMEWHERE/resource-mentions-relationships.tsv
			curl -o src/extract/raw_tsv/resource-mentions.tsv $SOMEWHERE/resource-mentions.tsv
			curl -o src/extract/raw_tsv/resource-metadata.tsv $SOMEWHERE/resource-metadata.tsv
			curl -o src/extract/raw_tsv/exclusion.tsv $SOMEWHERE/exclusion.tsv
			echo '[v] downloaded.'
			break
			;;
		"No worries (already have)")
			break
			;;
		*) echo invalid option;;
	esac
done

echo '[-] generating slm db'

python3 src/extract/for_slm.py 
java -jar src/extract/ModularityOptimizer.jar  'src/extract/process_data/slm_input.csv'  'src/extract/slm_output/slm_output250.txt' 1 2.5 3 10 0 0 1
python3 src/extract/slm_clu.py 
python3 src/extract/tsv_to_db.py 

echo '[v] slm db generated'

echo '[-] generating dunn db'
python3 src/extract/dunn.py
echo '[v] dunn db generated.'

python3 src/display/main.py
