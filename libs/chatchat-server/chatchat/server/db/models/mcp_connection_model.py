from datetime import datetime
from typing import Dict, List, Optional, Union
from sqlalchemy import Boolean, Column, DateTime, Integer, String, JSON, Text, func

from chatchat.server.db.base import Base


class MCPConnectionModel(Base):
    """
    MCP 连接配置模型 - 支持 StdioConnection 和 SSEConnection 类型
    """

    __tablename__ = "mcp_connection"

    # 基本信息
    id = Column(String(32), primary_key=True, comment="MCP连接ID")
    server_name = Column(String(100), unique=True, nullable=False, comment="服务器名称")
    transport = Column(String(20), nullable=False, comment="传输方式: stdio, sse")
    command = Column(String(500), nullable=True, comment="启动命令")
    args = Column(JSON, default=[], comment="命令参数列表")
    env = Column(JSON, default={}, comment="环境变量字典")
    cwd = Column(String(500), nullable=True, comment="工作目录")
    
    # 连接状态
    timeout = Column(Integer, default=30, comment="连接超时时间（秒）")
    enabled = Column(Boolean, default=True, comment="是否启用")
    description = Column(Text, nullable=True, comment="连接器描述")
    
    # 传输特定配置
    config = Column(JSON, default={}, comment="传输特定配置")
    
    # 元数据
    last_connected_at = Column(DateTime, nullable=True, comment="最后连接时间")
    connection_status = Column(String(50), default="disconnected", comment="连接状态")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<MCPConnection(id='{self.id}', server_name='{self.server_name}', transport='{self.transport}', enabled={self.enabled})>"

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "server_name": self.server_name,
            "transport": self.transport,
            "command": self.command,
            "args": self.args or [],
            "env": self.env or {},
            "cwd": self.cwd,
            "timeout": self.timeout,
            "enabled": self.enabled,
            "description": self.description,
            "config": self.config or {},
            "last_connected_at": self.last_connected_at.isoformat() if self.last_connected_at else None,
            "connection_status": self.connection_status,
            "error_message": self.error_message,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None,
        }

    def get_stdio_config(self) -> Dict[str, Union[str, List[str], Dict[str, str]]]:
        """获取 stdio 传输配置"""
        if self.transport != "stdio":
            raise ValueError("Not a stdio connection")
        
        return {
            "transport": "stdio",
            "command": self.command or "",
            "args": self.args or [],
            "env": self.env or {},
            "cwd": self.cwd or "",
            "encoding": self.config.get("encoding", "utf-8") if self.config else "utf-8",
            "encoding_error_handler": self.config.get("encoding_error_handler", "strict") if self.config else "strict",
        }

    def get_sse_config(self) -> Dict[str, Union[str, Dict[str, str], float]]:
        """获取 SSE 传输配置"""
        if self.transport != "sse":
            raise ValueError("Not an SSE connection")
        
        config = self.config or {}
        return {
            "transport": "sse",
            "url": config.get("url", ""),
            "headers": config.get("headers", None),
            "timeout": config.get("timeout", 30),
            "sse_read_timeout": config.get("sse_read_timeout", 30),
            "encoding": config.get("encoding", "utf-8"),
            "encoding_error_handler": config.get("encoding_error_handler", "strict"),
        }

    def set_stdio_config(
        self,
        encoding: str = "utf-8",
        encoding_error_handler: str = "strict",
    ):
        """设置 stdio 传输配置"""
        if self.transport != "stdio":
            raise ValueError("Not a stdio connection")
        
        if not self.config:
            self.config = {}
        
        self.config.update({
            "encoding": encoding,
            "encoding_error_handler": encoding_error_handler,
        })

    def set_sse_config(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
        sse_read_timeout: float = 30.0,
        encoding: str = "utf-8",
        encoding_error_handler: str = "strict",
    ):
        """设置 SSE 传输配置"""
        if self.transport != "sse":
            raise ValueError("Not an SSE connection")
        
        if not self.config:
            self.config = {}
        
        self.config.update({
            "url": url,
            "headers": headers,
            "timeout": timeout,
            "sse_read_timeout": sse_read_timeout,
            "encoding": encoding,
            "encoding_error_handler": encoding_error_handler,
        })


class MCPProfileModel(Base):
    """
    MCP 通用配置模型
    """

    __tablename__ = "mcp_profile"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="配置ID")
    timeout = Column(Integer, default=30, nullable=False, comment="默认连接超时时间（秒）")
    working_dir = Column(String(500), default="/tmp", nullable=False, comment="默认工作目录")
    env_vars = Column(JSON, default={}, nullable=False, comment="默认环境变量配置")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<MCPProfile(id={self.id}, timeout={self.timeout}, working_dir='{self.working_dir}', update_time='{self.update_time}')>"