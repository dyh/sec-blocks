# coding=utf-8
import logging
import psycopg2

from blocks.masscan_block import MasscanBlock
from config import Config
from libs.cli_output import console, console_progress
from libs.psqldb import Psqldb


class GetPortsList:

    def __init__(self):

        self.database = Config.database_local
        self.user = Config.user_local
        self.password = Config.password_local
        self.host = Config.host_local
        self.port = Config.port_local
        self.ips_table_name = Config.ips_table_name_local
        self.ports_table_name = Config.ports_table_name_local

    def run(self):
        console(__name__, "connecting PostgreSQL", self.host + ":" + self.port)

        # 查询数据用
        sqldb_query = Psqldb(database=self.database, user=self.user,
                             password=self.password, host=self.host, port=self.port)

        console(__name__, "PostgreSQL", "connected")

        # 当前行数
        data_index = 0

        # target=是否为扫描目标, list_times=port扫描次数, time=数据更新的日期时间
        sql_str = "SELECT count(ip) FROM " + self.ips_table_name + \
                  " WHERE target=1 AND synced=1 AND org_name LIKE %s"
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
            try:
                # 分页读取，表ips_all里的数据，筛选"公司"的ip
                sql_str = "SELECT ip FROM " + self.ips_table_name + \
                          " WHERE target=1 AND synced=1 AND org_name LIKE %s " \
                          " ORDER BY list_times ASC, id ASC LIMIT %s OFFSET %s*%s"

                sql_value = ("%公司", page_size, page_index, page_size)

                # 查询数据用
                sqldb_query = Psqldb(database=self.database, user=self.user,
                                     password=self.password, host=self.host, port=self.port)
                result_query = sqldb_query.fetchall(sql_str, sql_value)

                if result_query and len(result_query) > 0:
                    # 组成ip的list，传递给masscan，批量扫描
                    list_ips = []
                    for ip_tmp in result_query:
                        list_ips.append(ip_tmp[0])

                    # 关闭数据库
                    sqldb_query.close()

                    # 获取到ip，传递给masscan扫描1-65535端口
                    dict_temp = mas.batch_scan(list_ips, "1-65535", "--max-rate 10000")

                    # 更新数据用
                    sqldb_update = Psqldb(database=self.database, user=self.user,
                                          password=self.password, host=self.host, port=self.port)

                    if dict_temp and len(dict_temp) > 0:
                        # 扫描结果，insert到表ports_list表的list字段
                        for key1, value1 in dict_temp.items():
                            # ips_list存储打开的端口号list[]
                            list_open_ports = list(value1["tcp"].keys())
                            insert_sql_str = "INSERT INTO " + self.ports_table_name + \
                                             " (ip,list,synced) VALUES (%s,%s,0)"
                            insert_sql_value = (key1, str(list_open_ports))
                            sqldb_update.execute_non_query(insert_sql_str, insert_sql_value)
                            # 打印扫描到的端口
                            console(__name__, key1, str(list_open_ports))

                    # 更新扫描次数
                    for item in list_ips:
                        # 序号自增
                        data_index = data_index + 1
                        # 扫描次数自增+1
                        # 同步
                        update_sql_str = "UPDATE " + self.ips_table_name + \
                                         " SET list_times=list_times+1,synced=0,time=CURRENT_TIMESTAMP WHERE ip=%s"
                        update_sql_value = (item,)
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

            except psycopg2.OperationalError as e:
                logging.exception(e)
                console(__name__, "except psycopg2.OperationalError as e")
            except Exception as e:
                logging.exception(e)
                console(__name__, "except Exception as e")

        console(__name__, "jobs", "done!")
