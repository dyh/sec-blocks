# coding=utf-8
import logging
import subprocess
import time
from blocks.zap_block import ZapBlock
from config import Config
from libs.cli_output import console, console_progress
from libs.sqldb import Sqldb
from tools.websites_worker import WebsitesWorker


# 重启zap的docker
def restart_docker_zap(docker_name):
    subp = subprocess.Popen("docker restart " + docker_name, shell=True)
    subp.wait()
    subp.terminate()
    pass


# 截取中间的字符串
def get_middle_string(str_content='', begin='', end=''):
    start = str_content.find(begin)
    if start >= 0:
        start += len(begin)
        end = str_content.find(end, start)
        if end >= 0:
            return str_content[start:end].strip()
        else:
            return ''


class GetWebsitesDetail:
    def __init__(self):
        self.zap = None
        self.database_name = Config.database_name
        self.domains_table_name = Config.domains_table_name
        self.websites_table_name = Config.websites_table_name

    def run(self):
        try:
            self.scan()
        except Exception as e:
            str_exception = str(e)
            if "Max retries exceeded with url" in str_exception:
                # 找到端口号
                # HTTPConnectionPool(host='127.0.0.1', port=50501): Max
                # retries exceeded with url: http://zap/JSON/core/action/
                str_begin = 'HTTPConnectionPool(host=\'127.0.0.1\', port='
                str_end = '): Max retries exceeded with url:'
                str_port = get_middle_string(str_exception, str_begin, str_end)
                if str_port and len(str_port) > 0:
                    docker_container_name = 'zap' + str_port
                    # 重启zap的docker
                    restart_docker_zap(docker_container_name)
                    # 睡眠60秒，等待容器
                    console(__name__, 'time.sleep(120)')
                    time.sleep(120)
                    # 重启程序
                    self.run()
                else:
                    logging.exception(e)
                    console(__name__, 'restart docker failed!', str(e))
                pass
            else:
                # 其他错误打印出来
                logging.exception(e)
                console(__name__, 'zap dead, again...', str_exception)
                pass
        pass

    def scan(self):
        self.zap = ZapBlock(api_key=Config.zap_api_key, local_proxy_ip=Config.zap_proxy_ip,
                            local_proxy_port=Config.zap_proxy_port)
        # 初始化客户端
        worker_obj = WebsitesWorker()
        worker_obj.get_websites_detail_job_info(self.websites_table_name)

        console(__name__, "connecting", self.database_name)
        # 查询数据用
        sqldb_query = Sqldb(self.database_name)
        console(__name__, self.database_name, "connected")

        # 当前行数
        data_index = 0

        # target=是否为扫描目标, list_times=zap扫描次数，synced=是否已经与服务器端postgresql同步
        sql_str = "SELECT count(domain) FROM " + self.domains_table_name + \
                  " WHERE worker_id=? AND target=1 AND synced=1"
        sql_value = (worker_obj.id,)
        result_count = sqldb_query.fetchone(sql_str, sql_value)
        # 总行数
        data_total = int(result_count[0])
        # 关闭数据库
        sqldb_query.close()

        # 打印目标domain数量
        console(__name__, "target domain count", str(data_total))

        # 每页数据数量
        page_size = 10

        # 页码
        page_index = 0

        # 翻页循环的flag
        loop_flag = True

        # 从websites_detail表中，分页读取domain，用zap扫描
        # 因为扫描一次的速度较慢，所以这里的分页其实没有什么用处，复制粘贴来的代码，索性不改了
        while loop_flag:
            # 根据wordker_id，筛选出目标
            sql_str = "SELECT domain FROM " + self.domains_table_name + \
                      " WHERE worker_id=? AND target=1 AND synced=1 " \
                      " ORDER BY scan_times ASC, id ASC LIMIT ? OFFSET ?*?"

            sql_value = (worker_obj.id, page_size, page_index, page_size)

            # 查询数据用
            sqldb_query = Sqldb(self.database_name)
            result_query = sqldb_query.fetchall(sql_str, sql_value)

            if result_query and len(result_query) > 0:
                # 缓存到list里
                domains_list = []
                for domain_tmp in result_query:
                    domains_list.append(domain_tmp[0])

                # 关闭数据库
                sqldb_query.close()

                # domains_list
                for domain_item in domains_list:
                    # 测试用：
                    # domain_item = 'http://192.168.31.1/'
                    # 从数据库里读取domains，扫描，html报告的结果存入数据库
                    str_html = self.zap.single_scan(target_url=domain_item)

                    # 更新数据用
                    sqldb_update = Sqldb(self.database_name)

                    # 生成时间字符串
                    datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                    if str_html and len(str_html) > 0:
                        # 扫描结果，insert到domains_list表
                        insert_sql_str = "INSERT INTO " + self.websites_table_name + \
                                         " (domain,detail,synced,time) VALUES (?,?,0,?)"
                        insert_sql_value = (domain_item, str_html, datetime)
                        sqldb_update.execute_non_query(insert_sql_str, insert_sql_value)
                        # 打印扫描到的端口
                        console(__name__, domain_item, str(len(str_html)))

                    # 更新扫描次数
                    # 序号自增
                    data_index = data_index + 1
                    # 扫描次数自增+1
                    # 同步
                    update_sql_str = "UPDATE " + self.domains_table_name + \
                                     " SET scan_times=scan_times+1,synced=0,time=? WHERE domain=?"
                    update_sql_value = (datetime, domain_item)
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
                pass

        console(__name__, "jobs", "done!")
        pass
