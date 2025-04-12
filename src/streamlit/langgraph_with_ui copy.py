from typing import Any, Dict

import streamlit as st

from src.agent.app_session_manager import SessionManager
from src.agent.app_user_input_logic import input_additional_info

from src.agent.app_util import stream_graph

THREAD_ID = "1"
def main():
    st.set_page_config(
        page_title="Streamlit×LangGraph コピー生成",
        page_icon="🤖",
    )
    st.title("Streamlit×LangGraph コピー生成")

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

    # スタートノードなら最初に実行
    if agent.is_start_node(thread):
        stream_graph(agent, st.session_state.initial_input, thread, st.session_state.session_manager)

    # ユーザー入力が必要なノードに来た場合
    next_graph = agent.get_next_node(thread)
    if next_graph:
        node_name = next_graph[0]

        if node_name == "user_action" and not st.session_state.user_input_done:
            print("$$$ input $$$")
            st.session_state.await_user = True
            input_additional_info(agent, thread, as_node=node_name)
            st.stop()  # 入力を表示して一旦ここで止める

        elif node_name == "user_action" and st.session_state.user_input_done:
            # ユーザー入力が完了していれば Graph を進める
            print("$$$ stream graph $$$")
            stream_graph(agent, None, thread, st.session_state.session_manager)
            st.session_state.user_input_done = False
            st.session_state.await_user = False

        else:
            print("$$$ normal $$$")
            # 通常ノード（ユーザー入力なし）
            stream_graph(agent, None, thread, st.session_state.session_manager)

    if agent.is_end_node(thread):
        st.success("コピー生成完了！ 🎉")



if __name__ == "__main__":
    main()