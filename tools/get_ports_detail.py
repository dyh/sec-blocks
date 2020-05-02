# coding=utf-8
import time
from blocks.nmap_block import NmapBlock
from config import Config
from libs.cli_output import console, console_progress
from libs.sqldb import Sqldb


class GetPortsDetail:

    def __init__(self):
        self.database_name = Config.database_name
        self.ips_table_name = Config.ips_table_name
        self.ports_table_name = Config.ports_table_name
        self.detail_table_name = Config.detail_table_name

    def run(self):
        console(__name__, "connecting", self.database_name)
        # 查询数据用
        sqldb_query = Sqldb(self.database_name)
        console(__name__, "SQLite", "connected")

        # 当前行数
        data_index = 0
        # target=是否为扫描目标
        # sql_str = "SELECT count(ip) FROM " + self.ips_table_name + " WHERE target=1 AND org_name LIKE %s"
        sql_str = "SELECT COUNT(" + self.ports_table_name + ".ip) FROM " + self.ports_table_name + \
                  " INNER JOIN " + self.ips_table_name + " ON " + self.ports_table_name + ".ip=" + \
                  self.ips_table_name + ".ip AND " + self.ips_table_name + ".target=1 AND " + \
                  self.ips_table_name + ".synced=1 AND " + self.ips_table_name + ".org_name LIKE ?"
        sql_value = ("%公司",)
        result_count = sqldb_query.fetchone(sql_str, sql_value)

        # 总行数
        data_total = int(result_count[0])

        # 关闭数据库
        sqldb_query.close()

        # 打印总ip数量
        console(__name__, "target ip total", str(data_total))

        # 每页数据数量
        page_size = 10

        # 页码
        page_index = 0

        # 翻页循环的flag
        loop_flag = True

        nm = NmapBlock()
        # 从ip_all表中，分页读取IP和端口，用nmap扫描
        while loop_flag:
            # 分页读取
            sql_str = "SELECT " + self.ports_table_name + ".ip, " + self.ports_table_name + ".list FROM " + \
                      self.ports_table_name + " INNER JOIN " + self.ips_table_name + " ON " + \
                      self.ports_table_name + ".ip=" + self.ips_table_name + ".ip AND " + \
                      self.ips_table_name + ".target=1 AND " + self.ips_table_name + \
                      ".synced=1 AND " + self.ips_table_name + ".org_name LIKE ? ORDER BY " + \
                      self.ips_table_name + ".detail_times, " + self.ports_table_name + \
                      ".id LIMIT ? OFFSET ?*? "

            # SELECT ports_list.ip, ports_list.list FROM ports_list INNER JOIN ips_list ON
            # ports_list.ip=ips_list.ip AND ips_list.target=1 AND ips_list.synced=1 AND
            # ips_list.org_name LIKE '%公司' ORDER BY ips_list.detail_times, ports_list.id

            sql_value = ("%公司", page_size, page_index, page_size)
            # 查询数据用
            sqldb_query = Sqldb(self.database_name)
            result_query = sqldb_query.fetchall(sql_str, sql_value)

            if result_query and len(result_query) > 0:
                # 关闭数据库
                sqldb_query.close()
                for ip_tmp, ports_tmp in result_query:
                    # open_ports存储打开的端口号list[]
                    dict_ports_info = {}

                    # if len(ports_tmp) > 1000:
                    #     # 字符串太长的，开放大量端口的主机，不扫描
                    #     console(__name__, "too many open ports", str(len(ports_tmp)))
                    # else:

                    # 获取到ip，传递给nmap扫描端口
                    # ip_tmp = "192.168.31.1"
                    dict_temp = nm.single_scan(target_ip=ip_tmp, target_port=ports_tmp,
                                               arguments="-O -n -sS -sV -T4")

                    # 更新数据用
                    sqldb_update = Sqldb(self.database_name)

                    # 生成时间字符串
                    datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                    if dict_temp and len(dict_temp) > 0:
                        # 因为只扫描一个ip，所以循环一次即获得全部值
                        for value1 in dict_temp.values():
                            dict_ports_info = value1
                            break
                        insert_sql_str = "INSERT INTO " + self.detail_table_name + \
                                         " (ip,detail,synced,time) VALUES (?,?,0,?)"
                        insert_sql_value = (ip_tmp, str(dict_ports_info), datetime)
                        sqldb_update.execute_non_query(insert_sql_str, insert_sql_value)

                        # 打印扫描到的端口
                        console(__name__, ip_tmp, str(dict_ports_info))

                    # 同步 detail_times 端口详细信息的扫描次数
                    update_sql_str = "UPDATE " + self.ips_table_name + \
                                     " SET detail_times=detail_times+1,synced=0," \
                                     "time=? WHERE ip=?"
                    update_sql_value = (datetime, ip_tmp)
                    sqldb_update.execute_non_query(update_sql_str, update_sql_value)
                    # 提交数据
                    sqldb_update.commit()
                    # 关闭数据库
                    sqldb_update.close()

                    # 序号自增
                    data_index = data_index + 1
                    # 打印进度
                    console_progress(data_index, data_total, __name__)
            else:
                loop_flag = False
                # 关闭数据库
                sqldb_query.close()
