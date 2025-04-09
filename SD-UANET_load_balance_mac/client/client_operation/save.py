import sys
import os
import time
import platform
import threading

current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件夹路径
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))  # 获取上级目录
sys.path.append(parent_dir)  # 添加到 sys.path
from client_operation.client_request import ClientRequest
from client_operation.receive_result import ReceivePacket
from client_operation.file_utils import File_Utils
from client_operation.nas_samba import Samba
import config.setting as setting
import pymysql


def insert_file_info(symbol, file_name, file_path, file_size, op_time):
    """
    将文件信息插入MySQL数据库中的file_infomation表。
    数据表结构：
        symbol    VARCHAR(50)
        file_name VARCHAR(255)
        file_path VARCHAR(255)
        file_size INT
        time      VARCHAR(50)
    示例SQL：
    INSERT INTO file_infomation(symbol, file_name, file_size, time)
    VALUES ('R001', 'test.tar', 20000, '2025-02-26 14:30:00')
    """
    # 数据库连接参数
    host_db = 'localhost'  # 数据库主机
    user_db = 'root'       # 数据库用户名
    password_db = 'guet'   # 数据库密码
    database_db = 'file_info'  # 数据库名称

    try:
        connection = pymysql.connect(
            host=host_db,
            user=user_db,
            password=password_db,
            database=database_db
        )
        cursor = connection.cursor()
        # 如果数据表不存在，则创建数据表
        # create_table_sql = '''
        #     CREATE TABLE IF NOT EXISTS file_infomation (
        #         symbol VARCHAR(50),
        #         file_name VARCHAR(255),
        #         file_size INT,
        #         time VARCHAR(50)
        #     )
        # '''
        # cursor.execute(create_table_sql)
        insert_sql = '''
            INSERT INTO file_infomation(symbol, file_name, file_path, file_size, time)
            VALUES (%s, %s, %s, %s, %s)
        '''
        cursor.execute(insert_sql, (symbol, file_name, file_path, file_size, op_time))
        connection.commit()
        print("File info inserted into MySQL database successfully.")
    except Exception as e:
        print("Error inserting file info into MySQL:", e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def insert_part_file_info(part_symbol, origin_symbol, part_index, file_size, host_ip, remote_file_path):
    """
    将分块文件信息插入MySQL数据库中的part_file_infomation表。
    数据表结构：
        part_symbol    VARCHAR(50)
        origin_symbol  VARCHAR(50)
        `index`        INT
        file_size      INT
        host_ip        VARCHAR(50)
        remote_file_path VARCHAR(255)
    示例SQL：
    INSERT INTO part_file_infomation(part_symbol, origin_symbol, `index`, file_size, host_ip, remote_file_path)
    VALUES ('P001','R001',1,10000,'10.0.0.201','/test_part/test_1.tar')
    """
    host_db = 'localhost'
    user_db = 'root'
    password_db = 'guet'
    database_db = 'part_file_info'

    try:
        connection = pymysql.connect(
            host=host_db,
            user=user_db,
            password=password_db,
            database=database_db
        )
        cursor = connection.cursor()
        # 如果数据表不存在，则创建数据表
        # create_table_sql = '''
        #     CREATE TABLE IF NOT EXISTS part_file_infomation (
        #         part_symbol VARCHAR(50),
        #         origin_symbol VARCHAR(50),
        #         `index` INT,
        #         file_size INT,
        #         host_ip VARCHAR(50),
        #         remote_file_path VARCHAR(255)
        #     )
        # '''
        # cursor.execute(create_table_sql)
        insert_sql = '''
            INSERT INTO part_file_infomation(part_symbol, origin_symbol, `index`, file_size, host_ip, remote_file_path)
            VALUES (%s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(insert_sql, (part_symbol, origin_symbol, part_index, file_size, host_ip, remote_file_path))
        connection.commit()
        print(f"Part file info inserted: part_symbol={part_symbol}, origin_symbol={origin_symbol}, index={part_index}")
    except Exception as e:
        print("Error inserting part file info into MySQL:", e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


class ThreadUploadFile(threading.Thread):  
    def __init__(self, threadID, host_ip, local_file_path, save_remote_path_complete, save_info):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.host_ip = host_ip
        self.local_file_path = local_file_path
        self.file_utils = File_Utils()
        self.save_remote_path_complete = save_remote_path_complete  # 服务器存储位置的路径
        self.save_info = save_info

    def run(self):
        host_smb = Samba(host=self.host_ip, username=setting.DEFAULT_USERNAME, password=setting.DEFAULT_PASSWORD)
        result = host_smb.connect()
        part_file_name = self.file_utils.file_name(self.local_file_path)  # 截取完整文件名
        if result:
            print("Connecting to the client %s successfully, uploading files %s ..." % (self.host_ip, part_file_name))

        try:
            host_smb.smb_client.createDirectory(setting.DEFAULT_SHARE_FOLDER_NAME, \
                                                os.path.join('/', self.save_remote_path_complete))
        except Exception as e:
            print("%s smaba createDirectory fail" % self.host_ip)
            pass

        remote_file_path = self.save_remote_path_complete + part_file_name
        print("uploading files to %s" % self.host_ip)
        host_smb.upload_files(local_file_path=self.local_file_path, remote_file_path=remote_file_path)

        print("(%s-%s) has been uploaded successfully！" % (self.host_ip, self.local_file_path))
        host_smb.close()
        self.save_info[self.host_ip] = remote_file_path  


class ThreadPullSpeed(threading.Thread):  
    def __init__(self, threadID, host_ip, locate_path, part_file_name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.host_ip = host_ip
        self.locate_path = locate_path
        self.part_file_name = part_file_name

    def run(self):
        host_smb = Samba(host=self.host_ip, username=setting.DEFAULT_USERNAME, password=setting.DEFAULT_PASSWORD)
        result = host_smb.connect()
        # if result:
        #     while host_smb.connect_state:
        #         host_smb.get_pull_speed(self.locate_path, self.part_file_name)
        #     print("Thread {} end".format(self.threadID))


def upload_files(file_path):
    print("▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲upload_files   start▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲")
    my_client_platform = platform.system()  # 读取客户端平台类型
    file_utils = File_Utils()
    program_start_time = time.time()  # 记录程序开始运行时间
    host_ip = ''
    
    # Determine platform and IP address
    if my_client_platform == 'Windows':
        host_ip = ClientRequest.get_wlan_ip_windows()
    elif my_client_platform == 'Linux':
        host_ip = ClientRequest.get_host_IP_linux()
    else:
        print("The client platform is another platform")

    # -----------------------执行存储-----------------------
    
    print("Select the upload file function my_host_ip is %s." % (host_ip))
    storage_request = ClientRequest(host_ip)  # 构造请求实例
    storage_request.request_save(file_path)  # 发送请求至控制器
    print("Request to upload file")

    print("Listening for split result of the controller, please wait %s s." % setting.SNIFF_TIMEOUT)
    receive = ReceivePacket()  # 实例化一个数据包接收类
    # receive.catch_pack()  # 监听主机收到的数据包(仅监听arp数据包)
    listener_thread = threading.Thread(target=receive.catch_pack, daemon=True)
    listener_thread.start()

    # 主线程轮询等待直到获得文件分割结果或达到超时
    wait_time = 0
    while wait_time < setting.SNIFF_TIMEOUT and not receive.receive_dict:
        time.sleep(1)
        wait_time += 1

    if not receive.receive_dict:
        print("Unable to get split result from the controller")
        return
    else:
        print("☆☆☆☆☆☆☆☆☆☆☆The split result was successfully obtained☆☆☆☆☆☆☆☆☆☆☆")

    samba_transfer_info = file_utils.file_split(file_path=file_path, split_dict=receive.receive_dict)  # 根据决策结果分割文件
    file_split_info = [file_utils.file_name(file_name) for file_name in samba_transfer_info.values()]  # 截取分割后的文件名
    file_save_host_info = [host_ip for host_ip in samba_transfer_info.keys()]
    print("☆☆☆☆☆☆☆☆☆☆☆The split result is☆☆☆☆☆☆☆☆☆☆☆: %s" % file_split_info)
    print("☆☆☆☆☆☆☆☆☆☆☆The client corresponding to the split result is☆☆☆☆☆☆☆☆☆☆☆: %s" % file_save_host_info)

    file_name_complete = file_utils.file_name(file_path)  # 截取完整文件名
    file_name_part = file_name_complete.split('.')[0]  # 截取不含后缀的文件名
    save_remote_path_complete = f"/{file_name_part}_part/"  # 构造存储远程的路径(xxx_part/xxx_1.xxx)不含文件名
    save_info = {}  # 保存信息，远程取文件的时候要用
    threads = []  # 用于存储线程的列表

    for step, (host_ip, local_file_path) in enumerate(samba_transfer_info.items()):
        thread = ThreadUploadFile(step + 1, host_ip, local_file_path, save_remote_path_complete, save_info)
        threads.append(thread)  # 将线程对象添加到列表中
        thread.start()  # 启动线程
        time.sleep(5)

    for each_thread in threads:
        each_thread.join()

    # 将存储信息保存到txt文件中，用于下次取文件的依赖
    save_info_path = file_utils.save_storage_info(file_path, save_info)
    program_run_time = time.time() - program_start_time
    print('The distributed storage information has been saved to: %s' % save_info_path)
    m, s = divmod(program_run_time, 60)
    h, m = divmod(m, 60)
    print('The time for uploading files is: %02d:%02d:%02d \n' % (h, m, s))
    
    # symbol 的生成方式：使用 "R" + 当前时间戳（格式：YYYYMMDDHHMMSS）
    symbol = "R" + time.strftime("%Y%m%d%H%M%S", time.localtime())
    try:
        file_size = int(file_utils.file_size(file_path))
    except Exception as e:
        file_size = 0
    op_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    insert_file_info(symbol, file_name_complete, file_path, file_size, op_time)

    # 将每个分块文件信息存入MySQL数据库中的 part_file_infomation 表
    for step, (host_ip, local_file_path) in enumerate(samba_transfer_info.items()):
        part_index = step + 1
        part_symbol = "P" + str(part_index).zfill(3)
        try:
            part_file_size = int(file_utils.file_size(local_file_path))
        except Exception as e:
            part_file_size = 0
        # 从 save_info 中获取该分块在远程存储的路径
        remote_file_path = save_info.get(host_ip, "")
        insert_part_file_info(part_symbol, symbol, part_index, part_file_size, host_ip, remote_file_path)
        print("☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆存储成功")


def pull_files(file_path):
    merge_delete_flag = 1
    file_utils = File_Utils()
    program_start_time = time.time()
    path = file_utils.file_path(file_path)
    file_name_complete = file_utils.file_name(file_path)  # 取完整文件名
    storage_info_file_path = path + file_name_complete + '_storage_info' + '.txt'

    if not os.path.exists(storage_info_file_path):
        print('The index file %s does not exit' % storage_info_file_path)
        return
    else:
        print('★★★★★★★★★The index file was read successfully★★★★★★★★★')
    
    save_info, object_file_size = file_utils.loading_storage_info(file_name_complete, storage_info_file_path)  # 读取存储文件信息
    print("filename：%s , filesize: %s byte" % (file_name_complete, object_file_size))
    
    if not save_info:
        print('The index file was incorrectly read')

    download_file_size_cumulte = 0  # 记录下的文件总大小
    merge_list = []  # 保存下载的分块文件的路径
    
    for step, (host_ip, remote_path) in enumerate(save_info.items()):
        host_smb = Samba(host=host_ip, username=setting.DEFAULT_USERNAME, password=setting.DEFAULT_PASSWORD)  # 构造samba主机实例
        result = host_smb.connect()  # 尝试连接主机
        part_file_name = file_utils.file_name(remote_path)  # 截取完整文件名
        local_file_path = path + part_file_name   # 下载文件保存的完整路径
        merge_list.append(local_file_path)
        if result:
            print("\nConnecting to the server %s ★★★★★★★★★successfully★★★★★★★★★, pulling files %s ..." % (host_ip, part_file_name))

        thread_pull_speed = ThreadPullSpeed(step, host_ip, local_file_path, part_file_name)
        thread_pull_speed.start()

        host_smb.download_files(local_file_path=local_file_path, remote_file_path=remote_path)
        print("★★★★★★★★★The files have been pulled successfully！★★★★★★★★★")
        download_file_size_cumulte += int(file_utils.file_size(local_file_path))
        thread_pull_speed.join()

        host_smb.close()

    if download_file_size_cumulte != object_file_size:
        print('File size check error')

    # 合并文件
    result = file_utils.file_merge(file_path, merge_list, delete_flag=merge_delete_flag)
    if result:
        print('★★★★★★★The files are successfully merged★★★★★★★★★, the save path is: %s \n' % file_path)

    program_run_time = time.time() - program_start_time
    m, s = divmod(program_run_time, 60)
    h, m = divmod(m, 60)
    print('The time for pulling files is: %02d:%02d:%02d \n' % (h, m, s))



def delet_files(file_path):
    file_utils = File_Utils()
    path = file_utils.file_path(file_path)
    file_name_complete = file_utils.file_name(file_path)  # 取完整文件名
    storage_info_file_path = path + file_name_complete + '_storage_info' + '.txt'

    if not os.path.exists(storage_info_file_path):
        print('The index file %s does not exit' % storage_info_file_path)
        return
    else:
        print('🔺🔺🔺🔺🔺🔺🔺The delete file was read successfully🔺🔺🔺🔺🔺🔺🔺')
    
    save_info, object_file_size  = file_utils.loading_storage_info(file_name_complete, storage_info_file_path)  # 读取存储文件信息
    if not save_info:
        print('The index file was incorrectly read')
        return
    
    # 如果读取的数据不是字典，则尝试转换
    if not isinstance(save_info, dict):
        try:
            save_info = dict(save_info)
        except Exception as e:
            print("Error converting save_info to dict:", e)
            return
        
    for host_ip, remote_path in save_info.items():
        host_smb = Samba(host=host_ip, username=setting.DEFAULT_USERNAME, password=setting.DEFAULT_PASSWORD)  # 连接 Samba 服务器
        result = host_smb.connect()

        if result:
            print(f"Connected to {host_ip}, attempting to delete {remote_path}...")
            try:
                host_smb.delete_file(remote_path)
                print(f"File {remote_path} deleted🔺🔺🔺 successfully 🔺🔺🔺from {host_ip}.")
            except Exception as e:
                print(f"Failed to delete file {remote_path} from {host_ip}: {e}")
            host_smb.close()
        else:
            print(f"Failed to connect to {host_ip}, unable to delete {remote_path}.")
     # 删除本地索引文件
    try:
        os.remove(storage_info_file_path)
        print(f"Local index file {storage_info_file_path} deleted🔺🔺🔺 successfully.🔺🔺🔺")
    except Exception as e:
        print(f"Failed to delete local index file {storage_info_file_path}: {e}")
    

if __name__ == "__main__":
    file_path = 'E:/ubuntu18.04镜像/txupd.exe'
    upload_files(file_path)
    #pull_files(file_path)
    #delet_files(file_path)