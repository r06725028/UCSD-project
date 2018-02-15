# UCSD-project

### 安裝

```sh
$ git clone https://github.com/r06725028/UCSD-project.git
$ cd UCSD-project
$ sh install.sh # (非必要)下載產生db之檔案 & 產生圖表之db
```

### Usage

```sh
$ python3 src/extract/tsv_to_db.py mode r # 例：產生ucsd_slm325.db
$ python3 src/extract/slm_clu_all.py r # 例：產生“./180130/slm325/”的資料夾
$ python3 src/extract/lda_clu_all.py r # 例：產生“./180130/lda325/”的資料夾
$ python3 src/extract/auc_all.py mode r sort # 例：產生auc_slm_emi.txt
$ python3 src/extract/count_lm_all.py mode r # 例：產生lm_slm.txt
  [mode=slm,lda，r=050,075,...350，sort=emi,value]
```

### 目錄
* docs/ : 留存文件
* sample_file/ : 範例檔案 (ex: 路徑_[input | output])
* src/ : 圖表、資料庫生成的原始碼
* utils/ : 臨時需求的原始碼

### src程式碼與相依檔案
| 路徑 | 說明 |
| ------ | ------ |
| src/extract/tsv_to_db.py | 新增有mention、relationship、node的db，需輸入兩個參數指定要採用的分群結果|
| src/extract/process_duplicate.py | 移除duplicate及exclusion的module |
| src/extract/slm_clu_all.py | 處理slm分群的output，和rid做對應，並整理出各群包含的rid，輸出為txt檔 |
| src/extract/lda_clu_all.py | 跑lda分群，並整理出各群包含的rid，輸出為txt檔 |
| src/extract/auc_all.py | 計算auc，需輸入三個參數指定計算方式，輸出為txt檔 |
| src/extract/count_lm_all.py | 計算lm，需輸入兩個參數指定計算方式，輸出為txt檔 |

### utils程式碼與相依檔案
| 路徑 | 說明 |
| ------ | ------ |
| utils/exclusion_append.py | 將輸入檔案append至exclusion.tsv |
| utils/exclusion_choice.py | 將輸入檔案轉化為方便人工篩選的csv格式 |
| utils/to_csv.py | 從資料庫中取出relationship table資料轉為csv檔做為分群的input |



### docs檔案
| 路徑 | 說明 |
| ------ | ------ |
| docs/emi_check.xlsx | 輸入et、ec、t&c三欄即可自動計算出調整後的EMI值 |
| docs/clu_num_r.txt | 紀錄不同r分出的群數 |
| docs/180130/ | slm_clu_all.py處理好的分群結果，供程式讀取的版本 |
| docs/community_result/ | comm_result.py、comm_res_add_lda.py整理出的分群結果，方便人閱讀的版本 |
| xxx.pdf | 工作說明 |



### 遠端ftp與google drive連結(若install.sh失效，供手動下載)
1. FTP: ftp://140.112.107.150/UCSD/
2. Google Drive: http://goo.gl/3TYLnq
