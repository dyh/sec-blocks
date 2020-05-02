# coding=utf-8
import logging
import os
import masscan

from libs.cli_output import console


class MasscanBlock:
    def __init__(self):
        self.mas = masscan.PortScanner()
        self.temp_file = "masscan_temp_file.txt"

        # 不打印debug信息
        masscan.logger.setLevel(logging.ERROR)
        pass

    # 相同端口的批量扫描，传入ip的list，返回 ip-端口 的字典
    def batch_scan(self, list_target_ip, target_port="1-65535", arguments="--max-rate 5000"):
        # 扫描结果
        dict_return = {}

        # 用换行符 join list，写入临时文件
        str_txt_content = "\n".join(list_target_ip)
        f_temp = open(self.temp_file, 'w')
        f_temp.write(str_txt_content)
        f_temp.close()

        # 尝试读或扫描结果
        dict_scan_result_tmp = None

        # 解析此ip下，要扫描的端口，例如 '1-65535'，或'8009'
        try:
            # str_arguments = ' --includefile {0} {1} '.format("1.txt", arguments)
            str_arguments = ' --includefile {0} {1} '.format(self.temp_file, arguments)
            console(__name__, "scanning " + str(len(list_target_ip)) + " hosts, ports: " + target_port, str_arguments)
            self.mas.scan('', ports=target_port, arguments=str_arguments)

            try:
                dict_scan_result_tmp = self.mas.scan_result
            except Exception as e:
                # Do a scan before trying to get result !
                if "Do a scan before trying to get result !" == str(e):
                    # 如果只是没扫到开放的端口，则忽略
                    console(__name__, "exception", str(e))
                    pass
                else:
                    # 其他错误打印出来
                    logging.exception(e)
                    console(__name__, "error", str(e))

        except Exception as e:
            # network is unreachable.
            if "network is unreachable." == str(e):
                # 如果只是无法访问目标主机，则忽略
                console(__name__, "exception", str(e))
                pass
            else:
                # 其他错误打印出来
                logging.exception(e)
                console(__name__, "error", str(e))

        # 扫描结果存入dict
        if dict_scan_result_tmp is not None:
            try:
                dict_return.update(dict_scan_result_tmp["scan"])
            except Exception as e:
                logging.exception(e)
                console(__name__, "error", str(e))
                pass
        pass

        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        else:
            console(__name__, self.temp_file, "file does not exist")

        return dict_return

    # 循环单一扫描，传入 ip-端口 字典，返回 ip-端口 的字典
    def loop_scan(self, target_dict_ip_port, arguments="--max-rate 5000"):
        # 扫描结果
        dict_return = {}

        # 解析ip
        for target_ip_tmp, target_port_tmp in target_dict_ip_port.items():
            # 尝试读或扫描结果
            dict_scan_result_tmp = None

            # 解析此ip下，要扫描的端口，例如 '1-65535'，或'8009'
            try:
                console(__name__, "scanning " + target_ip_tmp + " : " + target_port_tmp, arguments)
                self.mas.scan(target_ip_tmp, target_port_tmp, arguments=arguments)

                try:
                    dict_scan_result_tmp = self.mas.scan_result
                except Exception as e:
                    # Do a scan before trying to get result !
                    if "Do a scan before trying to get result !" == str(e):
                        # 如果只是没扫到开放的端口，则忽略
                        console(__name__, target_ip_tmp, str(e))
                        pass
                    else:
                        # 其他错误打印出来
                        logging.exception(e)
                        console(__name__, target_ip_tmp, str(e))

            except Exception as e:
                # network is unreachable.
                if "network is unreachable." == str(e):
                    # 如果只是无法访问，则忽略
                    console(__name__, target_ip_tmp, str(e))
                    pass
                else:
                    # 其他错误打印出来
                    logging.exception(e)
                    console(__name__, target_ip_tmp, str(e))

            # 扫描结果是open还是close，还是什么
            if dict_scan_result_tmp is not None:
                # 尝试解析ip和端口号，然后存储入数据库
                try:
                    dict_return.update(dict_scan_result_tmp["scan"])
                    # for ip_result, item_result in dict_scan_result_tmp["scan"].items():
                    #     dict_return[ip_result] = item_result["tcp"]
                except Exception as e:
                    logging.exception(e)
                    console(__name__, target_ip_tmp, str(e))
                    pass

        return dict_return

    # 批量扫描，传入ip和port，返回字典
    def single_scan(self, target_ip="", target_port="1-65535", arguments="--max-rate 5000"):
        dict_return = self.loop_scan({target_ip: target_port}, arguments)
        return dict_return
