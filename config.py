# coding:utf-8


class Config:
    # 客户端ID
    # 如需同时启动多个owasp zap进行检测，请修改数据库[sqlite.db]中，表[workers]的字段[workers.id]值
    workers_id_local = 1

    # zap的apikey
    zap_api_key = 'oh804vn496tg1fpvf2f3bsgldm'
    zap_proxy_ip = '127.0.0.1'
    zap_proxy_port = '50501'

    # 本地数据库文件
    database_name = "sqlite.db"
    # 本地数据库默认参数
    workers_table_name_local = "workers"
    ips_table_name = "ips_list"
    ports_table_name = "ports_list"
    detail_table_name = "ports_detail"
    domains_table_name = "domains_list"
    websites_table_name = "websites_detail"

    # 如果不使用远程同步功能[-s]，不用修改以下参数
    # 远程postgresql数据库参数
    database_remote = "secblocks"
    user_remote = "username1"
    password_remote = "password1"
    host_remote = "1.1.1.1"
    port_remote = "5432"
    # postgresql的表名
    ips_table_name_remote = "ips_list"
    ports_table_name_remote = "ports_list"
    detail_table_name_remote = "ports_detail"
    domains_table_name_remote = "domains_list"
    websites_table_name_remote = "websites_detail"
