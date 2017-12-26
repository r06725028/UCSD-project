# UCSD-project

### 安裝

```sh
$ git clone https://github.com/r06725028/UCSD-project.git
$ cd UCSD-project
$ sh install.sh # (非必要)下載產生db之檔案 & 產生圖表之db
```

### Usage

```sh
$ python3 src/extract/men_rel.py src/extract/node.py # 產生db
```

### 目錄
* docs/ : 留存文件
* sample_file/ : 範例檔案 (ex: 路徑_[input | output])
* src/ : 圖表、資料庫生成的原始碼
* utils/ : 臨時需求的原始碼

### 程式碼與相依檔案
| 路徑 | 說明 |
| ------ | ------ |
| src/extract/171224/ | 各群包含的rid的txt檔 |
| src/extract/tsv_to_db.py | 新增mention、relationship、tablenode table的程式  |
| src/extract/process_duplicate.py | 移除duplicate及exclusion的module |
| utils/check_db.py| 檢查db格式是否正確 |
| utils/exclusion_append.py | 將輸入檔案append至exclusion.tsv |
| utils/exclusion_choice.py | 將輸入檔案轉化為方便人工篩選的csv格式 |
| utils/to_csv.py | 從資料庫中取出relationship table資料轉為csv檔做為分群的input |
| utils/cluster_process.py | 處理分群的output，和rid做對應，並整理出各群包含的rid，輸出為txt檔 |

### docs檔案
| 路徑 | 說明 |
| ------ | ------ |
| docs/emi_check.xlsx | 輸入et、ec、t&c三欄即可自動計算出調整後的EMI值 |
| docs/input.csv | 用來分群的input |
| docs/output.txt | 原始的分群結果 |
| docs/cluster_error.csv | 列出EMI值為零、自己一群的rid及其原因 |
| docs/cluster_num.txt | 紀錄各群包含的rid個數 |



### 遠端ftp與google drive連結(若install.sh失效，供手動下載)
1. FTP: ftp://140.112.107.150/UCSD/
2. Google Drive: http://goo.gl/3TYLnq
