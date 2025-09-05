from sqlalchemy import JSON, Column, DateTime, Integer, String, func, Boolean, Text

from chatchat.server.db.base import Base


class MCPConnectionModel(Base):
    """
    MCP 连接配置模型
    """

    __tablename__ = "mcp_connection"

    id = Column(String(32), primary_key=True, comment="MCP连接ID")
    name = Column(String(100), nullable=False, comment="连接名称")
    server_type = Column(String(50), nullable=False, comment="服务器类型")
    server_name = Column(String(100), nullable=False, comment="服务器名称")
    command = Column(String(500), nullable=False, comment="启动命令")
    args = Column(JSON, default=[], comment="命令参数")
    env = Column(JSON, default={}, comment="环境变量")
    cwd = Column(String(500), comment="工作目录")
    transport = Column(String(20), default="stdio", comment="传输方式：stdio 或 sse")
    timeout = Column(Integer, default=30, comment="连接超时时间（秒）")
    auto_connect = Column(Boolean, default=False, comment="是否自动连接")
    enabled = Column(Boolean, default=True, comment="是否启用")
    description = Column(Text, comment="连接描述")
    config = Column(JSON, default={}, comment="额外配置")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<MCPConnection(id='{self.id}', name='{self.name}', server_type='{self.server_type}', server_name='{self.server_name}', enabled={self.enabled}, create_time='{self.create_time}')>"


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