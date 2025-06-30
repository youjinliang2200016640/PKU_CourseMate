import sys
import os
import json
import markdown
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                            QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
                            QToolBar, QSizePolicy, QFileDialog, QHeaderView, QMessageBox,
                            QLineEdit, QListWidget, QLabel, QListWidgetItem, QTextEdit,
                            QSplitter, QScrollArea)
from PyQt5.QtCore import Qt, QDir, QTimer, QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QPalette, QColor, QFont, QTextCursor
from PyQt5.QtWebEngineWidgets import QWebEngineView
import requests
from openai import OpenAI

class ChatAssistantWindow(QWidget):
    def __init__(self, bg_color):
        super().__init__()
        self.bg_color = bg_color
        self.dialog_history = []  # 存储完整的对话历史
        self.init_ui()
        self.setWindowTitle("🎓 智能选课助手")
        self.setGeometry(400, 300, 800, 600)
        self.setMinimumSize(600, 400)

        self.send_course_info()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建分割器，使聊天区域可以调整大小
        splitter = QSplitter(Qt.Vertical)
        
        # 聊天记录显示区域（可滚动）
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 180);
                border-radius: 10px;
                padding: 15px;
                font-size: 20px;
                border: none;
            }
        """)
        scroll_area.setWidget(self.chat_history)
        splitter.addWidget(scroll_area)
        
        # 输入区域
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 10, 0, 0)
        
        # 用户输入区域
        input_row = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("输入你的选课问题...")
        self.user_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border-radius: 15px;
                border: 2px solid #87CEFA;
                font-size: 20px;
            }
        """)
        self.user_input.returnPressed.connect(self.send_message)  # 支持回车发送
        
        self.send_btn = QPushButton("发送")
        self.send_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                border-radius: 15px;
                background-color: #87CEFA;
                color: white;
                font-weight: bold;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #6495ED;
            }
            QPushButton:disabled {
                background-color: #B0C4DE;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        
        input_row.addWidget(self.user_input, 5)
        input_row.addWidget(self.send_btn, 1)
        
        input_layout.addLayout(input_row)
        # input_layout.addLayout(button_row)
        splitter.addWidget(input_container)
        
        # 设置分割器大小比例
        splitter.setSizes([500, 100])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        self.update_color(self.bg_color)
        
        # 添加初始欢迎消息
        # self.append_message("🤖 DeepSeek", "你好！我是选课助手，我可以帮助你分析课程、制定学习计划。请问有什么可以帮您的？\n")

    def load_course_info(self):
        """加载课程信息"""
        try:
            with open('./dataset/info.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法加载课程信息: {str(e)}")
            return {}
    
    def send_course_info(self):
        """将课程信息发送给大模型"""
        
        self.course_info = self.load_course_info()
            
        # 构建课程信息摘要
        course_summary = "以下是可选的课程信息：\n"
        for course_id, details in self.course_info.items():
            course_summary += f"- {details['课程名']} ({course_id}): {details['学分']}学分, 教师: {details['教师']}\n"
        
        # 添加到对话历史并显示
        self.append_message("📚 系统", "已加载课程信息")
        self.dialog_history.append({"role": "system", "content": course_summary})
        
        # 添加提示消息
        self.append_message("🤖 DeepSeek", "你好！我是选课助手，我已了解所有课程信息，我可以帮助你分析课程、制定学习计划。请问有什么可以帮您的？")

    def update_color(self, color):
        palette = self.palette()
        palette.setColor(QPalette.Window, color)
        self.setPalette(palette)

    def send_message(self):
        user_text = self.user_input.text().strip()
        if not user_text:
            return
        
        # 禁用发送按钮防止重复发送
        self.send_btn.setEnabled(False)
        self.user_input.clear()
        
        # 添加用户消息到对话历史
        self.append_message("👤 我", user_text)
        self.dialog_history.append({"role": "user", "content": user_text})
        
        # 启动API调用线程
        self.worker = APIWorker(self.dialog_history)
        self.worker.finished.connect(self.handle_response)
        self.worker.error.connect(self.handle_error)
        self.worker.start()

    def append_message(self, role, content):
        # 添加带样式的消息
        self.chat_history.moveCursor(QTextCursor.End)
        self.chat_history.insertHtml(f"<div style='margin-bottom: 15px;'><b>{role}:</b> {content}</div><br>")
        self.chat_history.ensureCursorVisible()

    def handle_response(self, response):
        # 重新启用发送按钮
        self.send_btn.setEnabled(True)
        
        # 添加AI回复到对话历史
        self.append_message("🤖 DeepSeek", response)
        self.dialog_history.append({"role": "assistant", "content": response})

    def handle_error(self, error):
        # 重新启用发送按钮
        self.send_btn.setEnabled(True)
        
        error_msg = f"请求失败：{error}"
        self.append_message("⚠️ 系统", error_msg)
        QMessageBox.warning(self, "请求错误", error_msg)

# API调用线程
class APIWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, dialog_history):
        super().__init__()
        self.dialog_history = dialog_history
        self.api_key = "sk-2fb58629e2f24b0787f42de347071f88"  # 替换为你的API密钥
        self.api_url = "https://api.deepseek.com"  # 替换为实际API地址

    def run(self):
        try:
            client = OpenAI(api_key=self.api_key, base_url=self.api_url)

            # 创建完整的对话上下文（包括系统消息）
            messages = [
                {"role": "system", "content": "你是一个专业的选课顾问，请帮助用户分析课程、制定学习计划。回答要专业、详细。"}
            ] + self.dialog_history
            
            # 发送请求
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=False  # 使用非流式响应简化处理
            )
            
            # 获取完整回复
            answer = response.choices[0].message.content
            self.finished.emit(answer.strip())
            
        except Exception as e:
            self.error.emit(str(e))

# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatAssistantWindow(QColor(240, 248, 255))  # 淡蓝色背景
    window.show()
    sys.exit(app.exec_())