import os

from config import Config
from libs.cli_output import console
from libs.sqldb import Sqldb


# 客户端
class WebsitesWorker:
    def __init__(self):
        self.id = Config.workers_id_local
        # 配置文件中的客户端id
        self.database_name = Config.database_name
        self.table_name = Config.workers_table_name_local
        self.worker_name = ''
        # w = websites_detail任务
        self.w_job_data_count = 0

    # 获取websites_detail的任务信息
    def get_websites_detail_job_info(self, str_job_table_name='websites_detail'):
        console(__name__, "connecting", self.database_name)
        # 查询数据用
        sqldb_query = Sqldb(self.database_name)
        console(__name__, self.database_name, "connected")
        # 根据程序配置文件中的客户端id和业务类型，查询要处理的任务信息
        sql_str = "SELECT name,job_data_count FROM " + self.table_name + " WHERE id=? AND job_table_name=?"
        sql_value = (self.id, str_job_table_name)
        result_worker = sqldb_query.fetchone(sql_str, sql_value)

        # 客户端名称，例如“#1, zap:docker, secblocks:kali, kali:pc”
        self.worker_name = result_worker[0]
        # 分配给此客户端的任务总数，例如1000个
        self.w_job_data_count = int(result_worker[1])

        # 关闭数据库
        sqldb_query.close()
        console(__name__, self.worker_name, str(self.w_job_data_count))

    # 显示所有worker的进度。单独做一个方法的原因是，用zap扫描的时候，打印的信息太多，
    # 看不到整体进度，不知道是否应该同步到远程postgresql数据库
    def show_workers_progress(self):
        # 假设数据库路径为 sec-blocks-1、2、3/sqlite.db
        for i in range(1, 4):
            str_db_path = '../sec-blocks-' + str(i) + '/sqlite.db'
            str_id = str(i)
            # 判断数据库文件是否存在
            if os.path.exists(str_db_path):
                sqldb_query = Sqldb(str_db_path)
                sql_str = "SELECT count(domain) FROM " + Config.domains_table_name + \
                          " WHERE worker_id=? AND target=1 AND synced=1"
                # 假设worker_id=1、2、3
                sql_value = (str_id,)
                result_count = sqldb_query.fetchone(sql_str, sql_value)
                console(__name__, str_db_path, str(result_count[0]))
                sqldb_query.close()
            else:
                console(__name__, str_db_path, "does not exist")
                pass
            pass
        pass
