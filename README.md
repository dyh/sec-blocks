
# sec-blocks
Security Blocks - 安全积木

像搭建积木一样刷SRC

```
 ____            ____  _            _        
/ ___|  ___  ___| __ )| | ___   ___| | _____ 
\___ \ / _ \/ __|  _ \| |/ _ \ / __| |/ / __|
 ___) |  __/ (__| |_) | | (_) | (__|   <\__ \
|____/ \___|\___|____/|_|\___/ \___|_|\_\___/
                                             

usage: sec-blocks.py [-h] [-l] [-d] [-w] [-s] [-ti] [-td]

SecBlocks V0.0.1

optional arguments:
  -h, --help            show this help message and exit
  -l, --ports_list      get open ports of targets
  -d, --ports_detail    get detail of ports
  -w, --websites_detail
                        get detail of websites
  -s, --database_sync   synchronize remote postgresql
  -ti, --txtfile_ip_to_database
                        insert [ip] into postgresql
  -td, --txtfile_domain_to_database
                        insert [domain] into postgresql
```


### 如何使用
0. 在kali linux下，用conda配置运行环境
    ```
    conda env create -f conda-export.yaml
    ```

1. 启动kali linux自带的PostgreSQL数据库，并创建表结构
    ```
    数据库结构文件：postgresql_table_structs.sql
    ```

2. 下载补天公益SRC列表
    ```
    https://github.com/m4yfly/butian-src-domains/raw/master/files/out/targets.txt
    ```

3. 更改配置文件
    ```
    config.py
    ```

4. 将SRC的IP导入数据库
    ```
    python sec-blocks.py -ti
    ```
   
5. 扫描SRC的开放端口
    ```
    python sec-blocks.py -l
    ```

6. 扫描SRC的开放端口的详细信息
    ```
    python sec-blocks.py -d
    ```

7. 将SRC的域名导入数据库
    ```
    python sec-blocks.py -td
    ```
   
8. 扫描SRC的网站详细信息
    ```
    python sec-blocks.py -w
    ```
   
9. 同步本地PostgreSQL数据到远程的PostgreSQL数据库
    ```
    python sec-blocks.py -s
    ```