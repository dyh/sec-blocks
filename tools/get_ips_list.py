# coding=utf-8
import time
from config import Config
from libs.cli_output import console_progress
from libs.cli_output import console
from libs.sqldb import Sqldb

'''txt文件格式 targets.txt
 {"name": "x公司", "url": "https://www.butian.net/Loo/submit?cid=x", "domain2ip": {
"http://x.x.cn": ["192.168.1.x"], "http://www.x.cn": ["192.168.1.x"], "http://x.x.cn": ["192.168.1.x"], 
"http://x.cn": ["192.168.1.x"]}} {"name": "xx公司", "url": "https://www.butian.net/Loo/submit?cid=xx", "domain2ip": {
"http://xx.xx.xx.cn": ["192.168.1.x"]}} {"name": "xxx公司", "url": "https://www.butian.net/Loo/submit?cid=xxx", 
"domain2ip": {"http://xxx.xxx.cn": ["192.168.1.x"], "http://x.xxx.cn": ["192.168.1.x"], "http://xx.xxx.cn": [
"192.168.1.x"]}} '''


# 域名文本文件转到sqlite数据库，将ip存储到表ips_all
class GetIpsList:
    def __init__(self, txt_filename=""):
        # 将要读取的文本文件路径
        self.txt_filename = txt_filename
        self.database_name = Config.database_name
        self.table_name = Config.ips_table_name
        console(__name__, self.database_name, self.table_name)

    def run(self):
        console(__name__, "connecting", self.database_name)
        # 查询数据用
        sqldb_query = Sqldb(self.database_name)
        # 更新数据用
        sqldb_update = Sqldb(self.database_name)
        console(__name__, "SQLite", "connected")

        # 当前行数
        row_index = 0
        # 总行数
        rows_total = self.get_file_rows_count()

        # 逐行读取txt文件
        with open(self.txt_filename, "r", encoding="utf-8") as f:

            while True:
                line = f.readline()
                if not line:
                    break

                # 解析字符串，写入数据库
                dict_tmp = eval(line)
                str_org_name = dict_tmp["name"]

                for key, value in dict_tmp["domain2ip"].items():
                    for ip_item in value:
                        str_ip = ip_item
                        sql_str = "SELECT ID FROM " + self.table_name + " WHERE ip=? LIMIT 1"
                        sql_value = (str_ip,)
                        result_query = sqldb_query.fetchone(sql_str, values=sql_value)

                        # 生成时间字符串
                        datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                        if result_query and len(result_query) > 0:
                            sql_str = "UPDATE " + self.table_name + " SET org_name=?, time=? WHERE ip=?"
                            sql_value = (str_org_name, datetime, str_ip)
                        else:
                            sql_str = "INSERT INTO " + self.table_name + " (ip,org_name,time) VALUES (?,?,?)"
                            sql_value = (str_ip, str_org_name, datetime)

                        sqldb_update.execute_non_query(sql_str, values=sql_value)
                        sqldb_update.commit()

                        console_progress(row_index, rows_total, __name__, str_ip, str_org_name)
                row_index = 1 + row_index
        f.close()

        sqldb_update.close()
        sqldb_query.close()

    # 统计文件行数
    def get_file_rows_count(self):
        total = 0
        with open(self.txt_filename, "r", encoding="utf-8") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                total = 1 + total
        f.close()
        return total
