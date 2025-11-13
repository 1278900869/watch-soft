#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强制登录窗口 - USB插入时必须登录
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                QLineEdit, QPushButton, QMessageBox)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint
from datetime import datetime


class LoginDialog(QDialog):
    """强制登录对话框"""
    
    def __init__(self, drive_letter: str, parent=None):
        super().__init__(parent)
        
        self.drive_letter = drive_letter
        self.username = None
        self.login_id = None
        
        # 窗口设置
        self.setWindowTitle("USB监控 - 用户登录")
        self.setFixedSize(400, 250)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowStaysOnTopHint |  # 始终置顶
            Qt.WindowType.CustomizeWindowHint |   # 自定义窗口
            Qt.WindowType.WindowTitleHint          # 只保留标题栏
        )
        self.setModal(True)  # 模态对话框
        
        # 抖动动画
        self.shake_animation = QPropertyAnimation(self, b"pos")
        self.shake_animation.setDuration(100)
        
        # 初始化UI
        self.init_ui()
        
        # 失去焦点时抖动
        self.installEventFilter(self)
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 标题
        title = QLabel(f"🔒 检测到USB设备插入")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2196F3; padding: 10px;")
        layout.addWidget(title)
        
        # 提示信息
        info = QLabel(f"驱动器: {self.drive_letter}:\n\n请输入您的姓名以继续使用")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("""
            QLabel {
                background-color: #fff3cd;
                color: #856404;
                padding: 15px;
                border-radius: 5px;
                border: 1px solid #ffc107;
            }
        """)
        layout.addWidget(info)
        
        # 输入框
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入姓名...")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                font-size: 14px;
                border: 2px solid #ccc;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """)
        self.username_input.returnPressed.connect(self.on_login)
        layout.addWidget(self.username_input)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        self.login_btn = QPushButton("✅ 登录")
        self.login_btn.clicked.connect(self.on_login)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        btn_layout.addStretch()
        btn_layout.addWidget(self.login_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # 聚焦输入框
        self.username_input.setFocus()
    
    def on_login(self):
        """处理登录"""
        username = self.username_input.text().strip()
        
        if not username:
            QMessageBox.warning(
                self,
                "提示",
                "请输入您的姓名！"
            )
            self.shake()
            return
        
        if len(username) < 2:
            QMessageBox.warning(
                self,
                "提示",
                "姓名至少需要2个字符！"
            )
            self.shake()
            return
        
        # 保存登录信息
        self.username = username
        
        # 记录登录到数据库
        from database import db
        self.login_id = db.insert_login(username, self.drive_letter)
        
        # 关闭对话框
        self.accept()
    
    def shake(self):
        """窗口抖动效果"""
        if self.shake_animation.state() == QPropertyAnimation.State.Running:
            return
        
        original_pos = self.pos()
        
        # 抖动序列
        self.shake_animation.setStartValue(original_pos)
        self.shake_animation.setKeyValueAt(0.1, original_pos + QPoint(-10, 0))
        self.shake_animation.setKeyValueAt(0.3, original_pos + QPoint(10, 0))
        self.shake_animation.setKeyValueAt(0.5, original_pos + QPoint(-10, 0))
        self.shake_animation.setKeyValueAt(0.7, original_pos + QPoint(10, 0))
        self.shake_animation.setKeyValueAt(0.9, original_pos + QPoint(-5, 0))
        self.shake_animation.setEndValue(original_pos)
        
        self.shake_animation.start()
    
    def closeEvent(self, event):
        """拦截关闭事件"""
        # 只有登录成功后才能关闭
        if self.username is None:
            event.ignore()
            self.shake()
            QMessageBox.warning(
                self,
                "无法关闭",
                "必须完成登录才能继续使用USB设备！"
            )
    
    def changeEvent(self, event):
        """窗口状态变化"""
        super().changeEvent(event)
        # 防止最小化
        if event.type() == event.Type.WindowStateChange:
            if self.windowState() & Qt.WindowState.WindowMinimized:
                self.setWindowState(Qt.WindowState.WindowNoState)
                self.shake()
    
    def eventFilter(self, obj, event):
        """事件过滤器"""
        # 窗口失去焦点时抖动并强制回到前台
        if obj == self and event.type() == event.Type.WindowDeactivate:
            if self.username is None:  # 未登录时
                QTimer.singleShot(100, self.bring_to_front)
        return super().eventFilter(obj, event)
    
    def bring_to_front(self):
        """强制窗口回到前台"""
        self.raise_()
        self.activateWindow()
        self.shake()
