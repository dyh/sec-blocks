# coding=utf-8
import logging

import psycopg2

from blocks.zap_block import ZapBlock
from config import Config
from libs.cli_output import console, console_progress
from libs.psqldb import Psqldb


class GetWebsitesDetail:

    def __init__(self):
        self.zap = ZapBlock(api_key=Config.zap_api_key, local_proxy_ip=Config.zap_proxy_ip,
                            local_proxy_port=Config.zap_proxy_port)
        self.database = Config.database_local
        self.user = Config.user_local
        self.password = Config.password_local
        self.host = Config.host_local
        self.port = Config.port_local
        self.domains_table_name = Config.domains_table_name_local
        self.websites_table_name = Config.websites_table_name_local

    def run(self):
        console(__name__, "connecting PostgreSQL", self.host + ":" + self.port)

        # 查询数据用
        sqldb_query = Psqldb(database=self.database, user=self.user,
                             password=self.password, host=self.host, port=self.port)

        console(__name__, "PostgreSQL", "connected")

        # 当前行数
        data_index = 0

        # target=是否为扫描目标, list_times=port扫描次数, time=数据更新的日期时间
        sql_str = "SELECT count(domain) FROM " + self.domains_table_name + \
                  " WHERE target=1 AND synced=1 AND org_name LIKE %s"
        sql_value = ("%公司",)
        result_count = sqldb_query.fetchone(sql_str, sql_value)
        # 总行数
        data_total = int(result_count[0])
        # 关闭数据库
        sqldb_query.close()

        # 打印总ip数量
        console(__name__, "target domain count", str(data_total))

        # 每页数据数量
        page_size = 1

        # 页码
        page_index = 0

        # 翻页循环的flag
        loop_flag = True

        # 从websites_detail表中，分页读取domain，用zap扫描
        while loop_flag:
            try:
                # 分页读取，表ips_all里的数据，筛选"公司"的ip
                sql_str = "SELECT domain FROM " + self.domains_table_name + \
                          " WHERE target=1 AND synced=1 AND org_name LIKE %s " \
                          " ORDER BY scan_times ASC, id ASC LIMIT %s OFFSET %s*%s"

                sql_value = ("%公司", page_size, page_index, page_size)

                # 查询数据用
                sqldb_query = Psqldb(database=self.database, user=self.user,
                                     password=self.password, host=self.host, port=self.port)
                result_query = sqldb_query.fetchall(sql_str, sql_value)

                if result_query and len(result_query) > 0:
                    domains_list = []
                    for domain_tmp in result_query:
                        domains_list.append(domain_tmp[0])

                    # 关闭数据库
                    sqldb_query.close()

                    # domains_list
                    for domain_item in domains_list:
                        # 从数据库里读取domains，扫描，html报告的结果存入数据库
                        str_html = self.zap.single_scan(target_url=domain_item)

                        # 更新数据用
                        sqldb_update = Psqldb(database=self.database, user=self.user,
                                              password=self.password, host=self.host, port=self.port)

                        if str_html and len(str_html) > 0:
                            # 扫描结果，insert到domains_list表
                            insert_sql_str = "INSERT INTO " + self.websites_table_name + \
                                             " (domain,detail,synced) VALUES (%s,%s,0)"
                            insert_sql_value = (domain_item, str_html)
                            sqldb_update.execute_non_query(insert_sql_str, insert_sql_value)
                            # 打印扫描到的端口
                            console(__name__, domain_item, str(len(str_html)))

                        # 更新扫描次数
                        # 序号自增
                        data_index = data_index + 1
                        # 扫描次数自增+1
                        # 同步
                        update_sql_str = "UPDATE " + self.domains_table_name + \
                                         " SET scan_times=scan_times+1,synced=0,time=CURRENT_TIMESTAMP WHERE domain=%s"
                        update_sql_value = (domain_item,)
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

        pass
