from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QPushButton, QLabel, QScrollArea, QFrame, QSplitter,
                            QTextEdit, QMessageBox, QSizePolicy, QApplication)

import sys

class CourseTableWindow(QWidget):
    def __init__(self, bg_color=None, parent=None):
        super().__init__()
        self.bg_color = bg_color or QColor(240, 248, 255)
        self.parent = parent
        self.course_details = {}  # 存储课程详细信息
        if self.parent:
            self.course_details = self.parent.course_details
        self.init_ui()
        self.setWindowTitle("📅 我的课表")
        self.resize(1200, 800)
        
    def init_ui(self):
        palette = self.palette()
        palette.setColor(QPalette.Window, self.bg_color)
        self.setPalette(palette)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题
        title_label = QLabel("我的课程表")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #9370DB;
                margin-bottom: 15px;
                text-align: center;
            }
        """)
        main_layout.addWidget(title_label)
        
        # 使用垂直分割器，允许调整上下区域大小
        splitter = QSplitter(Qt.Vertical)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #D8BFD8;
                height: 4px;
            }
        """)
        
        # 上半部分 - 课表主体（可滚动）
        schedule_scroll = QScrollArea()
        schedule_scroll.setWidgetResizable(True)
        schedule_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        schedule_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                width: 12px;
                background: #F0F0F0;
            }
            QScrollBar::handle:vertical {
                background: #D8BFD8;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        schedule_widget = QWidget()
        schedule_layout = QHBoxLayout(schedule_widget)
        
        # 左侧时间轴
        time_axis = QVBoxLayout()
        time_axis.setContentsMargins(0, 40, 0, 0)  # 顶部留出空间
        time_axis.addWidget(QLabel(""))  # 占位符，对应日期标题位置
        
        time_list = ["8:00 ~ 8:50","9:00 ~ 9:50","10:10 ~ 11:00","11:10 ~ 12:00","13:00 ~ 13:50","14:00 ~ 14:50","15:10 ~ 16:00","16:10 ~ 17:00","17:10 ~ 18:00","18:40 ~ 19:30","19:40 ~ 20:30","20:40 ~ 21:30"]
        for i in range(12):
            time_label = QLabel(time_list[i])
            time_label.setAlignment(Qt.AlignCenter)
            time_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    background-color: #E6E6FA;
                    border-radius: 8px;
                    padding: 8px;
                    margin: 2px;
                    min-height: 60px;
                }
            """)
            time_axis.addWidget(time_label)
        
        schedule_layout.addLayout(time_axis, 1)  # 时间轴占1份宽度
        
        # 课表网格（放在滚动区域内）
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(2)
        
        # 日期标题
        days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        for col, day in enumerate(days):
            day_label = QLabel(day)
            day_label.setAlignment(Qt.AlignCenter)
            day_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    background-color: #D8BFD8;
                    border-radius: 8px;
                    padding: 6px;
                    margin: 2px;
                }
            """)
            day_label.setFixedHeight(50)
            grid_layout.addWidget(day_label, 0, col)
        
        # 创建课程格子
        self.course_cells = [[None for _ in range(7)] for _ in range(12)]
        for row in range(12):  # 12节课
            for col in range(7):  # 7天
                cell = QPushButton("")
                cell.setFixedSize(140, 60)
                cell.setStyleSheet("""
                    QPushButton {
                        background-color: #F8F8FF;
                        border: 1px solid #E6E6FA;
                        border-radius: 8px;
                        font-size: 12px;
                        padding: 8px;     
                        margin: 2px;    
                        min-height: 60px;
                    }
                    QPushButton:hover {
                        background-color: #E6E6FA;
                    }
                """)
                cell.clicked.connect(lambda _, r=row, c=col: self.show_course_details(r, c))
                cell.setProperty("row", row)
                cell.setProperty("col", col)
                cell.installEventFilter(self)  # 用于双击事件
                self.course_cells[row][col] = cell
                grid_layout.addWidget(cell, row+1, col)
        
        # 设置网格大小策略，使其可以扩展
        grid_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        schedule_layout.addWidget(grid_widget, 7)  # 课表网格占7份宽度
        
        # 将课表添加到滚动区域
        schedule_scroll.setWidget(schedule_widget)
        splitter.addWidget(schedule_scroll)
        
        # 下半部分 - 课程详细信息
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setContentsMargins(10, 10, 10, 10)
        
        details_label = QLabel("课程详细信息")
        details_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #9370DB;
                margin: 10px 0;
            }
        """)
        details_layout.addWidget(details_label)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                border: 1px solid #E6E6FA;
            }
        """)
        self.details_text.setMinimumHeight(150)
        details_layout.addWidget(self.details_text)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_remove = QPushButton("删除课程")
        self.btn_remove.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #FF6B6B;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
            QPushButton:disabled {
                background-color: #D3D3D3;
            }
        """)
        self.btn_remove.setEnabled(False)
        self.btn_remove.clicked.connect(self.remove_course)
        btn_layout.addWidget(self.btn_remove)
        
        btn_layout.addStretch()
        details_layout.addLayout(btn_layout)
        
        splitter.addWidget(details_widget)
        
        # 设置初始分割比例 (70% 课表, 30% 详情)
        splitter.setSizes([int(self.height() * 0.7), int(self.height() * 0.3)])
        
        main_layout.addWidget(splitter)
        
        # 初始化状态
        self.selected_cell = None

        self.initialize_courses()

    def initialize_courses(self):
        """根据 course_details 初始化课表"""
        for (row, col), course_info in self.course_details.items():
            if 0 <= row < 12 and 0 <= col < 7:  # 确保行列在有效范围内
                cell = self.course_cells[row][col]
                name = course_info.get("name", "")
                classroom = ""
                
                # 从课程信息中查找对应的教室
                for session in course_info.get("schedule", []):
                    if session.get("day") == col:
                        classroom = session.get("classroom", "")
                        break
                
                # 设置单元格内容和样式
                cell.setText(f"{name}\n{classroom}")
                cell.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #77DD77;
                        border: 1px solid #66CC66;
                        border-radius: 8px;
                        font-size: 12px;
                        padding: 5px;
                        color: #333;
                    }}
                    QPushButton:hover {{
                        background-color: #66CC66;
                    }}
                """)
    
    def eventFilter(self, source, event):
        """处理双击事件"""
        if event.type() == event.MouseButtonDblClick and source in [cell for row in self.course_cells for cell in row]:
            row = source.property("row")
            col = source.property("col")
            self.remove_course(row, col)
            return True
        return super().eventFilter(source, event)
    
    def add_course_to_schedule(self, course_info):
        """将课程添加到课表，如果任何时间段有冲突则不添加"""
        name = course_info.get("name", "未命名课程")
        schedule = course_info.get("schedule", [])
        
        if not schedule:
            QMessageBox.warning(self, "添加失败", "该课程没有有效的时间安排")
            return
        
        # 第一步：检查所有时间段是否有冲突
        conflicts = []  # 存储冲突信息
        
        for session in schedule:
            day = session.get("day", -1)
            sections = session.get("sections", [])
            classroom = session.get("classroom", "")
            
            if day < 0 or day > 6 or not sections:
                continue
                
            for section in sections:
                if 1 <= section <= 12:
                    row = section - 1
                    cell = self.course_cells[row][day]
                    
                    # 如果该时间段已有课程
                    if cell.text():
                        conflict_name = cell.text().split("\n")[0]
                        # 避免与自己冲突（同一课程的不同时间段）
                        if conflict_name != name:
                            conflicts.append({
                                "time": f"周{['一','二','三','四','五','六','日'][day]} 第{section}节",
                                "existing": conflict_name,
                                "new": name
                            })
        
        # 如果检测到冲突，显示冲突信息并返回
        if conflicts:
            conflict_message = "检测到以下时间冲突，无法添加课程：\n\n"
            for conflict in conflicts:
                conflict_message += f"{conflict['time']} 已有课程: {conflict['existing']}\n"
                conflict_message += f"    尝试添加: {conflict['new']}\n\n"
            
            QMessageBox.warning(self, "时间冲突", conflict_message)
            return
        
        # 第二步：如果没有冲突，添加课程到所有时间段
        added = False
        for session in schedule:
            day = session.get("day", -1)
            sections = session.get("sections", [])
            classroom = session.get("classroom", "")
            
            if day < 0 or day > 6 or not sections:
                continue
                
            for section in sections:
                if 1 <= section <= 12:
                    row = section - 1
                    cell = self.course_cells[row][day]
                    
                    # 添加课程到课表
                    cell.setText(f"{name}\n{classroom}")
                    cell.setStyleSheet(f"""
                        QPushButton {{
                            background-color: #77DD77;
                            border: 1px solid #66CC66;
                            border-radius: 8px;
                            font-size: 12px;
                            padding: 5px;
                            color: #333;
                        }}
                        QPushButton:hover {{
                            background-color: #66CC66;
                        }}
                    """)
                    
                    # 存储课程详细信息
                    self.course_details[(row, day)] = course_info
                    added = True
        
        # 第三步：更新父窗口
        if added:
            QMessageBox.information(self, "添加成功", f"课程 '{name}' 已添加到课表")
            if self.parent:
                self.parent.course_details = self.course_details
        else:
            QMessageBox.warning(self, "添加失败", "无法添加课程到课表，请检查时间安排")
    
    def show_course_details(self, row, col):
        """显示选中课程的详细信息"""
        self.selected_cell = (row, col)
        
        # 重置所有单元格样式
        for r in range(12):
            for c in range(7):
                cell = self.course_cells[r][c]
                if cell.text():
                    cell.setStyleSheet(f"""
                        QPushButton {{
                            background-color: #77DD77;
                            border: 1px solid #66CC66;
                            border-radius: 8px;
                            font-size: 12px;
                            padding: 5px;
                            color: #333;
                        }}
                        QPushButton:hover {{
                            background-color: #66CC66;
                        }}
                    """)
        
        # 高亮选中单元格
        cell = self.course_cells[row][col]
        if cell.text():
            cell.setStyleSheet(f"""
                QPushButton {{
                    background-color: #FFD700;
                    border: 2px solid #FFA500;
                    border-radius: 8px;
                    font-size: 12px;
                    padding: 5px;
                    color: #333;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #FFC107;
                }}
            """)
            self.btn_remove.setEnabled(True)
            
            # 显示课程详细信息
            course_info = self.course_details.get((row, col), {})
            details = self.format_course_details(course_info)
            self.details_text.setHtml(details)
        else:
            self.details_text.setHtml("<p style='color:#888; text-align:center;'>请选择有课程的时段</p>")
            self.btn_remove.setEnabled(False)
    
    def format_course_details(self, course_info):
        """格式化课程详细信息为HTML"""
        if not course_info:
            return "<p>无课程信息</p>"
        
        name = course_info.get("name", "未知课程")
        teacher = course_info.get("teacher", "未知教师")
        credit = course_info.get("学分", "未知学分")
        course_id = course_info.get("课程号", "未知课程号")
        department = course_info.get("开课单位", "未知单位")
        schedule = course_info.get("schedule", [])
        
        details = f"""
        <div style='font-family: Arial;'>
            <h2 style='color: #9370DB;'>{name}</h2>
            <p><b>教师:</b> {teacher}</p>
            <p><b>课程号:</b> {course_id}</p>
            <p><b>学分:</b> {credit}</p>
            <p><b>开课单位:</b> {department}</p>
            
            <h3 style='color: #9370DB; margin-top: 15px;'>时间安排</h3>
        """
        
        if schedule:
            details += "<ul>"
            for session in schedule:
                day_map = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
                day = day_map[session.get("day", 0)] if session.get("day") is not None else "未知"
                sections = session.get("sections", [])
                weeks = session.get("weeks", "未知周次")
                classroom = session.get("classroom", "未知教室")
                
                section_str = ", ".join(map(str, sections))
                details += f"<li>{weeks} {day} 第{section_str}节 @{classroom}</li>"
            details += "</ul>"
        else:
            details += "<p>无时间安排信息</p>"
        
        details += "</div>"
        return details
    
    def remove_course(self, row=None, col=None):
        """删除课程 - 删除所有同名课程的所有时间段"""
        if row is None or col is None:
            if self.selected_cell:
                row, col = self.selected_cell
            else:
                return
        
        cell = self.course_cells[row][col]
        if not cell.text():
            return
            
        # 获取课程名称（不包含教室信息）
        course_name = cell.text().split("\n")[0]
        
        # 检查是否有多个时间段
        time_slots = []
        for r in range(12):
            for c in range(7):
                other_cell = self.course_cells[r][c]
                if other_cell.text() and other_cell.text().split("\n")[0] == course_name:
                    time_slots.append((r, c))
        
        if not time_slots:
            return
        
        # 确认对话框
        if len(time_slots) > 1:
            message = f"课程 '{course_name}' 有 {len(time_slots)} 个时间段\n确定要删除所有时间段吗?"
        else:
            message = f"确定要删除课程 '{course_name}' 吗?"
        
        reply = QMessageBox.question(
            self, "确认删除",
            message,
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 删除所有同名课程的时间段
            for r, c in time_slots:
                cell = self.course_cells[r][c]
                cell.setText("")
                cell.setStyleSheet("""
                    QPushButton {
                        background-color: #F8F8FF;
                        border: 1px solid #E6E6FA;
                        border-radius: 8px;
                        font-size: 12px;
                        padding: 8px;     
                        margin: 2px;    
                        min-height: 60px;
                    }
                    QPushButton:hover {
                        background-color: #E6E6FA;
                    }
                """)
                
                # 删除存储的课程信息
                if (r, c) in self.course_details:
                    del self.course_details[(r, c)]
            
            # 更新UI状态
            self.details_text.setHtml(f"<p style='color:#888; text-align:center;'>已删除课程 '{course_name}' 的所有时间段</p>")
            self.btn_remove.setEnabled(False)
            
            # 如果当前选中的单元格被删除，清除选中状态
            if self.selected_cell in time_slots:
                self.selected_cell = None

        if self.parent:
            self.parent.course_details = self.course_details

    def update_color(self, color):
        palette = self.palette()
        palette.setColor(QPalette.Window, color)
        self.setPalette(palette)
if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    app.setFont(QFont("Comic Sans MS", 12))
    schedule_window = CourseTableWindow(parent=None)

    # 添加课程到课表
    course_info = {
        "name": "人工智能前沿",
        "teacher": "张教授",
        "学分": 3,
        "课程号": "CS101",
        "开课单位": "计算机学院",
        "schedule": [
            {"day": 1, "sections": [3, 4], "weeks": "1-16周", "classroom": "二教201"},
            {"day": 3, "sections": [5, 6], "weeks": "1-16周", "classroom": "三教305"}
        ]
    }
    schedule_window.add_course_to_schedule(course_info)

    # 显示窗口
    schedule_window.show()
    sys.exit(app.exec_())