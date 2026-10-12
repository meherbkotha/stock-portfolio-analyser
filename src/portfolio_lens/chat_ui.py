"""Session-scoped Streamlit chat and secret configuration."""
import hashlib
import os

import streamlit as st

from portfolio_lens.assistant import AssistantError, DEFAULT_MODEL, answer_question

MAX_SESSION_REQUESTS = 20


def setting(name, default=""):
    """Prefer server environment variables, then Streamlit Secrets."""
    if os.environ.get(name):
        return os.environ[name]
    try:
        return str(st.secrets.get(name, default))
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return default


def render_assistant(context):
    st.subheader("Ask about your portfolio")
    st.write("Ask about performance, allocation, volatility, drawdowns, or how the selected strategy works.")
    st.caption('Try: "Summarize my portfolio" · "Which stock had the highest return?" · "Explain my maximum drawdown"')
    fingerprint = hashlib.sha256(context.encode()).hexdigest()
    if st.session_state.get("chat_portfolio") != fingerprint:
        st.session_state.chat_portfolio = fingerprint
        st.session_state.portfolio_messages = []
    st.session_state.setdefault("chat_requests", 0)
    api_key = setting("OPENAI_API_KEY")
    model = setting("OPENAI_MODEL", DEFAULT_MODEL)
    if not api_key:
        st.info("The assistant needs an OpenAI API key. Add OPENAI_API_KEY in Streamlit app settings → Secrets, then reboot the app.")
    st.caption("When you send a question, your question, recent chat, and calculated portfolio summary are sent to OpenAI. The full price CSV is not sent. Answers can contain mistakes; verify figures against the dashboard.")
    if st.button("Clear conversation", key="clear_portfolio_chat"):
        st.session_state.portfolio_messages = []
    for message in st.session_state.portfolio_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    limited = st.session_state.chat_requests >= MAX_SESSION_REQUESTS
    if limited:
        st.info("This session has reached its 20-question limit.")
    question = st.chat_input("Ask a portfolio question", disabled=not api_key or limited, max_chars=3000, key="portfolio_question")
    if question:
        st.session_state.chat_requests += 1
        try:
            with st.spinner("Reviewing your portfolio…"):
                answer = answer_question(question, context, st.session_state.portfolio_messages, api_key, model)
        except AssistantError as error:
            st.error(str(error))
            return
        st.session_state.portfolio_messages.extend([
            {"role": "user", "content": question}, {"role": "assistant", "content": answer},
        ])
        st.session_state.portfolio_messages = st.session_state.portfolio_messages[-20:]
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            st.markdown(answer)
