'''
Author: 孙石泉 786721684@qq.com
Date: 2024-08-05 14:54:48
LastEditTime: 2024-10-02 20:02:36
LastEditors: GuetYe
Description: 
FilePath: \SD-UANET_load_balance\client\result\result_show_English.py
'''
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei'] #显示中文
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号



def plt_storage_node_init():

    plt.figure(1) # 生成一个图
    x_data = range(1,11)
    y_data_TEDS_2g_ordinary = [13.65, 13.16, 12.89, 13.68, 14.68, 14.69, 13.95, 15.26, 14.68, 14.44]
    y_data_EDWS_2g_ordinary = [12.37, 12.52, 13.26, 13.15, 12.26, 14.39, 13.68, 14.16, 12.85, 12.72]

    y_data_TEDS_5g_ordinary = [7.65, 7.84, 7.24, 7.64, 7.94, 7.16, 6.92, 7.64, 7.28, 7.19]
    y_data_EDWS_5g_ordinary = [6.84, 6.95, 6.85, 6.93, 6.91, 7.15, 7.17, 6.98, 6.53, 7.10]

    plt.plot(x_data, y_data_TEDS_2g_ordinary, color='r', linestyle='-', marker='o', label='TEDS-2.4G')
    plt.plot(x_data, y_data_EDWS_2g_ordinary, color='g', linestyle='-', marker='o', label='EDWS-2.4G')
    plt.plot(x_data, y_data_TEDS_5g_ordinary, color='b', linestyle='-', marker='o', label='TEDS-5G')
    plt.plot(x_data, y_data_EDWS_5g_ordinary, color='y', linestyle='-', marker='o', label='EDWS-5G')

    x_interval = range(11)
    y_interval = range(22)
    plt.xticks(x_interval[::2])  #5是步长
    plt.yticks(y_interval[::3])  #5是步长

    # 显示图例
    plt.legend()  # 默认loc=Best

    # 添加标题
    plt.xlabel('Experiment round')
    plt.ylabel('Transmission time (min)')
    
    plt.savefig('./test_strorage_node_ordinary_english.png',dpi=300,format='png')  # 保存为svg图像

def plt_test_dual_band_init():

    plt.figure(2) # 生成一个图
    x_data = range(1,11)
    y_data_test_dual_band_2g_ordinary = [30.73, 27.32, 27.80, 30.25, 31.28, 33.40, 30.67, 28.55, 28.85, 29.05]
    y_data_test_dual_band_5g_ordinary = [14.07, 13.10, 14.37, 13.73, 14.33, 13.82, 14.33, 13.98, 14.27, 14.60]

    plt.plot(x_data, y_data_test_dual_band_2g_ordinary, color='r', linestyle='-', marker='o', label='EDWS-2.4G')
    plt.plot(x_data, y_data_test_dual_band_5g_ordinary, color='g', linestyle='-', marker='o', label='EDWS-5G')

    x_interval = range(11)
    y_interval = range(50)
    plt.xticks(x_interval[::2])  #5是步长
    plt.yticks(y_interval[::5])  #5是步长

    # 显示图例
    plt.legend()  # 默认loc=Best

    # 添加标题
    plt.xlabel('Experiment round')
    plt.ylabel('Transmission time (min)')
    
    plt.savefig('./test_dual_band_ordinary_english.png',dpi=400,format='png')  # 保存为svg图像


def plt_test_2g_init():
    
    plt.figure(3) # 生成一个图
    x_data = range(1,11)
    y_data_test_2g_ordinary = [12.55, 12.27, 14.90, 14.93, 12.43, 13.22, 13.72, 13.58, 14.00, 13.88]
    y_data_test_2g_mobile = [11.25, 11.5, 12.17, 11.88, 11.08, 11.75, 12.08, 11.43, 11.83, 11.27]

    plt.plot(x_data, y_data_test_2g_ordinary, color='r', linestyle='-', marker='o', label='EDWS-2.4G')
    plt.plot(x_data, y_data_test_2g_mobile, color='g', linestyle='-', marker='o', label='MEDWS-2.4G')

    x_interval = range(11)
    y_interval = range(20)
    plt.xticks(x_interval[::2])  #5是步长
    plt.yticks(y_interval[::2])  #5是步长

    # 显示图例
    plt.legend()  # 默认loc=Best

    # 添加标题
    plt.xlabel('Experiment round')
    plt.ylabel('Transmission time (min)')
    
    plt.savefig('./test_2g_ordinary_english.png',dpi=400,format='png')  # 保存为svg图像


    plt.figure(4) # 生成一个图
    x_data = range(1,11)
    # y_data_test_2g_ordinary = [12.55, 12.27, 14.90, 14.93, 12.43, 13.22, 13.72, 13.58, 14.00, 13.88]
    # y_data_test_2g_mobile = [11.25, 11.5, 12.17, 11.88, 11.08, 11.75, 12.08, 11.43, 11.83, 11.27]
    y_data_test_2g_add_load_ordinary = [17.9, 14.72, 18.7, 16.43, 15.65, 14.3, 15.42, 16.93, 15.25, 16.23]
    y_data_test_2g_add_load_mobile = [11.88, 12.25, 11.43, 12.7, 12.01, 11.5, 12.58, 13.08, 12.83, 11.96]

    plt.plot(x_data, y_data_test_2g_ordinary, color='r', linestyle='-', marker='o', label='EDWS-2.4G')
    plt.plot(x_data, y_data_test_2g_mobile, color='g', linestyle='-', marker='o', label='MEDWS-2.4G')
    plt.plot(x_data, y_data_test_2g_add_load_ordinary, color='b', linestyle='-', marker='o', label='EDWS-2.4G-add load')
    plt.plot(x_data, y_data_test_2g_add_load_mobile, color='y', linestyle='-', marker='o', label='MEDWS-2.4G-add load')

    x_interval = range(11)
    y_interval = range(25)
    plt.xticks(x_interval[::2])  #5是步长
    plt.yticks(y_interval[::2])  #5是步长

    # 显示图例
    plt.legend()  # 默认loc=Best

    # 添加标题
    plt.xlabel('Experiment round')
    plt.ylabel('Transmission time (min)')
    
    plt.savefig('./test_2g_add_load_english.english',dpi=400,format='png')  # 保存为svg图像


def plt_test_5g_init():
    plt.figure(5) # 生成一个图
    x_data = range(1,11)
    y_data_test_5g_ordinary = [10.52, 10.65, 10.22, 10.85, 12.07, 10.42, 11.80, 11.32, 10.57, 11.23]
    y_data_test_5g_mobile = [9.17, 9.43, 8.87, 9.85, 9.97, 10.17, 9.5, 9.67, 10.58, 9.7]

    plt.plot(x_data, y_data_test_5g_ordinary, color='r', linestyle='-', marker='o', label='EDWS-5G')
    plt.plot(x_data, y_data_test_5g_mobile, color='g', linestyle='-', marker='o', label='MEDWS-5G')

    x_interval = range(11)
    y_interval = range(20)
    plt.xticks(x_interval[::2])  #5是步长
    plt.yticks(y_interval[::2])  #5是步长

    # 显示图例
    plt.legend()  # 默认loc=Best

    # 添加标题
    plt.xlabel('Experiment round')
    plt.ylabel('Transmission time (min)')
    
    plt.savefig('./test_5g_ordinary_englisg.png',dpi=400,format='png')  # 保存为svg图像



    plt.figure(6) # 生成一个图
    x_data = range(1,11)
    y_data_test_5g_ordinary_add_load = [12.08, 13.5, 14.15, 12.7, 11.88, 12.93, 12.9, 13.35, 12.8, 12.18]
    y_data_test_5g_mobile_add_load = [10.08, 10.27, 10.87, 9.96, 9.5, 10.16, 9.8, 9.48, 10.37, 9.92]

    plt.plot(x_data, y_data_test_5g_ordinary, color='r', linestyle='-', marker='o', label='EDWS-5G')
    plt.plot(x_data, y_data_test_5g_mobile, color='g', linestyle='-', marker='o', label='MEDWS-5G')
    plt.plot(x_data, y_data_test_5g_ordinary_add_load, color='b', linestyle='-', marker='o', label='EDWS-5G-add load')
    plt.plot(x_data, y_data_test_5g_mobile_add_load, color='y', linestyle='-', marker='o', label='MEDWS-5G-add load')

    x_interval = range(11)
    y_interval = range(20)
    plt.xticks(x_interval[::2])  #5是步长
    plt.yticks(y_interval[::2])  #5是步长

    # 显示图例
    plt.legend()  # 默认loc=Best

    # 添加标题
    plt.xlabel('Experiment round')
    plt.ylabel('Transmission time (min)')
    
    plt.savefig('./test_5g_add_load_englisg.png',dpi=400,format='png')  # 保存为svg图像






if __name__ == '__main__':
    plt_storage_node_init()
    # plt_test_dual_band_init()
    # plt_test_2g_init()
    # plt_test_5g_init()
    plt.show()





