#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本
用于将Python应用打包为Windows可执行文件
"""

import os
import sys
import shutil
from pathlib import Path
import subprocess

def check_dependencies():
    """检查必要的依赖"""
    print("检查依赖...")

    try:
        import PyInstaller
        print("✓ PyInstaller 已安装")
    except ImportError:
        print("✗ PyInstaller 未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller 安装完成")

def create_icon():
    """创建应用图标"""
    icon_path = Path("resources/icon.png")
    if not icon_path.exists():
        print("创建默认应用图标...")
        icon_path.parent.mkdir(exist_ok=True)

        # 这里可以添加图标生成代码
        # 或者手动准备一个icon.png文件
        print("请手动添加 resources/icon.png 文件")

def build_exe():
    """构建可执行文件"""
    print("开始构建可执行文件...")

    # 构建命令
    cmd = [
        "pyinstaller",
        "--windowed",  # 无控制台窗口
        "--onefile",   # 单文件模式
        "--name", "桌面管理程序",  # 程序名称
        "--icon", "resources/icon.png",  # 图标
        "--add-data", "01-登录.html;.",  # 添加HTML文件
        "--add-data", "02-主页面.html;.",  # 添加HTML文件
        "--add-data", "03-设置.html;.",   # 添加HTML文件
        "--add-data", "resources;resources",  # 添加资源目录
        "--hidden-import", "PyQt6.QtWebEngineWidgets",
        "--hidden-import", "PyQt6.QtWebEngineCore",
        "main.py"
    ]

    try:
        subprocess.check_call(cmd)
        print("✓ 构建完成")
    except subprocess.CalledProcessError as e:
        print(f"✗ 构建失败: {e}")
        return False

    return True

def create_installer():
    """创建安装程序（可选）"""
    print("创建安装程序...")

    # 这里可以添加NSIS或其他安装工具的配置
    # 暂时跳过
    print("安装程序创建跳过")

def clean_build_files():
    """清理构建文件"""
    print("清理构建文件...")

    # 删除临时文件
    build_dir = Path("build")
    spec_file = Path("桌面管理程序.spec")

    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("✓ 删除build目录")

    if spec_file.exists():
        spec_file.unlink()
        print("✓ 删除spec文件")

def main():
    """主函数"""
    print("=== 桌面管理程序打包工具 ===")
    print()

    # 检查当前目录
    if not Path("main.py").exists():
        print("错误: 请在项目根目录运行此脚本")
        sys.exit(1)

    # 执行打包步骤
    try:
        # 1. 检查依赖
        check_dependencies()
        print()

        # 2. 创建图标
        create_icon()
        print()

        # 3. 清理之前的构建文件
        clean_build_files()
        print()

        # 4. 构建可执行文件
        if build_exe():
            print()

            # 5. 创建安装程序
            create_installer()
            print()

            print("=== 打包完成 ===")
            print("可执行文件位于: dist/桌面管理程序.exe")

        else:
            print("构建失败，请检查错误信息")

    except KeyboardInterrupt:
        print("\n用户取消操作")
    except Exception as e:
        print(f"打包过程中发生错误: {e}")

if __name__ == "__main__":
    main()