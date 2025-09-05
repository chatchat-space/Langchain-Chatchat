import uuid
from typing import Dict, List, Optional

from chatchat.server.db.models.mcp_connection_model import MCPConnectionModel, MCPProfileModel
from chatchat.server.db.session import with_session


@with_session
def add_mcp_connection(
    session,
    name: str,
    server_type: str,
    server_name: str,
    command: str,
    args: List[str] = None,
    env: Dict[str, str] = None,
    cwd: str = None,
    transport: str = "stdio",
    timeout: int = 30,
    auto_connect: bool = False,
    enabled: bool = True,
    description: str = "",
    config: Dict = None,
    connection_id: str = None,
):
    """
    新增 MCP 连接配置
    """
    if not connection_id:
        connection_id = uuid.uuid4().hex
    
    if args is None:
        args = []
    if env is None:
        env = {}
    if config is None:
        config = {}
    
    mcp_connection = MCPConnectionModel(
        id=connection_id,
        name=name,
        server_type=server_type,
        server_name=server_name,
        command=command,
        args=args,
        env=env,
        cwd=cwd,
        transport=transport,
        timeout=timeout,
        auto_connect=auto_connect,
        enabled=enabled,
        description=description,
        config=config,
    )
    session.add(mcp_connection)
    session.commit()
    return mcp_connection.id


@with_session
def update_mcp_connection(
    session,
    connection_id: str,
    name: str = None,
    server_type: str = None,
    server_name: str = None,
    command: str = None,
    args: List[str] = None,
    env: Dict[str, str] = None,
    cwd: str = None,
    transport: str = None,
    timeout: int = None,
    auto_connect: bool = None,
    enabled: bool = None,
    description: str = None,
    config: Dict = None,
):
    """
    更新 MCP 连接配置
    """
    mcp_connection = get_mcp_connection_by_id(session, connection_id)
    if mcp_connection is not None:
        if name is not None:
            mcp_connection.name = name
        if server_type is not None:
            mcp_connection.server_type = server_type
        if server_name is not None:
            mcp_connection.server_name = server_name
        if command is not None:
            mcp_connection.command = command
        if args is not None:
            mcp_connection.args = args
        if env is not None:
            mcp_connection.env = env
        if cwd is not None:
            mcp_connection.cwd = cwd
        if transport is not None:
            mcp_connection.transport = transport
        if timeout is not None:
            mcp_connection.timeout = timeout
        if auto_connect is not None:
            mcp_connection.auto_connect = auto_connect
        if enabled is not None:
            mcp_connection.enabled = enabled
        if description is not None:
            mcp_connection.description = description
        if config is not None:
            mcp_connection.config = config
        
        session.add(mcp_connection)
        session.commit()
        return mcp_connection.id
    return None


@with_session
def get_mcp_connection_by_id(session, connection_id: str) -> Optional[MCPConnectionModel]:
    """
    根据 ID 查询 MCP 连接配置
    """
    mcp_connection = session.query(MCPConnectionModel).filter_by(id=connection_id).first()
    return mcp_connection


@with_session
def get_mcp_connection_by_name(session, name: str) -> Optional[MCPConnectionModel]:
    """
    根据名称查询 MCP 连接配置
    """
    mcp_connection = session.query(MCPConnectionModel).filter_by(name=name).first()
    return mcp_connection


@with_session
def get_mcp_connections_by_server_name(session, server_name: str) -> List[MCPConnectionModel]:
    """
    根据服务器名称查询 MCP 连接配置列表
    """
    connections = (
        session.query(MCPConnectionModel)
        .filter_by(server_name=server_name)
        .all()
    )
    return connections


@with_session
def get_all_mcp_connections(session, enabled_only: bool = False) -> List[MCPConnectionModel]:
    """
    获取所有 MCP 连接配置
    """
    query = session.query(MCPConnectionModel)
    if enabled_only:
        query = query.filter_by(enabled=True)
    
    connections = query.order_by(MCPConnectionModel.create_time.desc()).all()
    return connections


@with_session
def get_enabled_mcp_connections(session) -> List[MCPConnectionModel]:
    """
    获取所有启用的 MCP 连接配置
    """
    connections = (
        session.query(MCPConnectionModel)
        .filter_by(enabled=True)
        .order_by(MCPConnectionModel.create_time.desc())
        .all()
    )
    return connections


@with_session
def get_auto_connect_mcp_connections(session) -> List[MCPConnectionModel]:
    """
    获取所有自动连接的 MCP 连接配置
    """
    connections = (
        session.query(MCPConnectionModel)
        .filter_by(enabled=True, auto_connect=True)
        .order_by(MCPConnectionModel.create_time.desc())
        .all()
    )
    return connections


@with_session
def delete_mcp_connection(session, connection_id: str) -> bool:
    """
    删除 MCP 连接配置
    """
    mcp_connection = get_mcp_connection_by_id(session, connection_id)
    if mcp_connection is not None:
        session.delete(mcp_connection)
        session.commit()
        return True
    return False


@with_session
def enable_mcp_connection(session, connection_id: str) -> bool:
    """
    启用 MCP 连接配置
    """
    mcp_connection = get_mcp_connection_by_id(session, connection_id)
    if mcp_connection is not None:
        mcp_connection.enabled = True
        session.add(mcp_connection)
        session.commit()
        return True
    return False


@with_session
def disable_mcp_connection(session, connection_id: str) -> bool:
    """
    禁用 MCP 连接配置
    """
    mcp_connection = get_mcp_connection_by_id(session, connection_id)
    if mcp_connection is not None:
        mcp_connection.enabled = False
        session.add(mcp_connection)
        session.commit()
        return True
    return False


@with_session
def set_auto_connect(session, connection_id: str, auto_connect: bool) -> bool:
    """
    设置 MCP 连接的自动连接状态
    """
    mcp_connection = get_mcp_connection_by_id(session, connection_id)
    if mcp_connection is not None:
        mcp_connection.auto_connect = auto_connect
        session.add(mcp_connection)
        session.commit()
        return True
    return False


@with_session
def search_mcp_connections(
    session,
    keyword: str = None,
    server_type: str = None,
    enabled: bool = None,
    auto_connect: bool = None,
    limit: int = 50,
) -> List[MCPConnectionModel]:
    """
    搜索 MCP 连接配置
    """
    query = session.query(MCPConnectionModel)
    
    if keyword:
        keyword = f"%{keyword}%"
        query = query.filter(
            MCPConnectionModel.name.like(keyword) |
            MCPConnectionModel.server_name.like(keyword) |
            MCPConnectionModel.description.like(keyword)
        )
    
    if server_type:
        query = query.filter_by(server_type=server_type)
    
    if enabled is not None:
        query = query.filter_by(enabled=enabled)
    
    if auto_connect is not None:
        query = query.filter_by(auto_connect=auto_connect)
    
    connections = query.order_by(MCPConnectionModel.create_time.desc()).limit(limit).all()
    return connections


# MCP Profile 相关操作
@with_session
def get_mcp_profile(session) -> Optional[MCPProfileModel]:
    """
    获取 MCP 通用配置
    """
    profile = session.query(MCPProfileModel).first()
    return profile


@with_session
def create_mcp_profile(
    session,
    timeout: int = 30,
    working_dir: str = "/tmp",
    env_vars: Dict[str, str] = None,
):
    """
    创建 MCP 通用配置
    """
    if env_vars is None:
        env_vars = {
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "PYTHONPATH": "/app",
            "HOME": "/tmp"
        }
    
    # 检查是否已存在配置
    existing_profile = get_mcp_profile(session)
    if existing_profile:
        return update_mcp_profile(
            session,
            timeout=timeout,
            working_dir=working_dir,
            env_vars=env_vars,
        )
    
    profile = MCPProfileModel(
        timeout=timeout,
        working_dir=working_dir,
        env_vars=env_vars,
    )
    session.add(profile)
    session.commit()
    return profile.id


@with_session
def update_mcp_profile(
    session,
    timeout: int = None,
    working_dir: str = None,
    env_vars: Dict[str, str] = None,
):
    """
    更新 MCP 通用配置
    """
    profile = get_mcp_profile(session)
    if profile is not None:
        if timeout is not None:
            profile.timeout = timeout
        if working_dir is not None:
            profile.working_dir = working_dir
        if env_vars is not None:
            profile.env_vars = env_vars
        
        session.add(profile)
        session.commit()
        return profile.id
    else:
        # 如果不存在配置，则创建新的
        return create_mcp_profile(
            session,
            timeout=timeout or 30,
            working_dir=working_dir or "/tmp",
            env_vars=env_vars,
        )


@with_session
def reset_mcp_profile(session):
    """
    重置 MCP 通用配置为默认值
    """
    profile = get_mcp_profile(session)
    if profile is not None:
        profile.timeout = 30
        profile.transport = "stdio"
        profile.auto_connect = False
        profile.working_dir = "/tmp"
        profile.env_vars = {
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "PYTHONPATH": "/app",
            "HOME": "/tmp"
        }
        
        session.add(profile)
        session.commit()
        return True
    return False


@with_session
def delete_mcp_profile(session):
    """
    删除 MCP 通用配置
    """
    profile = get_mcp_profile(session)
    if profile is not None:
        session.delete(profile)
        session.commit()
        return True
    return False