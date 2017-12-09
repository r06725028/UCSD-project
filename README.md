# UCSD-project

### 安裝

```sh
$ git clone https://github.com/r06725028/UCSD-project.git
$ cd UCSD-project # 下載產生db之檔案 & 產生圖表之db (皆非必要)
$ sh install.sh
```

### Usage

```sh
$ python3 extract/men_rel.py extract/node.py # 產生db
```

### 目錄
* docs/ : 留存文件
* sample_file/ : 範例檔案 (ex: 路徑_[input | output])
* src/ : 圖表、資料庫生成的原始碼
* utils/ : 臨時需求的原始碼

### 程式碼與相依檔案(src/)
| 路徑 | 說明 |
| ------ | ------ |
| extract/20171019/ | 分成30群的txt檔 |
| src/extract/node.py | 新增node table的程式  |
| src/extract/men_rel.py | 新增mention、relationship table的程式 |
| src/extract/process_duplicate.py | 移除duplicate及exclusion的module |
| utils/exclusion_append.py | 將輸入檔案append至exclusion.tsv |
| utils/exclusion_choice.py | 將輸入檔案轉化為方便人工篩選的csv格式 |

### 遠端ftp與google drive連結
1. FTP [USCD目錄](ftp://140.112.107.148/UCSD/)
2. newdb.db所在的[雲端硬碟連結](https://drive.google.com/file/d/1Pdlg_IOHJ1OrctheDo8N0P9voRDXGLvH/view?usp=sharing)
