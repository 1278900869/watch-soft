#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
USB监控后端 - 主程序入口（带系统托盘）
作者：董明照
"""

import sys
import threading
import webbrowser
import logging
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PySide6.QtGui import QAction
import uvicorn
from config import config
from api import app as fastapi_app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrayApp:
    """系统托盘应用"""
    
    def __init__(self, qt_app):
        self.qt_app = qt_app
        self.host = str(config.get('host', 'localhost'))
        port_value = config.get('port', 8888)
        self.port = int(port_value) if port_value is not None else 8888
        
        # 创建托盘图标
        self.tray = QSystemTrayIcon()
        icon = qt_app.style().standardIcon(QApplication.style().StandardPixmap.SP_ComputerIcon)
        self.tray.setIcon(icon)
        self.tray.setToolTip("USB监控后端")
        
        # 创建菜单
        menu = QMenu()
        
        status_action = QAction("🟢 服务运行中", menu)
        status_action.setEnabled(False)
        menu.addAction(status_action)
        
        menu.addSeparator()
        
        api_action = QAction("📖 打开API文档", menu)
        api_action.triggered.connect(self.open_api_docs)
        menu.addAction(api_action)
        
        logs_action = QAction("📂 打开日志目录", menu)
        logs_action.triggered.connect(self.open_logs)
        menu.addAction(logs_action)
        
        menu.addSeparator()
        
        about_action = QAction("ℹ️ 关于", menu)
        about_action.triggered.connect(self.show_about)
        menu.addAction(about_action)
        
        quit_action = QAction("❌ 退出", menu)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)
        
        self.tray.setContextMenu(menu)
        self.tray.show()
        
        # 显示启动消息
        self.tray.showMessage(
            "USB监控后端",
            f"服务已启动\n地址: http://{self.host}:{self.port}",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )
    
    def open_api_docs(self):
        """打开API文档"""
        webbrowser.open(f"http://{self.host}:{self.port}/docs")
    
    def open_logs(self):
        """打开日志目录"""
        import os
        from pathlib import Path
        logs_dir = Path(__file__).parent / 'logs'
        logs_dir.mkdir(exist_ok=True)
        os.startfile(str(logs_dir))
    
    def show_about(self):
        """显示关于信息"""
        QMessageBox.information(
            None,
            "关于 USB监控后端",
            f"USB监控后端服务\n\n"
            f"服务地址: http://{self.host}:{self.port}\n"
            f"API文档: http://{self.host}:{self.port}/docs\n\n"
            f"作者: 董明照"
        )
    
    def quit_app(self):
        """退出应用"""
        reply = QMessageBox.question(
            None,
            "确认退出",
            "确定要退出USB监控后端吗？\n服务将停止运行。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.tray.hide()
            self.qt_app.quit()


def run_server(host, port):
    """运行FastAPI服务器"""
    logger.info("="*50)
    logger.info("USB监控后端启动")
    logger.info(f"服务地址: http://{host}:{port}")
    logger.info(f"API文档: http://{host}:{port}/docs")
    logger.info("="*50)
    
    # 设置登录回调 (延迟导入避免循环依赖)
    from server import usb_service  # type: ignore
    usb_service.set_login_callback(show_login_dialog)
    
    uvicorn.run(
        fastapi_app,
        host=host,
        port=port,
        log_level="info"
    )


def show_login_dialog(drive_letter: str) -> tuple:
    """显示登录对话框"""
    from login_dialog import LoginDialog
    from PySide6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        return ("未知用户", 0)
    
    # 创建并显示登录窗口
    dialog = LoginDialog(drive_letter)
    result = dialog.exec()
    
    if result == dialog.DialogCode.Accepted:
        return (dialog.username, dialog.login_id)
    else:
        return (None, None)


def main():
    """主函数"""
    # 读取配置
    host = str(config.get('host', 'localhost'))
    port_value = config.get('port', 8888)
    port = int(port_value) if port_value is not None else 8888
    
    # 创建Qt应用
    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName("USB监控后端")
    qt_app.setQuitOnLastWindowClosed(False)
    
    # 启动FastAPI服务器（后台线程）
    server_thread = threading.Thread(
        target=run_server,
        args=(host, port),
        daemon=True
    )
    server_thread.start()
    
    # 创建托盘应用
    tray_app = TrayApp(qt_app)
    
    # 运行Qt事件循环
    sys.exit(qt_app.exec())


if __name__ == '__main__':
    main()
