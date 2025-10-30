from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from chatchat.server.api_server.api_schemas import (
    MCPConnectionCreate,
    MCPConnectionUpdate,
    MCPConnectionResponse,
    MCPConnectionListResponse,
    MCPConnectionSearchRequest,
    MCPConnectionStatusResponse,
    MCPProfileCreate,
    MCPProfileResponse,
    MCPProfileStatusResponse,
)
from chatchat.server.db.repository.mcp_connection_repository import (
    add_mcp_connection,
    update_mcp_connection,
    get_mcp_connection_by_id,
    get_mcp_connections_by_server_name,
    get_all_mcp_connections,
    get_enabled_mcp_connections,
    delete_mcp_connection,
    enable_mcp_connection,
    disable_mcp_connection,
    search_mcp_connections,
    get_mcp_profile,
    create_mcp_profile,
    update_mcp_profile,
    reset_mcp_profile,
    delete_mcp_profile,
)
from chatchat.utils import build_logger


logger = build_logger()
mcp_router = APIRouter(prefix="/api/v1/mcp_connections", tags=["MCP Connections"])


# MCP Profile 相关路由 - 放在前面避免与 {connection_id} 冲突
@mcp_router.get("/profile", response_model=MCPProfileResponse, summary="获取 MCP 通用配置")
async def get_mcp_profile_endpoint():
    """
    获取 MCP 通用配置
    """
    logger.info("获取 MCP 通用配置")
    try:
        profile = get_mcp_profile()
        if profile:
            logger.info("成功获取 MCP 通用配置")
            return MCPProfileResponse(
                timeout=profile["timeout"],
                working_dir=profile["working_dir"],
                env_vars=profile["env_vars"],
                update_time=profile["update_time"]
            )
        else:
            logger.info("MCP 通用配置不存在，返回默认配置")
            # 如果不存在配置，返回默认配置
            return MCPProfileResponse(
                timeout=30,
                working_dir="/tmp",
                env_vars={
                    "PATH": "/usr/local/bin:/usr/bin:/bin",
                    "PYTHONPATH": "/app",
                    "HOME": "/tmp"
                },
                update_time=datetime.now().isoformat()
            )
    
    except Exception as e:
        logger.error(f"获取 MCP 通用配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/profile", response_model=MCPProfileResponse, summary="创建/更新 MCP 通用配置")
async def create_or_update_mcp_profile(profile_data: MCPProfileCreate):
    """
    创建或更新 MCP 通用配置
    """
    logger.info(f"创建/更新 MCP 通用配置: timeout={profile_data.timeout}, working_dir={profile_data.working_dir}")
    try:
        profile_id = create_mcp_profile(
            timeout=profile_data.timeout,
            working_dir=profile_data.working_dir,
            env_vars=profile_data.env_vars,
        )
        
        profile = get_mcp_profile()
        logger.info(f"成功创建/更新 MCP 通用配置，ID: {profile_id}")
        return MCPProfileResponse(
            timeout=profile["timeout"],
            working_dir=profile["working_dir"],
            env_vars=profile["env_vars"],
            update_time=profile["update_time"]
        )
    
    except Exception as e:
        logger.error(f"创建/更新 MCP 通用配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.put("/profile", response_model=MCPProfileResponse, summary="更新 MCP 通用配置")
async def update_mcp_profile_endpoint(profile_data: MCPProfileCreate):
    """
    更新 MCP 通用配置
    """
    logger.info(f"更新 MCP 通用配置: timeout={profile_data.timeout}, working_dir={profile_data.working_dir}")
    try:
        profile_id = update_mcp_profile(
            timeout=profile_data.timeout,
            working_dir=profile_data.working_dir,
            env_vars=profile_data.env_vars,
        )
        
        profile = get_mcp_profile()
        logger.info(f"成功更新 MCP 通用配置，ID: {profile_id}")
        return MCPProfileResponse(
            timeout=profile["timeout"],
            working_dir=profile["working_dir"],
            env_vars=profile["env_vars"],
            update_time=profile["update_time"]
        )
    
    except Exception as e:
        logger.error(f"更新 MCP 通用配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/profile/reset", response_model=MCPProfileStatusResponse, summary="重置 MCP 通用配置")
async def reset_mcp_profile_endpoint():
    """
    重置 MCP 通用配置为默认值
    """
    logger.info("重置 MCP 通用配置为默认值")
    try:
        success = reset_mcp_profile()
        if success:
            logger.info("成功重置 MCP 通用配置")
            return MCPProfileStatusResponse(
                success=True,
                message="MCP 通用配置已重置为默认值"
            )
        else:
            logger.error("重置 MCP 通用配置失败")
            return MCPProfileStatusResponse(
                success=False,
                message="重置 MCP 通用配置失败"
            )
    
    except Exception as e:
        logger.error(f"重置 MCP 通用配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.delete("/profile", response_model=MCPProfileStatusResponse, summary="删除 MCP 通用配置")
async def delete_mcp_profile_endpoint():
    """
    删除 MCP 通用配置
    """
    logger.info("删除 MCP 通用配置")
    try:
        success = delete_mcp_profile()
        if success:
            logger.info("成功删除 MCP 通用配置")
            return MCPProfileStatusResponse(
                success=True,
                message="MCP 通用配置已删除"
            )
        else:
            logger.error("删除 MCP 通用配置失败")
            return MCPProfileStatusResponse(
                success=False,
                message="删除 MCP 通用配置失败"
            )
    
    except Exception as e:
        logger.error(f"删除 MCP 通用配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def model_to_response(model) -> MCPConnectionResponse:
    """将数据库模型转换为响应对象"""
    return MCPConnectionResponse(
        id=model.id,
        server_name=model.server_name,
        args=model.args,
        env=model.env,
        cwd=model.cwd,
        transport=model.transport,
        timeout=model.timeout,
        enabled=model.enabled,
        description=model.description,
        config=model.config,
        create_time=model.create_time.isoformat() if model.create_time else None,
        update_time=model.update_time.isoformat() if model.update_time else None,
    )


@mcp_router.post("/", response_model=MCPConnectionResponse, summary="创建 MCP 连接")
async def create_mcp_connection(connection_data: MCPConnectionCreate):
    """
    创建新的 MCP 连接配置
    """
    logger.info(f"创建 MCP 连接: {connection_data.server_name}")
    try:
        # 检查服务器名称是否已存在
        existing = get_mcp_connections_by_server_name(server_name=connection_data.server_name)
        if existing:
            logger.error(f"服务器名称 '{connection_data.server_name}' 已存在")
            raise HTTPException(
                status_code=400,
                detail=f"服务器名称 '{connection_data.server_name}' 已存在"
            )
        
        connection_id = add_mcp_connection(
            server_name=connection_data.server_name,
            args=connection_data.args,
            env=connection_data.env,
            cwd=connection_data.cwd,
            transport=connection_data.transport,
            timeout=connection_data.timeout,
            enabled=connection_data.enabled,
            description=connection_data.description,
            config=connection_data.config,
        )
        
        connection = get_mcp_connection_by_id(connection_id)
        logger.info(f"成功创建 MCP 连接: {connection_data.server_name}, ID: {connection_id}")
        return MCPConnectionResponse(
            id=connection["id"],
            server_name=connection["server_name"],
            args=connection["args"],
            env=connection["env"],
            cwd=connection["cwd"],
            transport=connection["transport"],
            timeout=connection["timeout"],
            enabled=connection["enabled"],
            description=connection["description"],
            config=connection["config"],
            create_time=connection["create_time"],
            update_time=connection["update_time"],
        )
    
    except Exception as e:
        logger.error(f"创建 MCP 连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.get("/", response_model=MCPConnectionListResponse, summary="获取 MCP 连接列表")
async def list_mcp_connections(
    enabled_only: bool = Query(False, description="仅返回启用的连接")
):
    """
    获取所有 MCP 连接配置列表
    """
    logger.info(f"获取 MCP 连接列表, enabled_only={enabled_only}")
    try:
        if enabled_only:
            connections = get_enabled_mcp_connections()
        else:
            connections = get_all_mcp_connections()
        
        response_connections = [MCPConnectionResponse(
            id=conn["id"],
            server_name=conn["server_name"],
            args=conn["args"],
            env=conn["env"],
            cwd=conn["cwd"],
            transport=conn["transport"],
            timeout=conn["timeout"],
            enabled=conn["enabled"],
            description=conn["description"],
            config=conn["config"],
            create_time=conn["create_time"],
            update_time=conn["update_time"],
        ) for conn in connections]
        logger.info(f"成功获取 MCP 连接列表，共 {len(response_connections)} 个连接")
        return MCPConnectionListResponse(
            connections=response_connections,
            total=len(response_connections)
        )
    
    except Exception as e:
        logger.error(f"获取 MCP 连接列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.get("/{connection_id}", response_model=MCPConnectionResponse, summary="获取 MCP 连接详情")
async def get_mcp_connection(connection_id: str):
    """
    根据 ID 获取 MCP 连接配置详情
    """
    logger.info(f"获取 MCP 连接详情: {connection_id}")
    try:
        connection = get_mcp_connection_by_id(connection_id)
        if not connection:
            logger.error(f"连接 ID '{connection_id}' 不存在")
            raise HTTPException(
                status_code=404,
                detail=f"连接 ID '{connection_id}' 不存在"
            )
        
        logger.info(f"成功获取 MCP 连接详情: {connection_id}")
        return model_to_response(connection)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取 MCP 连接详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.put("/{connection_id}", response_model=MCPConnectionStatusResponse, summary="更新 MCP 连接")
async def update_mcp_connection_by_id(
    connection_id: str, 
    update_data: MCPConnectionUpdate
):
    """
    更新 MCP 连接配置
    """
    logger.info(f"更新 MCP 连接: {connection_id}")
    try:
        # 检查连接是否存在
        existing = get_mcp_connection_by_id(connection_id)
        if not existing:
            logger.error(f"连接 ID '{connection_id}' 不存在")
         
            return MCPConnectionStatusResponse(
                    connection_id=connection_id,
                    success=False,
                    message=f"连接 ID '{connection_id}' 不存在"
            )   
        
        
        # 如果更新名称，检查是否与其他连接冲突
        if update_data.server_name and update_data.server_name != existing.server_name:
            name_existing = get_connections_by_server_name(server_name=update_data.server_name)
            if name_existing:
                logger.error(f"服务器名称 '{update_data.server_name}' 已存在")
                return MCPConnectionStatusResponse(
                    connection_id=connection_id,
                    success=False,
                    message=f"服务器名称 '{update_data.server_name}' 已存在"
                )   
        
        updated_id = update_mcp_connection(
            connection_id=connection_id,
            server_name=update_data.server_name,
            args=update_data.args,
            env=update_data.env,
            cwd=update_data.cwd,
            transport=update_data.transport,
            timeout=update_data.timeout,
            enabled=update_data.enabled,
            description=update_data.description,
            config=update_data.config,
        )
        
        if updated_id:
            connection = get_mcp_connection_by_id(connection_id)
            logger.info(f"成功更新 MCP 连接: {connection_id}")
            return MCPConnectionStatusResponse(
                connection_id=connection["id"],
                success=True,
                message="成功更新",
            )
        else:
            logger.error("更新 MCP 连接失败")
            return MCPConnectionStatusResponse(
                connection_id=connection_id,
                success=False,
                message=f"更新 MCP 连接失败",
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新 MCP 连接失败: {str(e)}")
        return MCPConnectionStatusResponse(
                connection_id=connection_id,
                success=False,
                message=f"更新 MCP 连接失败: {str(e)}",
        )


@mcp_router.delete("/{connection_id}", response_model=MCPConnectionStatusResponse, summary="删除 MCP 连接")
async def delete_mcp_connection_by_id(connection_id: str):
    """
    删除 MCP 连接配置
    """
    logger.info(f"删除 MCP 连接: {connection_id}")
    try:
        # 检查连接是否存在
        existing = get_mcp_connection_by_id(connection_id)
        if not existing:
            logger.error(f"连接 ID '{connection_id}' 不存在")
            raise HTTPException(
                status_code=404,
                detail=f"连接 ID '{connection_id}' 不存在"
            )
        
        success = delete_mcp_connection(connection_id)
        if success:
            logger.info(f"成功删除 MCP 连接: {connection_id}")
            return MCPConnectionStatusResponse(
                success=True,
                message="连接删除成功",
                connection_id=connection_id
            )
        else:
            logger.error(f"删除 MCP 连接失败: {connection_id}")
            return MCPConnectionStatusResponse(
                success=False,
                message="连接删除失败",
                connection_id=connection_id
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除 MCP 连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/{connection_id}/enable", response_model=MCPConnectionStatusResponse, summary="启用 MCP 连接")
async def enable_mcp_connection_endpoint(connection_id: str):
    """
    启用指定的 MCP 连接
    """
    logger.info(f"启用 MCP 连接: {connection_id}")
    try:
        # 检查连接是否存在
        existing = get_mcp_connection_by_id(connection_id)
        if not existing:
            logger.error(f"连接 ID '{connection_id}' 不存在")
            raise HTTPException(
                status_code=404,
                detail=f"连接 ID '{connection_id}' 不存在"
            )
        
        success = enable_mcp_connection(connection_id)
        if success:
            logger.info(f"成功启用 MCP 连接: {connection_id}")
            return MCPConnectionStatusResponse(
                success=True,
                message="连接启用成功",
                connection_id=connection_id
            )
        else:
            logger.error(f"启用 MCP 连接失败: {connection_id}")
            return MCPConnectionStatusResponse(
                success=False,
                message="连接启用失败",
                connection_id=connection_id
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启用 MCP 连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/{connection_id}/disable", response_model=MCPConnectionStatusResponse, summary="禁用 MCP 连接")
async def disable_mcp_connection_endpoint(connection_id: str):
    """
    禁用指定的 MCP 连接
    """
    logger.info(f"禁用 MCP 连接: {connection_id}")
    try:
        # 检查连接是否存在
        existing = get_mcp_connection_by_id(connection_id)
        if not existing:
            logger.error(f"连接 ID '{connection_id}' 不存在")
            raise HTTPException(
                status_code=404,
                detail=f"连接 ID '{connection_id}' 不存在"
            )
        
        success = disable_mcp_connection(connection_id)
        if success:
            logger.info(f"成功禁用 MCP 连接: {connection_id}")
            return MCPConnectionStatusResponse(
                success=True,
                message="连接禁用成功",
                connection_id=connection_id
            )
        else:
            logger.error(f"禁用 MCP 连接失败: {connection_id}")
            return MCPConnectionStatusResponse(
                success=False,
                message="连接禁用失败",
                connection_id=connection_id
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"禁用 MCP 连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))




@mcp_router.post("/search", response_model=MCPConnectionListResponse, summary="搜索 MCP 连接")
async def search_mcp_connections_endpoint(search_request: MCPConnectionSearchRequest):
    """
    根据条件搜索 MCP 连接配置
    """
    logger.info(f"搜索 MCP 连接: keyword={search_request.keyword}, transport={search_request.transport}, enabled={search_request.enabled}, limit={search_request.limit}")
    try:
        connections = search_mcp_connections(
            keyword=search_request.keyword,
            transport=search_request.transport,
            enabled=search_request.enabled,
            limit=search_request.limit,
        )
        
        response_connections = [MCPConnectionResponse(
            id=conn["id"],
            server_name=conn["server_name"],
            args=conn["args"],
            env=conn["env"],
            cwd=conn["cwd"],
            transport=conn["transport"],
            timeout=conn["timeout"],
            enabled=conn["enabled"],
            description=conn["description"],
            config=conn["config"],
            create_time=conn["create_time"],
            update_time=conn["update_time"],
        ) for conn in connections]
        logger.info(f"成功搜索 MCP 连接，找到 {len(response_connections)} 个连接")
        return MCPConnectionListResponse(
            connections=response_connections,
            total=len(response_connections)
        )
    
    except Exception as e:
        logger.error(f"搜索 MCP 连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.get("/server/{server_name}", response_model=MCPConnectionListResponse, summary="根据服务器名称获取连接")
async def get_connections_by_server_name(server_name: str):
    """
    根据服务器名称获取 MCP 连接配置列表
    """
    logger.info(f"根据服务器名称获取 MCP 连接: {server_name}")
    try:
        connections = get_mcp_connections_by_server_name(server_name)
        
        response_connections = [MCPConnectionResponse(
            id=conn["id"],
            server_name=conn["server_name"],
            args=conn["args"],
            env=conn["env"],
            cwd=conn["cwd"],
            transport=conn["transport"],
            timeout=conn["timeout"],
            enabled=conn["enabled"],
            description=conn["description"],
            config=conn["config"],
            create_time=conn["create_time"],
            update_time=conn["update_time"],
        ) for conn in connections]
        logger.info(f"成功根据服务器名称获取 MCP 连接，找到 {len(response_connections)} 个连接")
        return MCPConnectionListResponse(
            connections=response_connections,
            total=len(response_connections)
        )
    
    except Exception as e:
        logger.error(f"根据服务器名称获取 MCP 连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.get("/enabled/list", response_model=MCPConnectionListResponse, summary="获取启用的 MCP 连接")
async def list_enabled_mcp_connections():
    """
    获取所有启用的 MCP 连接配置
    """
    logger.info("获取启用的 MCP 连接列表")
    try:
        connections = get_enabled_mcp_connections()
        
        response_connections = [MCPConnectionResponse(
            id=conn["id"],
            server_name=conn["server_name"],
            args=conn["args"],
            env=conn["env"],
            cwd=conn["cwd"],
            transport=conn["transport"],
            timeout=conn["timeout"],
            enabled=conn["enabled"],
            description=conn["description"],
            config=conn["config"],
            create_time=conn["create_time"],
            update_time=conn["update_time"],
        ) for conn in connections]
        logger.info(f"成功获取启用的 MCP 连接列表，共 {len(response_connections)} 个连接")
        return MCPConnectionListResponse(
            connections=response_connections,
            total=len(response_connections)
        )
    
    except Exception as e:
        logger.error(f"获取启用的 MCP 连接列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))




# MCP Profile 相关路由已移至文件开头以避免路由冲突