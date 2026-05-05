import streamlit as st
from agent import DeepSeekAgent

st.set_page_config(page_title="DeepSeek 最小 Agent Demo", page_icon="🤖", layout="wide")
st.title("🤖 DeepSeek 最小单 Agent Demo")

if "agent" not in st.session_state:
    st.session_state.agent = DeepSeekAgent()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

col1, col2 = st.columns([3, 1])
with col2:
    if st.button("重置上下文"):
        st.session_state.agent.reset()
        st.session_state.chat_history = []
        st.rerun()

for role, content in st.session_state.chat_history:
    with st.chat_message(role):
        st.write(content)

user_input = st.chat_input("请输入你的问题，例如：帮我读取 ~/test.pdf 并总结要点")
if user_input:
    st.session_state.chat_history.append(("user", user_input))
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Agent 思考中..."):
            answer = st.session_state.agent.run(user_input)
            st.write(answer)

    st.session_state.chat_history.append(("assistant", answer))
