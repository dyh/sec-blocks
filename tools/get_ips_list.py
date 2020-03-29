# coding=utf-8
from config import Config
from libs.cli_output import console_progress
from libs.psqldb import Psqldb
from libs.cli_output import console

'''txt文件格式 targets.txt
 {"name": "x公司", "url": "https://www.butian.net/Loo/submit?cid=x", "domain2ip": {
"http://x.x.cn": ["192.168.1.x"], "http://www.x.cn": ["192.168.1.x"], "http://x.x.cn": ["192.168.1.x"], 
"http://x.cn": ["192.168.1.x"]}} {"name": "xx公司", "url": "https://www.butian.net/Loo/submit?cid=xx", "domain2ip": {
"http://xx.xx.xx.cn": ["192.168.1.x"]}} {"name": "xxx公司", "url": "https://www.butian.net/Loo/submit?cid=xxx", 
"domain2ip": {"http://xxx.xxx.cn": ["192.168.1.x"], "http://x.xxx.cn": ["192.168.1.x"], "http://xx.xxx.cn": [
"192.168.1.x"]}} '''


# 域名文本文件转到postgresql数据库，将ip存储到表ips_all
class GetIpsList:
    def __init__(self, txt_filename=""):
        # 将要读取的文本文件路径
        self.txt_filename = txt_filename

        self.database = Config.database_local
        self.user = Config.user_local
        self.password = Config.password_local
        self.host = Config.host_local
        self.port = Config.port_local
        self.table_name = Config.ips_table_name_local
        console(__name__, self.database, self.table_name)

    def run(self):
        # 查询数据用
        sqldb_query = Psqldb(database=self.database, user=self.user,
                             password=self.password, host=self.host, port=self.port)
        # 更新数据用
        sqldb_update = Psqldb(database=self.database, user=self.user,
                              password=self.password, host=self.host, port=self.port)

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
                    # str_domain_name = str(key)
                    # str_ip = str(value)

                    for ip_item in value:
                        str_ip = ip_item

                        sql_str = "SELECT ID FROM " + self.table_name + " WHERE ip=%s LIMIT 1"
                        sql_value = (str_ip,)
                        result_query = sqldb_query.fetchone(sql_str, values=sql_value)

                        if not result_query:
                            sql_str = "INSERT INTO " + self.table_name + " (ip,org_name) VALUES (%s,%s)"
                            sql_value = (str_ip, str_org_name)
                        else:
                            sql_str = "UPDATE " + self.table_name + " SET org_name=%s WHERE ip=%s"
                            sql_value = (str_org_name, str_ip)

                        sqldb_update.execute_non_query(sql_str, values=sql_value)
                        sqldb_update.commit()

                        console_progress(row_index, rows_total, __name__, str_ip, str_org_name)

                row_index = 1 + row_index

        f.close()

        sqldb_update.close()
        sqldb_query.close()

    # '''
    # ips_all表结构
    # -- ----------------------------
    # -- Table structure for ips_all
    # -- ----------------------------
    # CREATE TABLE IF NOT EXISTS "ips_all" (
    #   "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    #   "ip" text NOT NULL,
    #   "domain" text,
    #   "org_name" text,
    #   "is_actived" integer,
    #   "is_exploited" integer,
    #   "open_ports" text,
    #   "ports_info" text,
    #   "time" text
    # );
    # '''
    # def create_table_domains_all(self):
    #     sqldb = Psqldb(database=self.database, user=self.user, password=self.password, host=self.host, port=self.port)
    #
    #     sql = """
    #     CREATE TABLE IF NOT EXISTS "{}" (
    #       "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    #       "ip" text NOT NULL,
    #       "domain" text,
    #       "org_name" text,
    #       "is_actived" integer,
    #       "is_exploited" integer,
    #       "open_ports" text,
    #       "ports_info" text,
    #       "time" text
    #     );
    #     """.format(self.table_name)
    #
    #     sqldb.execute_non_query(sql)
    #     sqldb.commit()
    #     sqldb.close()

    # # 删除表
    # def drop_table_domains_all(self):
    #     sqldb = Psqldb(database=self.database, user=self.user, password=self.password, host=self.host, port=self.port)
    #     sqldb.drop_table(self.table_name)
    #     sqldb.commit()
    #     sqldb.close()

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
