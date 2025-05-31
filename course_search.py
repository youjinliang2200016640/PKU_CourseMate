import sys
import os
import json
import markdown
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QStatusBar,
                            QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
                            QToolBar, QSizePolicy, QFileDialog, QHeaderView, QMessageBox,
                            QLineEdit, QListWidget, QLabel, QListWidgetItem, QTextEdit)
from PyQt5.QtCore import Qt, QDir, QTimer, QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView

from course import CourseDetailWindow

class CourseSearchWindow(QWidget):
    def __init__(self, initial_query="", bg_color=None, parent=None):
        super().__init__()
        self.parent = parent
        self.bg_color = bg_color or QColor(240, 248, 255)  # 浅蓝色背景
        self.initial_query = initial_query
        self.dataset_path = "./dataset"  # 使用更兼容的路径格式
        self.course_data = self.load_course_data()
        self.init_ui()
        self.setWindowTitle("🔍 课程查询系统")
        self.resize(1000, 800)
        self.children = []
        
    def load_course_data(self):
        """加载课程数据"""
        try:
            with open(os.path.join(self.dataset_path, "info.json"), 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法加载课程数据: {str(e)}")
            return {}
    
    def init_ui(self):
        # 设置窗口背景色
        palette = self.palette()
        palette.setColor(QPalette.Window, self.bg_color)
        self.setPalette(palette)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 查询栏
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入课程名、教师或课程号...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border-radius: 18px;
                border: 2px solid #87CEFA;
                font-size: 18px;
                background-color: white;
            }
        """)
        self.search_input.textChanged.connect(self.search_courses)
        main_layout.addWidget(self.search_input)
        
        # 结果列表
        self.result_list = QListWidget()
        self.result_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(255, 255, 255, 200);
                border-radius: 10px;
                padding: 10px;
                font-size: 18px;
                border: 1px solid #E0E0E0;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #EEEEEE;
            }
            QListWidget::item:selected {
                background-color: #E3F2FD;
                color: black;
            }
        """)
        self.result_list.itemDoubleClicked.connect(self.open_course_detail)
        main_layout.addWidget(self.result_list, 1)
        
        # 执行初始查询
        if self.initial_query:
            self.search_input.setText(self.initial_query)
            self.search_courses(self.initial_query)
        else:
            # 初始显示所有课程
            self.search_courses("")
    
    def search_courses(self, keyword):
        """根据输入查询课程"""
        keyword = keyword.lower()
        self.result_list.clear()
        
        for course_id, course in self.course_data.items():
            # 检查关键字是否匹配课程名、教师或课程号
            match_condition = (
                not keyword or  # 空关键字显示所有
                keyword in course["课程名"].lower() or
                keyword in course_id
            )
            
            if match_condition:
                item_text = f"{course['课程名']} - {course.get('教师', '未知教师')} ({course_id})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, course_id)
                self.result_list.addItem(item)
    
    def open_course_detail(self, item):
        """打开课程详情窗口"""
        course_id = item.data(Qt.UserRole)
        course = self.course_data.get(course_id)
        
        if not course:
            QMessageBox.warning(self, "错误", "未找到课程信息")
            return
            
        # 创建详情窗口
        course_path = os.path.join(
            self.dataset_path,
            course["课程类别"],
            course["开课单位"],
            course["课程名"]
        )
        
        # 使用父窗口的bg_color
        parent = self.parent
        bg_color = self.bg_color
        if parent and hasattr(parent, 'current_color'):
            bg_color = parent.current_color
        
        self.children.append(CourseDetailWindow(course_path, bg_color, self.parent))
        self.children[-1].show()

    def update_color(self, color):
        palette = self.palette()
        palette.setColor(QPalette.Window, color)
        self.setPalette(palette)
        for child in self.children:
            child.update_color(color)

if __name__ == "__main__":
    app = QApplication([])
    app.setFont(QFont("Microsoft YaHei", 10))
    window = CourseSearchWindow("太极拳")
    window.show()
    app.exec_()