import os
import sys
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItemIterator,
                            QTreeWidgetItem, QSplitter, QLabel, QPushButton, QLineEdit,
                            QTextEdit, QFileDialog, QMessageBox, QHeaderView, QApplication)
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtGui import QPalette, QColor, QFont

from course import CourseDetailWindow

class CourseListWindow(QWidget):
    def __init__(self, bg_color=None, parent=None):
        super().__init__()
        self.dataset_path =".\dataset"
        self.parent = parent
        self.bg_color = bg_color or QColor(240, 248, 255)
        self.init_ui()
        self.load_courses()
        self.children = []
        self.setWindowTitle("📚 课程列表")
        self.resize(1000, 700)
        
    def init_ui(self):
        
        palette = self.palette()
        palette.setColor(QPalette.Window, self.bg_color)
        self.setPalette(palette)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题
        title_label = QLabel("课程列表")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #9370DB;
                margin-bottom: 15px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # 课程树
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)  # 隐藏表头
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
                font-size: 20px;
                border: 1px solid #E6E6FA;
            }
            QTreeWidget::item {
                padding: 6px 8px;  /* 减少上下内边距 */
            }
            QTreeWidget::item:hover {
                background-color: #F5F5F5;
            }
            QTreeWidget::item:selected {
                background-color: #E6E6FA;
                color: black;
            }
        """)
        self.tree.itemDoubleClicked.connect(self.open_course_detail)

        main_layout.addWidget(self.tree)
    
    def load_courses(self):
        """加载课程分类和课程"""
        if not os.path.exists(self.dataset_path):
            QMessageBox.warning(self, "错误", f"数据集路径不存在: {self.dataset_path}")
            return
        
        self.tree.clear()
        
        # 添加顶级分类
        categories = ["专业课", "体育课", "公选课", "英语课", "通识课"]
        for category in categories:
            category_path = os.path.join(self.dataset_path, category)
            if not os.path.exists(category_path):
                continue
                
            category_item = QTreeWidgetItem(self.tree)
            category_item.setText(0, category)
            category_item.setFirstColumnSpanned(True)
            category_item.setData(0, Qt.UserRole, category_path)
            
            # 加载学院
            for college in os.listdir(category_path):
                college_path = os.path.join(category_path, college)
                if not os.path.isdir(college_path):
                    continue
                    
                college_item = QTreeWidgetItem(category_item)
                college_item.setText(0, college)
                college_item.setData(0, Qt.UserRole, college_path)
                
                # 加载课程
                for course in os.listdir(college_path):
                    course_path = os.path.join(college_path, course)
                    if not os.path.isdir(course_path):
                        continue
                        
                    course_item = QTreeWidgetItem(college_item)
                    course_item.setText(0, course)  # 单列显示课程名[3](@ref)
                    course_item.setData(0, Qt.UserRole, course_path)
        
        self.tree.expandAll()

    def load_course_info(self, course_path):
        """从课程文件夹加载info.json"""
        info_path = ".\dataset\info.json"
        if not os.path.exists(info_path):
            return None
            
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载课程信息失败: {str(e)}")
            return None
    
    def open_course_detail(self, item, column):
        """打开课程详情窗口"""
        course_path = item.data(0, Qt.UserRole)
        if not course_path or not os.path.isdir(course_path):
            return
        # 只处理课程项（叶子节点）
        if item.childCount() > 0:
            return
            
        # 加载课程信息
        course_data = self.load_course_info(course_path)
        if not course_data:
            QMessageBox.warning(self, "错误", "无法加载课程信息")
            return
            
        # 创建详情窗口
        self.children.append( CourseDetailWindow(
            course_path,
            bg_color=self.bg_color,  # 浅蓝色背景
            parent=self.parent
        ))
        self.children[-1].show()

    def update_color(self, color):
        palette = self.palette()
        palette.setColor(QPalette.Window, color)
        self.setPalette(palette)
        for child in self.children:
            child.update_color(color)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Comic Sans MS", 12))

    # 创建并显示窗口
    detail_window = CourseListWindow()
    detail_window.show()
    
    sys.exit(app.exec_())