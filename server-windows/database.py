#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import logging

from config import config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        db_name: str = config.get('database', 'usb_monitor.db')  # type: ignore
        # 数据库文件放在database文件夹内
        db_dir = Path(__file__).parent / 'database'
        db_dir.mkdir(exist_ok=True)  # 确保文件夹存在
        self.db_file = db_dir / db_name
        self.init_database()
    
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """初始化数据库"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 创建用户登录记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_logins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                login_time TEXT NOT NULL,
                drive_letter TEXT,
                machine_name TEXT,
                ip_address TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建事件表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                machine_name TEXT,
                ip_address TEXT,
                username TEXT NOT NULL,
                login_id INTEGER,
                drive_letter TEXT,
                file_name TEXT,
                file_path TEXT,
                action TEXT,
                file_size INTEGER DEFAULT 0,
                is_folder BOOLEAN DEFAULT 0,
                folder_structure TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (login_id) REFERENCES user_logins(id)
            )
        ''')
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_machine ON events(machine_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_action ON events(action)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_username ON events(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logins_username ON user_logins(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logins_time ON user_logins(login_time)')
        
        conn.commit()
        conn.close()
        
        logger.info("数据库初始化完成")
    
    def insert_login(self, username: str, drive_letter: str) -> int:
        """插入用户登录记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        import os
        cursor.execute('''
            INSERT INTO user_logins (
                username, login_time, drive_letter, machine_name, ip_address
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            username,
            datetime.now().isoformat(),
            drive_letter,
            os.environ.get('COMPUTERNAME', 'Unknown'),
            '127.0.0.1'
        ))
        
        login_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return int(login_id) if login_id is not None else 0
    
    def insert_event(self, event_data: Dict):
        """插入事件"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 如果有文件夹结构，序列化为JSON
        folder_structure = event_data.get('folder_structure')
        if folder_structure:
            import json
            folder_structure = json.dumps(folder_structure, ensure_ascii=False)
        
        cursor.execute('''
            INSERT INTO events (
                timestamp, machine_name, ip_address, username, login_id,
                drive_letter, file_name, file_path, action,
                file_size, is_folder, folder_structure
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_data.get('timestamp'),
            event_data.get('machine_name'),
            event_data.get('ip_address'),
            event_data.get('username'),
            event_data.get('login_id'),
            event_data.get('drive_letter'),
            event_data.get('file_name'),
            event_data.get('file_path'),
            event_data.get('action'),
            event_data.get('file_size', 0),
            event_data.get('is_folder', False),
            folder_structure
        ))
        
        conn.commit()
        conn.close()
    
    def get_events(self, limit: int = 100, machine_name: Optional[str] = None) -> List[Dict]:
        """获取事件列表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if machine_name:
            cursor.execute('''
                SELECT * FROM events 
                WHERE machine_name = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (machine_name, limit))
        else:
            cursor.execute('''
                SELECT * FROM events 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 总事件数
        cursor.execute('SELECT COUNT(*) FROM events')
        total_events = cursor.fetchone()[0]
        
        # 今日事件数
        today = datetime.now().date().isoformat()
        cursor.execute('SELECT COUNT(*) FROM events WHERE DATE(timestamp) = ?', (today,))
        today_events = cursor.fetchone()[0]
        
        # 各类型事件统计
        cursor.execute('''
            SELECT action, COUNT(*) as count 
            FROM events 
            GROUP BY action
        ''')
        action_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total_events': total_events,
            'today_events': today_events,
            'action_stats': action_stats
        }
    
    def get_user(self, username: str) -> Optional[Dict]:
        """获取用户"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_all_users(self) -> List[Dict]:
        """获取所有用户"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users ORDER BY username')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def add_user(self, username: str, password: str = ''):
        """添加用户"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (username, password) 
            VALUES (?, ?)
        ''', (username, password))
        
        conn.commit()
        conn.close()


# 全局数据库实例
db = DatabaseManager()
