#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版桌面管理程序主入口
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """测试基础导入"""
    print("测试基础导入...")

    try:
        from PyQt6.QtWidgets import QApplication
        print("✓ QApplication导入成功")
        return True
    except ImportError as e:
        print(f"✗ QApplication导入失败: {e}")
        return False

def test_advanced_imports():
    """测试高级导入"""
    print("\n测试高级导入...")

    try:
        from PyQt6.QtWidgets import (
            QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QMenuBar, QStatusBar, QLabel, QFrame, QDialog,
            QPushButton, QLineEdit, QCheckBox, QMessageBox,
            QToolBar, QSystemTrayIcon, QMenu
        )
        print("✓ 所有QtWidgets组件导入成功")
    except ImportError as e:
        print(f"✗ QtWidgets组件导入失败: {e}")
        return False

    try:
        from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, QUrl
        print("✓ QtCore组件导入成功")
    except ImportError as e:
        print(f"✗ QtCore组件导入失败: {e}")
        return False

    try:
        from PyQt6.QtGui import QIcon, QAction, QKeySequence, QFont
        print("✓ QtGui组件导入成功")
    except ImportError as e:
        print(f"✗ QtGui组件导入失败: {e}")
        return False

    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        print("✓ WebEngine组件导入成功")
    except ImportError as e:
        print(f"✗ WebEngine组件导入失败: {e}")
        return False

    return True

def create_simple_app():
    """创建简单的应用"""
    try:
        from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton
        from PyQt6.QtCore import Qt

        app = QApplication(sys.argv)

        # 创建简单窗口
        window = QWidget()
        window.setWindowTitle("桌面管理程序")
        window.resize(400, 300)

        layout = QVBoxLayout()

        label = QLabel("桌面管理程序启动成功！")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        button = QPushButton("启动主程序")
        button.clicked.connect(lambda: launch_main_app(app))
        layout.addWidget(button)

        window.setLayout(layout)
        window.show()

        return app.exec()

    except Exception as e:
        print(f"创建简单应用失败: {e}")
        return 1

def launch_main_app(current_app):
    """启动主应用"""
    current_app.quit()

    # 尝试启动完整主程序
    try:
        from main import main as app_main
        app_main()
    except Exception as e:
        print(f"启动主程序失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("=== 桌面管理程序简化版启动器 ===")

    # 确保在正确的目录
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)

    # 测试基础导入
    if not test_basic_imports():
        input("基础导入失败，按回车键退出...")
        return 1

    # 测试高级导入
    if not test_advanced_imports():
        print("高级导入失败，启动简化版本...")
        return create_simple_app()

    # 尝试启动完整主程序
    try:
        print("\n尝试启动完整主程序...")
        from main import main as app_main
        app_main()
    except Exception as e:
        print(f"完整主程序启动失败: {e}")
        print("启动简化版本...")
        return create_simple_app()

    return 0

if __name__ == "__main__":
    exit_code = main()
    if exit_code != 0:
        input("按回车键退出...")
    sys.exit(exit_code)