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
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

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

        # 初始化管理器
        self.settings_manager = SettingsManager()
        self.theme_manager = ThemeManager()

        # 设置应用属性（统一来源：settings.app）
        self.app_name = self.settings_manager.get('app.name', '桌面管理程序')
        app_icon_setting = self.settings_manager.get('app.icon_path', 'resources/icon.png')

        self.setApplicationName(self.app_name)
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName(self.app_name)

        icon_path = self._resolve_icon_path(app_icon_setting)
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # 单实例控制
        self.local_server = None
        self.server_name = self._build_server_name(self.app_name)
        self.should_exit = not self._init_single_instance()
        if self.should_exit:
            return

        # 初始化样式
        self.init_style()

        # 主对话框引用，避免被回收
        self.login_dialog = None

        # 创建主窗口
        self.create_main_window()

    def _resolve_icon_path(self, icon_setting: str) -> str:
        """解析图标路径（优先用户settings目录，其次打包资源/项目目录）"""
        if not icon_setting:
            return ""

        icon_path = Path(icon_setting)
        if icon_path.is_absolute() and icon_path.exists():
            return str(icon_path)

        candidates = []

        # 1) 相对settings.json目录（例如 AppData/.../config/logo.png）
        settings_dir = self.settings_manager.settings_file.parent
        candidates.append(settings_dir / icon_path)

        # 2) 打包资源目录
        if getattr(sys, 'frozen', False):
            candidates.append(Path(getattr(sys, '_MEIPASS', '')) / icon_path)

        # 3) 开发目录
        candidates.append((Path(__file__).parent / icon_path).resolve())

        for candidate in candidates:
            if candidate.exists():
                return str(candidate)

        return ""

    def _build_server_name(self, app_name: str) -> str:
        safe_name = ''.join(ch if ch.isalnum() else '_' for ch in app_name)
        return f"single_instance_{safe_name or 'desktop_manager'}"

    def _init_single_instance(self) -> bool:
        """初始化单实例：已有实例则通知激活并退出当前进程"""
        socket = QLocalSocket(self)
        socket.connectToServer(self.server_name)
        if socket.waitForConnected(300):
            socket.write(b"ACTIVATE")
            socket.flush()
            socket.waitForBytesWritten(300)
            socket.disconnectFromServer()
            return False

        # 清理陈旧socket文件并启动监听
        QLocalServer.removeServer(self.server_name)
        self.local_server = QLocalServer(self)
        self.local_server.newConnection.connect(self._handle_activation_request)
        if not self.local_server.listen(self.server_name):
            logger.warning("单实例监听启动失败，继续运行当前实例")
        return True

    def _handle_activation_request(self):
        while self.local_server and self.local_server.hasPendingConnections():
            client = self.local_server.nextPendingConnection()
            if client:
                client.waitForReadyRead(100)
                _ = client.readAll()
                client.disconnectFromServer()
            self._activate_main_window()

    def _activate_main_window(self):
        """激活已打开窗口"""
        if not self.login_dialog:
            return

        if self.login_dialog.isMinimized():
            self.login_dialog.showNormal()
        self.login_dialog.raise_()
        self.login_dialog.activateWindow()

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

    if getattr(app, 'should_exit', False):
        sys.exit(0)

    try:
        # 运行应用
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"应用程序运行错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
