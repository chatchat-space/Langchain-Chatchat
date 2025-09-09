import streamlit as st
import streamlit_antd_components as sac
from chatchat.webui_pages.utils import *
from chatchat.settings import Settings
import requests
import json



def mcp_management_page(api: ApiRequest, is_lite: bool = False):
    """
    MCP管理页面 - 连接器设置界面
    采用超感官极简主义×液态数字形态主义设计风格
    使用Streamlit语法实现
    """
    
    # 初始化会话状态
    if 'mcp_profile_loaded' not in st.session_state:
        st.session_state.mcp_profile_loaded = False
    if 'mcp_connections_loaded' not in st.session_state:
        st.session_state.mcp_connections_loaded = False
    if 'mcp_connections' not in st.session_state:
        st.session_state.mcp_connections = []
    if 'mcp_profile' not in st.session_state:
        st.session_state.mcp_profile = {}
        
    if "show_add_conn" not in st.session_state:
        st.session_state.show_add_conn = False

    # 页面CSS样式
    st.markdown("""
        <style>
            /* CSS变量定义 */
            :root {
                --accent-primary: linear-gradient(135deg, #4F46E5 0%, #818CF8 100%);
                --accent-warning: linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%);
                --bg-nav: #F9FAFB;
                --bg-card: #FFFFFF;
                --text-primary: #111827;
                --text-secondary: #6B7280;
                --border-light: #E5E7EB;
                --shadow-hover: 0 8px 24px rgba(79, 70, 229, 0.1);
            }
            
            /* 全局样式重置 */
            .stApp {
                background-color: #FAFAFA !important;
            }
            
            /* 隐藏Streamlit默认元素 */
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display: none;}
            
            /* 导航栏样式 */
            .nav-container {
                background: var(--bg-nav);
                border-right: 1px solid var(--border-light);
                padding: 16px 8px;
                border-radius: 12px;
                margin-bottom: 24px;
            }
            
            .nav-item {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 12px 16px;
                margin: 4px 0;
                color: var(--text-secondary);
                text-decoration: none;
                border-radius: 8px;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            
            .nav-item:hover {
                background: rgba(0, 0, 0, 0.05);
            }
            
            .nav-item.active {
                background: var(--bg-card);
                color: var(--text-primary);
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                border-left: 3px solid #4F46E5;
            }
            
            /* 连接器卡片样式 */
            .connector-card {
                background: var(--bg-card);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 16px;
                border: 1px solid var(--border-light);
                transition: all 0.3s ease;
                cursor: pointer;
            }
            
            .connector-card:hover {
                border-color: rgba(79, 70, 229, 0.2);
                box-shadow: var(--shadow-hover);
                transform: translateY(-2px);
            }
            
            .connector-card.warning {
                border-color: rgba(245, 158, 11, 0.2);
            }
            
            .connector-content {
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .connector-left {
                display: flex;
                align-items: center;
                gap: 16px;
            }
            
            .connector-icon {
                width: 48px;
                height: 48px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                font-size: 20px;
                color: white;
                flex-shrink: 0;
            }
            
            .connector-info h3 {
                margin: 0 0 4px 0;
                font-size: 16px;
                font-weight: 600;
                color: var(--text-primary);
            }
            
            .connector-info p {
                margin: 0;
                font-size: 12px;
                color: var(--text-secondary);
            }
            
            .status-indicator {
                display: flex;
                align-items: center;
                gap: 6px;
                margin-top: 8px;
            }
            
            .status-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: var(--accent-warning);
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            /* 浏览连接器卡片样式 */
            .browse-card {
                background: var(--bg-card);
                border-radius: 12px;
                padding: 24px;
                border: 1px solid var(--border-light);
                text-align: center;
                transition: all 0.3s ease;
                cursor: pointer;
                height: 100%;
            }
            
            .browse-card:hover {
                border-color: rgba(79, 70, 229, 0.3);
                box-shadow: var(--shadow-hover);
                transform: scale(1.03);
            }
            
            .browse-icon {
                width: 56px;
                height: 56px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 12px;
                transition: transform 0.5s ease;
            }
            
            .browse-card:hover .browse-icon {
                transform: scale(1.1);
            }
            
            .browse-card h3 {
                margin: 0;
                font-size: 14px;
                font-weight: 500;
                color: var(--text-primary);
            }
            
            /* 页面标题样式 */
            .page-title {
                font-size: 24px;
                font-weight: 600;
                color: var(--text-primary);
                margin-bottom: 32px;
            }
            
            /* Section标题样式 */
            .section-title {
                font-size: 18px;
                font-weight: 600;
                color: var(--text-primary);
                margin: 32px 0 16px 0;
            }
            
            /* 响应式设计 */
            @media (max-width: 768px) {
                .connector-content {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 12px;
                }
            }
        </style>
    """, unsafe_allow_html=True)
    
    # 页面布局
    with st.container():
        # 页面标题
        st.markdown('<h1 class="page-title">连接器管理</h1>', unsafe_allow_html=True)
        
        # 通用设置部分
        with st.expander("⚙️ 通用设置", expanded=False): 
            
            # 加载当前配置
            if not st.session_state.mcp_profile_loaded:
                try:
                    profile_data = api.get_mcp_profile()
                    if profile_data:
                        st.session_state.mcp_profile = profile_data
                        # 初始化环境变量列表
                        env_vars = st.session_state.mcp_profile.get("env_vars", {})
                        st.session_state.env_vars_list = [
                            {"key": k, "value": v} for k, v in env_vars.items()
                        ]
                        st.session_state.mcp_profile_loaded = True
                    else:
                        # 使用默认值
                        st.session_state.mcp_profile = {
                            "timeout": 30,
                            "working_dir": str(Settings.CHATCHAT_ROOT),
                            "env_vars": {
                                "PATH": "/usr/local/bin:/usr/bin:/bin",
                                "PYTHONPATH": "/app",
                                "HOME": str(Settings.CHATCHAT_ROOT)
                            }
                        }
                        st.session_state.env_vars_list = [
                            {"key": "PATH", "value": "/usr/local/bin:/usr/bin:/bin"},
                            {"key": "PYTHONPATH", "value": "/app"},
                            {"key": "HOME", "value": str(Settings.CHATCHAT_ROOT)}
                        ]
                except Exception as e:
                    st.error(f"加载配置失败: {str(e)}")
                    return
            
            # 默认超时时间设置
            timeout_value = st.slider(
                "默认连接超时时间（秒）",
                min_value=10,
                max_value=300,
                value=st.session_state.mcp_profile.get("timeout", 30),
                step=5,
                help="设置MCP连接器的默认超时时间，范围：10-300秒"
            )
            
            # 工作目录设置
            working_dir = st.text_input(
                "默认工作目录",
                value=st.session_state.mcp_profile.get("working_dir", str(Settings.CHATCHAT_ROOT)),
                help="设置MCP连接器的默认工作目录"
            )
            # 环境变量设置
            st.subheader("环境变量配置")
            
            # 环境变量键值对编辑
            st.write("添加环境变量键值对：")
            
            # 初始化环境变量列表
            if 'env_vars_list' not in st.session_state:
                st.session_state.env_vars_list = [
                    {"key": "PATH", "value": "/usr/local/bin:/usr/bin:/bin"},
                    {"key": "PYTHONPATH", "value": "/app"},
                    {"key": "HOME", "value": str(Settings.CHATCHAT_ROOT)}
                ]
            
            # 显示现有环境变量
            for i, env_var in enumerate(st.session_state.env_vars_list):
                col1, col2, col3 = st.columns([2, 3, 1])
                
                with col1:
                    key = st.text_input(
                        "变量名",
                        value=env_var["key"],
                        key=f"env_key_{i}",
                        placeholder="例如：PATH"
                    )
                    env_var["key"] = key
                with col2:
                    value = st.text_input(
                        "变量值",
                        value=env_var["value"],
                        key=f"env_value_{i}",
                        placeholder="例如：/usr/bin"
                    )
                
                    env_var["value"] = value
                with col3:
                    if st.button("🗑️", key=f"env_delete_{i}", help="删除此环境变量"):
                        st.session_state.env_vars_list.pop(i)
                        # 删除后立即保存到数据库
                        try:
                            env_vars_dict = {}
                            for env_var in st.session_state.env_vars_list:
                                if env_var["key"] and env_var["value"]:
                                    env_vars_dict[env_var["key"]] = env_var["value"]
                            
                            result = api.update_mcp_profile(
                                timeout=timeout_value,
                                working_dir=working_dir,
                                env_vars=env_vars_dict
                            )
                             
                            # 更新值
                            if key != env_var["key"] or value != env_var["value"]:
                                st.session_state.env_vars_list[i] = {"key": key, "value": value}
                        except Exception as e:
                            st.error(f"删除失败: {str(e)}")
                        st.rerun()
                
            # 添加新环境变量按钮
            if st.button("➕ 添加环境变量", key="add_env_var"):
                st.session_state.env_vars_list.append({"key": "", "value": ""})
                st.rerun()
            
            # 显示当前环境变量预览
            if st.session_state.env_vars_list:
                st.markdown("### 当前环境变量")
                env_preview = {}
                for env_var in st.session_state.env_vars_list:
                    if env_var["key"] and env_var["value"]:
                        env_preview[env_var["key"]] = env_var["value"]
                
                st.code(
                    "\n".join([f'{k}="{v}"' for k, v in env_preview.items()]),
                    language="bash",
                    line_numbers=False
                )
            else:
                st.info("暂无配置的环境变量")
            
            
            # 保存设置按钮
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if st.button("💾 保存设置", type="primary", use_container_width=True):
                    try:
                        # 构建环境变量字典
                        env_vars_dict = {}
                        for env_var in st.session_state.env_vars_list:
                            if env_var["key"] and env_var["value"]:
                                env_vars_dict[env_var["key"]] = env_var["value"]
                        
                        # 保存到数据库
                        result = api.update_mcp_profile(
                            timeout=timeout_value,
                            working_dir=working_dir,
                            env_vars=env_vars_dict
                        )
                        
                        if result:
                            st.success("通用设置已保存")
                            st.session_state.mcp_profile['timeout'] = timeout_value
                            st.session_state.mcp_profile['working_dir'] = working_dir
                            st.session_state.mcp_profile_loaded = False  # 重新加载
                        else:
                            st.error("保存失败，请检查配置")
                    except Exception as e:
                        st.error(f"保存失败: {str(e)}")
            
            with col2:
                if st.button("🔄 重置默认", use_container_width=True):
                    try:
                        result = api.reset_mcp_profile()
                        if result and result.get("success"):
                            # 重置UI状态
                            st.session_state.env_vars_list = [
                                {"key": "PATH", "value": "/usr/local/bin:/usr/bin:/bin"},
                                {"key": "PYTHONPATH", "value": "/app"},
                                {"key": "HOME", "value": str(Settings.CHATCHAT_ROOT)}
                            ]
                            st.session_state.mcp_profile_loaded = False
                            st.rerun()
                        else:
                            st.error("重置失败")
                    except Exception as e:
                        st.error(f"重置失败: {str(e)}")
             
        
        # 连接器导航
        st.markdown('<h2 class="section-title">🔗 连接器管理</h2>', unsafe_allow_html=True)
        
        # 加载MCP连接数据
        if not st.session_state.mcp_connections_loaded:
            try:
                connections_data = api.get_all_mcp_connections()
                if connections_data:
                    st.session_state.mcp_connections = connections_data.get("connections", [])
                    st.session_state.mcp_connections_loaded = True
                else:
                    st.session_state.mcp_connections = []
            except Exception as e:
                st.error(f"加载连接器失败: {str(e)}")
                return
        
        # 已启用连接器部分
        st.markdown('<h2 class="section-title">已启用连接器</h2>', unsafe_allow_html=True)
        
        # 显示已启用的连接器
        enabled_connections = [conn for conn in st.session_state.mcp_connections if conn.get("enabled", False)]
        
        if enabled_connections:
            for connection in enabled_connections:
                # 生成连接器图标颜色
                icon_colors = {
                    "stdio": "#111827",
                    "sse": "linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%)"
                }
                
                # 获取传输类型作为图标标识
                transport = connection.get("transport", "stdio").lower()
                icon_letter = "S" if transport == "stdio" else "E"
                icon_bg = icon_colors.get("stdio", "linear-gradient(135deg, #4F46E5 0%, #818CF8 100%)") if transport == "stdio" else icon_colors.get("sse", "linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%)")
                
                # 连接器卡片
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"""
                            <div class="connector-card">
                                <div class="connector-content">
                                    <div class="connector-left">
                                        <div class="connector-icon" style="background: {icon_bg};">
                                            <span>{icon_letter}</span>
                                        </div>
                                        <div class="connector-info">
                                            <h3>{connection.get('server_name', '')}</h3>
                                            <p>{json.dumps(connection.get('config', {}), ensure_ascii=False, indent=2)}</p>
                                            <div class="status-indicator">
                                                <div class="status-dot" style="background: #6B7280;"></div>
                                                <span style="color: #6B7280; font-size: 12px; font-weight: 500;">连接</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("🔄 禁用", key=f"toggle_disable_{connection.get('id', i)}", use_container_width=True):
                            toggle_connection_status(api, connection.get('id', i), False)
        else:
            st.info("暂无已启用的连接器")
        
        # 浏览连接器部分
        st.markdown('<h2 class="section-title">浏览连接器</h2>', unsafe_allow_html=True)
        
        # 显示所有连接器（包括未启用的）
        disabled_connections = [conn for conn in st.session_state.mcp_connections if not conn.get("enabled", True)]
        
        if disabled_connections:
            # 连接器网格
            cols = st.columns(3)
            
            for i, connection in enumerate(disabled_connections):
                with cols[i % 3]:
                    # 生成连接器图标
                    icon_emojis = {
                        "stdio": "💻",
                        "sse": "🌐"
                    }
                    
                    transport = connection.get("transport", "stdio").lower()
                    icon_emoji = icon_emojis.get(transport, "🔗")
                    
                    # 连接器卡片
                    st.markdown(f"""
                        <div class="browse-card">
                            <div class="browse-icon" style="background: rgba(107, 114, 128, 0.1);">
                                <span style="color: #6B7280; font-size: 24px;">{icon_emoji}</span>
                            </div>
                            <h3>{connection.get('server_name', '')}</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("🔄 启用", key=f"toggle_enable_{connection.get('id', i)}", use_container_width=True):
                        toggle_connection_status(api, connection.get('id', i), True)
        else:
            st.info("暂无其他连接器")
    
    # 添加一些交互功能
    st.divider()
    
    # 连接器操作区域
    st.subheader("连接器操作")
      
    # 点击后仅修改状态，立刻重跑
    if st.button("➕ 添加新连接器", type="primary"):
        st.session_state.show_add_conn = True
        st.rerun()

    # 用一个占位容器承载“弹窗内容”
    placeholder = st.empty()
    if st.session_state.show_add_conn:
        with placeholder.container():
            add_new_connection_form(api)     # 表单本体 
    # 添加一些说明信息
    st.divider()
    
    with st.expander("📖 使用说明", expanded=False):
        st.markdown("""
        ### 连接器管理
        
        **已启用连接器**：显示当前已配置并启用的连接器，支持直接点击进入详细设置。
        
        **浏览连接器**：展示可用的连接器类型，点击可快速添加和配置。
        
        **状态指示**：
        - ✅ 正常运行
        - ⚠️ 设置未完成或配置错误
        - ❌ 连接失败
        
        **支持的连接器类型**：
        - 文档协作：Canva, Notion
        - 代码托管：GitHub
        - 沟通工具：Gmail, Slack
        - 云存储：Box, Google Drive
        - 社交媒体：Twitter
        """)
    
    # 页脚信息
    st.markdown("---")
    st.caption("💡 提示：连接器需要正确的API权限和网络访问才能正常工作")


def add_new_connection_form(api: "ApiRequest"):
    """
    添加新连接器的弹窗表单（修正版）
    - 统一使用 st.form 保证一次性提交
    - 健壮的 Session State 初始化
    - 根据 transport 显示不同必填项
    """
    import streamlit as st

    # ---- State 初始化 ----
    if "connection_args" not in st.session_state:
        st.session_state.connection_args = []
    if "connection_env_vars" not in st.session_state:
        # 形如 [{"key":"FOO","value":"bar"}]
        st.session_state.connection_env_vars = st.session_state.env_vars_list or []

    st.subheader("新连接器配置")

    with st.form("new_mcp_connection"):
        # ===== 基本信息 =====
        col1, col2 = st.columns(2)
        with col1:
            server_name = st.text_input(
                "服务器名称 *",
                placeholder="例如：my-server",
                help="服务器的唯一标识符",
                key="conn_server_name",
            )
        with col2:
            transport = st.selectbox(
                "传输方式 *",
                options=["sse", "stdio"],
                help="连接传输协议",
                key="conn_transport",
            )

        # ===== 启动命令 / SSE 配置 =====
        st.subheader("传输配置")
        # 统一给 command 一个默认值，避免未定义
        command = ""

        if transport == "stdio":
            command = st.text_input(
                "启动命令 *",
                placeholder="例如：python -m mcp_server",
                help="启动 MCP 服务器的命令",
                key="conn_command",
            )
            
            # Stdio 特定配置
            st.subheader("Stdio 传输配置")
            encoding = st.selectbox(
                "文本编码",
                options=["utf-8", "gbk", "ascii", "latin-1"],
                index=0,
                help="文本编码格式",
                key="conn_encoding",
            )
            
            encoding_error_handler = st.selectbox(
                "编码错误处理",
                options=["strict", "ignore", "replace"],
                index=0,
                help="编码错误处理方式",
                key="conn_encoding_error_handler",
            )
        else:
            # SSE 模式下通常需要 URL；字段名按你的后端需要调整
            sse_url = st.text_input(
                "SSE 服务器地址 *",
                placeholder="例如：https://example.com/mcp/sse",
                help="SSE 服务器的 URL",
                key="conn_sse_url",
            )
            
            # SSE 特定配置
            st.subheader("SSE 传输配置")
            
            # 可选：SSE 额外 header
            sse_headers = st.text_area(
                "SSE Headers（可选，JSON）",
                placeholder='例如：{"Authorization":"Bearer xxx"}',
                help="以 JSON 形式填写可选的请求头",
                key="conn_sse_headers",
            )
            
            col_ti1, col_ti2 = st.columns(2)
            with col_ti1:
                
                sse_encoding_error_handler = st.selectbox(
                    "编码错误处理",
                    options=["strict", "ignore", "replace"],
                    index=0,
                    help="编码错误处理方式",
                    key="conn_sse_encoding_error_handler",
                )

            with col_ti2:
                
                # SSE 编码配置
                sse_encoding = st.selectbox(
                    "文本编码",
                    options=["utf-8", "gbk", "ascii", "latin-1"],
                    index=0,
                    help="文本编码格式",
                    key="conn_sse_encoding",
                )
            
        # ===== 命令参数（可选） =====
        st.write("命令参数（可选）：")
        # 展示已添加的参数
        for i, arg in enumerate(st.session_state.connection_args):
            col_arg, col_del = st.columns([4, 1])
            with col_arg:
                new_arg = st.text_input(
                    f"参数 {i+1}",
                    value=arg,
                    key=f"conn_arg_{i}",
                    placeholder="例如：--port=8080",
                )
                if new_arg != arg:
                    st.session_state.connection_args[i] = new_arg
            with col_del:
                # 注意：表单内的按钮也会触发表单提交，这里使用不同的 key 且仅做状态修改
                if st.form_submit_button(f"🗑️ 删除_{i}", use_container_width=True):
                    st.session_state.connection_args.pop(i)
                    st.rerun()

        # 添加参数按钮（表单内）
        if st.form_submit_button("➕ 添加参数", use_container_width=False):
            st.session_state.connection_args.append("")
            st.rerun()

        # ===== 环境变量（可选） =====
        st.write("环境变量（可选）：")
        # 展示已添加的 env
        for i, pair in enumerate(st.session_state.connection_env_vars):
            col_k, col_v, col_del = st.columns([3, 4, 1])
            with col_k:
                new_k = st.text_input(
                    f"键 {i+1}",
                    value=pair.get("key", ""),
                    key=f"env_k_{i}",
                    placeholder="例如：GITHUB_TOKEN",
                )
            with col_v:
                new_v = st.text_input(
                    f"值 {i+1}",
                    value=pair.get("value", ""),
                    key=f"env_v_{i}",
                    placeholder="例如：xxxxxx",
                    type="password",
                )
            with col_del:
                if st.form_submit_button(f"🗑️ 删ENV_{i}", use_container_width=True):
                    st.session_state.connection_env_vars.pop(i)
                    st.rerun()
            # 同步修改
            st.session_state.connection_env_vars[i] = {"key": new_k, "value": new_v}

        # 添加 ENV 按钮
        if st.form_submit_button("➕ 添加环境变量"):
            st.session_state.connection_env_vars.append({"key": "", "value": ""})
            st.rerun()

        # ===== 高级设置 =====
        with st.expander("高级设置", expanded=False):
            col_adv1, col_adv2 = st.columns(2)
            with col_adv1:
                timeout = st.number_input(
                    "连接超时（秒）",
                    min_value=10,
                    max_value=300,
                    value=st.session_state.mcp_profile.get("timeout", 30),
                    help="连接超时时间",
                    key="conn_timeout",
                )
                cwd = st.text_input(
                    "工作目录",
                    value=st.session_state.mcp_profile.get("working_dir", str(Settings.CHATCHAT_ROOT)),
                    placeholder="/tmp",
                    help="服务器运行的工作目录",
                    key="conn_cwd",
                )
            with col_adv2:
                enabled = st.checkbox(
                    "启用连接器",
                    value=False,
                    help="是否启用此连接器",
                    key="conn_enabled",
                )

        # ===== 描述信息 =====
        description = st.text_area(
            "连接器描述",
            placeholder="描述此连接器的用途和配置...",
            help="可选的连接器描述信息",
            key="conn_description",
        )

        # ===== 提交/取消 =====
        col_submit, col_cancel = st.columns([1, 1])
        with col_submit:
            submitted = st.form_submit_button("💾 创建连接器", type="primary", use_container_width=True)
        with col_cancel:
            cancel_clicked = st.form_submit_button("❌ 取消", use_container_width=True)

        # ----- 提交处理 -----
        if cancel_clicked:
            # 清理状态并刷新
            st.session_state.connection_args = []
            st.session_state.connection_env_vars = []
            st.session_state.show_add_conn = False
            st.rerun()

        if submitted:
            # 校验
            errors = []
            if not server_name:
                errors.append("服务器名称")

            if transport == "stdio":
                if not command:
                    errors.append("启动命令（stdio）")
            else:
                if not sse_url:
                    errors.append("SSE 服务器地址")

            if errors:
                st.error("请填写所有必填字段（*）：" + "、".join(errors))
                return

            # 解析 env
            env_vars_dict = {}
            for env_var in st.session_state.connection_env_vars:
                k = (env_var.get("key") or "").strip()
                v = (env_var.get("value") or "").strip()
                if k and v:
                    env_vars_dict[k] = v

            # 组装 API 参数
            payload = dict(
                server_name=server_name,
                args=st.session_state.connection_args,
                env=env_vars_dict,
                cwd=cwd or "",
                transport=transport,
                timeout=timeout,               # 传递整数
                enabled=bool(enabled),
                description=description or None,
                config={},                     # 预留
            )

            if transport == "stdio":
                # Add command to config instead of payload root
                payload["config"]["command"] = command
                # Add stdio-specific config
                payload["config"]["encoding"] = encoding
                payload["config"]["encoding_error_handler"] = encoding_error_handler
            else:
                # SSE transport - store SSE-specific fields in config
                payload["config"]["url"] = sse_url
                if sse_headers:
                    # 尽量解析为 JSON；失败则当作原文本
                    import json
                    try:
                        payload["config"]["headers"] = json.loads(sse_headers)
                    except Exception as e:
                        st.error(f"sse_headers出错：{e}")
                else:
                    payload["config"]["headers"] = None
                
                # Set encoding config for SSE
                payload["config"]["encoding"] = sse_encoding
                payload["config"]["encoding_error_handler"] = sse_encoding_error_handler

            try:
                result = api.add_mcp_connection(**payload)
                # 约定：返回 True/非空 dict 视为成功
                if result:
                    st.success("连接器创建成功！")
                    # 清理并刷新列表
                    st.session_state.connection_args = []
                    st.session_state.connection_env_vars = []
                    st.session_state.mcp_connections_loaded = False
                    st.session_state.show_add_conn = False
                    st.rerun()
                else:
                    st.error(f"创建失败：{getattr(result,'msg', None) or (result.get('msg') if isinstance(result, dict) else '未知错误')}")
            except Exception as e:
                st.error(f"创建连接器时出错：{e}")

def toggle_connection_status(api: ApiRequest, connection_id: str, enabled: bool):
    """
    切换连接器启用/禁用状态
    """
    try:
        result = api.update_mcp_connection(connection_id=connection_id, enabled=enabled)
        if result and result.get("success"):
            status = "启用" if enabled else "禁用"
            st.success(f"连接器{status}成功！")
            st.session_state.mcp_connections_loaded = False  # 重新加载连接列表
            st.rerun()
        else:
            status = "启用" if enabled else "禁用"
            st.error(f"{status}失败：{result.get('message', '未知错误')}")
    except Exception as e:
        status = "启用" if enabled else "禁用"
        st.error(f"{status}连接器时出错：{str(e)}")

def delete_connection(api: ApiRequest, connection_id: str):
    """
    删除连接器
    """
    try:
        result = api.delete_mcp_connection(connection_id=connection_id)
        if result and result.get("code") == 200:
            st.success("连接器删除成功！")
            st.session_state.mcp_connections_loaded = False  # 重新加载连接列表
            st.rerun()
        else:
            st.error(f"删除失败：{result.get('msg', '未知错误')}")
    except Exception as e:
        st.error(f"删除连接器时出错：{str(e)}")