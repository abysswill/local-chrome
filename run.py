#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行脚本
快速启动桌面管理程序
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 12):
        print("错误: 需要Python 3.12或更高版本")
        print(f"当前版本: {sys.version}")
        sys.exit(1)

def check_dependencies():
    """检查依赖包"""
    print("检查依赖包...")

    required_packages = [
        ("PyQt6", "PyQt6"),
        ("PyQt6-WebEngine", "PyQt6.QtWebEngineWidgets")
    ]

    missing_packages = []

    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"✗ {package_name} - 未安装")
            missing_packages.append(package_name)

    if missing_packages:
        print(f"\n缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False

    print("所有依赖包检查通过")
    return True

def setup_environment():
    """设置运行环境"""
    # 确保在正确的目录
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)

    # 添加当前目录到Python路径
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

    # 创建必要的目录
    directories = ["config", "logs", "resources"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def main():
    """主函数"""
    print("=== 桌面管理程序启动器 ===")
    print()

    # 检查Python版本
    check_python_version()
    print()

    # 检查依赖包
    if not check_dependencies():
        input("按回车键退出...")
        return
    print()

    # 设置环境
    setup_environment()
    print()

    # 启动主程序
    try:
        print("启动桌面管理程序...")
        from main import main as app_main
        app_main()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")

if __name__ == "__main__":
    main()