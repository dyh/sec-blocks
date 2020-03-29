# coding=utf-8
import nmap

from libs.cli_output import console


class NmapBlock:
    def __init__(self):
        self.nm = nmap.PortScanner()
        pass

    # 批量扫描，传入字典，返回字典
    # -O：进行系统探测
    # -n：不做DNS解析
    # -sV：探测开启的端口来获取服务、版本信息
    # -sS：使用SYN
    # -T4：指定扫描过程使用的时序（Timing）
    def batch_scan(self, target_dict_ip_port, arguments="-O -n -sS -sV -T4"):
        # 扫描结果
        dict_return = {}

        # 解析ip
        for target_ip_tmp, target_port_tmp in target_dict_ip_port.items():
            # 尝试读或扫描结果
            dict_scan_result_tmp = None

            # 解析此ip下，要扫描的端口，例如 '1-65535'，或'8009'
            try:
                console(__name__, "scanning " + target_ip_tmp + " , ports: " + target_port_tmp, arguments)

                dict_scan_result_tmp = self.nm.scan(hosts=target_ip_tmp, ports=target_port_tmp, arguments=arguments)
            except Exception as e:
                # network is unreachable.
                if "network is unreachable." == str(e):
                    # 如果只是无法访问，则忽略
                    console(__name__, target_ip_tmp, str(e))
                    pass
                else:
                    # 其他错误打印出来
                    console(__name__, target_ip_tmp, str(e))

            # 扫描结果是open还是close，还是什么
            if dict_scan_result_tmp is not None:
                # 尝试解析ip和端口号，然后存储入数据库
                try:
                    dict_return.update(dict_scan_result_tmp["scan"])
                except Exception as e:
                    console(__name__, target_ip_tmp, str(e))
                    pass

        return dict_return

    # 批量扫描，传入ip和port，返回字典
    def single_scan(self, target_ip="", target_port="",  arguments="-O -n -sS -sV -T4"):
        dict_return = self.batch_scan({target_ip: target_port}, arguments)
        return dict_return
