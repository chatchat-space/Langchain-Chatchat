import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml import SafeLoader
import webui
import os
import sys
from configs import VERSION

# chage streamlit icon
#st.set_page_config(page_title='Oracle KM Authenticator', page_icon=':lock:')
#st.write(':lock: 请登录')

st.set_page_config(
    page_title = "企业智能 AI 应用",
    page_icon = os.path.join("img", "chatchat_icon_blue_square_v2.png"),
#   layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
         'Get Help': 'https://github.com/chatchat-space/Langchain-Chatchat',
         'Report a bug': "https://github.com/chatchat-space/Langchain-Chatchat/issues",
         'About': f"""欢迎使用 Langchain-Chatchat WebUI {VERSION}！"""
    }
)

# --------------------------- #
# 1. Load authenticator       #
# --------------------------- #

with open('./configs/credentials.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

#name, authentication_status, username = authenticator.login('Login', 'main')
name, authentication_status, username = authenticator.login()

# --------------------------- #
# 2. Logic Control            #
# --------------------------- #
if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'sidebar')
#   st.write(f'Welcome *{st.session_state["name"]}*')
    st.header(f'Welcome *{st.session_state["name"]}*', divider='rainbow')
    webui.main()
elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')
