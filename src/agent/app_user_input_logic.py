import streamlit as st

from src.agent.sandbox import Agent
# from utils.app_util import find_item_by_title


# def select_item(
#     agent: Agent,
#     thread: dict,
#     state_key: str,
#     selectbox_message: str,
#     state_update_key: str,
#     as_node: str,
# ) -> None:
#     """
#     項目選択関数

#     Args:
#         agent (Agent): エージェントオブジェクト
#         thread (dict): 現在のスレッドの辞書
#         state_key (str): ステートから取得する項目のキー
#         selectbox_message (str): セレクトボックスのメッセージ
#         state_update_key (str): ステートを更新する際のキー
#         as_node (str): ステート更新ノード名
#     """
#     items = agent.get_state_value(thread, state_key)

#     # セレクトボックスのオプション作成
#     select_options = [item["title"] for item in items]
#     select_options.append("再検討を依頼する")

#     selected = st.selectbox(
#         selectbox_message,
#         select_options,
#         key=f"{as_node}_select_{agent.get_state_value(thread, 'iteration_count')}",
#     )

#     if not st.button(
#         "次へ",
#         key=f"{as_node}_button_{agent.get_state_value(thread, 'iteration_count')}",
#     ):
#         print("User Input Stop")
#         st.stop()  # この時点で処理が停止

#     print("Entered User Input: ", selected)

#     if selected == "再検討を依頼する":
#         agent.graph.update_state(
#             thread,
#             {
#                 state_update_key: None,
#                 "display_message_dict": None,
#                 "is_rethink": True,
#             },
#             as_node=as_node,
#         )
#     else:
#         selected_item = find_item_by_title(items, selected)
#         agent.graph.update_state(
#             thread,
#             {
#                 state_update_key: selected_item,
#                 "display_message_dict": None,
#                 "is_rethink": False,
#             },
#             as_node=as_node,
#         )


def input_additional_info(agent: Agent, thread: dict, as_node: str) -> None:
    agent_replay = agent.get_state_value(thread, "agent_reply")

    with st.chat_message("agent"):
        st.markdown(agent_replay)

    user_input = st.chat_input("メッセージを入力してください", key=f"user_input_{as_node}")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        print("Entered User Input: ", user_input)

        agent.graph.update_state(
            thread,
            {
                "user_input": user_input,
                "display_message_dict": None,
            },
            as_node=as_node,
        )

        # ✅ セッションのフラグ更新を明示的に行う
        st.session_state.user_input_done = True


def display_input_chat_massage(agent: Agent, thread: dict, as_node: str) -> None:
    agent_replay = agent.get_state_value(thread, "agent_reply")
    # if agent_reply:
    #     with st.chat_message("agent"):
    #         st.markdown(agent_reply)

    if user_input := st.chat_input("メッセージを入力してください"):
        
        print("Entered User Input: ", user_input)

        with st.chat_message("user"):
            st.markdown(user_input)
        
        st.session_state.messages.append({"role": "user", "content": user_input})

        print("Entered User Input: ", user_input)

        agent.graph.update_state(
            thread,
            {
                "user_input": user_input,
                "display_message_dict": None,
            },
            as_node=as_node,
        )

        
        st.session_state.user_input_done = True
