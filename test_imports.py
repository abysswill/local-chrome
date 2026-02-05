#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PyQt6导入
"""

print("测试PyQt6导入...")

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QMenuBar, QStatusBar, QLabel, QFrame, QSplitter, QDialog,
        QPushButton, QLineEdit, QCheckBox, QMessageBox, QToolBar,
        QSystemTrayIcon, QMenu
    )
    print("✓ QtWidgets导入成功")
except ImportError as e:
    print(f"✗ QtWidgets导入失败: {e}")

try:
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, QUrl
    print("✓ QtCore导入成功")
except ImportError as e:
    print(f"✗ QtCore导入失败: {e}")

try:
    from PyQt6.QtGui import QIcon, QAction, QKeySequence, QFont
    print("✓ QtGui导入成功")
except ImportError as e:
    print(f"✗ QtGui导入失败: {e}")

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    print("✓ QtWebEngineWidgets导入成功")
except ImportError as e:
    print(f"✗ QtWebEngineWidgets导入失败: {e}")

try:
    from PyQt6.QtWebEngineCore import QWebEnginePage
    print("✓ QtWebEngineCore导入成功")
except ImportError as e:
    print(f"✗ QtWebEngineCore导入失败: {e}")

# 测试QAction具体位置
print("\n测试QAction具体位置:")
try:
    from PyQt6.QtGui import QAction
    print("✓ QAction在QtGui中")
except ImportError:
    print("✗ QAction不在QtGui中")

try:
    from PyQt6.QtWidgets import QAction
    print("✓ QAction在QtWidgets中")
except ImportError:
    print("✗ QAction不在QtWidgets中")

# 测试QApplication创建
print("\n测试QApplication创建:")
try:
    app = QApplication([])
    print("✓ QApplication创建成功")
    app.quit()
except Exception as e:
    print(f"✗ QApplication创建失败: {e}")