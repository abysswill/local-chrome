# 桌面管理程序

一个基于Python和PyQt6的Windows桌面管理程序，用于Web管理系统的功能导航。

## 功能特性

- 🔐 **用户登录系统** - 支持用户认证和会话管理
- 🌐 **WebView集成** - 嵌式HTML页面，保持Web界面体验
- 🎨 **主题切换** - 支持明亮/暗黑主题切换，可跟随系统设置
- ⚙️ **设置管理** - 完整的配置管理系统
- 🖥️ **原生桌面体验** - 支持窗口管理、系统托盘等桌面特性
- 🔗 **外部链接管理** - 可配置各种功能模块的外部链接
- 💾 **数据持久化** - 设置和用户信息本地存储

## 技术栈

- **Python 3.12+**
- **PyQt6** - GUI框架
- **PyQt6-WebEngine** - WebView组件
- **HTML/CSS/JavaScript** - 界面技术

## 项目结构

```
桌面管理程序/
├── main.py                          # 主程序入口
├── requirements.txt                 # 依赖包列表
├── README.md                       # 项目说明
├── config/                         # 配置文件目录
│   └── settings.json              # 应用设置文件
├── logs/                          # 日志文件目录
├── components/                    # 组件模块
│   ├── __init__.py
│   ├── main_window.py            # 主窗口类
│   ├── login_dialog.py           # 登录对话框
│   ├── settings_manager.py       # 设置管理器
│   ├── theme_manager.py          # 主题管理器
│   └── window_manager.py         # 窗口管理器
├── utils/                        # 工具模块
│   ├── __init__.py
│   └── logger.py                 # 日志工具
├── resources/                    # 资源文件
│   ├── icon.png                  # 应用图标
│   └── themes/                   # 主题文件
├── 01-登录.html                  # 登录页面
├── 02-主页面.html                 # 主页面
└── 03-设置.html                  # 设置页面
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行程序

```bash
python main.py
```

## 默认登录信息

- **用户名**: admin
- **密码**: password

## 主要功能

### 1. 用户登录
- 支持用户名密码登录
- 记住密码功能
- 登录状态保持

### 2. 功能导航
- 患者管理
- 评估管理
- 饮食管理
- 运动管理
- 系统管理
- 工作管理
- 人工智能
- 帮助文档

### 3. 主题设置
- 明亮主题
- 暗黑主题
- 跟随系统主题
- 一键快捷键切换 (Ctrl+Shift+T)

### 4. 系统设置
- 功能URL配置
- 窗口行为设置
- 用户信息管理
- 数据导入导出

## 配置说明

应用程序配置文件位于 `config/settings.json`，包含以下主要设置：

```json
{
  "urls": {
    "user_management": "https://example.com/patients",
    "assessment": "https://example.com/assessment",
    "diet": "https://example.com/diet",
    "exercise": "https://example.com/exercise",
    "system": "https://example.com/system",
    "work": "https://example.com/work",
    "ai": "https://example.com/ai",
    "help": "https://example.com/help"
  },
  "startup_page_url": "",
  "theme_mode": "light",
  "auto_login": false,
  "default_browser": "system"
}
```

## 开发说明

### 自定义主题

1. 在 `resources/themes/` 目录下创建JSON格式的主题文件
2. 主题文件结构参考默认主题配置
3. 重启应用即可使用新主题

### 添加功能模块

1. 在HTML页面的功能卡片中添加新模块
2. 在设置页面中配置对应的URL
3. 程序会自动加载配置的URL地址

### 自定义WebView页面

1. 修改HTML文件以更改界面样式和功能
2. 使用JavaScript与Python交互
3. 通过 `window.desktopManager` 对象调用Python功能

## 构建和打包

使用PyInstaller打包为可执行文件：

```bash
pip install pyinstaller
pyinstaller --windowed --onefile main.py
```

或使用 `build_exe.bat` 并传入启动页面地址（可选）：

```bat
build_exe.bat "https://example.com/login"
```

## 系统要求

- Windows 10/11
- Python 3.12+
- 网络连接（用于外部链接）

## 故障排除

### 常见问题

1. **程序无法启动**
   - 检查Python版本是否为3.12+
   - 确认所有依赖包已正确安装

2. **WebView无法显示**
   - 安装Windows系统更新
   - 确认系统支持WebEngine

3. **主题切换无效**
   - 检查CSS样式是否正确加载
   - 确认JavaScript注入是否成功

## 版本历史

### v1.0.0
- 初始版本发布
- 基本登录和导航功能
- 主题切换支持
- 设置管理功能

## 许可证

本项目仅供学习和演示使用。

## 联系方式

如有问题或建议，请联系开发者。
