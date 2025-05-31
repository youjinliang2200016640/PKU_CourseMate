import sys
import os
import re
import json
import markdown
import csv
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                            QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
                            QToolBar, QSizePolicy, QFileDialog, QHeaderView, QMessageBox,
                            QLineEdit, QListWidget, QLabel, QListWidgetItem, QTextEdit)
from PyQt5.QtCore import Qt, QDir, QTimer, QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QPalette, QColor, QFont, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView

class MarkdownViewer(QWidget):
    def __init__(self, bg_color):
        super().__init__()
        self.bg_color = bg_color
        self.current_md = ""  # 新增：存储当前Markdown内容
        self.current_path = ""  # 新增：存储当前文件路径
        self.init_ui()
        self.setWindowTitle("📖 Markdown浏览器")
        self.setGeometry(200, 200, 600, 400)
        self.auto_load_md()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Web视图
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("background-color: transparent;")
        
        # layout.addLayout(toolbar)
        layout.addWidget(self.web_view)
        self.setLayout(layout)
        self.update_color(self.bg_color)

    def update_color(self, color):
        """更新颜色并刷新显示"""
        self.bg_color = color
        
        # 更新窗口背景
        palette = self.palette()
        palette.setColor(QPalette.Window, color)
        self.setPalette(palette)
        
        # 更新网页背景
        self.web_view.page().setBackgroundColor(color)
        
        # 重新渲染当前内容（新增）
        if self.current_md:
            self._render_md(self.current_md)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开Markdown文件", "", "Markdown文件 (*.md)"
        )
        if file_path:
            self.load_markdown(file_path)

    def auto_load_md(self):
        """自动加载test.md"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        md_path = os.path.join(current_dir, "test.md")
        
        if os.path.exists(md_path):
            self.load_markdown(md_path)
        else:
            error_html = """
            <h2 style='color: #ff4444;'>⚠️ 文件未找到</h2>
            <p>请在程序同级目录创建<code>test.md</code>文件</p>
            """
            self.web_view.setHtml(error_html)

    def load_markdown(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.current_md = f.read()  # 存储内容
                self.current_path = file_path
                self._render_md(self.current_md)
        except Exception as e:
            self.web_view.setHtml(f"<h2>❌ 读取文件失败：{str(e)}</h2>")

    def _render_md(self, md_text):
        # 转换Markdown为HTML
        md_text = md_text.replace(
            '![wordcloud](wordcloud.png)',
            ''
        )
        html = markdown.markdown(md_text)
        
        # 获取基础目录URL
        base_dir = os.path.dirname(self.current_path)

        # 构建带基础路径的HTML
        styled_html = f"""
        <html><head>
        <base href="file://{base_dir}/">
        <style>
            body {{
                background-color: {self.bg_color.name()};
                font-family: 'Comic Sans MS', cursive;
                line-height: 1.6;
                padding: 20px;
            }}
            img {{ max-width: 90%; height: auto; }}
        </style>
        </head>
        <body>{html}</body></html>
        """
        
        # 设置基础URL并渲染
        base_url = QUrl.fromLocalFile(base_dir + '/')
        self.web_view.setHtml(styled_html, base_url)

class CourseDetailWindow(QWidget):
    def __init__(self, filepath, bg_color=None, parent=None):
        super().__init__()
        self.filepath = filepath
        
        self.parent = parent  # 存储父窗口引用
        
        # 设置默认背景色
        self.bg_color = bg_color or QColor(240, 248, 255)  # 浅蓝色背景
        self.course_data = self._load_course_data()
        self.init_ui()

    def _load_course_data(self):
        """从info.csv和dataset/info.json中加载课程数据"""
        # 1. 从info.csv中提取课程号
        course_id = self._extract_course_id_from_csv()
        if not course_id:
            raise ValueError("无法从info.csv中提取课程号")
        
        # 2. 从dataset/info.json中查找课程信息
        json_path = "./dataset/info.json"
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"找不到JSON文件: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            all_courses = json.load(f)
        
        if course_id not in all_courses:
            raise KeyError(f"课程号 {course_id} 不在info.json中")
        
        return all_courses[course_id]

    def _extract_course_id_from_csv(self):
        """从同目录下的info.csv中提取课程号"""
        csv_path = os.path.join(self.filepath, "info.csv")
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"找不到CSV文件: {csv_path}")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)  # 读取标题行
            if "课程号" not in header:
                raise ValueError("info.csv中没有'课程号'列")
            
            course_id_index = header.index("课程号")
            first_row = next(reader)  # 读取第一行数据
            return first_row[course_id_index]
        
    def init_ui(self):
        # 设置窗口背景色
        palette = self.palette()
        palette.setColor(QPalette.Window, self.bg_color)
        self.setPalette(palette)
        
        main_layout = QHBoxLayout(self)
        
        # 左侧信息面板 (30%宽度)
        info_widget = QWidget()
        info_layout = QVBoxLayout()
        info_widget.setStyleSheet(f"""
            background-color: white;
            border-radius: 10px;
            padding: 15px;
        """)
        
        # 添加课程标题
        title = self.course_data.get("课程名", "未知课程")
        self.setWindowTitle(title)
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #FF69B4;
                margin-bottom: 15px;
            }
        """)
        info_layout.addWidget(title_label)
        
        # 创建课程信息文本区域
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
                font-size: 20px;
                border: none;
            }
        """)
        
        # 需要显示的字段
        display_fields = [
            ("课程号", "课程号"),
            ("课程类别", "课程类别"),
            ("学分", "学分"),
            ("教师", "教师"),
            ("开课单位", "开课单位"),
            ("备注", "备注")
        ]
        
        # 构建信息文本
        info_lines = []
        for display_name, field_name in display_fields:
            value = self.course_data.get(field_name, "")
            if value is None:
                value = ""
            if value:  # 只显示有值的字段
                info_lines.append(f"<b>{display_name}:</b> {value}")
        
        info_text.setHtml("<br>".join(info_lines))
        info_layout.addWidget(info_text)
        
        # 添加时间信息标签
        time_label = QLabel("📅 课程时间安排")
        time_label.setStyleSheet("font-size: 28px; font-weight: bold; margin-top: 15px;")
        info_layout.addWidget(time_label)
        
        time_content = QTextEdit()
        time_content.setReadOnly(True)
        time_content.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
                font-size: 20px;
                border: none;
            }
        """)
        time_content.setFixedHeight(230)
        time_content.setHtml(self.parse_time_info())
        info_layout.addWidget(time_content)
        
        # 添加"加入课表"按钮
        btn_add = QPushButton("加入课表")
        btn_add.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: #77DD77;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #66CC66;
            }
        """)
        btn_add.clicked.connect(self.add_to_schedule)
        info_layout.addWidget(btn_add)
        
        info_widget.setLayout(info_layout)
        main_layout.addWidget(info_widget, 1)  # 左侧占1份宽度
        
        # 右侧AI摘要面板 (70%宽度)
        summary_widget = QWidget()
        summary_layout = QVBoxLayout()
        summary_widget.setStyleSheet("""
            background-color: rgba(255, 250, 250, 0.9);
            border-radius: 10px;
        """)
        
        # 添加标题
        summary_title = QLabel("📊 AI课程分析摘要")
        summary_title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #4169E1;
                padding: 10px;
                background-color: rgba(255, 250, 250, 0);
                border-radius: 8px;
            }
        """)
        summary_layout.addWidget(summary_title)
        
        # 添加Markdown浏览器，使用传入的背景色
        viewer_bg = QColor(255, 255, 255)
        # if viewer_bg.lightness() > 180:  # 如果背景色太亮，则使用浅粉色
        #     viewer_bg = QColor(255, 240, 245)
        
        self.viewer = MarkdownViewer(viewer_bg)  # 使用调整后的背景色
        
        # 使用传入的filepath加载AI摘要
        summary_path = os.path.join(self.filepath, "AI_summary.md")
        if os.path.exists(summary_path):
            self.viewer.load_markdown(summary_path)
        else:
            self.viewer.web_view.setHtml("<h2>❌ 未找到AI摘要文件</h2>")
        
        summary_layout.addWidget(self.viewer)
        summary_widget.setLayout(summary_layout)

        if os.path.exists(os.path.join(self.filepath, "wordcloud.png")):
            # 创建图片标题
            img_title = QLabel("📊 词云分析")
            img_title.setStyleSheet("""
                QLabel {
                    font-size: 28px;
                    font-weight: bold;
                    color: #4169E1;
                    margin-top: 15px;
                }
            """)
            summary_layout.addWidget(img_title)
            
            # 创建图片展示区域
            img_label = QLabel()
            pixmap = QPixmap(os.path.join(self.filepath, "wordcloud.png"))
            
            # 调整图片大小以适应窗口
            scaled_pixmap = pixmap.scaledToWidth(500, Qt.SmoothTransformation)
            img_label.setPixmap(scaled_pixmap)
            img_label.setAlignment(Qt.AlignCenter)  # 居中显示
            
            # 添加样式
            img_label.setStyleSheet("""
                QLabel {
                    background-color: white;
                    border-radius: 10px;
                    padding: 10px;
                    margin-bottom: 0px;
                }
            """)
            
            summary_layout.addWidget(img_label)
        main_layout.addWidget(summary_widget, 2)  # 右侧占2份宽度
    
    def parse_time_info(self):
        """解析课程时间信息"""
        time_data = self.course_data.get("上课时间及教室", [])
        if not time_data:
            return "暂无时间安排信息"
        
        day_map = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        formatted = []
        
        for item in time_data:
            if len(item) >= 4:
                week = item[0]
                day = day_map[item[1]] if 0 <= item[1] < 7 else f"未知({item[1]})"
                time_range = item[2]
                classroom = item[3]
                
                # 处理时间范围格式
                if "~" in time_range:
                    start, end = time_range.split("~")
                    time_desc = f"{start}-{end}节"
                else:
                    time_desc = f"{time_range}节"
                
                formatted.append(f"{week} {day} {time_desc} @{classroom}")
        
        return "<br>".join(formatted)
    
    def add_to_schedule(self):
        """将课程添加到课表"""
        time_data = self.course_data.get("上课时间及教室", [])
        if not time_data:
            QMessageBox.warning(self, "提示", "该课程没有有效的时间安排信息，无法添加到课表")
            return
        
        # 解析时间信息为课表需要的格式
        schedule_data = []
        day_map = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        
        for item in time_data:
            if len(item) >= 4:
                week_info = item[0]  # 如"2~2周"
                day_index = item[1]  # 0-6表示周一到周日
                time_range = item[2]  # 如"2~4"
                classroom = item[3]  # 教室
                
                # 解析节次范围
                if "~" in time_range:
                    start, end = map(int, time_range.split("~"))
                    sections = list(range(start, end+1))
                else:
                    sections = [int(time_range)]
                
                # 添加到课表数据
                schedule_data.append({
                    "day": day_index,
                    "sections": sections,
                    "weeks": week_info,
                    "classroom": classroom
                })
        
        # 调用父窗口方法添加课程
        if self.parent and hasattr(self.parent, "add_course_to_schedule"):
            self.parent.add_course_to_schedule(self.course_data.get("课程号",""))
        else:
            QMessageBox.warning(self, "错误", "无法连接到课表系统")

    def update_color(self, color):
        palette = self.palette()
        palette.setColor(QPalette.Window, color)
        self.setPalette(palette)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Comic Sans MS", 12))

    # 创建并显示窗口
    detail_window = CourseDetailWindow(".\dataset\专业课\信息科学技术学院\人工智能前沿")
    detail_window.show()
    
    sys.exit(app.exec_())