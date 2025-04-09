'''
Date: 2024-01-21 10:23:16
LastEditTime: 2024-04-01 22:40:49
Description: 接收控制器发过来的文件分割方案
FilePath: \SD-UANET_load_balance\client\client_operation\receive_result.py
'''

import sys
import platform
import re, os
import json
import pymysql
import ast

my_client_platform = platform.system()  # 读取客户端平台类型
if my_client_platform == 'Windows':  # Windows平台下加载模块的方法
    current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件夹路径
    parent_dir = os.path.abspath(os.path.join(current_dir, '../'))  # 获取上级目录
    sys.path.append(parent_dir)  # 添加到 sys.path
    import config.setting as setting
    from scapy.all import sniff
elif my_client_platform == 'Linux':  # Linux平台下加载模块的方法
    sys.path.append('../Client_Project/config')
    from scapy.sendrecv import sniff
    import config.setting as setting


class ReceivePacket:
    def __init__(self) -> None:
        self.receive_dict = {}
        
    def parsing_packet(self, packet):
        eth_src_mac = packet.src
        print("<receive_result> -->  eth_src_mac:", eth_src_mac)
        # 来自控制器的包
        if eth_src_mac == setting.CONTROLLER_MAC:
            # 新增：收到来自控制器的包时，打印提示信息
            
            arp_src_ip = packet.payload.psrc
            print("<receive_result> Received a packet from the controller")
            print("<receive_result> -->  arp_src_ip:", arp_src_ip)
        else:
            return
        
        if arp_src_ip in setting.CONTROLLER_IP:  # 必须筛选包的源IP为控制器
            #arp_packet_load = str(packet.payload.load)
            arp_packet_load = packet.payload.load.decode('utf-8', errors='ignore').lstrip('\x00')
            
            print("<receive_result> Raw packet payload:")
            print(arp_packet_load)
            # 解析数据包的不同类型
            self.parse_control_packet(arp_packet_load)
            # 使用re模块搜索结果
        
    
    """ 根据数据包内容解析不同的控制信息。解析文件分割结果、链路表和链路属性信息、交换机状态信息。"""
    def parse_control_packet(self, arp_packet_load):
        # 如果数据包中包含文件分割的特定标识，则跳过处理
        if "SplitResult" in arp_packet_load:
            arp_packet_load = str(arp_packet_load)
            print("<receive_result> 检测到文件分割数据，跳过交换机信息处理")
            result = re.findall(pattern='\{.+\}', string=arp_packet_load, )
            if result:
                try:
                    self.receive_dict = eval(result[0])
                    print("<receive_result> Split result:")
                except Exception as e:
                    self.receive_dict = None
            else:
                print("<receive_result.py> The split result returned by the controller cannot be found")
                self.receive_dict = None
            return
        
        # 检查是否为链路信息数据包
        if "switch_stats" in arp_packet_load or "topology" in arp_packet_load:
            result = re.search(r'\{.*\}', arp_packet_load, re.DOTALL)
            if result:
                json_str = result.group(0)
                try:
                    self.typo_dict = ast.literal_eval(json_str)
                    # arp_packet_load = json.loads(result[0])
                except Exception as e:
                    print("<receive_result> JSON解析错误:", e)
                    return
            else:
                print("<receive_result> 未在数据包中找到 JSON 数据")
                return
            print("<receive_result> --> 数据包中包含拓扑信息和交换机状态信息")
            self.parse_and_store_packet(self.typo_dict)

    def parse_and_store_packet(self, arp_packet_load):
        switch_stats = arp_packet_load.get("switch_stats")
        topology = arp_packet_load.get("topology")
        if switch_stats is None or topology is None:
            print("接收到的数据不包含预期的 switch_stats 或 topology 字段")
            return

        try:
            connection_sw = pymysql.connect(
            host='localhost',
            user='root',
            password='guet',
            database='sw_info',
            charset='utf8mb4'
        )
            cursor_sw = connection_sw.cursor()
        except Exception as e:
            print("连接 sw_info 数据库失败:", e)
            return

        # 连接到 typo_info 数据库（用于存储拓扑链路信息）
        try:
            connection_typo = pymysql.connect(
            host='localhost',
            user='root',
            password='guet',
            database='typo_info',
            charset='utf8mb4'
        )
            cursor_typo = connection_typo.cursor()
        except Exception as e:
            print("连接 typo_info 数据库失败:", e)
            return
            
        # 遍历 switch_stats 字典，格式为：
        # { switch_id: {'Cpu_Uti': value, 'Mem_uti': value, 'Remain_Capacity': value}, ... }
        for sw, stats in switch_stats.items():
            cpu_uti = stats.get("Cpu_Uti", 0)
            mem_uti = stats.get("Mem_uti", 0)
            remain_capacity = stats.get("Remain_Capacity", 0)
            insert_query = """
                INSERT INTO sw_infomation (sw, Cpu_Uti, Mem_Uti, Remain_Capacity)
                VALUES (%s, %s, %s, %s)
            """
            try:
                cursor_sw.execute(insert_query, (sw, cpu_uti, mem_uti, remain_capacity))
            except Exception as e:
                print("插入 sw_infomation 失败:", e)
        connection_sw.commit()
        cursor_sw.close()
        connection_sw.close()
        print("成功插入交换机状态信息到 sw_infomation 表。")

       # 处理拓扑信息。这里拓扑数据采用 networkx 的 node_link_data 格式，
        # 链路信息存放在 topology 中的 "links" 字段，格式为列表，每个链路字典包含：
        # "source"、"target"、"bw"、"delay"、"loss" 等属性
        links = topology.get("links")
        if links is None:
            print("拓扑数据中未找到 'links' 字段")
        else:
            sql_topo = """
                INSERT INTO typo_infomation (src, dst, bw, delay, loss)
                VALUES (%s, %s, %s, %s, %s)
            """
            data_to_insert = []
            for link in links:
                src = link.get("source")
                dst = link.get("target")
                bw = link.get("bw", 0)
                delay = link.get("delay", 0)
                loss = link.get("loss", 0.0)
                data_to_insert.append((src, dst, bw, delay, loss))
            try:
                cursor_typo.executemany(sql_topo, data_to_insert)
                connection_typo.commit()
                print(f"成功插入 {len(data_to_insert)} 条记录到 typo_infomation 表。")
            except Exception as e:
                connection_typo.rollback()
                print(f"数据库插入失败: {e}")
        
        cursor_typo.close()
        connection_typo.close()
       
    def catch_pack(self):
        self.receive_dict = {}  # 清空属性
        # count等0表示一直监听，要想监听数据包，需要首先安装winpcap或npcap  iface=setting.SNIFF_IFACE,
        # 一定要指定接口iface才可以接受包

        sniff(filter='arp', prn=self.parsing_packet, count=0, iface="WLAN")


if __name__ == '__main__':
    a = ReceivePacket()
    a.catch_pack()
    