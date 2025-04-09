import sys, os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QWidget, QVBoxLayout, QLabel, \
    QPushButton, QToolTip
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem, \
    QSizePolicy, QMenu, QAction
from PyQt5.QtCore import QTimer, QDateTime, Qt, QRectF
from PyQt5.uic import loadUi
from PyQt5.QtGui import QColor, QBrush
import random
import pymysql
import re, math, time
import threading
current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件夹路径
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))  # 获取上级目录
sys.path.append(parent_dir)  # 添加到 sys.path
from client_operation import client_request_info, receive_result, save

def request_info():
    """请求信息"""
    print("请求信息中...")
    client = client_request_info.ClientRequest('10.0.0.88')
    while True:
        client.request_link_info()
        time.sleep(1)

def receive_info():
    """接收信息"""
    print("等待一段时间后，开始接收信息...")
    time.sleep(5)  # 等待 5 秒
    receiver = receive_result.ReceivePacket()
    receiver.catch_pack()

class DataManager:
    _instance = None  # 单例模式

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DataManager, cls).__new__(cls, *args, **kwargs)
            cls._instance.files = {}  # 初始化文件列表
        return cls._instance

    def add_file(self, key, file_path):
        self.files[key] = file_path

    def get_files(self):
        return self.files

    def delete_file(self, key):
        if key in self.files:
            file_path = self.files.pop(key)
            if os.path.exists(file_path):
                os.remove(file_path)

    def load_files_from_db(self):
        """从数据库加载文件信息"""
        # 假设数据库已经存在文件信息表：files(id, file_name, file_path)
        try:
            connection = pymysql.connect(
                host='localhost',  # 数据库主机
                user='root',  # 数据库用户名
                password='guet',  # 数据库密码
                database='file_info'  # 数据库名称
            )
            cursor = connection.cursor()
            query = "SELECT file_name file_path FROM file_infomation"
            cursor.execute(query)
            results = cursor.fetchall()

            # 将查询结果添加到文件列表
            for result in results:
                file_name = result[0]
                DataManager().add_file(file_name, file_name)

            connection.close()

        except pymysql.MySQLError as e:
            print(f"数据库连接失败: {e}")
            QMessageBox.warning(None, "数据库连接失败", "无法连接到数据库，无法加载文件信息。")


class SecondWindow(QMainWindow):
    def __init__(self):
        super(SecondWindow, self).__init__()
        loadUi('client\\client_operation\\show2.ui', self)
        self.setWindowTitle("交换机信息")

        # 更新系统信息
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_switch_info)
        self.timer.start(5000)
        self.update_switch_info()

        # 设置布局和控件
        layout = QVBoxLayout()
        label = QLabel("这是第二个窗口")
        layout.addWidget(label)

        self.setLayout(layout)

        self.pushButton.clicked.connect(self.open_third_window)
        self.pushButton_switchWindow.clicked.connect(self.open_main_window)

    def fetch_switch_info(self):
        """从数据库中获取交换机的 CPU、内存和磁盘信息"""
        try:
            # 数据库连接
            connection = pymysql.connect(host='localhost', user='root', password='guet', database='sw_info')
            cursor = connection.cursor()

            # 获取最新的交换机数据
            query = """
                SELECT sw, Cpu_Uti, Mem_Uti, Remain_Capacity 
                FROM sw_infomation 
                ORDER BY id DESC
            """
            cursor.execute(query)
            row = cursor.fetchall()

            if row:
                return row  # 返回交换机的 id, CPU利用率, 内存利用率, 剩余容量
            else:
                return None
        except Exception as e:
            print(f"数据库查询错误: {str(e)}")
            return None
        finally:
            cursor.close()
            connection.close()

    def update_switch_info(self):
        """更新显示在 QLineEdit 中的交换机信息"""
        switch_info = self.fetch_switch_info()
        # print("查询到的数据：", switch_info)  # 调试用
        if switch_info:
            # 初始化一个字典来存储每个交换机的信息
            switch_data = {sw: {'cpu': cpu_util, 'mem': mem_util, 'remain_capacity': remain_capacity}
                           for sw, cpu_util, mem_util, remain_capacity in switch_info}

            # 动态更新 QLineEdit 控件中的交换机信息
            self.update_line_edit(self.lineEdit, switch_data, 1)
            self.update_line_edit(self.lineEdit_2, switch_data, 2)
            self.update_line_edit(self.lineEdit_3, switch_data, 3)
            self.update_line_edit(self.lineEdit_4, switch_data, 4)

            # 动态更新 QProgressBar 控件中的进度条信息
            self.update_progress_bar(self.progressBar, switch_data, 1)
            self.update_progress_bar(self.progressBar_2, switch_data, 2)
            self.update_progress_bar(self.progressBar_3, switch_data, 3)
            self.update_progress_bar(self.progressBar_4, switch_data, 4)
        else:
            # 如果无法获取到数据，显示错误信息
            self.lineEdit.setText("无法获取数据")
            self.lineEdit_2.setText("无法获取数据")
            self.lineEdit_3.setText("无法获取数据")
            self.lineEdit_4.setText("无法获取数据")

    def update_line_edit(self, line_edit, switch_data, switch_number):
        """根据 switch_number 更新相应的 QLineEdit 控件"""
        switch_key = switch_number  # 1 -> 交换机1, 2 -> 交换机2 等
        if switch_key in switch_data:
            cpu_util = switch_data[switch_key]['cpu']
            mem_util = switch_data[switch_key]['mem']
            remain_capacity = switch_data[switch_key]['remain_capacity']
            line_edit.setText(
                f"交换机 {switch_key} CPU 使用率: {cpu_util}%, 内存使用率: {mem_util}%, 剩余容量: {remain_capacity}GB")
        else:
            line_edit.setText(f"交换机 {switch_key} 数据未找到")

    def update_progress_bar(self, progress_bar, switch_data, switch_number):
        """根据 switch_number 更新相应的 QProgressBar 控件"""
        switch_key = switch_number
        if switch_key in switch_data:
            remain_capacity = switch_data[switch_key]['remain_capacity']

            # 清理和验证 remain_capacity
            try:
                # 只提取有效的数字部分，去除多余字符（如重复值等）
                # 使用正则表达式提取浮动数字，匹配浮动数值模式
                valid_values = re.findall(r'\d*\.\d+|\d+', remain_capacity)

                # 假设剩余容量只有一个有效值，取第一个有效数字
                if valid_values:
                    remain_capacity = float(valid_values[0])  # 取第一个有效的数字
                else:
                    remain_capacity = 0  # 如果没有有效的数字，则设置为 0
            except ValueError:
                remain_capacity = 0  # 如果转换失败，则设置为 0

            # 保证 remain_capacity 在合理范围内，通常范围是 0 到 1 之间
            remain_capacity = max(0, min(remain_capacity, 1))

            # 将 remain_capacity 转换为 0 到 100 的百分比
            progress_percentage = int(remain_capacity * 100)

            # 设置进度条值，保证其在 0 到 100 之间
            progress_bar.setValue(max(0, min(progress_percentage, 100)))
        else:
            progress_bar.setValue(0)

    def open_third_window(self):
        # 创建并显示第二个窗口
        self.third_window = ThirdWindow()
        # 获取当前窗口的位置
        main_window_position = self.pos()

        # 设置第二个窗口的位置为与当前窗口相同
        self.third_window.move(main_window_position)

        self.third_window.show()
        self.close()  # 关闭当前窗口

    def open_main_window(self):
        # 创建并显示第二个窗口
        self.main_window = MainWindow()
        # 获取当前窗口的位置
        third_window_position = self.pos()

        # 设置第二个窗口的位置为与当前窗口相同
        self.main_window.move(third_window_position)

        self.main_window.show()

        self.close()  # 关闭当前窗口


class ThirdWindow(QMainWindow):
    def __init__(self):
        super(ThirdWindow, self).__init__()
        loadUi('client\\client_operation\\show3.ui', self)
        self.setWindowTitle("数据存储")

        # 绑定按钮点击事件
        self.pushButton_switchWindow.clicked.connect(self.open_second_window)
        self.pushButton_topology.clicked.connect(self.open_main_window)
        self.refresh_file_list()

        # 为 listWidget 设置右键菜单
        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        """显示右键菜单"""
        context_menu = QMenu(self)

        # 添加“存储”选项
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(self.delete_file)
        context_menu.addAction(delete_action)

        # 添加“下载”选项
        download_action = QAction("下载", self)
        download_action.triggered.connect(self.download_file)
        context_menu.addAction(download_action)

        # 显示右键菜单
        context_menu.exec_(self.listWidget.mapToGlobal(pos))

    def delete_file(self):
        """处理文件删除"""
        selected_item = self.listWidget.currentItem()
        if selected_item:
            file_info = selected_item.text()
            # 获取文件的路径
            file_path = self.get_file_path(file_info)
            if not file_path:
                QMessageBox.warning(self, "删除", f"无法找到文件: {file_info}的路径")
                return

            # 打印出文件路径，调试用
            print(f"尝试删除的文件路径: {file_path}")

            # 弹出确认框确认删除操作
            reply = QMessageBox.question(self, '删除文件', f"是否确认删除文件: {file_info}?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    # 删除文件系统中的源文件
                    os.remove(file_path)
                    # 从文件列表中删除文件
                    DataManager().files.remove(file_info)
                    self.refresh_file_list()  # 刷新文件列表
                    QMessageBox.information(self, "删除", f"文件 {file_info} 已删除。")
                except Exception as e:
                    QMessageBox.warning(self, "删除失败", f"删除文件失败: {str(e)}")

    def get_file_path(self, file_info):
        """根据文件信息获取文件的完整路径"""
        # 这里需要根据保存的路径来修改
        # 假设保存路径在 DataManager 中已经保存
        files = DataManager().get_files()
        for file in files:
            if file_info in file:
                # 返回保存时的路径
                return file  # 这里假设保存路径就存储在文件信息中
        return None

    def download_file(self):
        """处理文件下载"""
        selected_item = self.listWidget.currentItem()
        if selected_item:
            file_info = selected_item.text()
            QMessageBox.information(self, "下载", f"正在下载文件: {file_info}")
            # 你可以在这里添加下载文件的具体实现

    def open_second_window(self):
        # 创建并显示第二个窗口
        self.second_window = SecondWindow()
        # 获取当前窗口的位置
        main_window_position = self.pos()

        # 设置第二个窗口的位置为与当前窗口相同
        self.second_window.move(main_window_position)

        self.second_window.show()
        self.close()  # 关闭当前窗口

    def open_main_window(self):
        # 创建并显示第二个窗口
        self.main_window = MainWindow()
        # 获取当前窗口的位置
        third_window_position = self.pos()

        # 设置第二个窗口的位置为与当前窗口相同
        self.main_window.move(third_window_position)

        self.main_window.show()
        self.close()  # 关闭当前窗口

    def refresh_file_list(self):
        """刷新文件列表"""
        self.listWidget.clear()  # 清空当前的文件列表
        DataManager().load_files_from_db()  # 从数据库加载文件名
        files = DataManager().get_files()  # 获取所有文件名
        for file_name in files:
            self.listWidget.addItem(file_name)  # 只显示文件名


class NodeItem(QGraphicsEllipseItem):
    def __init__(self, x, y, cpu_usage, memory_usage):
        super(NodeItem, self).__init__(0, 0, 50, 50)  # 创建一个圆形节点
        self.cpu_usage = cpu_usage
        self.memory_usage = memory_usage
        self.setBrush(QBrush(Qt.blue))
        self.setPos(x, y)
        self.setAcceptHoverEvents(True)  # 启用 hover 事件

    def hoverEnterEvent(self, event):
        # 显示节点信息（CPU 使用率，内存使用率）
        node_info = f"CPU Usage: {self.cpu_usage}%\nMemory Usage: {self.memory_usage}MB"
        QToolTip.showText(event.screenPos(), node_info)
        super(NodeItem, self).hoverEnterEvent(event)  # 保持默认行为

    def hoverLeaveEvent(self, event):
        QToolTip.hideText()  # 隐藏提示
        super(NodeItem, self).hoverLeaveEvent(event)  # 保持默认行为


class EdgeItem(QGraphicsLineItem):
    def __init__(self, node1, node2, bandwidth, delay, packet_loss):
        super(EdgeItem, self).__init__(node1.x() + 25, node1.y() + 25, node2.x() + 25, node2.y() + 25)
        self.bandwidth = bandwidth
        self.delay = delay
        self.packet_loss = packet_loss
        self.setPen(Qt.black)
        self.setAcceptHoverEvents(True)  # 启用 hover 事件

    def hoverEnterEvent(self, event):
        # 显示边信息（带宽，延迟，丢包率）
        edge_info = f"Bandwidth: {self.bandwidth} Mbps\nDelay: {self.delay} ms\nPacket Loss: {self.packet_loss}%"
        QToolTip.showText(event.screenPos(), edge_info)
        super(EdgeItem, self).hoverEnterEvent(event)  # 保持默认行为

    def hoverLeaveEvent(self, event):
        QToolTip.hideText()  # 隐藏提示
        super(EdgeItem, self).hoverLeaveEvent(event)  # 保持默认行为


class NetworkTopology:
    def __init__(self, graphics_view):
        self.graphics_view = graphics_view
        self.scene = QGraphicsScene()  # 初始化 QGraphicsScene
        self.graphics_view.setScene(self.scene)  # 将场景设置到 QGraphicsView

        # 创建节点和连接
        self.create_nodes()

        # 设置场景的视图范围（根据节点位置设置）
        self.set_scene_rect()

    def fetch_topology_data(self):
        try:
            # 数据库连接
            connection = pymysql.connect(host='localhost', user='root', password='guet', database='typo_info')
            cursor = connection.cursor()

            query = "SELECT src, dst, bw, delay, loss FROM typo_infomation"
            cursor.execute(query)
            rows = cursor.fetchall()

            cursor.close()
            connection.close()
        except Exception as e:
            print(f"读取拓扑数据失败：{e}")
            return [], set()
        
        # 使用字典存储最新的 (src, dst) 对：如果同一对出现多次，则保留最后一条记录
        latest_links = {}
        # links = []
        # nodes_set = set()  # 用于存储所有唯一的节点ID

        for row in rows:
            src, dst, bw, delay, loss = row
            key = (src, dst)
            latest_links[key] = {
                "src": key[0],
                "dst": key[1],
                "bw": bw,
                "delay": delay,
                "loss": loss
            }
            # 从最新的连接记录中提取列表和节点信息
            links = list(latest_links.values())
            nodes_set = set()
            for link in links:
                nodes_set.add(link["src"])
                nodes_set.add(link["dst"])

        return links, nodes_set

    def create_nodes(self):
        links, nodes_set = self.fetch_topology_data()

        n = len(nodes_set)
        node_positions = {}

        # 定义圆心和半径，半径根据节点数量自适应，确保相邻节点间隔足够
        center_x, center_y = 250, 250
        # radius = max(250, (n * 60) / (2 * math.pi))
        # angle_increment = 2 * math.pi / n if n > 0 else 0
        area_size = 550  # 限定绘制范围
        min_distance = 55  # 节点之间的最小距离

        def generate_random_position():
            """生成不重叠的随机坐标"""
            while True:
                x = random.randint(center_x - area_size // 2, center_x + area_size // 2)
                y = random.randint(center_y - area_size // 2, center_y + area_size // 2)

                # 确保新点与已有点的距离足够远
                if all(math.hypot(x - px, y - py) >= min_distance for px, py in node_positions.values()):
                    return x, y

        # 生成节点位置，确保不会重叠
        for node_id in sorted(nodes_set):
            node_positions[node_id] = generate_random_position()

        # # 每次刷新时增加一个随机偏移角度
        # random_offset = random.uniform(0, 2 * math.pi)

        # for node_id in nodes_set:
        #     x, y = random.randint(50, 400), random.randint(50, 400)
        #     node_positions[node_id] = (x, y)

        # for i, node_id in enumerate(sorted(nodes_set)):
        #     angle = random_offset + i * angle_increment
        #     x = center_x + radius * math.cos(angle)
        #     y = center_y + radius * math.sin(angle)
        #     node_positions[node_id] = (x, y)

        # 创建节点
        nodes = {}
        for node_id, (x, y) in node_positions.items():
            node = NodeItem(x, y, cpu_usage=random.randint(20, 80), memory_usage=random.randint(1000, 8000))
            self.scene.addItem(node)
            nodes[node_id] = node

            # 为每个节点添加标签 ap1, ap2, ..., ap6
            label = QGraphicsTextItem(f"ap{node_id}")
            label.setPos(x, y - 20)  # 将标签位置设置为节点上方
            label.setDefaultTextColor(QColor(0, 0, 0))  # 设置标签颜色为黑色
            self.scene.addItem(label)

        # 连接节点 (示例连接)
        for link in links:
            src_node = nodes.get(link["src"])
            dst_node = nodes.get(link["dst"])
            if src_node and dst_node:
                edge = EdgeItem(src_node, dst_node, bandwidth=link["bw"], delay=link["delay"], packet_loss=link["loss"])
                self.scene.addItem(edge)

    def clear_topology(self):
        """清空当前场景中的所有项"""
        self.scene.clear()  # 清空场景中的所有项（节点、边等）

    def set_scene_rect(self):
        """根据场景中的元素设置视图范围"""
        # 获取场景的边界
        items = self.scene.items()
        if items:
            # 获取所有项的矩形区域，计算最大范围
            scene_rect = QRectF()
            for item in items:
                scene_rect = scene_rect.united(item.sceneBoundingRect())

            # 设置视图的场景范围
            self.graphics_view.setSceneRect(scene_rect)

from PyQt5.QtCore import QThread, pyqtSignal 
class UploadThread(QThread):
    """用于处理文件上传的线程类"""
    finished = pyqtSignal(bool, str)  # 上传完成信号，参数：是否成功，消息内容

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        
    def run(self):
        try:
            save.upload_files(self.file_path)
            self.finished.emit(True, "文件上传成功！")
        except Exception as e:
            self.finished.emit(False, f"上传文件时出错：{str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # 加载 .ui 文件
        loadUi('client\\client_operation\\show1.ui', self)

        # 设置全局缩放
        self.setup_scaling()

        # 新增：上传/拉取线程实例
        self.upload_thread = None

        # 设置定时器用于更新时间
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(5000)  # 每5秒更新一次

        # 设置定时器用于刷新拓扑显示
        self.topology_timer = QTimer(self)
        self.topology_timer.timeout.connect(self.update_topology)
        self.topology_timer.start(3000)

        # 初始化时更新时间
        self.update_time()

        # 绑定浏览按钮的点击事件
        self.pushButton_browse.clicked.connect(self.browse_file)
        # Save 按钮绑定
        self.pushButton_browse_2.clicked.connect(self.save_file)

        # 增加一个按钮用于切换到第二个窗口
        self.pushButton_switchWindow.clicked.connect(self.open_second_window)
        # 增加一个按钮用于切换到第三个窗口
        self.pushButton_switchWindow_3.clicked.connect(self.open_third_window)

        # 创建并添加 NetworkTopology 到布局
        self.network_topology = NetworkTopology(self.graphicsView)  # 创建 NetworkTopology 实例

        # 确保 graphicsView 能够适应布局
        self.graphicsView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.third_window = None  # 用于存储第三窗口的实例

    def setup_scaling(self):
        """根据系统缩放比例调整界面"""
        # 获取当前的设备像素比
        scale_factor = QApplication.instance().devicePixelRatio()
        if scale_factor > 1:  # 如果设备支持高分辨率缩放
            self.setStyleSheet(f"font-size: {10 * scale_factor}px;")

    def showEvent(self, event):
        """每次窗口显示时重新刷新拓扑数据"""
        self.update_topology()
        super(MainWindow, self).showEvent(event)
        
    def update_time(self):
        # 获取当前日期和时间
        current_datetime = QDateTime.currentDateTime()
        formatted_time = current_datetime.toString('yyyy-MM-dd HH:mm:ss')  # 包括年份
        self.label_time.setText(f"Current Time: {formatted_time}")

    def update_topology(self):
        """每隔3秒刷新拓扑显示"""
        self.network_topology.clear_topology()
        self.network_topology.create_nodes()  # 更新节点和连接
        self.network_topology.set_scene_rect()  # 更新视图的显示范围

    def browse_file(self):
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "All Files (*)")
        if file_path:  # 如果选择了文件
            self.lineEdit_savePath.setText(file_path)  # 将路径设置到文本框中

    def save_file(self):
        # 获取选择的文件路径
        source_file = self.lineEdit_savePath.text()
        print("★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★", source_file)
        if not source_file:
            QMessageBox.warning(self, "Warning", "请先选择文件！")
            return
        
        # 禁用保存按钮，防止重复点击
        self.pushButton_browse_2.setEnabled(False)
        QApplication.processEvents()  # 立即更新界面

        # 显示等待提示
        self.wait_dialog = QMessageBox(
            QMessageBox.Information,
            "上传中",
            "文件正在上传，请稍候...",
            QMessageBox.NoButton,
            self
        )
        self.wait_dialog.show()

        # 创建并启动上传线程
        self.upload_thread = UploadThread(source_file)
        self.upload_thread.finished.connect(self.handle_upload_result)
        self.upload_thread.start()

        # try:
        #     save.upload_files(source_file)
        #     QMessageBox.information(self, "成功", "文件上传成功！")
        # except Exception as e:
        #     QMessageBox.critical(self, "错误", f"上传文件时出错：{str(e)}")
    
    def handle_upload_result(self, success, message):
        """处理上传结果"""
        # 关闭等待对话框并恢复按钮状态
        self.wait_dialog.close()
        self.pushButton_browse_2.setEnabled(True)

        # 显示结果提示
        if success:
            QMessageBox.information(self, "成功", message)
        else:
            QMessageBox.critical(self, "错误", message)
            
    def open_second_window(self):
        # 创建并显示第二个窗口
        self.second_window = SecondWindow()
        # 获取当前窗口的位置
        main_window_position = self.pos()

        # 设置第二个窗口的位置为与第一个窗口相同
        self.second_window.move(main_window_position)

        self.second_window.show()
        self.close()  # 可选：关闭当前窗口

    def open_third_window(self):
        # 创建并显示第三个窗口
        if not self.third_window:
            self.third_window = ThirdWindow()

        # 如果第三窗口已经显示，重新刷新文件列表
        self.third_window.refresh_file_list()  # 假设你有一个刷新文件列表的方法

        # 获取当前窗口的位置
        main_window_position = self.pos()
        # 设置第三个窗口的位置为与第一个窗口相同
        self.third_window.move(main_window_position)

        self.third_window.show()
        self.close()  # 关闭当前窗口


if __name__ == "__main__":

    request_thread = threading.Thread(target=request_info, daemon=True)
    request_thread.start()

    receive_thread = threading.Thread(target=receive_info, daemon=True)
    receive_thread.start()

    print("启动界面显示...")
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())