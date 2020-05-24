
# sec-blocks
Security Blocks - 安全积木

像搭建积木一样检测网络安全

```
 ____            ____  _            _        
/ ___|  ___  ___| __ )| | ___   ___| | _____ 
\___ \ / _ \/ __|  _ \| |/ _ \ / __| |/ / __|
 ___) |  __/ (__| |_) | | (_) | (__|   <\__ \
|____/ \___|\___|____/|_|\___/ \___|_|\_\___/
                                             

usage: sec-blocks.py [-h] [-l] [-d] [-w] [-s] [-ti] [-td]

SecBlocks V0.0.2

optional arguments:
  -h, --help            show this help message and exit
  -l, --ports_list      get open ports of targets
  -d, --ports_detail    get detail of ports
  -w, --websites_detail
                        get detail of websites
  -s, --database_sync   synchronize remote postgresql
  -ti, --txt_ip_to_db   insert [ip] into sqlite
  -td, --txt_domain_to_db
                        insert [domain] into sqlite
```

### 如何使用
1. 安装，在Raspberry Pi或kali linux中，使用pip安装如下包
    ```
    $pip list
    Package               Version
    --------------------- ----------
    certifi               2020.4.5.1
    chardet               3.0.4
    idna                  2.9
    pip                   20.1.1
    psycopg2-binary       2.8.5
    pyfiglet              0.8.post1
    python-masscan        0.1.6
    python-nmap           0.6.1
    python-owasp-zap-v2.4 0.0.16
    requests              2.23.0
    setuptools            46.4.0
    six                   1.15.0
    urllib3               1.25.9
    ```

2. 下载SRC列表到"sec-blocks"目录
    ```
    https://github.com/m4yfly/butian-src-domains/raw/master/files/out/targets.txt
    ```

3. 将SRC的IP导入数据库
    ```
    python3 sec-blocks.py -ti
    ```

4. 将SRC的域名导入数据库
    ```
    python3 sec-blocks.py -td
    ```

5. 扫描SRC的开放端口列表
    ```
    python3 sec-blocks.py -l
    ```

6. 扫描SRC的端口详细信息
    ```
    python3 sec-blocks.py -d
    ```
   
7. 扫描SRC的网站详细信息
    ```
    - 启动 OWASP ZAP 执行：zap.sh -daemon -host 0.0.0.0 -port 50501 -config api.addrs.addr.name=.* -config api.addrs.addr.regex=true -config api.key=oh804vn496tg1fpvf2f3bsgldm
    - 启动检测：python3 sec-blocks.py -w
    - 查看进度：python3 sec-blocks.py -wp
    ```

8. 同时启动多个实例
    ```
    如需同时启动多个实例进行检测，请拷贝目录[sec-blocks]中的所有文件到新的文件夹，然后：
    - 修改配置文件"config.py"的"workers_id_local = 2"
    - 修改数据库[sqlite.db]-->表[workers]-->字段[id]值，增加或者修改一行记录"id=2"
    - 批量修改数据库[sqlite.db]-->表[domains_list]-->字段[worker_id]值。例如，把其中的1000行数据设置为"worker_id=2"
    - 输入"python sec-blocks.py -w"启动检测
    ```
   
9. 同步本地SQLite数据库到远程的PostgreSQL数据库
    ```
    - 启动kali linux自带的PostgreSQL数据库
    - 根据数据库结构文件"postgresql_table_structs.sql"创建表结构
    - 执行python3 sec-blocks.py -s
    ```
