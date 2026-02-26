#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌面管理程序主入口
Windows桌面应用程序，用于Web管理系统的功能导航
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.settings_manager import SettingsManager
from components.theme_manager import ThemeManager
from components.login_dialog import LoginDialog
from utils.logger import setup_logger

# 设置日志
logger = setup_logger(__name__)

class DesktopApp(QApplication):
    """桌面应用程序主类"""

    def __init__(self, argv):
        super().__init__(argv)

        # 设置应用属性
        self.setApplicationName("桌面管理程序")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("Desktop Manager")

        # 设置应用图标 - 处理打包后的路径问题
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe程序
            icon_path = os.path.join(sys._MEIPASS, "resources", "icon.png")
        else:
            # 如果是开发环境
            icon_path = "resources/icon.png"

        # 如果图标文件不存在，则跳过设置图标
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # 初始化管理器
        self.settings_manager = SettingsManager()
        self.theme_manager = ThemeManager()

        # 初始化样式
        self.init_style()

        # 主对话框引用，避免被回收
        self.login_dialog = None

        # 创建主窗口
        self.create_main_window()

    def init_style(self):
        """初始化应用样式"""
        # 应用主题设置
        self.theme_manager.apply_theme(self.settings_manager.get('theme_mode', 'light'))

        # 应用主题样式（如果需要全局样式，可以在这里设置）

    def create_main_window(self):
        """创建并显示登录窗口"""
        # 显示登录对话框（登录成功后会在同一窗口中加载主页面）
        self.show_login_dialog()

    def show_login_dialog(self):
        """显示登录对话框"""
        self.login_dialog = LoginDialog(self.settings_manager)
        # 对话框关闭后退出应用，避免后台残留进程
        self.login_dialog.finished.connect(self.quit)
        self.login_dialog.show()

def main():
    """主函数"""
    # 创建QApplication实例
    app = DesktopApp(sys.argv)

    try:
        # 运行应用
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"应用程序运行错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
