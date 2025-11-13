#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
USB监控核心服务 - 专注于文件拷入监控
"""

import os
import time
import threading
import logging
from typing import Dict
from datetime import datetime
from pathlib import Path

# Windows特定模块
import win32api
import win32file
import win32con
import win32event
import wmi

from database import db

logger = logging.getLogger(__name__)


class FileMonitor(threading.Thread):
    """文件系统监控器 - 只监控拷入操作"""
    
    def __init__(self, drive_letter: str, callback):
        super().__init__(daemon=True)
        self.drive_letter = drive_letter
        self.drive_path = f"{drive_letter}:\\"
        self.callback = callback
        self.running = False
        self.processed_items = set()  # 防止重复处理
        self.pending_folders = {}  # 待处理的文件夹（用于合并子项）
        self.folder_wait_time = 1.0  # 文件夹等待时间（秒）
    
    def run(self):
        """运行监控"""
        self.running = True
        logger.info(f"开始监控拷入: {self.drive_path}")
        
        try:
            handle = win32file.CreateFile(
                self.drive_path,
                win32con.GENERIC_READ,
                win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
                None,
                win32con.OPEN_EXISTING,
                win32con.FILE_FLAG_BACKUP_SEMANTICS | win32con.FILE_FLAG_OVERLAPPED,
                None
            )
            
            overlapped = win32file.OVERLAPPED()
            overlapped.hEvent = win32event.CreateEvent(None, False, False, None)
            buffer = win32file.AllocateReadBuffer(8192)
            
            # 只监控文件创建（拷入）
            win32file.ReadDirectoryChangesW(  # type: ignore
                handle, buffer, True,  # type: ignore
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME,
                overlapped
            )
            
            while self.running:
                result = win32event.WaitForSingleObject(overlapped.hEvent, 1000)
                
                if result == win32event.WAIT_OBJECT_0:
                    num_bytes = win32file.GetOverlappedResult(handle, overlapped, True)  # type: ignore
                    if num_bytes > 0:
                        results = win32file.FILE_NOTIFY_INFORMATION(buffer, num_bytes)  # type: ignore
                        
                        for action, filename in results:
                            # 只处理创建操作（action=1表示创建）
                            if action == 1:
                                self._handle_copy_in(filename)
                        
                        if self.running:
                            win32file.ReadDirectoryChangesW(  # type: ignore
                                handle, buffer, True,  # type: ignore
                                win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                                win32con.FILE_NOTIFY_CHANGE_DIR_NAME,
                                overlapped
                            )
        
        except Exception as e:
            logger.error(f"文件监控错误: {e}")
        finally:
            try:
                win32file.CancelIo(handle)  # type: ignore
                win32file.CloseHandle(handle)  # type: ignore
            except:
                pass
    
    def _handle_copy_in(self, filename: str):
        """处理拷入操作 - 只处理顶层项目"""
        try:
            full_path = os.path.join(self.drive_path, filename)
            
            # 防止重复处理
            if full_path in self.processed_items:
                return
            
            # 关键：如果路径包含\\，说明是子项，直接忽略
            if '\\' in filename:
                return
            
            self.processed_items.add(full_path)
            
            # 等待文件完全拷入
            time.sleep(0.5)
            
            if not os.path.exists(full_path):
                return
            
            is_folder = os.path.isdir(full_path)
            
            if is_folder:
                # 处理文件夹拷入
                self._handle_folder(full_path, filename)
            else:
                # 处理文件拷入
                self._handle_file(full_path, filename)
        
        except Exception as e:
            logger.error(f"处理拷入失败: {e}")
    
    def _handle_file(self, full_path: str, filename: str):
        """处理单个文件拷入"""
        try:
            file_size = os.path.getsize(full_path)
            file_ext = os.path.splitext(filename)[1].lower() or '无扩展名'
            
            event = {
                'timestamp': datetime.now().isoformat(),
                'machine_name': os.environ.get('COMPUTERNAME', 'Unknown'),
                'ip_address': '127.0.0.1',
                'username': '本地用户',
                'drive_letter': self.drive_letter,
                'file_name': filename,
                'file_path': full_path,
                'action': f'拷入文件 ({file_ext})',
                'file_size': file_size,
                'is_folder': False
            }
            
            self.callback(event)
            logger.info(f"📄 文件拷入: {filename} ({file_ext}, {self._format_size(file_size)})")
        
        except Exception as e:
            logger.error(f"处理文件失败: {e}")
    
    def _handle_folder(self, full_path: str, foldername: str):
        """处理文件夹拷入 - 完整索引结构"""
        try:
            # 扫描文件夹结构
            structure = self._scan_folder_structure(full_path)
            
            # 创建日志文件，记录完整文件夹结构
            self._create_folder_structure_log(foldername, full_path, structure)
            
            event = {
                'timestamp': datetime.now().isoformat(),
                'machine_name': os.environ.get('COMPUTERNAME', 'Unknown'),
                'ip_address': '127.0.0.1',
                'username': '本地用户',
                'drive_letter': self.drive_letter,
                'file_name': foldername,
                'file_path': full_path,
                'action': f"拷入文件夹 (共{structure['total_files']}个文件, {structure['total_folders']}个子文件夹)",
                'file_size': structure['total_size'],
                'is_folder': True,
                'folder_structure': structure['structure']  # 完整文件夹结构
            }
            
            self.callback(event)
            logger.info(f"📁 文件夹拷入: {foldername} (文件:{structure['total_files']}, 文件夹:{structure['total_folders']}, {self._format_size(structure['total_size'])})")
        
        except Exception as e:
            logger.error(f"处理文件夹失败: {e}")
    
    def _scan_folder_structure(self, folder_path: str) -> Dict:
        """扫描文件夹完整结构"""
        structure = []
        total_files = 0
        total_folders = 0
        total_size = 0
        
        try:
            for root, dirs, files in os.walk(folder_path):
                # 相对路径
                rel_path = os.path.relpath(root, folder_path)
                if rel_path == '.':
                    rel_path = ''
                
                # 文件夹信息
                folder_info = {
                    'path': rel_path,
                    'files': [],
                    'subfolders': dirs.copy()
                }
                
                # 统计子文件夹
                total_folders += len(dirs)
                
                # 文件信息
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        file_size = os.path.getsize(file_path)
                        file_ext = os.path.splitext(file)[1].lower() or '无'
                        
                        folder_info['files'].append({
                            'name': file,
                            'size': file_size,
                            'type': file_ext
                        })
                        
                        total_files += 1
                        total_size += file_size
                    except:
                        pass
                
                structure.append(folder_info)
        
        except Exception as e:
            logger.error(f"扫描文件夹结构失败: {e}")
        
        return {
            'structure': structure,
            'total_files': total_files,
            'total_folders': total_folders,
            'total_size': total_size
        }
    
    def _create_folder_structure_log(self, foldername: str, folder_path: str, structure: Dict):
        """创建文件夹结构日志文件"""
        try:
            # 日志文件目录
            log_dir = Path(__file__).parent / 'logs' / 'folder_structures'
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # 日志文件名：时间戳_文件夹名.txt
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_foldername = "".join(c for c in foldername if c.isalnum() or c in (' ', '-', '_')).strip()
            log_filename = f"{timestamp}_{safe_foldername}.txt"
            log_file = log_dir / log_filename
            
            # 写入日志
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write(f"文件夹结构日志\n")
                f.write("="*80 + "\n\n")
                
                f.write(f"文件夹名称: {foldername}\n")
                f.write(f"完整路径: {folder_path}\n")
                f.write(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"驱动器: {self.drive_letter}:\\\n")
                f.write("\n" + "-"*80 + "\n")
                f.write(f"统计信息:\n")
                f.write(f"  总文件数: {structure['total_files']}\n")
                f.write(f"  总文件夹数: {structure['total_folders']}\n")
                f.write(f"  总大小: {self._format_size(structure['total_size'])}\n")
                f.write("-"*80 + "\n\n")
                
                f.write("文件夹结构树:\n")
                f.write("="*80 + "\n\n")
                
                # 绘制文件树
                self._write_tree_structure(f, structure['structure'])
            
            logger.info(f"✅ 文件夹结构日志已生成: {log_file}")
        
        except Exception as e:
            logger.error(f"创建文件夹结构日志失败: {e}")
    
    def _write_tree_structure(self, file, structure_list):
        """写入树形结构到文件"""
        for folder_info in structure_list:
            path = folder_info['path']
            files = folder_info['files']
            subfolders = folder_info['subfolders']
            
            # 计算缩进级别
            if path == '':
                indent = ''
                display_path = '📁 [根目录]'
            else:
                level = path.count(os.sep)
                indent = '  ' * level
                folder_name = os.path.basename(path)
                display_path = f"{indent}📂 {folder_name}/"
            
            file.write(f"{display_path}\n")
            
            # 写入文件
            for file_info in files:
                file_indent = indent + '  '
                file_icon = self._get_file_icon(file_info['type'])
                file.write(f"{file_indent}{file_icon} {file_info['name']} ({self._format_size(file_info['size'])})\n")
            
            # 如果有子文件夹，显示列表
            if subfolders and not files:
                for subfolder in subfolders:
                    file.write(f"{indent}  📂 {subfolder}/\n")
            
            file.write("\n")
    
    def _get_file_icon(self, file_type: str) -> str:
        """根据文件类型返回图标"""
        icons = {
            '.txt': '📄',
            '.doc': '📄', '.docx': '📄',
            '.xls': '📊', '.xlsx': '📊',
            '.pdf': '📃',
            '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️', '.bmp': '🖼️',
            '.mp4': '🎥', '.avi': '🎥', '.mkv': '🎥',
            '.mp3': '🎵', '.wav': '🎵', '.flac': '🎵',
            '.zip': '🗄️', '.rar': '🗄️', '.7z': '🗄️',
            '.exe': '⚙️', '.msi': '⚙️',
            '.py': '🐍', '.js': '🔶', '.html': '🌐', '.css': '🎨',
        }
        return icons.get(file_type.lower(), '📄')
    
    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        size_float = float(size)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_float < 1024.0:
                return f"{size_float:.2f}{unit}"
            size_float /= 1024.0
        return f"{size_float:.2f}TB"
    
    def stop(self):
        """停止监控"""
        self.running = False


class USBMonitorService:
    """UUSB监控服务"""
    
    def __init__(self):
        self.running = False
        self.monitor_thread = None
        self.file_monitors: Dict[str, FileMonitor] = {}
        self.user_sessions: Dict[str, tuple] = {}  # 驱动器 -> (用户名, login_id)
        self.login_callback = None  # 登录回调函数
    
    def set_login_callback(self, callback):
        """设置登录回调函数"""
        self.login_callback = callback
    
    def start(self):
        """启动监控"""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("✅ USB监控服务已启动")
    
    def stop(self):
        """停止监控"""
        self.running = False
        
        for monitor in list(self.file_monitors.values()):
            monitor.stop()
        self.file_monitors.clear()
        
        logger.info("❌ USB监控服务已停止")
    
    def is_running(self) -> bool:
        """检查是否运行中"""
        return self.running
    
    def _monitor_loop(self):
        """监控循环"""
        previous_drives = set(self._get_usb_drives())
        
        while self.running:
            try:
                time.sleep(0.5)
                current_drives = set(self._get_usb_drives())
                
                # 新插入的U盘
                for drive in current_drives - previous_drives:
                    self._on_usb_inserted(drive)
                
                # 移除的U盘
                for drive in previous_drives - current_drives:
                    self._on_usb_removed(drive)
                
                previous_drives = current_drives
            
            except Exception as e:
                logger.error(f"监控循环错误: {e}")
    
    def _get_usb_drives(self) -> set:
        """获取USB驱动器"""
        usb_drives = set()
        
        try:
            bitmask = win32api.GetLogicalDrives()
            for i, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
                if bitmask & (1 << i):
                    if self._is_usb_drive(letter):
                        usb_drives.add(letter)
        except Exception as e:
            logger.error(f"获取USB驱动器失败: {e}")
        
        return usb_drives
    
    def _is_usb_drive(self, letter: str) -> bool:
        """检查是否为USB设备（包括U盘和移动硬盘）"""
        try:
            drive_path = f"{letter}:\\"
            drive_type = win32file.GetDriveType(drive_path)
            
            # 1. 可移动设备（U盘）
            if drive_type == win32file.DRIVE_REMOVABLE:
                logger.debug(f"{letter}: 检测为可移动设备")
                return True
            
            # 2. 固定设备（可能是移动硬盘）
            if drive_type == win32file.DRIVE_FIXED:
                # 方法1: WMI查询
                try:
                    c = wmi.WMI()
                    for disk in c.Win32_LogicalDisk(DeviceID=f"{letter}:"):
                        for partition in disk.associators("Win32_LogicalDiskToPartition"):
                            for drive in partition.associators("Win32_DiskDriveToDiskPartition"):
                                interface = getattr(drive, 'InterfaceType', '').upper()
                                pnp = getattr(drive, 'PNPDeviceID', '').upper()
                                media_type = getattr(drive, 'MediaType', '').upper()
                                
                                # 检查是否为USB接口
                                if 'USB' in interface or 'USB' in pnp or 'REMOVABLE' in media_type:
                                    logger.debug(f"{letter}: WMI检测为USB设备 (Interface={interface}, PNP={pnp})")
                                    return True
                except Exception as e:
                    logger.debug(f"{letter}: WMI查询失败: {e}")
                
                # 方法2: 检查是否为系统盘（C:、D:通常不是USB）
                # 如果不是系统盘，也认为是可移动设备
                if letter not in ['C', 'D']:
                    try:
                        # 尝试访问硬盘序列号，系统盘通常有固定序列号
                        volume_info = win32api.GetVolumeInformation(drive_path)
                        # 如果能访问且不是C/D盘，认为是移动设备
                        logger.debug(f"{letter}: 非系统盘，认为是USB设备")
                        return True
                    except:
                        pass
            
            return False
        except Exception as e:
            logger.error(f"检查{letter}:失败: {e}")
            return False
    
    def _on_usb_inserted(self, drive: str):
        """UUSB插入事件"""
        logger.info(f"🔵 USB插入: {drive}:")
        
        # 弹出登录窗口（通过回调函数）
        if self.login_callback:
            username, login_id = self.login_callback(drive)
            if username and login_id:
                # 保存用户会话
                self.user_sessions[drive] = (username, login_id)
                logger.info(f"✅ 用户 {username} 登录成功 (驱动器: {drive}:)")
            else:
                logger.warning(f"⚠️ 用户取消登录 (驱动器: {drive}:)")
                return
        else:
            # 没有登录回调，使用默认用户
            self.user_sessions[drive] = ("未登录用户", 0)
        
        # 记录插入事件
        username, login_id = self.user_sessions.get(drive, ("未知用户", 0))
        event = {
            'timestamp': datetime.now().isoformat(),
            'machine_name': os.environ.get('COMPUTERNAME', 'Unknown'),
            'ip_address': '127.0.0.1',
            'username': username,
            'login_id': login_id,
            'drive_letter': drive,
            'file_name': '',
            'file_path': f"{drive}:\\",
            'action': 'USB插入',
            'file_size': 0,
            'is_folder': False
        }
        self._save_event(event)
        
        # 启动文件拷入监控
        monitor = FileMonitor(drive, lambda evt: self._save_event_with_user(evt, drive))
        monitor.start()
        self.file_monitors[drive] = monitor
    
    def _on_usb_removed(self, drive: str):
        """UUSB移除事件"""
        logger.info(f"🔴 USB移除: {drive}:")
        
        # 停止文件监控
        if drive in self.file_monitors:
            self.file_monitors[drive].stop()
            del self.file_monitors[drive]
        
        # 记录移除事件
        username, login_id = self.user_sessions.get(drive, ("未知用户", 0))
        event = {
            'timestamp': datetime.now().isoformat(),
            'machine_name': os.environ.get('COMPUTERNAME', 'Unknown'),
            'ip_address': '127.0.0.1',
            'username': username,
            'login_id': login_id,
            'drive_letter': drive,
            'file_name': '',
            'file_path': f"{drive}:\\",
            'action': 'USB移除',
            'file_size': 0,
            'is_folder': False
        }
        self._save_event(event)
        
        # 清除用户会话
        if drive in self.user_sessions:
            del self.user_sessions[drive]
    
    def _save_event_with_user(self, event: dict, drive: str):
        """保存事件到数据库（带用户信息）"""
        # 添加用户信息
        username, login_id = self.user_sessions.get(drive, ("未知用户", 0))
        event['username'] = username
        event['login_id'] = login_id
        self._save_event(event)
    
    def _save_event(self, event: dict):
        """保存事件到数据库"""
        try:
            db.insert_event(event)
        except Exception as e:
            logger.error(f"保存事件失败: {e}")


# 全局服务实例
usb_service = USBMonitorService()
