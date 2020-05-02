# coding=utf-8
import time
from blocks.masscan_block import MasscanBlock
from config import Config
from libs.cli_output import console, console_progress
from libs.sqldb import Sqldb


class GetPortsList:

    def __init__(self):
        self.database_name = Config.database_name
        self.ips_table_name = Config.ips_table_name
        self.ports_table_name = Config.ports_table_name

    def run(self):
        console(__name__, "connecting", self.database_name)
        # 查询数据用
        sqldb_query = Sqldb(self.database_name)
        console(__name__, "SQLite", "connected")

        # 当前行数
        data_index = 0

        # target=是否为扫描目标, list_times=port扫描次数, time=数据更新的日期时间
        sql_str = "SELECT count(ip) FROM " + self.ips_table_name + \
                  " WHERE target=1 AND synced=1 AND org_name LIKE ?"
        sql_value = ("%公司",)
        result_count = sqldb_query.fetchone(sql_str, sql_value)
        # 总行数
        data_total = int(result_count[0])
        # 关闭数据库
        sqldb_query.close()

        # 打印总ip数量
        console(__name__, "target ip count", str(data_total))

        # 每页数据数量
        page_size = 20

        # 页码
        page_index = 0

        # 翻页循环的flag
        loop_flag = True

        mas = MasscanBlock()

        # 从ip_all表中，分页读取IP和端口，用masscan扫描
        while loop_flag:
            # 分页读取，表ips_all里的数据，筛选"公司"的ip
            sql_str = "SELECT ip FROM " + self.ips_table_name + \
                      " WHERE target=1 AND synced=1 AND org_name LIKE ? " \
                      " ORDER BY list_times ASC, id ASC LIMIT ? OFFSET ?*?"

            sql_value = ("%公司", page_size, page_index, page_size)

            # 查询数据用
            sqldb_query = Sqldb(self.database_name)
            result_query = sqldb_query.fetchall(sql_str, sql_value)

            if result_query and len(result_query) > 0:
                # 组成ip的list，传递给masscan，批量扫描
                list_ips = []
                for ip_tmp in result_query:
                    list_ips.append(ip_tmp[0])
                    pass

                # 关闭数据库
                sqldb_query.close()

                # 获取到ip，传递给masscan扫描1-65535端口
                dict_temp = mas.batch_scan(list_ips, "1-65535", "--max-rate 10000")

                # 更新数据用
                sqldb_update = Sqldb(self.database_name)

                # 生成时间字符串
                datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                if dict_temp and len(dict_temp) > 0:
                    # 扫描结果，insert到表ports_list表的list字段
                    for key1, value1 in dict_temp.items():
                        # ips_list存储打开的端口号list[]
                        list_open_ports = list(value1["tcp"].keys())
                        insert_sql_str = "INSERT INTO " + self.ports_table_name + \
                                         " (ip,list,synced,time) VALUES (?,?,0,?)"
                        insert_sql_value = (key1, str(list_open_ports), datetime)
                        sqldb_update.execute_non_query(insert_sql_str, insert_sql_value)
                        # 打印扫描到的端口
                        console(__name__, key1, str(list_open_ports))

                # 更新扫描次数
                for ip_item in list_ips:
                    # 序号自增
                    data_index = data_index + 1
                    # 扫描次数自增+1
                    # 同步
                    update_sql_str = "UPDATE " + self.ips_table_name + \
                                     " SET list_times=list_times+1,synced=0,time=? WHERE ip=?"
                    update_sql_value = (datetime, ip_item)
                    sqldb_update.execute_non_query(update_sql_str, update_sql_value)

                # 提交数据
                sqldb_update.commit()
                # 关闭数据库
                sqldb_update.close()

                # 打印进度
                console_progress(data_index, data_total, __name__)
            else:
                loop_flag = False
                # 关闭数据库
                sqldb_query.close()

        console(__name__, "jobs", "done!")
