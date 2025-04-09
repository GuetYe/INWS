'''
Author: Sun Shiquan email:786721684@qq.com
Date: 2024-11-25 17:16:47
LastEditTime: 2024-11-25 17:21:07
LastEditors: Sun Shiquan
Description: 
FilePath: \SD-UANET_load_balance_2\controller\ryu_operation\log_module.py
'''

import logging

# 创建一个日志记录器
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG) # 设置处理器(Handler)处理的日志消息最低级别

# 创建一个文件处理器
file_handler = logging.FileHandler('my_log_file.log')
file_handler.setLevel(logging.WARNING)

# 创建一个格式化器
formatter = logging.Formatter('%(asctime)s - %(levelname)-10s - %(filename)s - %(funcName)s:%(lineno)d - %(message)s')
# 将格式化器添加到文件处理器
file_handler.setFormatter(formatter)
# 将文件处理器添加到日志记录器
logger.addHandler(file_handler)


