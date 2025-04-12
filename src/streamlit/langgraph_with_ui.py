from typing import Any, Dict

import streamlit as st

from src.agent.app_session_manager import SessionManager
from src.agent.app_user_input_logic import input_additional_info, display_input_chat_massage

from src.agent.app_util import stream_graph

THREAD_ID = "1"
st.set_page_config(
        page_title="アニメ嗜好ヒアリングbot",
        page_icon="🦜",
    )
st.title("アニメ嗜好ヒアリングbot")

def main():
        # チャット履歴の初期化（初回のみ）
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # チャット履歴を毎回描画（過去分をすべて表示）
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    

    # セッションの初期化
    if "initialized" not in st.session_state:
        session_manager = SessionManager()
        st.session_state.session_manager = session_manager
        st.session_state.agent = session_manager.get_agent()
        st.session_state.thread = {"configurable": {"thread_id": THREAD_ID}}
        st.session_state.initial_input = {}
        st.session_state.await_user = False
        st.session_state.user_input_done = False
        st.session_state.initialized = True

    agent = st.session_state.agent
    thread = st.session_state.thread

    print("hoge")
    

    # スタートノードなら最初に実行
    if agent.is_start_node(thread):
        stream_graph(agent, st.session_state.initial_input, thread, st.session_state.session_manager)

    # ユーザー入力が必要なノードに来た場合
    next_graph = agent.get_next_node(thread)

    agent_reply = agent.get_state_value(thread, "agent_reply")
    


    if next_graph:
        node_name = next_graph[0]

        if node_name == "user_action":
            print("$$$ input $$$")
            st.session_state.await_user = True
            display_input_chat_massage(agent, thread, as_node=node_name)

            # ここで入力完了フラグが立っていたらstream_graph実行
            if st.session_state.user_input_done:
                stream_graph(agent, None, thread, st.session_state.session_manager)
                st.session_state.user_input_done = False
                st.session_state.await_user = False

        else:
            print("$$$ normal $$$")
            # 通常ノード（ユーザー入力なし）
            stream_graph(agent, None, thread, st.session_state.session_manager)
    
    if agent.is_end_node(thread):
        st.markdown("ヒアリング完了！ 🎉")
    
    elif agent_reply:
        agent_reply = agent.get_state_value(thread, "agent_reply")
        with st.chat_message("agent"):
            st.markdown(agent_reply)
        st.session_state.messages.append({"role": "agent", "content": agent_reply})
    else:
        pass
    
    

    
   



if __name__ == "__main__":
    main()