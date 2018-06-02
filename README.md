# UCSD-project

### Pre-install package
| package | version |
| ------ | ------ |
| argparse | 1.1 |
| termcolor | 1.1.0 |
| tqdm | 4.19.4 |
| sqlite3 | 3.15.2 |
| sqlalchemy | 1.1.9 |
| pickle | 4.0 |
| numpy | 1.13.3 |
| requests | 2.18.4 |
| lda | 1.0.5 |
| nltk | 3.0.3 |

### Usage
#### (法1) 分別執行指令
```sh 
# Step 1:
# 下載原始檔案(.tsv)
curl -o src/extract/raw_tsv/resource-duplicates.tsv ftp://140.112.107.150/UCSD/resource-duplicates.tsv
curl -o src/extract/raw_tsv/resource-mentions-relationships.tsv ftp://140.112.107.150/UCSD/resource-mentions-relationships.tsv
curl -o src/extract/raw_tsv/resource-mentions.tsv ftp://140.112.107.150/UCSD/resource-mentions.tsv
curl -o src/extract/raw_tsv/resource-metadata.tsv ftp://140.112.107.150/UCSD/resource-metadata.tsv
curl -o src/extract/raw_tsv/exclusion.tsv ftp://140.112.107.150/UCSD/exclusion.tsv

# Step 2:
# 產生slm DB(.db)，預設output_path為：
#   [1] src/extract/ucsd_slm250.db
#   [2] src/display/data/ucsd_slm250.db
$ python3 src/extract/tsv_to_db.py --output_path=[slm_db路徑]
# 產生dunn DB(.db)，預設output_path為：src/display/data/dunn.db
$ python3 src/extract/dunn.py --output_path=[dunn_db路徑]

# Step 3:
# 產生圖表(.html)，預設output路徑為：src/display/graph/[*.html]
$ python3 src/display/main.py --slm_db=[slm_db路徑] --dunn_db=[dunn_db路徑]
```

#### (法2) 直接執行我們包好的script
```sh
bash run.sh
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
| src/extract/slm_clu_all.py | 處理slm分群的output，和rid做對應，並整理出各群包含的rid，輸出為txt檔 |
| src/extract/lda_clu_all.py | 跑lda分群，並整理出各群包含的rid，輸出為txt檔 |
| src/extract/auc_all.py | 計算auc，需輸入三個參數指定計算方式，輸出為txt檔 |
| src/extract/count_lm_all.py | 計算lm，需輸入兩個參數指定計算方式，輸出為txt檔 |
