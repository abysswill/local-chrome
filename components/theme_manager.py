#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主题管理器
负责应用程序主题的管理和切换
"""

import sys
import os
import json
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

class ThemeManager(QObject):
    """主题管理器类"""

    theme_changed = pyqtSignal(str)  # 主题变更信号

    def __init__(self):
        """初始化主题管理器"""
        super().__init__()
        self._current_theme = "light"
        self._theme_cache = {}
        self._load_themes()

    def _load_themes(self):
        """加载主题文件"""
        # 获取程序运行时的正确路径
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe程序
            base_path = Path(sys._MEIPASS)
        else:
            # 如果是开发环境
            base_path = Path(__file__).parent.parent

        theme_dir = base_path / "resources" / "themes"

        # 尝试创建主题目录，如果失败则跳过（可能是只读环境）
        try:
            theme_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass  # 在只读环境中静默失败

        # 预定义主题
        self._theme_cache = {
            "light": self._get_light_theme(),
            "dark": self._get_dark_theme()
        }

        # 加载自定义主题文件（只有当目录存在且可访问时）
        try:
            for theme_file in theme_dir.glob("*.json"):
                theme_name = theme_file.stem
                try:
                    with open(theme_file, 'r', encoding='utf-8') as f:
                        self._theme_cache[theme_name] = json.load(f)
                except Exception as e:
                    print(f"加载主题文件 {theme_file} 失败: {e}")
        except Exception:
            pass  # 如果无法访问目录，则跳过自定义主题加载

    def _get_light_theme(self) -> dict:
        """获取明亮主题样式"""
        return {
            "name": "明亮主题",
            "colors": {
                "background": "#F8FAFC",
                "surface": "#FFFFFF",
                "primary": "#2563EB",
                "primary_hover": "#1D4ED8",
                "secondary": "#64748B",
                "success": "#16A34A",
                "warning": "#F97316",
                "error": "#DC2626",
                "border": "#E2E8F0",
                "text_primary": "#1E293B",
                "text_secondary": "#64748B",
                "shadow": "rgba(0, 0, 0, 0.1)"
            },
            "css": """
                QMainWindow {
                    background-color: #F8FAFC;
                }

                QWidget {
                    background-color: #FFFFFF;
                    color: #1E293B;
                }

                QPushButton {
                    background-color: #2563EB;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                }

                QPushButton:hover {
                    background-color: #1D4ED8;
                }

                QPushButton:pressed {
                    background-color: #1E40AF;
                }

                QLineEdit, QTextEdit {
                    border: 1px solid #E2E8F0;
                    border-radius: 6px;
                    padding: 8px 12px;
                    background-color: white;
                    color: #1E293B;
                }

                QLineEdit:focus, QTextEdit:focus {
                    border-color: #2563EB;
                    outline: none;
                }

                QMenuBar {
                    background-color: white;
                    border-bottom: 1px solid #E2E8F0;
                }

                QStatusBar {
                    background-color: white;
                    border-top: 1px solid #E2E8F0;
                    color: #64748B;
                }
            """
        }

    def _get_dark_theme(self) -> dict:
        """获取暗黑主题样式"""
        return {
            "name": "暗黑主题",
            "colors": {
                "background": "#0F172A",
                "surface": "#1E293B",
                "primary": "#3B82F6",
                "primary_hover": "#2563EB",
                "secondary": "#94A3B8",
                "success": "#22C55E",
                "warning": "#F97316",
                "error": "#EF4444",
                "border": "#334155",
                "text_primary": "#F1F5F9",
                "text_secondary": "#94A3B8",
                "shadow": "rgba(0, 0, 0, 0.3)"
            },
            "css": """
                QMainWindow {
                    background-color: #0F172A;
                }

                QWidget {
                    background-color: #1E293B;
                    color: #F1F5F9;
                }

                QPushButton {
                    background-color: #3B82F6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                }

                QPushButton:hover {
                    background-color: #2563EB;
                }

                QPushButton:pressed {
                    background-color: #1D4ED8;
                }

                QLineEdit, QTextEdit {
                    border: 1px solid #334155;
                    border-radius: 6px;
                    padding: 8px 12px;
                    background-color: #1E293B;
                    color: #F1F5F9;
                }

                QLineEdit:focus, QTextEdit:focus {
                    border-color: #3B82F6;
                    outline: none;
                }

                QMenuBar {
                    background-color: #1E293B;
                    border-bottom: 1px solid #334155;
                }

                QStatusBar {
                    background-color: #1E293B;
                    border-top: 1px solid #334155;
                    color: #94A3B8;
                }
            """
        }

    def get_available_themes(self) -> list:
        """获取可用主题列表

        Returns:
            主题名称列表
        """
        return list(self._theme_cache.keys())

    def get_theme_info(self, theme_name: str) -> dict:
        """获取主题信息

        Args:
            theme_name: 主题名称

        Returns:
            主题信息字典
        """
        return self._theme_cache.get(theme_name, self._get_light_theme())

    def apply_theme(self, theme_name: str) -> bool:
        """应用主题

        Args:
            theme_name: 主题名称

        Returns:
            是否应用成功
        """
        if theme_name not in self._theme_cache:
            return False

        theme = self._theme_cache[theme_name]
        app = QApplication.instance()

        if app and "css" in theme:
            app.setStyleSheet(theme["css"])

        self._current_theme = theme_name
        self.theme_changed.emit(theme_name)

        return True

    def get_current_theme(self) -> str:
        """获取当前主题

        Returns:
            当前主题名称
        """
        return self._current_theme

    def toggle_theme(self) -> str:
        """切换主题

        Returns:
            切换后的主题名称
        """
        if self._current_theme == "light":
            new_theme = "dark"
        else:
            new_theme = "light"

        self.apply_theme(new_theme)
        return new_theme

    def get_color(self, color_name: str) -> str:
        """获取当前主题的颜色值

        Args:
            color_name: 颜色名称

        Returns:
            颜色值
        """
        theme = self._theme_cache.get(self._current_theme, {})
        colors = theme.get("colors", {})
        return colors.get(color_name, "#000000")

    def inject_theme_to_webview(self, webview) -> None:
        """向WebView注入主题样式

        Args:
            webview: WebView实例
        """
        theme = self._theme_cache.get(self._current_theme, {})
        colors = theme.get("colors", {})

        # 生成CSS变量
        css_vars = []
        for key, value in colors.items():
            css_var_name = f"--{key.replace('_', '-')}"
            css_vars.append(f"{css_var_name}: {value};")

        css_variables = "\n  ".join(css_vars)

        # JavaScript代码注入主题
        js_code = f"""
        (function() {{
            // 创建或更新主题样式
            let themeStyle = document.getElementById('theme-override');
            if (!themeStyle) {{
                themeStyle = document.createElement('style');
                themeStyle.id = 'theme-override';
                document.head.appendChild(themeStyle);
            }}

            // 设置CSS变量
            themeStyle.textContent = `
                :root {{
                    {css_variables}
                }}

                body {{
                    background-color: var(--background);
                    color: var(--text-primary);
                }}

                .card, .navbar, .sidebar, .settings-group {{
                    background-color: var(--surface);
                    border-color: var(--border);
                }}

                .primary-button, .login-button {{
                    background-color: var(--primary);
                    color: white;
                }}

                .primary-button:hover, .login-button:hover {{
                    background-color: var(--primary-hover);
                }}
            `;
        }})();
        """

        # 注入JavaScript
        if webview.page():
            webview.page().runJavaScript(js_code)