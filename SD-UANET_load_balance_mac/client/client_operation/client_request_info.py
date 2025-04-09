import sys
import platform
import re
import subprocess
from scapy.layers.inet import IP, TCP
from scapy.sendrecv import send
import time
import os
my_client_platform = platform.system()  # 读取客户端平台类型

if my_client_platform == 'Windows':  # Windows平台下加载模块的方法
    current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件夹路径
    parent_dir = os.path.abspath(os.path.join(current_dir, '../'))  # 获取上级目录
    sys.path.append(parent_dir)  # 添加到 sys.path
    from client_operation.file_utils import File_Utils
    import config.setting as setting
elif my_client_platform == 'Linux':  # Linux平台下加载模块的方法
    sys.path.append('../Client_Project/client_operation')
    sys.path.append('../Client_Project/config')
    from client_operation.file_utils import File_Utils
    import config.setting as setting


class ClientRequest:
    def __init__(self, host_ip) -> None:
        self.src_ip = host_ip
        self.dst_ip = setting.CONTROLLER_IP[0]

    @staticmethod
    def get_host_IP_linux():
        """
        # description: 获取主机的IP(Linux)
        # return {*} 主机IP
        """
        # shell=True ： 执行的命令当初一个字符串
        original_data = subprocess.check_output("hostname -I", shell=True).decode('utf-8')
        # re.search、group(0)：返回第1个匹配到的IP地址
        host_ip = re.search('\d+.\d+.\d+.\d+', original_data).group(0)

        return host_ip
    
    @staticmethod
    def get_wlan_ip_windows():
        # 执行 `ipconfig` 命令
        output = subprocess.run("ipconfig", capture_output=True, text=True, shell=True).stdout

        # 匹配无线局域网适配器 WLAN 的内容块
        wlan_section = re.search(r"无线局域网适配器 WLAN:.*?(?=^\S|\Z)", output, re.DOTALL | re.MULTILINE)
        if wlan_section:
            # 查找 IPv4 地址
            ipv4_match = re.search(r"IPv4 地址[ .]*: ([\d.]+)", wlan_section.group(0))
            if ipv4_match:
                return ipv4_match.group(1)
        
        return None

    def request_link_info(self):
        """
        请求控制器发送链路信息
        符合正则表达式self.search_link_request_method
        """
        # 1. 构造链路信息请求数据，按照self.search_link_request_method的格式
        # 构造符合格式的链路请求数据
        data = '[ClientLinkRequest(source=client)]' # 根据要求的正则表达式构建格式

        # 2. 构造IP数据包
        ip_packet = IP()
        ip_packet.src = self.src_ip
        ip_packet.dst = self.dst_ip

        # 3. 构造TCP负载数据
        # tcp_packet = TCP(dport=12345, sport=random.randint(1024, 65535))  # 随机源端口
        tcp_packet = TCP()
        ip_packet.payload = tcp_packet / data

        # 4. 发送请求
        send(ip_packet)  # 发送请求包，广播到控制器

        print(f"Requesting link info from controller at {self.dst_ip}")


if __name__ == '__main__':
    while True:
        
        # IP包源地址为10.0.0.202，目的地址：控制器
        client_ = ClientRequest('10.0.0.88')
        # 通过TCP协议发送文件
        client_.request_link_info()
        time.sleep(1)
