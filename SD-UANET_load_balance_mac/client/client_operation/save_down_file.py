'''
Date: 2024-01-21 10:24:21
LastEditTime: 2024-12-26 15:23:09
Description: 客户端终端运行的py文件（上传/下载功能）
注意：
1.终端接收控制器发过来的文件分割方案功能需要安装winpcap(已经不在维护)或npcap的软件包


FilePath: \SD-UANET_load_balance_2\client\run\main.py
'''


import sys
import os
import time
import platform
import threading



sys.path.append('../')
from client_operation.client_request import ClientRequest
from client_operation.receive_result import ReceivePacket
from client_operation.file_utils import File_Utils
from client_operation.nas_samba import Samba
import config.setting as setting
import time


my_client_platform = platform.system()  # 读取客户端平台类型



class ThreadUploadFile (threading.Thread):   #继承父类threading.Thread
    def __init__(self, threadID, host_ip, local_file_path, save_remote_path_complete, save_info):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.host_ip = host_ip
        self.local_file_path = local_file_path
        self.save_remote_path_complete = save_remote_path_complete
        self.save_info = save_info
        self.file_utils = File_Utils()

    def run(self):                   #把要执行 的代码写到run函数里面 线程在创建后会直接运行run函数 
        # 为每一个服务器实例化一个samba类
        host_smb = Samba(host=self.host_ip, username=setting.DEFAULT_USERNAME, password=setting.DEFAULT_PASSWORD)
        result = host_smb.connect()  # 尝试连接服务器
        part_file_name = self.file_utils.file_name(self.local_file_path)  # 截取完整文件名

        if result:
            print("Connecting to the client %s successfully, uploading files %s ..." % (self.host_ip, part_file_name))
        # 尝试建立远程主机的保存文件夹
        # save_remote_path_complete已经包含了save_remote_path，还要 os.path.join？
        try:
            host_smb.smb_client.createDirectory(setting.DEFAULT_SHARE_FOLDER_NAME, \
                                                os.path.join('/', self.save_remote_path_complete))
        except Exception as e:
            print("%s smaba createDirectory fail" % self.host_ip)
            pass
        # 实际值（服务器）：save_remote_path + file_name_part + '_part/'文件名
        remote_file_path = self.save_remote_path_complete + part_file_name

        # 原本：remote_file_path=remote_file_path
        print("uploading files to %s" % self.host_ip)
        host_smb.upload_files(local_file_path=self.local_file_path, remote_file_path=remote_file_path)

        print("(%s-%s) has been uploaded successfully！" % (self.host_ip, self.local_file_path))
        host_smb.close()  # 上传完毕记得断开连接
        self.save_info[self.host_ip] = remote_file_path  # 存储信息字典，[ip]:服务器端的分块文件名

    # def stop(self):
    #     host_smb.connect_state == False

class ThreadPullSpeed (threading.Thread):   #继承父类threading.Thread
    def __init__(self, threadID, host_ip, locate_path, part_file_name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.host_ip = host_ip
        self.locate_path = locate_path
        self.part_file_name = part_file_name
    def run(self):                   #把要执行的代码写到run函数里面 线程在创建后会直接运行run函数 
        host_smb = Samba(host=self.host_ip, username=setting.DEFAULT_USERNAME, password=setting.DEFAULT_PASSWORD)
        result = host_smb.connect()  # 尝试连接服务器
        if result:
            while host_smb.connect_state:
                host_smb.get_pull_speed(self.remote_path, self.part_file_name)
            print("Thread {} end".format(self.threadID))

def upload_file(file_path, save_remote_path='/', experiment_number=0):
    file_utils = File_Utils()  # 实例化一个文件处理工具类
    program_start_time = time.time()  # 记录程序开始运行时间

    for number in range(experiment_number):
        print(f"\n=== Experiment {number+1}/{experiment_number} ===")

        # 获取客户端IP
        host_ip = ClientRequest.get_wlan_ip_windows() if platform.system() == 'Windows' \
                  else ClientRequest.get_host_IP_linux()
        
        storage_request = ClientRequest(host_ip)  # 构造请求实例
        storage_request.request_save(file_path)  # 发送请求至控制器

        receive = ReceivePacket()  # 实例化一个数据包接收类
        receive.catch_pack()  # 监听主机收到的数据包(仅监听arp数据包)

        if not receive.receive_dict:
            print("No split result received from controller")
            return None
        
        samba_transfer_info = file_utils.file_split(file_path=file_path, split_dict=receive.receive_dict)  # 根据决策结果分割文件

        file_split_info = [file_utils.file_name(file_name) for file_name in samba_transfer_info.values()]  # 截取分割后的文件名
        file_save_host_info = [host_ip for host_ip in samba_transfer_info.keys()]
        print("The split result is: %s" % file_split_info)
        print("The client corresponding to the split result is: %s" % file_save_host_info)

        file_name_complete = file_utils.file_name(file_path)  # 截取完整文件名

        file_name_part = file_name_complete.split('.')[0]  # 截取不含后缀的文件名
        save_remote_path_complete = f"/{file_name_part}_part/"
        save_info = {}  # 保存信息，远程取文件的时候要用

        # 多线程上传
        threads = []
        for step, (host_ip, local_path) in enumerate(samba_transfer_info.items()):
            thread = ThreadUploadFile(step+1, host_ip, local_path, 
                                    save_remote_path_complete, save_info)
            thread.start()
            threads.append(thread)
            time.sleep(5)  # 避免samba连接冲突

        for thread in threads:
            thread.join()


        # 保存存储信息
        save_info_path = file_utils.save_storage_info(file_path, save_info)

        # 记录实验时间
        total_time = time.time() - program_start_time
        h, m = divmod(total_time/60, 60)
        print(f'Upload time: {int(h):02d}:{int(m):02d}:{int(total_time%60):02d}')
    return save_info_path
    

def pull_file(file_path, save_info, merge_delete_flag=0):
    """从分布式存储中拉取并合并文件"""
    file_utils = File_Utils()
    program_start_time = time.time()
    path = file_utils.file_path(file_path)
    file_name_complete = file_utils.file_name(file_path)  # 取完整文件名
    storage_info_file_path = path + file_name_complete + '_storage_info' + '.txt'  # 构造存储的txt文件路径

    save_info, object_file_size = file_utils.loading_storage_info(file_name_complete, storage_info_file_path)
    if not save_info:
        print("Invalid storage info file")
        return False
    
    # 下载分块文件
    merge_list = []
    download_size = 0
    for step, (host_ip, remote_path) in enumerate(save_info.items()):
        host_smb = Samba(host_ip, setting.DEFAULT_USERNAME, setting.DEFAULT_PASSWORD)

        if not host_smb.connect():
            continue

        local_path = os.path.join(
            os.path.dirname(storage_info_path),
            file_utils.file_name(remote_path)
        )
        host_smb.download_files(local_path, remote_path)
        merge_list.append(local_path)
        download_size += os.path.getsize(local_path)
        host_smb.close()

    # 验证文件大小
    if download_size != object_file_size:
        print(f"Size mismatch: {download_size} vs {object_file_size}")

    # 合并文件
    original_path = storage_info_path.replace('_storage_info.txt', '')
    if file_utils.file_merge(original_path, merge_list, merge_delete_flag):
        print(f"File merged successfully: {original_path}")

    total_time = time.time() - program_start_time
    h, m = divmod(total_time/60, 60)
    print(f'Download time: {int(h):02d}:{int(m):02d}:{int(total_time%60):02d}')
    return True

    