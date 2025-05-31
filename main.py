import sys
import os
import json
import markdown
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                            QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
                            QToolBar, QSizePolicy, QFileDialog, QHeaderView, QMessageBox,
                            QLineEdit, QListWidget, QLabel, QListWidgetItem, QTextEdit)
from PyQt5.QtCore import Qt, QDir, QTimer, QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView

from course_table import CourseTableWindow
from course_search import CourseSearchWindow
from chat_assistant import ChatAssistantWindow
from course_list import CourseListWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.child_windows = {
            "table": None,
            "list": None,
            "search": None,
            "assistant" : None
        }
        self.current_color = QColor(255, 240, 240)        
        self.course_details = {}
        self.init_ui()
        self.child_windows["table"] = CourseTableWindow(bg_color=self.current_color, parent=self)
        self.child_windows["table"].setAttribute(Qt.WA_DeleteOnClose)
        self.child_windows["table"].destroyed.connect(
            lambda: self._on_child_close("table"))

    def init_ui(self):
        self._init_window_settings()
        self._init_toolbar()
        self._init_central_widget()

    def _init_window_settings(self):
        """初始化窗口基本设置"""
        cute_font = QFont("Comic Sans MS", 12)
        self.setFont(cute_font)
        self.setWindowTitle("🐻 主窗口")
        self.setGeometry(100, 100, 800, 500)

    def _init_toolbar(self):
        """初始化顶部颜色工具栏"""
        toolbar = QToolBar("工具栏")
        toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        
        # 颜色按钮容器
        button_container = self._create_color_buttons()
        toolbar.addWidget(button_container)

    def _create_color_buttons(self):
        """创建颜色按钮组"""
        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        colors = [
            ("🔴 红色", QColor(255,200,200)),
            ("🟢 绿色", QColor(200,255,200)),
            ("🔵 蓝色", QColor(200,200,255)),
            ("⚪ 白色", QColor(255,255,255))
        ]
        
        for text, color in colors:
            btn = self._create_color_button(text, color)
            layout.addWidget(btn)
        
        container.setLayout(layout)
        return container

    def _create_color_button(self, text, color):
        """创建单个颜色按钮"""
        btn = QPushButton(text)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        btn.setStyleSheet("""
            QPushButton { 
                margin:3px; padding:8px; border-radius:8px;
                background-color:rgba(255,255,255,150); 
            }
            QPushButton:hover { 
                background-color:rgba(255,255,255,200); 
            }
        """)
        btn.clicked.connect(lambda _,c=color: self.set_color(c))
        return btn

    def _create_search_bar(self):
        """创建自适应搜索框组件"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # 搜索输入框（占70%宽度）
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索课程...")
        self.search_input.setSizePolicy(
            QSizePolicy.Expanding,  # 水平策略
            QSizePolicy.Expanding     # 垂直固定
        )
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border-radius: 18px;
                font-size: 14px;
                border: 2px solid #FFB6C1;
                min-width: 400px;
            }
        """)
        
        # 搜索按钮（占30%宽度）
        self.btn_search = QPushButton("🔍")
        self.btn_search.setSizePolicy(
            QSizePolicy.Preferred,  # 水平自适应
            QSizePolicy.Expanding   # 垂直填充
        )
        self.btn_search.setStyleSheet("""
            QPushButton {
                min-width: 60px;
                max-width: 100px;
                border-radius: 18px;
                background-color: #FFB6C1;
                color: white;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #FF69B4;
            }
        """)
        self.btn_search.clicked.connect(self.toggle_search_window)
        
        # 设置布局比例（搜索框:按钮 = 5:1）
        layout.addWidget(self.search_input, stretch=5)
        layout.addWidget(self.btn_search, stretch=1)
        
        return container

    def _create_function_buttons(self):
        """创建功能按钮布局"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(50, 0, 50, 30)
        layout.setSpacing(20)
        
        # 添加新按钮
        layout.addWidget(self._create_course_button())
        layout.addWidget(self._create_list_button())
        layout.addWidget(self._create_assistant_button())  # 新增
        
        return container

    def _create_assistant_button(self):
        """智能助手按钮"""
        btn = QPushButton("🎓 智能选课助手")
        btn.setFixedSize(180, 50)
        btn.setStyleSheet("""
            QPushButton {
                padding: 12px;
                border-radius: 25px;
                background-color: #77DD77;
                color: #FFFFFF;
                font-size: 16px;
                border: 2px solid #FFFFFF;
            }
            QPushButton:hover {
                background-color: #66CC66;
                border-color: #77DD77;
            }
        """)
        btn.clicked.connect(self.toggle_assistant_window)
        return btn

    def _init_central_widget(self):
        """初始化自适应中央布局"""
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 添加弹性容器
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # 垂直居中布局
        container_layout.addStretch()
        container_layout.addWidget(self._create_title(), 0, Qt.AlignCenter)
        container_layout.addWidget(self._create_search_bar(), 0, Qt.AlignCenter)
        container_layout.addWidget(self._create_function_buttons(), 0, Qt.AlignCenter)
        container_layout.addStretch()
        
        # 设置弹性比例
        main_layout.addWidget(container, stretch=1)
        
        self.setCentralWidget(central_widget)


    def _create_course_button(self):
        """课表功能按钮（更新样式）"""
        btn = QPushButton("📅 我的课表")
        btn.setFixedSize(180, 50)  # 固定按钮尺寸
        btn.setStyleSheet("""
            QPushButton {
                padding: 12px;
                border-radius: 25px;
                background-color: #FFB6C1;
                color: #FFFFFF;
                font-size: 16px;
                border: 2px solid #FFFFFF;
            }
            QPushButton:hover {
                background-color: #FF69B4;
                border-color: #FFB6C1;
            }
        """)
        btn.clicked.connect(self.toggle_table_window)
        return btn

    def _create_list_button(self):
        """文档功能按钮（更新样式）"""
        btn = QPushButton("📚 课程列表")
        btn.setFixedSize(180, 50)  # 固定按钮尺寸
        btn.setStyleSheet("""
            QPushButton {
                padding: 12px;
                border-radius: 25px;
                background-color: #87CEFA;
                color: #FFFFFF;
                font-size: 16px;
                border: 2px solid #FFFFFF;
            }
            QPushButton:hover {
                background-color: #6495ED;
                border-color: #87CEFA;
            }
        """)
        btn.clicked.connect(self.toggle_list_window)
        return btn

    def _create_title(self):
        """创建标题组件"""
        label = QLabel("PKU智能选课助手")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                font-family: 'Comic Sans MS';
                font-size: 24px;
                color: #FF69B4;
                padding: 15px;
            }
        """)
        return label

    def _create_center_panel(self):
        """创建中央面板（含搜索框）"""
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 垂直居中实现
        layout.addStretch()
        layout.addWidget(self._create_search_bar())
        layout.addStretch()
        
        container.setLayout(layout)
        return container

    def set_color(self, color):
        self.current_color = color
        palette = self.palette()
        palette.setColor(QPalette.Window, color)
        self.setPalette(palette)
        
        # 同步所有子窗口颜色
        for window in self.child_windows.values():
            if window:
                window.update_color(color)

    def _on_child_close(self, window_type):
        
        if window_type == "table":
            self.course_details = self.child_windows["table"].course_details
            self.child_windows["table"] = CourseTableWindow(bg_color=self.current_color, parent=self)
            self.child_windows["table"].setAttribute(Qt.WA_DeleteOnClose)
            self.child_windows["table"].destroyed.connect(
                lambda: self._on_child_close("table"))
        else:
            self.child_windows[window_type] = None

    def toggle_table_window(self):
        if self.child_windows["table"] == None:
            self.child_windows["table"] = CourseTableWindow(bg_color=self.current_color, parent=self)
            self.child_windows["table"].setAttribute(Qt.WA_DeleteOnClose)
            self.child_windows["table"].destroyed.connect(
                lambda: self._on_child_close("table"))
            self.child_windows["table"].show()
        else:
            self.child_windows["table"].show()
            self.child_windows["table"].raise_()
            self.child_windows["table"].activateWindow()

    def toggle_list_window(self):
        if self.child_windows["list"] == None:
            self.child_windows["list"] = CourseListWindow(bg_color=self.current_color, parent=self)
            self.child_windows["list"].setAttribute(Qt.WA_DeleteOnClose)
            self.child_windows["list"].destroyed.connect(
                lambda: self._on_child_close("list"))
            self.child_windows["list"].show()
        else:
            self.child_windows["list"].raise_()
            self.child_windows["list"].activateWindow()

    def toggle_search_window(self):
        if self.child_windows["search"] == None:
            self.child_windows["search"] = CourseSearchWindow(initial_query=self.search_input.text(), bg_color=self.current_color, parent=self)
            self.child_windows["search"].setAttribute(Qt.WA_DeleteOnClose)
            self.child_windows["search"].destroyed.connect(
                lambda: self._on_child_close("search"))
            self.child_windows["search"].show()
        else:
            self.child_windows["search"].raise_()
            self.child_windows["search"].activateWindow()

    def toggle_assistant_window(self):
        if self.child_windows["assistant"] == None:
            self.child_windows["assistant"] = ChatAssistantWindow(bg_color=self.current_color)
            self.child_windows["assistant"].setAttribute(Qt.WA_DeleteOnClose)
            self.child_windows["assistant"].destroyed.connect(
                lambda: self._on_child_close("assistant"))
            self.child_windows["assistant"].show()
        else:
            self.child_windows["assistant"].raise_()
            self.child_windows["assistant"].activateWindow()

    def open_list_window(self, filepath):
        if not self.child_windows["list"]:
            self.toggle_list_window()
        if self.child_windows["list"]:
            self.child_windows["list"].load_list(filepath)

    def add_course_to_schedule(self, course_num):
        # 获取当前课表数据

        with open(os.path.join(".\dataset", "info.json"), 'r', encoding='utf-8') as f:
            data = json.load(f)[course_num]

        course_info = self.convert_course_data(data)
        if self.child_windows["table"] != None:
            self.child_windows["table"].add_course_to_schedule(course_info)

    def convert_course_data(self, course_data):
        # 基本字段转换
        converted = {
            "name": course_data["课程名"],
            "teacher": course_data["教师"],
            "学分": course_data["学分"],
            "课程号": course_data["课程号"],
            "开课单位": course_data["开课单位"],
            "schedule": []
        }
        
        # 处理上课时间及教室
        for session in course_data["上课时间及教室"]:
            # 解析周次信息（格式如："1~1周"）
            weeks_str = session[0]
            if "~" in weeks_str:
                start_week, end_week = weeks_str.split("~")
                end_week = end_week.replace("周", "")  # 移除末尾的"周"
                weeks = f"{start_week}-{end_week}周"
            else:
                weeks = weeks_str
            
            # 星期几（0=周一，1=周二，...）
            day = session[1]
            
            # 解析节次范围（格式如："5~8"）
            sections_range = session[2]
            if "~" in sections_range:
                start_section, end_section = map(int, sections_range.split("~"))
                sections = list(range(start_section, end_section + 1))
            else:
                # 如果只有单节
                sections = [int(sections_range)]
            
            # 教室信息
            if session[3]:
                classroom = session[3].strip()
            else:
                classroom = "无"
            
            # 添加到schedule
            converted["schedule"].append({
                "day": day,
                "sections": sections,
                "weeks": weeks,
                "classroom": classroom
            })
        
        return converted

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Comic Sans MS", 12))
    
    # 创建courses目录（如果不存在）
    course_dir = os.path.join(os.path.dirname(__file__), "courses")
    if not os.path.exists(course_dir):
        os.makedirs(course_dir)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())