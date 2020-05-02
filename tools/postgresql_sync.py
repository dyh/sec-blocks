# coding=utf-8
from config import Config
from libs.cli_output import console, console_progress
from libs.psqldb import Psqldb
from libs.sqldb import Sqldb


class PostgresqlSync:
    def __init__(self):
        # 本地SQLite数据库参数
        self.database_local = Config.database_name
        self.ips_table_name_local = Config.ips_table_name
        self.ports_table_name_local = Config.ports_table_name
        self.detail_table_name_local = Config.detail_table_name
        self.websites_table_name_local = Config.websites_table_name
        self.domains_table_name_local = Config.domains_table_name

        # 远程PostgreSQL数据库参数
        self.database_remote = Config.database_remote
        self.user_remote = Config.user_remote
        self.password_remote = Config.password_remote
        self.host_remote = Config.host_remote
        self.port_remote = Config.port_remote
        self.ips_table_name_remote = Config.ips_table_name_remote
        self.ports_table_name_remote = Config.ports_table_name_remote
        self.detail_table_name_remote = Config.detail_table_name_remote
        self.websites_table_name_remote = Config.websites_table_name_remote
        self.domains_table_name_remote = Config.domains_table_name_remote

        # 本地sqlite数据库
        self.sqlite_local = None
        # 远程PostgreSQL数据库
        self.postgresql_remote = None

    # 同步websites_detail表
    def sync_websites_detail_table(self):
        # 当前行数
        data_index = 0
        # 查询总行数
        sql_str = "SELECT count(domain) FROM " + self.websites_table_name_local + " WHERE synced=0"
        result_count = self.sqlite_local.fetchone(sql_str)

        # 总行数
        if result_count and int(result_count[0]) > 0:
            data_total = int(result_count[0])

            console(__name__, "synchronizing websites_detail table, rows count:", str(data_total))

            # 读取本地websites_detail表synced=0的数据
            sql_str = "SELECT domain,detail FROM " + self.websites_table_name_local + \
                      " WHERE synced=0 GROUP BY domain,detail ORDER BY domain ASC"
            result_query_local = self.sqlite_local.fetchall(sql_str)

            if result_query_local and len(result_query_local) > 0:
                for domain_tmp, detail_tmp in result_query_local:

                    if detail_tmp and len(detail_tmp) > 0:
                        # 更新远程websites_detail表，synced=-1
                        insert_sql_str_remote = "INSERT INTO " + self.websites_table_name_remote + \
                                                " (domain,detail,synced) VALUES (%s,%s,-1)"
                        insert_sql_value = (domain_tmp, detail_tmp)
                        self.postgresql_remote.execute_non_query(insert_sql_str_remote, insert_sql_value)
                        # 当前行
                        data_index = data_index + 1
                        # 打印进度和插入的数据
                        console_progress(data_index, data_total, __name__, domain_tmp, str(len(detail_tmp)))

                # 提交数据
                self.postgresql_remote.commit()

                # 更新本地websites_detail表，synced=0
                sql_str = "UPDATE " + self.websites_table_name_local + \
                          " SET synced=1 WHERE synced=0"
                self.sqlite_local.execute_non_query(sql_str)
                self.sqlite_local.commit()
                pass
            pass
        pass

    # 同步domains_list表
    def sync_domains_list_table(self):
        # 同步domains_list表
        data_index = 0
        # 查询总行数
        sql_str = "SELECT count(domain) FROM " + self.domains_table_name_local + " WHERE synced=0"
        result_count = self.sqlite_local.fetchone(sql_str)
        # 总行数
        if result_count and int(result_count[0]) > 0:
            data_total = int(result_count[0])

            console(__name__, "synchronizing domains_list table, rows count:", str(data_total))

            # 读取本地domains_list表synced=0的数据
            sql_str = "SELECT domain,scan_times,time FROM " + self.domains_table_name_local + \
                      " WHERE synced=0 ORDER BY domain ASC"
            result_query_local = self.sqlite_local.fetchall(sql_str)

            if result_query_local and len(result_query_local) > 0:
                for domain_tmp, scan_times_tmp, time_tmp in result_query_local:
                    if len(str(scan_times_tmp)) > 0:
                        # 更新远程domains_list表，synced=-1
                        update_sql_str_remote = "UPDATE " + self.domains_table_name_remote + \
                                                " SET scan_times=%s, synced=-1," \
                                                " time=%s WHERE domain=%s"
                        update_sql_value_remote = (scan_times_tmp, time_tmp, domain_tmp)
                        self.postgresql_remote.execute_non_query(update_sql_str_remote, update_sql_value_remote)

                        # 当前行
                        data_index = data_index + 1
                        # 打印进度和更新的数据
                        console_progress(data_index, data_total, __name__, domain_tmp, "scan_times: " +
                                         str(scan_times_tmp))
                        pass
                    pass
                pass

                # 提交数据
                self.postgresql_remote.commit()

                # 更新本地domains_list表，synced=1
                sql_str = "UPDATE " + self.domains_table_name_local + " SET synced=1 WHERE synced=0"
                self.sqlite_local.execute_non_query(sql_str)
                self.sqlite_local.commit()
                pass
            pass
        pass

    # 同步ports_detail表
    def sync_ports_detail_table(self):
        # 当前行数
        data_index = 0
        # 查询总行数
        sql_str = "SELECT count(ip) FROM " + self.detail_table_name_local + " WHERE synced=0"
        result_count = self.sqlite_local.fetchone(sql_str)

        # 总行数
        if result_count and int(result_count[0]) > 0:
            data_total = int(result_count[0])

            console(__name__, "synchronizing ports_detail table, rows count:", str(data_total))

            # 读取本地ports_list表synced=0的数据
            sql_str = "SELECT ip,detail FROM " + self.detail_table_name_local + \
                      " WHERE synced=0 GROUP BY ip,detail ORDER BY ip ASC"
            result_query_local = self.sqlite_local.fetchall(sql_str)

            if result_query_local and len(result_query_local) > 0:
                for ip_tmp, detail_tmp in result_query_local:

                    if detail_tmp and len(detail_tmp) > 0:
                        # 更新远程ports_list表，synced=-1
                        insert_sql_str_remote = "INSERT INTO " + self.detail_table_name_remote + \
                                                " (ip,detail,synced) VALUES (%s,%s,-1)"
                        insert_sql_value = (ip_tmp, detail_tmp)
                        self.postgresql_remote.execute_non_query(insert_sql_str_remote, insert_sql_value)
                        # 当前行
                        data_index = data_index + 1
                        # 打印进度和插入的数据
                        console_progress(data_index, data_total, __name__, ip_tmp, detail_tmp)
                        pass
                    pass
                pass
                # 提交数据
                self.postgresql_remote.commit()

                # 更新本地ports_list表
                sql_str = "UPDATE " + self.detail_table_name_local + " SET synced=1 WHERE synced=0"
                self.sqlite_local.execute_non_query(sql_str)
                self.sqlite_local.commit()
                pass
            pass
        pass

    # 同步ports_list表
    def sync_ports_list_table(self):
        # 当前行数
        data_index = 0
        # 查询总行数
        sql_str = "SELECT count(ip) FROM " + self.ports_table_name_local + " WHERE synced=0"
        result_count = self.sqlite_local.fetchone(sql_str)

        # 总行数
        if result_count and int(result_count[0]) > 0:
            data_total = int(result_count[0])

            console(__name__, "synchronizing ports_list table, rows count:", str(data_total))

            # 读取本地ports_list表synced=0的数据
            sql_str = "SELECT ip,list FROM " + self.ports_table_name_local + \
                      " WHERE synced=0 GROUP BY ip,list ORDER BY ip ASC"
            result_query_local = self.sqlite_local.fetchall(sql_str)

            if result_query_local and len(result_query_local) > 0:
                for ip_tmp, list_tmp in result_query_local:

                    if list_tmp and len(list_tmp) > 0:
                        # 更新远程ports_list表，synced=-1
                        insert_sql_str_remote = "INSERT INTO " + self.ports_table_name_remote + \
                                                " (ip,list,synced) VALUES (%s,%s,-1)"
                        insert_sql_value = (ip_tmp, list_tmp)
                        self.postgresql_remote.execute_non_query(insert_sql_str_remote, insert_sql_value)
                        # 当前行
                        data_index = data_index + 1
                        # 打印进度和插入的数据
                        console_progress(data_index, data_total, __name__, ip_tmp, list_tmp)
                        pass
                    pass
                pass

                # 提交数据
                self.postgresql_remote.commit()

                # 更新本地ports_list表
                sql_str = "UPDATE " + self.ports_table_name_local + \
                          " SET synced=1 WHERE synced=0"
                self.sqlite_local.execute_non_query(sql_str)
                self.sqlite_local.commit()
                pass
            pass
        pass

    # 同步ips_list表
    def sync_ips_list_table(self):
        # 同步ips_list表
        data_index = 0
        # 查询总行数
        sql_str = "SELECT count(ip) FROM " + self.ips_table_name_local + " WHERE synced=0"
        result_count = self.sqlite_local.fetchone(sql_str)
        # 总行数
        if result_count and int(result_count[0]) > 0:
            data_total = int(result_count[0])

            console(__name__, "synchronizing ips_list table, rows count:", str(data_total))

            # 读取本地ips_list表synced=0的数据
            sql_str = "SELECT ip,list_times,detail_times,time FROM " + self.ips_table_name_local + \
                      " WHERE synced=0 ORDER BY ip ASC"
            result_query_local = self.sqlite_local.fetchall(sql_str)

            if result_query_local and len(result_query_local) > 0:
                for ip_tmp, list_times_tmp, detail_times_tmp, time_tmp in result_query_local:
                    if len(str(list_times_tmp)) > 0 and len(str(detail_times_tmp)) > 0:
                        # 更新远程ips_list表
                        update_sql_str_remote = "UPDATE " + self.ips_table_name_remote + \
                                                " SET list_times=%s, detail_times=%s, synced=-1," \
                                                " time=%s WHERE ip=%s"
                        update_sql_value_remote = (list_times_tmp, detail_times_tmp, time_tmp, ip_tmp)
                        self.postgresql_remote.execute_non_query(update_sql_str_remote, update_sql_value_remote)

                        # 当前行
                        data_index = data_index + 1
                        # 打印进度和更新的数据
                        console_progress(data_index, data_total, __name__, ip_tmp, "list_times: " +
                                         str(list_times_tmp) + " | detail_times: " + str(detail_times_tmp))
                        pass
                    pass
                pass

                # 提交数据
                self.postgresql_remote.commit()

                # 更新本地ips_list表
                sql_str = "UPDATE " + self.ips_table_name_local + " SET synced=1 WHERE synced=0"
                self.sqlite_local.execute_non_query(sql_str)
                self.sqlite_local.commit()
                pass
            pass
        pass

    def run(self):
        # 连接本地SQLite数据库
        console(__name__, "connecting local SQLite", self.database_local)
        self.sqlite_local = Sqldb(self.database_local)
        console(__name__, "local SQLite", "connected")

        # 连接远程PostgreSQL数据库
        console(__name__, "connecting remote PostgreSQL", self.host_remote + ":" + self.port_remote)
        self.postgresql_remote = Psqldb(database=self.database_remote, user=self.user_remote,
                                        password=self.password_remote, host=self.host_remote, port=self.port_remote)
        console(__name__, "remote PostgreSQL", "connected")

        # 同步websites_detail表
        self.sync_websites_detail_table()

        # 同步domains_list表
        self.sync_domains_list_table()

        # 同步ports_detail表
        self.sync_ports_detail_table()

        # 同步ports_list表
        self.sync_ports_list_table()

        # 同步ips_list表
        self.sync_ips_list_table()

        # 关闭远端数据库
        self.postgresql_remote.close()

        # 关闭本地数据库
        self.sqlite_local.close()

        console(__name__, "synchronization has been completed!")
