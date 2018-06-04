# UCSD-project

### Environment
OS: Ubuntu 16.04.4
Python version: 3.6.3

### Pre-install package
| package | version |
| ------ | ------ |
| argparse | 1.1 |
| termcolor | 1.1.0 |
| tqdm | 4.19.4 |
| sqlalchemy | 1.1.9 |
| numpy | 1.13.3 |
| requests | 2.18.4 |
| lda | 1.0.5 |
| nltk | 3.0.3 |

### Usage
#### (法1) 分別執行指令
```sh 
# Step 0:
# 安裝packages
sudo pip3 install argparse==1.1 termcolor==1.1.0 tqdm==4.19.4 sqlalchemy==1.1.9 numpy==1.13.3 requests==2.18.4 lda==1.0.5 nltk==3.0.3

# Step 1: 取得raw data: .tsv檔，放至src/extract/raw_tsv/
# 如果src/extract/raw_tsv/已經存在所需的.tsv檔案，則可以跳過此步驟
wget -O src/extract/raw_tsv/resource-duplicates.tsv ftp://140.112.107.150/UCSD/resource-duplicates.tsv
wget -O src/extract/raw_tsv/resource-mentions-relationships.tsv ftp://140.112.107.150/UCSD/resource-mentions-relationships.tsv
wget -O src/extract/raw_tsv/resource-mentions.tsv ftp://140.112.107.150/UCSD/resource-mentions.tsv
wget -O src/extract/raw_tsv/resource-metadata.tsv ftp://140.112.107.150/UCSD/resource-metadata.tsv
wget -O src/extract/raw_tsv/exclusion.tsv ftp://140.112.107.150/UCSD/exclusion.tsv

# Step 2:
# (a) 產生slm DB(.db)，預設output_path為：
#     [1] src/extract/ucsd_slm250.db
#     [2] src/display/data/ucsd_slm250.db

#input:原始tsv檔
#output:跑slm分群需要的csv檔，包含rid1、rid2、emi三個欄位
#參數一：data_path，為原始tsv檔存放位置，default = 'src/extract/raw_tsv/'
#參數二：save_path，為各程式執行時中間產物的存放路徑，default = 'src/extract/process_data/'
$ python3 src/extract/for_slm.py 

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
$ java -jar src/extract/ModularityOptimizer.jar  'src/extract/process_data/slm_input.csv'  'src/extract/slm_output/slm_output250.txt' 1 2.5 3 10 0 0 1


#input:ModularityOptimizer.jar的輸出，原始的slm分群結果txt檔
#output:處理過後的slm分群結果，每群各輸出一個txt檔，其中為被分為該群的rid，並放在community_path下
#參數一：r，default = '250'，為原本r值的100倍
#參數二：data_path，為原始tsv檔存放位置，default = 'src/extract/raw_tsv/'
#參數三：save_path，為各程式執行時中間產物的存放路徑，default = 'src/extract/process_data/'
#參數四：community_path，為處理過後的slm分群結果存放資料夾名，default = 'src/extract/180306/'
$ python3 src/extract/slm_clu.py 

#input:原始tsv檔
#output:db檔，包含mention、relationship、node三個table
#參數一：mode，default = 'slm'
#參數二：r，default = '250'，為原本r值的100倍
#參數三：data_path，為原始tsv檔存放位置，default = 'src/extract/raw_tsv/'
#參數四：save_path，為各程式執行時中間產物的存放路徑，default = 'src/extract/process_data/'
#參數五：community_path，為處理過後的slm分群結果存放資料夾名，default = 'src/extract/180306/'
#參數六：output_path，為存放db檔的路徑，default = 'src/display/data/ucsd_slm250.db'
$ python3 src/extract/tsv_to_db.py --output_path=[slm_db路徑]

# (b) 產生dunn DB(.db)，預設output_path為：src/display/data/dunn.db
$ python3 src/extract/dunn.py --output_path=[dunn_db路徑]

# Step 3:
#   產生圖表(.html)，預設output路徑為：src/display/graph/[*.html]
$ python3 src/display/main.py --slm_db=[slm_db路徑] --dunn_db=[dunn_db路徑]
```

#### (法2) 直接執行我們包好的script
```sh
sudo bash run.sh
```

### 目錄說明
* src/ : 圖表、資料庫生成的原始碼
* utils/ : 臨時需求的原始碼

### src程式碼,相依檔案與說明
| 路徑 | 說明 |
| ------ | ------ |
| src/display/main.py | 統合[first|second|third]_graph_generator.py的入口執行檔，輸出三種圖表於src/graph |
| src/display/first_graph_generator.py | 處理輸出類別彼此的關係圖表 |
| src/display/second_graph_generator.py | 處理輸出類別內部的resource關係圖表 |
| src/display/third_graph_generator.py | 處理輸出每個resource的關係圖表 |
| src/display/formatter.py | 將資料轉為需要的html格式的函式庫 |
| src/display/data/html_text/ | 存放固定且相依的html內容 |
| src/extract/tsv_to_db.py | 新增有mention、relationship、node的db，需輸入兩個參數指定要採用的分群結果|
| src/extract/process_duplicate.py | 移除duplicate及exclusion的module |
| src/extract/slm_clu.py | 處理slm分群的output，和rid做對應，並整理出各群包含的rid，輸出為txt檔 |
| src/extract/lda_clu.py | 跑lda分群，並整理出各群包含的rid，輸出為txt檔 |

