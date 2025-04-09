import pymysql

def insert_file_storage_info(file_name, host_ip, remote_file_path):
    try:
        # 连接到数据库
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='guet',
            database='file_info',
            charset='utf8mb4'
        )
        cursor = connection.cursor()

        # 插入语句
        sql = """
            INSERT INTO file_infomation (file_name, host_ip, remote_file_path)
            VALUES (%s, %s, %s)
        """
        cursor.execute(sql, (file_name, host_ip, remote_file_path))
        connection.commit()
        print(f"文件存储信息已成功插入：{file_name}，{host_ip}，{remote_file_path}")
    except Exception as e:
        print(f"插入文件存储信息时出错：{e}")
    finally:
        cursor.close()
        connection.close()

# 示例数据
file_name = 'test.tar'
host_ip = '10.0.0.203'
remote_file_path = '/test_part/test_3.iso'

# 调用函数插入数据
insert_file_storage_info(file_name, host_ip, remote_file_path)
