#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志工具模块
"""

import sys
import logging
import os
from datetime import datetime
from pathlib import Path

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """设置日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别

    Returns:
        配置好的日志记录器
    """
    # 创建日志目录 - 处理打包后的路径问题
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe程序，使用临时目录
        import tempfile
        base_dir = Path(tempfile.gettempdir()) / "桌面管理程序"
    else:
        # 如果是开发环境，使用当前目录
        base_dir = Path.cwd()

    log_dir = base_dir / "logs"
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        # 如果无法创建日志目录，则禁用文件日志
        log_dir = None

    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加处理器
    if not logger.handlers:
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 创建控制台处理器（总是启用）
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 只有在可以创建日志目录时才添加文件处理器
        if log_dir:
            try:
                log_filename = f"app_{datetime.now().strftime('%Y%m%d')}.log"
                log_path = log_dir / log_filename
                file_handler = logging.FileHandler(log_path, encoding='utf-8')
                file_handler.setLevel(level)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception:
                # 如果无法创建文件处理器，仅使用控制台日志
                pass

    return logger