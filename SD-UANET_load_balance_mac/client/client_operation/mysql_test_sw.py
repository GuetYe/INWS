import pymysql
import random
import time

# 数据库连接参数
host = 'localhost'  # 数据库主机
user = 'root'  # 数据库用户名
password = 'guet'  # 数据库密码
database = 'sw_info'  # 数据库名称

# 连接到数据库
connection = pymysql.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

# 定义交换机节点
switches = [1, 2, 3, 4]  # 4个交换机

# 初始化CPU利用率、内存利用率和剩余容量的基础值
initial_cpu_util = 0.1  # 初始CPU利用率 10%
initial_mem_util = 0.05  # 初始内存利用率 5%
initial_remain_capacity = 0  # 初始剩余磁盘容量 3%

# 生成合理范围内的带宽、时延、丢包率随机浮动
def generate_random_data(previous_cpu, previous_mem, previous_remain_capacity):
    # CPU利用率浮动在 ±5% 之间
    cpu_util = previous_cpu + random.uniform(-0.05, 0.05)
    cpu_util = max(0, min(1, cpu_util))  # 限制在 0 到 1 之间

    # 内存利用率浮动在 ±5% 之间
    mem_util = previous_mem + random.uniform(-0.05, 0.05)
    mem_util = max(0, min(1, mem_util))  # 限制在 0 到 1 之间

    # 剩余磁盘容量浮动在 ±1% 之间
    # remain_capacity = previous_remain_capacity + random.uniform(-0.01, 0.01)
    remain_capacity = 0
    remain_capacity = max(0, min(1, remain_capacity))  # 限制在 0 到 1 之间

    # 保留两位小数
    cpu_util = round(cpu_util, 2)
    mem_util = round(mem_util, 2)
    remain_capacity = round(remain_capacity, 2)

    return cpu_util, mem_util, remain_capacity

# 定时刷新数据并存入数据库
try:
    cursor = connection.cursor()

    # 设置总运行时间为 10 分钟（600 秒）
    total_duration = 600
    refresh_interval = 5  # 每隔 5 秒刷新一次
    iterations = total_duration // refresh_interval  # 刷新次数

    # 初始化上一轮的CPU、内存和剩余容量
    previous_cpu = initial_cpu_util
    previous_mem = initial_mem_util
    previous_remain_capacity = initial_remain_capacity

    # 计算总的刷新次数（600秒 / 5秒 = 120次）
    for _ in range(iterations):
        # 遍历每个交换机
        for sw in switches:
            # 获取浮动后的CPU利用率、内存利用率、剩余磁盘容量
            cpu_util, mem_util, remain_capacity = generate_random_data(previous_cpu, previous_mem, previous_remain_capacity)

            # 插入数据的 SQL 语句
            insert_sql = """
            INSERT INTO sw_infomation (sw, Cpu_Uti, Mem_Uti, Remain_Capacity)
            VALUES (%s, %s, %s, %s)
            """

            # 执行插入操作
            cursor.execute(insert_sql, (sw, cpu_util, mem_util, remain_capacity))

            # 提交事务
            connection.commit()

            # 更新上一轮的值
            previous_cpu, previous_mem, previous_remain_capacity = cpu_util, mem_util, remain_capacity

            # 打印插入的数据（可选）
            # print(f"插入数据：交换机 {sw}, CPU利用率 {cpu_util}, 内存利用率 {mem_util}, 剩余容量 {remain_capacity}")

        # 每隔 5 秒刷新一次数据
        time.sleep(refresh_interval)

except Exception as e:
    # 如果发生错误，回滚事务
    connection.rollback()
    print(f"发生错误: {e}")

finally:
    # 关闭游标和数据库连接
    cursor.close()
    connection.close()