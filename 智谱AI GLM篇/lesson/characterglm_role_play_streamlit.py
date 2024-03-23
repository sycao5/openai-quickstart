"""
一个简单的demo，调用CharacterGLM实现角色扮演，调用CogView生成图片，调用ChatGLM生成CogView所需的prompt。

依赖：
pyjwt
requests
streamlit
zhipuai
python-dotenv

运行方式：
```bash
streamlit run characterglm_api_demo_streamlit.py
```
"""
import os
import itertools
import joblib
import time
from typing import Iterator, Optional

import streamlit as st
from dotenv import load_dotenv

# 通过.env文件设置环境变量
# reference: https://github.com/theskumar/python-dotenv
load_dotenv()

import api
from api import generate_chat_scene_prompt, generate_role_appearance, get_characterglm_response, generate_cogview_image
from data_types import TextMsg, ImageMsg, TextMsgList, MsgList, filter_text_msg


st.set_page_config(page_title="CharacterGLM Role Play Demo", page_icon="🤖", layout="wide")
debug = os.getenv("DEBUG", "").lower() in ("1", "yes", "y", "true", "t", "on")

st.title("智谱AI机器人自动聊天对话的界面")

def update_api_key(key: Optional[str] = None):
    if debug:
        print(f'update_api_key. st.session_state["API_KEY"] = {st.session_state["API_KEY"]}, key = {key}')
    key = key or st.session_state["API_KEY"]
    if key:
        api.API_KEY = key

# 设置API KEY
api_key = st.sidebar.text_input("API_KEY", value=os.getenv("API_KEY", ""), key="API_KEY", type="password", on_change=update_api_key)
update_api_key(api_key)


# 初始化
if "history" not in st.session_state:
    st.session_state["history"] = []
    st.session_state["history"].append(TextMsg({"role": "assistant", "content":"咱们开始对话吧"}))
    new_chat_id = f'{time.time()}'
    st.session_state.chat_id = new_chat_id

if "meta" not in st.session_state:
    st.session_state["meta"] = {
        "user_info": "",
        "bot_info": "",
        "bot_name": "",
        "user_name": ""
    }

# Create a data/ folder if it doesn't already exist
try:
    os.mkdir('data/')
except:
    # data/ folder already exists
    pass

# Load past chats (if available)
try:
    past_chats: dict = joblib.load('data/past_chats_list')
except:
    past_chats = {}


def init_session():
    st.session_state["history"] = []
    st.session_state["history"].append(TextMsg({"role": "assistant", "content":"咱们开始对话吧"}))


# 4个输入框，设置meta的4个字段
meta_labels = {
    "bot_name": "角色名",
    "user_name": "用户名", 
    "bot_info": "角色人设",
    "user_info": "用户人设"
}

# 2x2 layout
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.text_input(label="角色名", key="bot_name", on_change=lambda : st.session_state["meta"].update(bot_name=st.session_state["bot_name"]), help="模型所扮演的角色的名字，不可以为空")
        st.text_area(label="角色人设", key="bot_info", on_change=lambda : st.session_state["meta"].update(bot_info=st.session_state["bot_info"]), help="角色的详细人设信息，不可以为空")
        
    with col2:
        st.text_input(label="用户名", value="用户", key="user_name", on_change=lambda : st.session_state["meta"].update(user_name=st.session_state["user_name"]), help="用户的名字，默认为用户")
        st.text_area(label="用户人设", value="", key="user_info", on_change=lambda : st.session_state["meta"].update(user_info=st.session_state["user_info"]), help="用户的详细人设信息，可以为空")


def verify_meta() -> bool:
    # 检查`角色名`和`角色人设`是否空，若为空，则弹出提醒
    if st.session_state["meta"]["bot_name"] == "" or st.session_state["meta"]["bot_info"] == "":
        st.error("角色名和角色人设不能为空")
        return False
    else:
        return True


def save_history_to_file():
    joblib.dump(
        st.session_state["history"],
        f'data/{st.session_state.chat_id}-st_messages.txt'
    )
            

with st.chat_message(name="user", avatar="user"):
    input_placeholder = st.empty()
with st.chat_message(name="assistant", avatar="assistant"):
    message_placeholder = st.empty()


def output_stream_response(response_stream: Iterator[str], placeholder):
    content = ""
    for content in itertools.accumulate(response_stream):
        placeholder.markdown(content)
    return content


button_labels = {
    "gen_role_play": "生成人设",
    "user_send": "角色发送对话",
    "bot_send": "用户发送对话",
    "save_history": "保存对话到磁盘文件",
    "clear_meta": "清空人设",
    "clear_history": "清空对话历史"
}

if debug:
    button_labels.update({
        "show_api_key": "查看API_KEY",
        "show_meta": "查看meta",
        "show_history": "查看历史"
    })

# 在同一行排列按钮
with st.container():
    n_button = len(button_labels)
    cols = st.columns(n_button)
    button_key_to_col = dict(zip(button_labels.keys(), cols))
    
    with button_key_to_col["clear_meta"]:
        clear_meta = st.button(button_labels["clear_meta"], key="clear_meta")
        if clear_meta:
            st.session_state["meta"] = {
                "user_info": "",
                "bot_info": "",
                "bot_name": "",
                "user_name": ""
            }
            st.rerun()

    with button_key_to_col["clear_history"]:
        clear_history = st.button(button_labels["clear_history"], key="clear_history")
        if clear_history:
            init_session()
            st.rerun()         

    with button_key_to_col["user_send"]:
        user_send = st.button(button_labels["user_send"], key="user_send")
        if user_send: 
            response_stream_user = get_characterglm_response(filter_text_msg(st.session_state["history"]), meta=st.session_state["meta"])
            bot_response_user = output_stream_response(response_stream_user, input_placeholder)

            st.session_state["history"].append(TextMsg({"role": "user", "content": bot_response_user}))

    with button_key_to_col["bot_send"]:
        bot_send = st.button(button_labels["bot_send"], key="bot_send")
        if bot_send:
            response_stream = get_characterglm_response(filter_text_msg(st.session_state["history"]), meta=st.session_state["meta"])
            bot_response = output_stream_response(response_stream,  message_placeholder)
        
            if not bot_response:
                message_placeholder.markdown("生成出错")
                st.session_state["history"].pop()
            else:
                st.session_state["history"].append(TextMsg({"role": "assistant", "content": bot_response}))

    with button_key_to_col["save_history"]:
        save_history = st.button(button_labels["save_history"], key="save_history")
        if save_history:
            save_history_to_file()
    
    with button_key_to_col["gen_role_play"]:
        gen_role_play = st.button(button_labels["gen_role_play"], key="gen_role_play")

    if debug:
        with button_key_to_col["show_api_key"]:
            show_api_key = st.button(button_labels["show_api_key"], key="show_api_key")
            if show_api_key:
                print(f"API_KEY = {api.API_KEY}")
        
        with button_key_to_col["show_meta"]:
            show_meta = st.button(button_labels["show_meta"], key="show_meta")
            if show_meta:
                print(f"meta = {st.session_state['meta']}")
        
        with button_key_to_col["show_history"]:
            show_history = st.button(button_labels["show_history"], key="show_history")
            if show_history:
                print(f"history = {st.session_state['history']}")

if gen_role_play:
    if st.session_state['meta']['bot_info']:
        bot_role_appearance = "".join(generate_role_appearance(st.session_state['meta']['bot_info']))
        print(bot_role_appearance)
        st.session_state["history"].append(TextMsg({"role": "assistant", "content": bot_role_appearance}))
    if st.session_state['meta']['user_info']:
        user_role_appearance = "".join(generate_role_appearance(st.session_state['meta']['user_info']))
        print(user_role_appearance)
        st.session_state["history"].append(TextMsg({"role": "user", "content": user_role_appearance}))

# 展示对话历史
for msg in st.session_state["history"]:
    if msg["role"] == "user":
        with st.chat_message(name="user", avatar="user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message(name="assistant", avatar="assistant"):
            st.markdown(msg["content"])
    else:
        raise Exception("Invalid role")

