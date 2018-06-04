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

#input:原始tsv檔
#output:pkl檔，其中存一dict，key為pmid，value為年份
#參數一：data_path，為原始tsv檔存放位置
#參數二：save_path
#python3 get_year.py

#input:原始tsv檔
#output:跑slm分群需要的csv檔，包含rid1、rid2、emi三個欄位
#參數一：data_path，為原始tsv檔存放位置，default = './raw_tsv/'
#參數二：save_path，為各程式執行時中間產物的存放路徑，default = './process_data/'
python3 src/extract/for_slm.py 
#python3 for_slm.py --data_path --save_path


#input:for_slm.py的輸出，用來跑slm分群的tsv檔
#output:原始的slm分群結果txt檔，包含rid與其相應分到的cluster number
#參數一：Input file name
#參數二：Output file name
#參數三：Modularity function (1 = standard; 2 = alternative)，為求一致，我們皆使用1
#參數四：Resolution parameter，即r的值，default＝2.5
#參數五：Algorithm (1 = Louvain; 2 = Louvain with multilevel refinement; 3 = smart local moving)，使用3才為slm
#參數六：Number of random starts (e.g., 10)，為求一致，我們皆使用10
#參數七：Number of iterations (e.g., 10)，為求一致，我們皆使用0
#參數八：Random seed (e.g., 0)，為求一致，我們皆使用0
#參數九：Print output (0 = no; 1 = yes)，是否在分群期間輸出目前進度，default＝1
java -jar src/extract/ModularityOptimizer.jar  'src/extract/process_data/slm_input.csv'  'src/extract/slm_output/slm_output250.txt' 1 2.5 3 10 0 0 1

#input:ModularityOptimizer.jar的輸出，原始的slm分群結果txt檔
#output:處理過後的slm分群結果，每群各輸出一個txt檔，其中為被分為該群的rid，並放在community_path下
#參數一：r，default = '250'，為原本r值的100倍
#參數二：data_path，為原始tsv檔存放位置，default = './raw_tsv/'
#參數三：save_path，為各程式執行時中間產物的存放路徑，default = './process_data/'
#參數四：community_path，為處理過後的slm分群結果存放資料夾名，default = './180306/'
python3 src/extract/slm_clu.py 
#python3 slm_clu.py --r 250 

#input:原始tsv檔
#output:lda分群結果，每群各輸出一個txt檔，其中為被分為該群的rid，並放在community_path下
#參數一：r，default = '250'，為原本r值的100倍
#參數二：data_path，為原始tsv檔存放位置，default = './raw_tsv/'
#參數三：save_path，為各程式執行時中間產物的存放路徑，default = './process_data/'
#參數四：community_path，為處理過後的lda分群結果存放資料夾名，default = './180306/'
#python3 lda_clu.py

#input:原始tsv檔
#output:db檔，包含mention、relationship、node三個table
#參數一：mode，default = 'slm'
#參數二：r，default = '250'，為原本r值的100倍
#參數三：data_path，為原始tsv檔存放位置，default = './raw_tsv/'
#參數四：save_path，為各程式執行時中間產物的存放路徑，default = './process_data/'
#參數五：community_path，為處理過後的slm分群結果存放資料夾名，default = './180306/'
#參數六：output_path，為存放db檔的路徑，default = 'ucsd_slm250.db'
python3 src/extract/tsv_to_db.py 
#python3 tsv_to_db.py --mode lda 
echo '[v] slm db generated'

echo '[-] generating dunn db'
python3 src/extract/dunn.py
echo '[v] dunn db generated.'

python3 src/display/main.py
