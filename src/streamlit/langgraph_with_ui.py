import streamlit as st
from src.agent.sandbox import generate_graph  # あなたのLangGraph生成関数

# LangGraph用
from langgraph.graph import StateGraph

# 初期化処理
if "graph" not in st.session_state:
    st.session_state.graph = generate_graph()
    st.session_state.graph_stream = st.session_state.graph.stream({}, debug=False)
    st.session_state.state = None  # LangGraphの現在のstate
    st.session_state.await_user = False  # ユーザーの発話待ちかどうか

# チャット履歴の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# チャット履歴を表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# LangGraphのステップを進める（ユーザーの入力待ちでないとき）
if not st.session_state.await_user:
    for nested_dict in st.session_state.graph_stream:
        current_node = next(iter(nested_dict))
        state = nested_dict[current_node]
        st.session_state.state = state  # 最新ノード状態をセッションに保存

        if current_node == "generate_question":
            # エージェントの最新発話を取り出す
            agent_reply = state["agent_reply"]
            st.session_state.messages.append({"role": "assistant", "content": agent_reply})
            with st.chat_message("assistant"):
                st.markdown(agent_reply)

            # ノード１つ実行でループ抜ける
            break

        elif current_node == "user_action":
            # ここで入力待ちにする
            st.session_state.await_user = True
            break

        elif current_node == "judge_result":
            st.write("judge_result ノードを実行しました")
            st.write("現在の history:", state["history"])
            # ここでも１ステップで抜ける
            break

        elif current_node == "end_node":
            st.success("ヒアリング完了 🎉")
            break

# ユーザー入力欄
prompt = st.chat_input("あなたの返答を入力してください")
if prompt:
    # ユーザーメッセージの表示
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # **ユーザー入力を LangGraph の state に格納** (「明示的に代入する」方法)
    if st.session_state.state:
        st.session_state.state["user_input"] = prompt
    else:
        # まだ初期化されていない場合は適宜処理
        st.session_state.state = {}
        st.session_state.state["user_input"] = prompt

    # ノードを再開（user_actionノードを進めたい）
    print("=== state_send ===")
    print(st.session_state.state)
    st.session_state.graph_stream.send(st.session_state.state)

    # 入力待ち状態を解除して再描画
    st.session_state.await_user = False
    st.rerun()
