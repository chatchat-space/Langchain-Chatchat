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
    args = Column(JSON, default=[], comment="命令参数列表")
    env = Column(JSON, default={}, comment="环境变量字典")
    cwd = Column(String(500), nullable=True, comment="工作目录")
    
    # 连接状态
    timeout = Column(Integer, default=30, comment="连接超时时间（秒）")
    enabled = Column(Boolean, default=True, comment="是否启用")
    description = Column(Text, nullable=True, comment="连接器描述")
    
    # 传输特定配置
    config = Column(JSON, default={}, comment="传输特定配置，包含 command 等字段")
    
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