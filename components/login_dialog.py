#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录对话框
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QFrame, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QUrl
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from urllib.parse import urlparse, parse_qs
import webbrowser


class ExternalLinkPage(QWebEnginePage):
    """用于处理新窗口/新标签的页面，将链接交给系统浏览器"""

    def __init__(self, parent_dialog):
        super().__init__()
        self.parent_dialog = parent_dialog

    def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
        url_str = url.toString()
        if url_str:
            if self.parent_dialog:
                self.parent_dialog.open_external_url(url_str)
            else:
                webbrowser.open(url_str)
        return False


class LoginPage(QWebEnginePage):
    """自定义WebEngine页面，用于拦截登录请求"""
    
    def __init__(self, parent_dialog):
        super().__init__()
        self.parent_dialog = parent_dialog

    def createWindow(self, window_type):
        """处理页面内新窗口/新标签打开请求"""
        if self.parent_dialog:
            return self.parent_dialog.register_external_link_page()
        return ExternalLinkPage(None)
    
    def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
        """拦截导航请求"""
        url_str = url.toString()
        
        # 拦截登录请求
        if url_str.startswith('python://login'):
            # 解析URL参数
            parsed = urlparse(url_str)
            params = parse_qs(parsed.query)
            
            username = params.get('username', [''])[0]
            password = params.get('password', [''])[0]
            
            if username and password:
                # 使用QTimer延迟执行，避免在导航请求处理中直接调用
                QTimer.singleShot(10, lambda: self.parent_dialog.handle_login_request(username, password))
            
            # 阻止导航
            return False
        
        # 拦截外部URL打开请求（在系统浏览器中打开）
        if url_str.startswith('python://openurl'):
            # 解析URL参数
            parsed = urlparse(url_str)
            params = parse_qs(parsed.query)
            
            target_url = params.get('url', [''])[0]
            
            if target_url:
                # 使用QTimer延迟执行，避免在导航请求处理中直接调用
                QTimer.singleShot(10, lambda: self.parent_dialog.open_external_url(target_url))
            
            # 阻止导航
            return False
        
        # 拦截本地HTML文件导航（如 03-设置.html）
        # 检查是否是相对路径的HTML文件（如 "03-设置.html"）
        if url_str.endswith('.html') and not url_str.startswith('http') and not url_str.startswith('file://'):
            # 尝试从项目根目录查找HTML文件
            base_path = Path(__file__).parent.parent
            html_file = base_path / url_str
            
            if html_file.exists() and html_file.suffix == '.html':
                # 使用QTimer延迟加载，确保当前操作完成
                QTimer.singleShot(10, lambda: self.parent_dialog.load_html_file(html_file))
                return False
        
        # 允许其他导航（包括外部URL和已存在的文件URL）
        return super().acceptNavigationRequest(url, navigation_type, is_main_frame)


class LoginDialog(QDialog):
    """登录对话框类"""

    def __init__(self, settings_manager):
        """初始化登录对话框

        Args:
            settings_manager: 设置管理器实例
        """
        super().__init__()
        self.settings_manager = settings_manager
        self.webview = None
        self._external_link_pages = []

        self.setup_ui()
        self.load_saved_credentials()

    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("登录 - 桌面管理程序")
        
        # 设置窗口标志，确保有最小化、最大化、关闭按钮
        # 对于对话框，我们需要保持Dialog类型但添加按钮提示
        flags = self.windowFlags()
        flags |= Qt.WindowType.WindowCloseButtonHint
        flags |= Qt.WindowType.WindowMinimizeButtonHint
        flags |= Qt.WindowType.WindowMaximizeButtonHint
        self.setWindowFlags(flags)
        
        # 设置窗口大小（可调整大小，默认1920x1080）
        self.resize(1920, 1080)
        self.setMinimumSize(800, 600)  # 设置最小尺寸
        self.setModal(True)
        self.setWindowState(self.windowState() | Qt.WindowState.WindowMaximized)

        # 居中显示
        self.center_dialog()

        # 创建布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 创建WebView来显示HTML登录页面
        self.webview = QWebEngineView()
        
        # 设置自定义页面来拦截URL
        self.login_page = LoginPage(self)
        self.webview.setPage(self.login_page)

        # 设置启动页面路径（可配置）
        startup_page_url = self.settings_manager.get('startup_page_url', '').strip()
        html_path = Path(__file__).parent.parent / "01-登录.html"

        if startup_page_url:
            if startup_page_url.startswith(("http://", "https://")):
                self.webview.load(QUrl(startup_page_url))
            else:
                startup_path = Path(startup_page_url)
                if not startup_path.is_absolute():
                    startup_path = Path(__file__).parent.parent / startup_page_url
                if startup_path.exists():
                    self.webview.load(QUrl.fromLocalFile(str(startup_path.resolve())))
                elif html_path.exists():
                    self.webview.load(QUrl.fromLocalFile(str(html_path.resolve())))
                else:
                    # 如果HTML文件不存在，使用原生Qt界面
                    self.create_native_login_ui(main_layout)
                    return
        elif html_path.exists():
            self.webview.load(QUrl.fromLocalFile(str(html_path.resolve())))
        else:
            # 如果HTML文件不存在，使用原生Qt界面
            self.create_native_login_ui(main_layout)
            return

        # 连接信号
        self.webview.page().loadFinished.connect(self.on_page_loaded)

        main_layout.addWidget(self.webview)
        self.setLayout(main_layout)

    def register_external_link_page(self):
        """注册用于处理新窗口/新标签链接的页面，避免被垃圾回收"""
        page = ExternalLinkPage(self)
        self._external_link_pages.append(page)
        page.destroyed.connect(lambda: self._cleanup_external_link_page(page))
        return page

    def _cleanup_external_link_page(self, page):
        if page in self._external_link_pages:
            self._external_link_pages.remove(page)

    def create_native_login_ui(self, main_layout):
        """创建原生Qt登录界面（备用方案）

        Args:
            main_layout: 主布局
        """
        # Logo区域
        logo_layout = QVBoxLayout()
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo图标
        logo_label = QLabel("DM")
        logo_label.setFixedSize(64, 64)
        logo_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                         stop: 0 #2563EB, stop: 1 #60A5FA);
                color: white;
                font-size: 24px;
                font-weight: bold;
                border-radius: 16px;
            }
        """)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(logo_label)

        # 标题
        title_label = QLabel("桌面管理程序")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(title_label)

        # 副标题
        subtitle_label = QLabel("欢迎回来，请登录您的账户")
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setStyleSheet("color: #64748B;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(subtitle_label)

        main_layout.addLayout(logo_layout)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #E2E8F0;")
        main_layout.addWidget(line)

        # 表单区域
        form_layout = QVBoxLayout()
        form_layout.setSpacing(16)

        # 用户名输入框
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setMinimumHeight(40)
        form_layout.addWidget(QLabel("用户名"))
        form_layout.addWidget(self.username_input)

        # 密码输入框
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setMinimumHeight(40)
        form_layout.addWidget(QLabel("密码"))
        form_layout.addWidget(self.password_input)

        # 记住我复选框
        checkbox_layout = QHBoxLayout()
        self.remember_checkbox = QCheckBox("记住我")
        self.remember_checkbox.setChecked(True)
        checkbox_layout.addWidget(self.remember_checkbox)

        # 忘记密码链接
        forgot_label = QLabel("忘记密码？")
        forgot_label.setStyleSheet("color: #2563EB; cursor: pointer;")
        forgot_label.mousePressEvent = self.on_forgot_password
        checkbox_layout.addStretch()
        checkbox_layout.addWidget(forgot_label)

        form_layout.addLayout(checkbox_layout)

        main_layout.addLayout(form_layout)

        # 登录按钮
        self.login_button = QPushButton("登录")
        self.login_button.setMinimumHeight(44)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
            QPushButton:disabled {
                background-color: #94A3B8;
            }
        """)
        self.login_button.clicked.connect(self.on_login_clicked)
        main_layout.addWidget(self.login_button)

        # 网络状态标签
        self.status_label = QLabel("网络连接正常")
        self.status_label.setStyleSheet("color: #16A34A; font-size: 12px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                         stop: 0 #F8FAFC, stop: 1 #E2E8F0);
            }
            QLabel {
                color: #1E293B;
            }
            QLineEdit {
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #2563EB;
            }
        """)

    def center_dialog(self):
        """将对话框居中显示"""
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
        else:
            screen = self.screen()
            screen_rect = screen.geometry()
            x = (screen_rect.width() - self.width()) // 2
            y = (screen_rect.height() - self.height()) // 2

        self.move(x, y)

    def on_page_loaded(self, success):
        """页面加载完成回调

        Args:
            success: 是否加载成功
        """
        if success:
            # 获取当前加载的URL，判断是登录页面还是主页面
            current_url = self.webview.url().toString()
            if "01-登录.html" in current_url or "登录" in current_url:
                # 注入JavaScript来处理登录事件和默认填充账密
                self.webview.page().runJavaScript("""
                    (function() {
                        // 默认填充账密（方便测试）
                        function fillDefaultCredentials() {
                            const usernameInput = document.getElementById('username');
                            const passwordInput = document.getElementById('password');
                            if (usernameInput && !usernameInput.value) {
                                usernameInput.value = 'admin';
                            }
                            if (passwordInput && !passwordInput.value) {
                                passwordInput.value = 'password';
                            }
                        }
                        
                        // 等待DOM加载完成
                        function initLoginHandler() {
                            fillDefaultCredentials();
                            
                            const loginForm = document.getElementById('loginForm');
                            if (loginForm) {
                                loginForm.addEventListener('submit', function(e) {
                                    e.preventDefault();
                                    
                                    const username = document.getElementById('username').value;
                                    const password = document.getElementById('password').value;
                                    
                                    // 通过URL scheme调用Python方法
                                    // 使用自定义URL scheme来触发Python回调
                                    window.location.href = 'python://login?username=' + 
                                        encodeURIComponent(username) + 
                                        '&password=' + encodeURIComponent(password);
                                });
                            } else {
                                // 如果表单还没加载，延迟重试
                                setTimeout(initLoginHandler, 100);
                            }
                        }
                        
                        // 如果DOM已加载，立即执行；否则等待
                        if (document.readyState === 'loading') {
                            document.addEventListener('DOMContentLoaded', initLoginHandler);
                        } else {
                            initLoginHandler();
                        }
                    })();
                """)
            elif "02-主页面.html" in current_url or "主页面" in current_url:
                # 注入JavaScript来拦截主页面中的点击事件
                self.webview.page().runJavaScript("""
                    (function() {
                        // 拦截功能卡片的点击事件
                        function initMainPageHandler() {
                            const functionCards = document.querySelectorAll('.function-card');
                            
                            functionCards.forEach(card => {
                                // 移除原有的事件监听器（如果有）
                                const newCard = card.cloneNode(true);
                                card.parentNode.replaceChild(newCard, card);
                                
                                // 添加新的事件监听器
                                newCard.addEventListener('click', function(e) {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    
                                    const url = this.dataset.url;
                                    const title = this.dataset.title;
                                    
                                    if (!url) return;
                                    
                                    // 检查是否是本地HTML文件（如 03-设置.html）
                                    if (url.endsWith('.html') && !url.startsWith('http')) {
                                        // 本地HTML文件，在当前窗口加载
                                        window.location.href = url;
                                    } else if (url.startsWith('http')) {
                                        // 外部URL，通过Python在系统浏览器中打开
                                        window.location.href = 'python://openurl?url=' + encodeURIComponent(url);
                                    } else {
                                        // 其他情况，尝试作为本地文件加载
                                        window.location.href = url;
                                    }
                                });
                            });
                        }
                        
                        // 等待DOM加载完成
                        if (document.readyState === 'loading') {
                            document.addEventListener('DOMContentLoaded', initMainPageHandler);
                        } else {
                            initMainPageHandler();
                        }
                    })();
                """)

    def on_forgot_password(self, event):
        """忘记密码事件处理

        Args:
            event: 鼠标事件
        """
        QMessageBox.information(self, "密码重置", "请联系管理员重置密码")

    def on_login_clicked(self):
        """登录按钮点击事件"""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "登录失败", "请输入用户名和密码")
            return

        # 执行登录验证
        self.perform_login(username, password)

    def handle_login_request(self, username, password):
        """处理来自HTML的登录请求
        
        Args:
            username: 用户名
            password: 密码
        """
        # 通过JavaScript更新HTML页面中的按钮状态（如果存在）
        if self.webview:
            self.webview.page().runJavaScript("""
                (function() {
                    const loginButton = document.getElementById('loginButton');
                    if (loginButton) {
                        loginButton.disabled = true;
                        const buttonText = loginButton.querySelector('.button-text');
                        if (buttonText) {
                            buttonText.textContent = '登录中...';
                        }
                    }
                })();
            """)
        
        # 执行登录验证
        self.perform_login(username, password)
    
    def perform_login(self, username, password):
        """执行登录验证

        Args:
            username: 用户名
            password: 密码
        """
        # 模拟登录验证（这里应该连接到实际的认证服务）
        QTimer.singleShot(1500, lambda: self.check_credentials(username, password))

    def check_credentials(self, username, password):
        """验证用户凭据

        Args:
            username: 用户名
            password: 密码
        """
        # 简单的用户验证（实际应用中应该连接到认证服务）
        if username == "admin" and password == "password":
            # 登录成功
            self.on_login_success(username)
        else:
            # 登录失败
            self.on_login_failed()

    def on_login_success(self, username):
        """登录成功处理

        Args:
            username: 用户名
        """
        # 保存凭据
        if hasattr(self, 'remember_checkbox') and self.remember_checkbox.isChecked():
            self.settings_manager.set('remember_password', True)
            self.settings_manager.set('username', username)
        else:
            self.settings_manager.set('remember_password', False)
            self.settings_manager.set('username', '')
        
        # 保存用户名用于显示
        self.settings_manager.set('display_name', username)

        # 不关闭对话框，而是在WebView中加载主页面
        if self.webview and self.webview.page():
            try:
                # 加载主页面HTML
                html_path = Path(__file__).parent.parent / "02-主页面.html"
                if html_path.exists():
                    # 使用QTimer延迟加载，确保当前操作完成
                    QTimer.singleShot(100, lambda: self._load_main_page(html_path))
                else:
                    # 如果主页面不存在，显示错误
                    QMessageBox.warning(self, "错误", f"主页面文件不存在: {html_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载主页面失败: {str(e)}")
        else:
            # 如果没有WebView，使用备用方案
            QMessageBox.warning(self, "错误", "WebView未初始化")
    
    def _load_main_page(self, html_path):
        """加载主页面（内部方法）
        
        Args:
            html_path: HTML文件路径
        """
        try:
            if self.webview and self.webview.page():
                self.webview.load(QUrl.fromLocalFile(str(html_path.resolve())))
                # 更新窗口标题
                self.setWindowTitle("桌面管理程序 - 主页面")
                # 隐藏登录相关的原生UI（如果有）
                if hasattr(self, 'login_button'):
                    self.login_button.setVisible(False)
                if hasattr(self, 'username_input'):
                    self.username_input.setVisible(False)
                if hasattr(self, 'password_input'):
                    self.password_input.setVisible(False)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载主页面失败: {str(e)}")
    
    def load_html_file(self, html_path):
        """加载HTML文件（用于处理点击事件）
        
        Args:
            html_path: HTML文件路径（可以是Path对象或字符串）
        """
        try:
            if isinstance(html_path, str):
                html_path = Path(html_path)
            
            # 如果是相对路径，转换为绝对路径
            if not html_path.is_absolute():
                # 尝试从项目根目录查找
                base_path = Path(__file__).parent.parent
                html_path = base_path / html_path.name
            
            if html_path.exists() and html_path.suffix == '.html':
                if self.webview and self.webview.page():
                    self.webview.load(QUrl.fromLocalFile(str(html_path.resolve())))
                    # 更新窗口标题
                    file_name = html_path.stem
                    if "设置" in file_name:
                        self.setWindowTitle("桌面管理程序 - 设置")
                    elif "登录" in file_name:
                        self.setWindowTitle("桌面管理程序 - 登录")
                    elif "主页面" in file_name or "主页" in file_name:
                        self.setWindowTitle("桌面管理程序 - 主页面")
                    else:
                        self.setWindowTitle(f"桌面管理程序 - {file_name}")
            else:
                QMessageBox.warning(self, "错误", f"HTML文件不存在: {html_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载HTML文件失败: {str(e)}")
    
    def open_external_url(self, url):
        """在系统浏览器中打开外部URL
        
        Args:
            url: 要打开的URL
        """
        try:
            webbrowser.open(url)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开链接: {str(e)}")

    def on_login_failed(self):
        """登录失败处理"""
        # 恢复HTML页面中的按钮状态
        if self.webview:
            self.webview.page().runJavaScript("""
                (function() {
                    const loginButton = document.getElementById('loginButton');
                    if (loginButton) {
                        loginButton.disabled = false;
                        const buttonText = loginButton.querySelector('.button-text');
                        if (buttonText) {
                            buttonText.textContent = '登录';
                        }
                    }
                    // 显示错误消息
                    const passwordError = document.getElementById('passwordError');
                    if (passwordError) {
                        passwordError.textContent = '用户名或密码错误';
                        passwordError.classList.add('show');
                    }
                    // 清除密码输入框
                    const passwordInput = document.getElementById('password');
                    if (passwordInput) {
                        passwordInput.value = '';
                        passwordInput.focus();
                    }
                })();
            """)
        
        # 如果是原生UI，恢复按钮状态
        if hasattr(self, 'login_button'):
            self.login_button.setText("登录")
            self.login_button.setEnabled(True)
            if hasattr(self, 'password_input'):
                self.password_input.clear()
                self.password_input.setFocus()
        
        # 显示错误消息（仅原生UI）
        if hasattr(self, 'password_input'):
            QMessageBox.warning(self, "登录失败", "用户名或密码错误")

    def load_saved_credentials(self):
        """加载保存的凭据"""
        if self.settings_manager.get('remember_password', False):
            username = self.settings_manager.get('username', '')
            if hasattr(self, 'username_input') and username:
                self.username_input.setText(username)
                self.remember_checkbox.setChecked(True)
