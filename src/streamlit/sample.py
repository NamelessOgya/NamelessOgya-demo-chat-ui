import streamlit as st

class TmpChatBot:
    def __init__(self):
        self.messages = []
    
    def call(self, prompt):
        if prompt is None:  # 最初の会話
            reply = "あなたの返答の一文字目を記録して返します！"
        else:
            self.messages.append(prompt[0])  # 一文字目だけ記録
            reply = "".join(self.messages)   # 記録を連結して返答

        return reply

# bot をセッション状態に保持
if "bot" not in st.session_state:
    st.session_state.bot = TmpChatBot()

st.title("一文字目を記憶して返すbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # call the bot from session_state
    response = f"Echo: {st.session_state.bot.call(prompt)}"

    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
