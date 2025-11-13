#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理
"""

import json
import os
from pathlib import Path

class Config:
    """配置管理类"""
    
    def __init__(self):
        self.config_file = Path(__file__).parent / 'config.json'
        self.default_config = {
            "host": "localhost",
            "port": 8888,
            "api_key": "usb_monitor_2024",
            "database": "usb_monitor.db"
        }
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return {**self.default_config, **json.load(f)}
            except Exception as e:
                print(f"加载配置失败: {e}")
                return self.default_config
        else:
            self.save_config(self.default_config)
            return self.default_config
    
    def save_config(self, config_data):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value
        self.save_config(self.config)


# 全局配置实例
config = Config()
