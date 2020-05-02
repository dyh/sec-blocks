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
