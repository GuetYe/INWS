'''
Author: ��ʯȪ 786721684@qq.com
Date: 2024-01-21 10:24:21
LastEditTime: 2024-06-02 13:15:09
LastEditors: ��ʯȪ
Description: �ͻ����ն����е�py�ļ����ϴ�/���ع��ܣ�
ע�⣺
1.�ն˽��տ��������������ļ��ָ��������Ҫ��װwinpcap(�Ѿ�����ά��)��npcap�������


FilePath: \SD-UANET_load_balance-24-4-19\client\run\main.py
'''


import sys
import os
import time
import platform
import threading
import pymysql

my_client_platform = platform.system()  # ��ȡ�ͻ���ƽ̨����
if my_client_platform == 'Windows':  # Windowsƽ̨�¼���ģ��ķ���
    sys.path.append('../')
    from client_operation.client_request import ClientRequest
    from client_operation.receive_result import ReceivePacket
    from client_operation.file_utils import File_Utils
    from client_operation.nas_samba import Samba
    import config.setting as setting
elif my_client_platform == 'Linux':  # Linuxƽ̨�¼���ģ��ķ���
    sys.path.append('../')
    from client_operation.client_request import ClientRequest
    from client_operation.receive_result import ReceivePacket
    from client_operation.file_utils import File_Utils
    from client_operation.nas_samba import Samba
    import config.setting as setting



class ThreadUploadSpeed (threading.Thread):   #�̳и���threading.Thread
    def __init__(self, threadID, host_ip, remote_path, part_file_name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.host_ip = host_ip
        self.remote_path = remote_path
        self.part_file_name = part_file_name
    def run(self):                   #��Ҫִ�еĴ���д��run�������� �߳��ڴ������ֱ������run���� 
        self.host_smb = Samba(host=self.host_ip, username=setting.DEFAULT_USERNAME, password=setting.DEFAULT_PASSWORD)
        result = self.host_smb.connect()  # �������ӷ�����
        if result:
            while self.host_smb.connect_state:
                self.host_smb.get_upload_speed(self.remote_path, self.part_file_name)
            print("<main.py>   Thread {} end".format(self.threadID))

    def stop(self):
        self.host_smb.connect_state = False

class ThreadPullSpeed (threading.Thread):   #�̳и���threading.Thread
    def __init__(self, threadID, host_ip, locate_path, part_file_name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.host_ip = host_ip
        self.locate_path = locate_path
        self.part_file_name = part_file_name
    def run(self):                   #��Ҫִ�еĴ���д��run�������� �߳��ڴ������ֱ������run���� 
        host_smb = Samba(host=self.host_ip, username=setting.DEFAULT_USERNAME, password=setting.DEFAULT_PASSWORD)
        result = host_smb.connect()  # �������ӷ�����
        if result:
            while host_smb.connect_state:
                host_smb.get_pull_speed(self.locate_path, self.part_file_name)
            print("<main.py>   Thread {} end".format(self.threadID))



if __name__ == '__main__':
    # ��ȡ��ǰʱ��
    now_time = time.strftime("%Y-%m-%d %H:%M:%S")
    with open('../result/result_6 points_2g_and_5g.txt', 'a+', encoding='utf-8') as result_file:
        result_file.write(now_time)
        result_file.write("  5G-mesh����5G-����15db-test_dual-band.zip")
        result_file.write(":\n")
     # ʵ�����
    for number in range(setting.experiment_number):
        ################################����################################
        # ��Ҫ�洢 �� ��ȡ�ļ������·����������ģʽ(�洢������ȡ�ļ�)
        file_path = 'E:/ubuntu18.04����/ubuntu-18.04.6-desktop-amd64.iso'
        save_remote_path = '/'  # ��Ҫ�洢��Զ��������·��
        mode = 1  # 1 = �洢   2 = ��ȡ
        merge_delete_flag = 1  # ��ȡ�ļ����Ƿ�ɾ���ֿ��ļ� 1=ɾ��  0=��ɾ��
        ################################����################################

        # �ж���Linuxϵͳ����windowsϵͳ��windows
        print("<main.py>  The client platform is:%s" % my_client_platform)

        # ��windowsƽ̨��������IP��ַ����Linuxƽ̨�Զ�ʶ��
        host_ip = ''
        if my_client_platform == 'Windows':
            host_ip = '10.0.0.62'
        elif my_client_platform == 'Linux':
            host_ip = ClientRequest.get_host_IP()
        else:
            print("<main.py>  The client platform is another platform")


        file_utils = File_Utils()  # ʵ����һ���ļ���������
        program_start_time = time.time()  # ��¼����ʼ����ʱ��
        # -----------------------ִ�д洢-----------------------
        if mode == 1:
            print("<main.py>    Select the upload file function.")
            storage_request = ClientRequest(host_ip)  # ��������ʵ��

            storage_request.request_save(file_path)  # ����������������
            print("<main.py>    Request to upload file")

            print("<main.py>    Listening for split result of the controller, pleace wait %s s." % setting.SNIFF_TIMEOUT)
            receive = ReceivePacket()  # ʵ����һ�����ݰ�������
            receive.catch_pack()  # ���������յ������ݰ�(������arp���ݰ�)

            if not receive.receive_dict:  # ����Ƿ���յ��������ľ��߽��
                print("<main.py>    Unable to get split result from the controller")
                exit()
            else:
                print("<main.py>    The split result was successfully obtained")

            # samba_transfer_info��{'host_ip_1':file_name1, 'host_ip_2':file_name2, ...}
            samba_transfer_info = file_utils.file_split(file_path=file_path, split_dict=receive.receive_dict)  # ���ݾ��߽���ָ��ļ�
            file_split_info = [file_utils.file_name(file_name) for file_name in samba_transfer_info.values()]  # ��ȡ�ָ����ļ���
            file_save_host_info = [host_ip for host_ip in samba_transfer_info.keys()]
            print("<main.py>    The split result is: %s" % file_split_info)
            print("<main.py>    The client corresponding to the split result is: %s" % file_save_host_info)

            file_name_complete = file_utils.file_name(file_path)  # ��ȡ�����ļ���
            file_name_part = file_name_complete.split('.')[0]  # ��ȡ������׺���ļ���
            # �������洢λ�õ�·��
            save_remote_path_complete = save_remote_path + file_name_part + '_part/'  # ����洢Զ�̵�·��(xxx_part/xxx_1.xxx)�����ļ���
            save_info = {}  # ������Ϣ��Զ��ȡ�ļ���ʱ��Ҫ��

            # �����������յ����ļ��ָ���Ϣ�������ݿ�
            for host_ip, local_file_path in samba_transfer_info.items():
                part_file_name = file_utils.file_name(local_file_path)  # ��ȡ�ļ���
                remote_file_path = save_remote_path_complete + part_file_name  # Զ���ļ�·��
                insert_file_storage_info(file_name=file_name_complete, host_ip=host_ip,
                                         remote_path=remote_file_path)  # �洢�����ݿ�

            for step, (host_ip, local_file_path) in enumerate(samba_transfer_info.items()):

                # Ϊÿһ��������ʵ����һ��samba��
                host_smb = Samba(host=host_ip, username=setting.DEFAULT_USERNAME, password=setting.DEFAULT_PASSWORD)
                result = host_smb.connect()  # �������ӷ�����
                part_file_name = file_utils.file_name(local_file_path)  # ��ȡ�����ļ���
                if result:
                    print("\n<main.py>    Connecting to the client %s successfully, uploading files %s ..." % (host_ip, part_file_name))
                # ���Խ���Զ�������ı����ļ���
                # save_remote_path_complete�Ѿ�������save_remote_path����Ҫ os.path.join��
                try:
                    host_smb.smb_client.createDirectory(setting.DEFAULT_SHARE_FOLDER_NAME, \
                                                        os.path.join(save_remote_path, save_remote_path_complete))
                except Exception as e:
                    print("<main.py>   smaba createDirectory fail")
                    pass
                # ʵ��ֵ������������save_remote_path + file_name_part + '_part/'�ļ���
                remote_file_path = save_remote_path_complete + part_file_name
                # �ѷֿ��ļ��ϴ�����������Ӧ��·��
                thread_upload_speed = ThreadUploadSpeed(step, host_ip, save_remote_path_complete, part_file_name)


                thread_upload_speed.start()
                # ԭ����remote_file_path=remote_file_path
                host_smb.upload_files(local_file_path=local_file_path, remote_file_path=remote_file_path)

                print("<main.py>    The files has been uploaded successfully��")
                host_smb.close()  # �ϴ���ϼǵöϿ�����
                save_info[host_ip] = remote_file_path  # �洢��Ϣ�ֵ䣬[ip]:�������˵ķֿ��ļ���
                thread_upload_speed.stop()
                thread_upload_speed.host_smb.connect_state = False
                thread_upload_speed.join()
            # ���洢��Ϣ���浽txt�ļ��У������´�ȡ�ļ�������
            save_info_path = file_utils.save_storage_info(file_path, save_info)
            program_run_time = time.time() - program_start_time
            print('<main.py>    The distributed storage information has been saved to: %s' % save_info_path)
            m, s = divmod(program_run_time, 60)
            h, m = divmod(m, 60)
            print('<main.py>    The time for uploading files is: %02d:%02d:%02d \n' % (h, m, s))

            with open('../result/result_6 points_2g_and_5g.txt', 'a+', encoding='utf-8') as result_file:
                result_file.write(str(int(h)))
                result_file.write(":")
                result_file.write(str(int(m)))
                result_file.write(":")
                result_file.write(str(int(s)))
                result_file.write("\n")




        # -----------------------ִ����ȡ-----------------------
        elif mode == 2:
            print("<main.py>    Select the pull file function")
            path = file_utils.file_path(file_path)
            file_name_complete = file_utils.file_name(file_path)  # ȡ�����ļ���
            storage_info_file_path = path + file_name_complete + '_storage_info' + '.txt'  # ����洢��txt�ļ�·��

            # ���洢�ļ���Ϣ��TXT�ļ��Ƿ����
            if not os.path.exists(storage_info_file_path):
                print('<main.py>    The index file %s does not exit' % storage_info_file_path)
            else:
                print('<main.py>    The index file was read successfully')

            # ��ȡ�洢�ļ���Ϣ
            save_info, object_file_size = file_utils.loading_storage_info(file_name_complete, storage_info_file_path)
            print("<main.py>    filename��%s , filesize: %s byte" % (file_name_complete, object_file_size))
            if not save_info:
                print('<main.py>    The index file was incorrectly read')

            # �����洢��Ϣ�����ظ����ļ���file_path��
            download_file_size_cumulte = 0  # ��¼�µ��ļ��ܴ�С
            merge_list = []  # �������صķֿ��ļ���·��
            for step, (host_ip, remote_path) in enumerate(save_info.items()):
                # �ֱ���samba����ʵ��
                host_smb = Samba(host=host_ip, username=setting.DEFAULT_USERNAME, password=setting.DEFAULT_PASSWORD)
                result = host_smb.connect()  # ������������
                part_file_name = file_utils.file_name(remote_path)  # ��ȡ�����ļ���
                local_file_path = path + part_file_name  # �����ļ����������·��
                merge_list.append(local_file_path)  # ����÷ֿ��ļ�·������������ϲ�
                if result:
                    print("\n<main.py>    Connecting to the server  %s successfully,pulling files %s ..." % (host_ip, part_file_name))

                # �ѷֿ��ļ����ص�����
                thread_pull_speed = ThreadPullSpeed(step, local_file_path, part_file_name)
                thread_pull_speed.start()

                host_smb.download_files(local_file_path=local_file_path, remote_file_path=remote_path)
                print("<main.py>    The files has been pulled successfully��")
                download_file_size_cumulte += int(file_utils.file_size(local_file_path))  # �������ص��ļ��ۼ��ܴ�С
                thread_pull_speed.join()

                host_smb.close()  # ������ϼǵöϿ�����

            # ������ص��ļ���С�Ƿ�ʹ洢ʱ��¼���ļ���Сһ��
            if download_file_size_cumulte != object_file_size:
                print('<main.py>    File size check error')
            # �ϲ��ļ�
            result = file_utils.file_merge(file_path, merge_list, delete_flag=merge_delete_flag)
            if result:
                print('<main.py>    The files are successfully merged, the save path is: %s \n' % file_path)
            program_run_time = time.time() - program_start_time  # ��������ʱ��
            m, s = divmod(program_run_time, 60)
            h, m = divmod(m, 60)
            print('<main.py>    The time for pulling files is: %02d:%02d:%02d \n' % (h, m, s))

            with open('../result/result_6 points_5g.txt', 'a+', encoding='utf-8') as result_file:
                result_file.write(str(int(h)))
                result_file.write(":")
                result_file.write(str(int(m)))
                result_file.write(":")
                result_file.write(str(int(s)))
                result_file.write("\n")
