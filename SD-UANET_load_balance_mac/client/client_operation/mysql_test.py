import pymysql
import random
import time

# 数据库连接参数
host = 'localhost'  # 数据库主机
user = 'root'  # 数据库用户名
password = 'guet'  # 数据库密码
database = 'typo_info'  # 数据库名称

# 连接到数据库
connection = pymysql.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

# 定义固定连接的节点对
connections = [
    (1, 2),  # 节点 1-2
    (1, 3),  # 节点 1-3
    (2, 3),  # 节点 2-3
    (3, 4)   # 节点 3-4
]

# 初始化带宽、时延和丢包率的基础值
initial_bw = 30 # 初始带宽 50 Mbps
initial_delay = 10  # 初始时延 10 ms
initial_loss = 0.02  # 初始丢包率 2%

# 生成合理范围内的带宽、时延、丢包率随机浮动
def generate_random_data(previous_bw, previous_delay, previous_loss):
    # 带宽：带宽的浮动在 ±10% 之间
    bw = previous_bw + random.randint(-5, 5)  # 基于上一轮带宽波动
    bw = max(25, min(29, bw))  # 限制带宽在10-100 Mbps之间

    # 时延：时延的浮动在 ±5 ms 之间
    delay = previous_delay + random.randint(-2, 2)  # 基于上一轮时延波动
    delay = max(1, min(50, delay))  # 限制时延在1-50 ms之间

    # 丢包率：丢包率的浮动在 ±0.01 之间
    loss = previous_loss + round(random.uniform(-0.005, 0.005), 4)  # 基于上一轮丢包率波动
    loss = max(0, min(0.1, loss))  # 丢包率限制在0-30%之间

    loss = round(loss, 3)
    return bw, delay, loss

# 定时刷新数据并存入数据库
try:
    cursor = connection.cursor()

    # 设置总运行时间为 10 分钟（600 秒）
    total_duration = 800
    refresh_interval = 5  # 每隔 5 秒刷新一次
    iterations = total_duration // refresh_interval  # 刷新次数

    # 初始化上一轮的带宽、时延和丢包率
    previous_bw = initial_bw
    previous_delay = initial_delay
    previous_loss = initial_loss

    # 计算总的刷新次数（600秒 / 5秒 = 120次）
    for _ in range(iterations):
        # 遍历每个连接对（节点对）
        for src, dst in connections:
            # 获取浮动后的带宽、时延、丢包率
            bw, delay, loss = generate_random_data(previous_bw, previous_delay, previous_loss)

            # 插入数据的 SQL 语句
            insert_sql = """
            INSERT INTO typo_info.typo_infomation (src, dst, bw, delay, loss)
            VALUES (%s, %s, %s, %s, %s)
            """

            # 执行插入操作
            cursor.execute(insert_sql, (src, dst, bw, delay, loss))

            # 提交事务
            connection.commit()

            # 更新上一轮的值
            previous_bw, previous_delay, previous_loss = bw, delay, loss

            # print(f"插入数据：源节点 {src}, 目标节点 {dst}, 带宽 {bw} Mbps, 时延 {delay} ms, 丢包率 {loss}")

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
