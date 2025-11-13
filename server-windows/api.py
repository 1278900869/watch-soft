#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由定义
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging

from config import config
from database import db

logger = logging.getLogger(__name__)

# FastAPI应用
app = FastAPI(
    title="USB监控后端",
    description="USB文件拷入监控系统",
    version="1.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 数据模型 ====================

class FileEvent(BaseModel):
    """文件事件模型"""
    timestamp: str
    machine_name: str
    ip_address: str
    username: str
    drive_letter: str
    file_name: str
    file_path: str
    action: str
    file_size: int = 0
    is_folder: bool = False


class AuthRequest(BaseModel):
    """认证请求"""
    username: str
    password: str


# ==================== 工具函数 ====================

def verify_api_key(authorization: str = Header(..., alias="Authorization")):
    """验证API密钥"""
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="授权令牌格式错误")
    
    api_key = authorization[7:]
    expected_key = str(config.get('api_key', ''))
    
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="API密钥无效")
    
    return True


# ==================== API路由 ====================

@app.get("/api/ping")
def ping():
    """健康检查"""
    from server import usb_service  # type: ignore
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "usb_monitoring": usb_service.is_running()
    }


@app.get("/api/debug/drives")
def debug_drives():
    """调试：查看所有驱动器检测状态"""
    from server import usb_service  # type: ignore
    import win32api
    import win32file
    
    drives_info = []
    bitmask = win32api.GetLogicalDrives()
    
    for i, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        if bitmask & (1 << i):
            drive_path = f"{letter}:\\"
            try:
                drive_type = win32file.GetDriveType(drive_path)
                drive_type_names = {
                    0: "UNKNOWN",
                    1: "NO_ROOT_DIR",
                    2: "REMOVABLE",
                    3: "FIXED",
                    4: "REMOTE",
                    5: "CDROM",
                    6: "RAMDISK"
                }
                
                is_usb = usb_service._is_usb_drive(letter)
                
                drives_info.append({
                    "letter": letter,
                    "type": drive_type_names.get(drive_type, "UNKNOWN"),
                    "type_code": drive_type,
                    "is_usb": is_usb,
                    "is_monitoring": letter in usb_service.file_monitors
                })
            except Exception as e:
                drives_info.append({
                    "letter": letter,
                    "error": str(e)
                })
    
    return {
        "drives": drives_info,
        "usb_count": sum(1 for d in drives_info if d.get('is_usb')),
        "monitoring_count": len(usb_service.file_monitors)
    }


@app.get("/api/events")
def get_events(
    limit: int = 100,
    machine_name: Optional[str] = None,
    authorization: str = Header(..., alias="Authorization")
):
    """获取事件列表"""
    try:
        verify_api_key(authorization)
        events = db.get_events(limit, machine_name)
        return {"events": events}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取事件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/events")
def post_event(
    event: FileEvent,
    authorization: str = Header(..., alias="Authorization")
):
    """接收文件事件（外部客户端）"""
    try:
        verify_api_key(authorization)
        db.insert_event(event.dict())
        logger.info(f"收到事件: {event.action} - {event.file_name}")
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理事件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
def get_statistics(authorization: str = Header(..., alias="Authorization")):
    """获取统计信息"""
    try:
        verify_api_key(authorization)
        stats = db.get_statistics()
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth")
def authenticate(
    auth: AuthRequest,
    authorization: str = Header(..., alias="Authorization")
):
    """用户认证"""
    try:
        verify_api_key(authorization)
        user = db.get_user(auth.username)
        
        if not user:
            return {"success": False, "message": "用户不存在"}
        
        if user['password'] == auth.password:
            return {
                "success": True,
                "message": "认证成功",
                "user": {"username": user['username']}
            }
        else:
            return {"success": False, "message": "密码错误"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"认证失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users")
def get_users(authorization: str = Header(..., alias="Authorization")):
    """获取用户列表"""
    try:
        verify_api_key(authorization)
        users = db.get_all_users()
        usernames = [u['username'] for u in users]
        return {"users": usernames}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 应用生命周期 ====================

@app.on_event("startup")
def startup_event():
    """应用启动"""
    from server import usb_service  # type: ignore
    usb_service.start()
    logger.info("✅ USB监控服务已启动")


@app.on_event("shutdown")
def shutdown_event():
    """应用关闭"""
    from server import usb_service  # type: ignore
    usb_service.stop()
    logger.info("❌ USB监控服务已停止")
