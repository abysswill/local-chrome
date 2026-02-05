#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置管理器
负责应用程序配置的读取、写入和管理
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

class SettingsManager:
    """设置管理器类"""

    def __init__(self, settings_file: str = "config/settings.json"):
        """初始化设置管理器

        Args:
            settings_file: 设置文件路径
        """
        self.settings_file = Path(settings_file)
        self.settings_file.parent.mkdir(exist_ok=True)
        self._settings = self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        """从文件加载设置

        Returns:
            设置字典
        """
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    return self._merge_settings(self._get_default_settings(), loaded_settings)
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载设置文件失败: {e}")
                return self._get_default_settings()
        packaged_settings = self._load_packaged_settings()
        if packaged_settings is not None:
            return self._merge_settings(self._get_default_settings(), packaged_settings)
        return self._get_default_settings()

    def _get_default_settings(self) -> Dict[str, Any]:
        """获取默认设置

        Returns:
            默认设置字典
        """
        return {
            # 用户设置
            "username": "admin",
            "display_name": "管理员",
            "email": "admin@example.com",
            "auto_login": False,
            "remember_password": True,

            # 系统设置
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
            "default_browser": "system",
            "auto_start": False,
            "data_sync": False,

            # 外观设置
            "theme_mode": "light",  # light, dark, system
            "theme_shortcut": "Ctrl+Shift+T",
            "enable_animations": True,
            "font_size": "medium",  # small, medium, large, xlarge
            "zoom_level": 100,  # 80, 90, 100, 110, 125, 150

            # 窗口设置
            "window": {
                "maximized": False,
                "width": 1920,
                "height": 1080,
                "x": 100,
                "y": 100
            },

            # 其他设置
            "language": "zh-CN",
            "check_updates": True,
            "version": "1.0.0"
        }

    def _merge_settings(self, base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        """合并设置（保留默认值，覆盖自定义项）"""
        merged = dict(base)
        for key, value in overrides.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = self._merge_settings(merged[key], value)
            else:
                merged[key] = value
        return merged

    def _load_packaged_settings(self) -> Optional[Dict[str, Any]]:
        """从打包资源中加载设置（仅当settings文件不存在时尝试）"""
        if not getattr(sys, 'frozen', False):
            return None
        base_path = Path(getattr(sys, '_MEIPASS', ''))
        if not base_path:
            return None
        packaged_path = base_path / self.settings_file
        if not packaged_path.exists():
            return None
        try:
            with open(packaged_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"加载打包设置失败: {e}")
            return None

    def get(self, key: str, default: Any = None) -> Any:
        """获取设置值

        Args:
            key: 设置键，支持点号分隔的嵌套键
            default: 默认值

        Returns:
            设置值
        """
        keys = key.split('.')
        value = self._settings

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """设置值

        Args:
            key: 设置键，支持点号分隔的嵌套键
            value: 设置值
        """
        keys = key.split('.')
        settings = self._settings

        # 导航到目标位置
        for k in keys[:-1]:
            if k not in settings:
                settings[k] = {}
            settings = settings[k]

        # 设置值
        settings[keys[-1]] = value

    def save(self) -> bool:
        """保存设置到文件

        Returns:
            是否保存成功
        """
        try:
            # 创建备份
            if self.settings_file.exists():
                backup_file = self.settings_file.with_suffix('.bak')
                self.settings_file.rename(backup_file)

            # 保存新设置
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)

            return True
        except IOError as e:
            print(f"保存设置失败: {e}")
            return False

    def reset(self) -> None:
        """重置设置为默认值"""
        self._settings = self._get_default_settings()

    def get_url(self, name: str) -> str:
        """获取功能模块URL

        Args:
            name: 功能模块名称

        Returns:
            URL地址
        """
        return self.get(f"urls.{name}", "https://example.com")

    def set_url(self, name: str, url: str) -> None:
        """设置功能模块URL

        Args:
            name: 功能模块名称
            url: URL地址
        """
        self.set(f"urls.{name}", url)

    def get_window_state(self) -> Dict[str, Any]:
        """获取窗口状态

        Returns:
            窗口状态字典
        """
        return self.get("window", {})

    def save_window_state(self, width: int, height: int, x: int, y: int, maximized: bool) -> None:
        """保存窗口状态

        Args:
            width: 窗口宽度
            height: 窗口高度
            x: 窗口X坐标
            y: 窗口Y坐标
            maximized: 是否最大化
        """
        self.set("window", {
            "width": width,
            "height": height,
            "x": x,
            "y": y,
            "maximized": maximized
        })

    def export_settings(self, export_file: str) -> bool:
        """导出设置到文件

        Args:
            export_file: 导出文件路径

        Returns:
            是否导出成功
        """
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"导出设置失败: {e}")
            return False

    def import_settings(self, import_file: str) -> bool:
        """从文件导入设置

        Args:
            import_file: 导入文件路径

        Returns:
            是否导入成功
        """
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                self._settings = json.load(f)
            return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"导入设置失败: {e}")
            return False
