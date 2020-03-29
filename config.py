# coding:utf-8


class Config:
    database_local = "secblocks"
    user_local = "username"
    password_local = "your_password"
    host_local = "127.0.0.1"
    port_local = "5432"
    ips_table_name_local = "ips_list"
    ports_table_name_local = "ports_list"
    detail_table_name_local = "ports_detail"
    domains_table_name_local = "domains_list"
    websites_table_name_local = "websites_detail"

    # 远程postgresql数据库参数
    database_remote = "secblocks"
    user_remote = "username"
    password_remote = "your_password"
    host_remote = "remote_postgresql_address"
    port_remote = "5432"
    ips_table_name_remote = "ips_list"
    ports_table_name_remote = "ports_list"
    detail_table_name_remote = "ports_detail"
    domains_table_name_remote = "domains_list"
    websites_table_name_remote = "websites_detail"

    # zap的apikey
    zap_api_key = 'your_zap_api_key'
    zap_proxy_ip = '127.0.0.1'
    zap_proxy_port = '8080'

