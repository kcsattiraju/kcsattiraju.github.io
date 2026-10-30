r"""Small chat UI for the existing insurance agent API handler.

Run: .\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
"""

from uuid import uuid4
import logging

import streamlit as st

from context_manager import get_conversation_history, list_conversations
from database import SessionLocal


st.set_page_config(page_title="Insurance AI Copilot", page_icon=":material/chat:")
st.title("Insurance AI Copilot")
st.caption("Ask about insurance, premium estimates, or your policy documents.")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid4())
    st.session_state.messages = []

# Render the composer before querying history so it is always visible.
question = st.chat_input("Ask an insurance question", submit_mode="disable")

with st.sidebar:
    st.header("Conversation history")
    if st.button("New conversation", icon=":material/add_comment:", width="stretch"):
        st.session_state.session_id = str(uuid4())
        st.session_state.messages = []
        st.rerun()

    try:
        with SessionLocal() as db:
            conversations = list_conversations(db)
        if not conversations:
            st.caption("Your conversations will appear here after your first answer.")
        for conversation in conversations:
            title = " ".join((conversation["title"] or "Conversation").split())
            label = title[:60] + ("…" if len(title) > 60 else "")
            if st.button(
                label,
                key=f"conversation_{conversation['id']}",
                type="primary" if conversation["id"] == st.session_state.session_id else "secondary",
                width="stretch",
            ):
                with SessionLocal() as db:
                    messages = get_conversation_history(db, conversation["id"])
                st.session_state.session_id = conversation["id"]
                st.session_state.messages = messages
                st.rerun()
    except Exception:
        st.warning("Conversation history is unavailable. Try refreshing the page.")
        logging.getLogger(__name__).exception("Could not load conversation history")

if not st.session_state.messages:
    st.info("Start a conversation or select one from the sidebar to view its history.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if question:
    if not question.strip():
        st.stop()

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                # Reuse the existing handler, including history and persistence.
                from agent_api import AgentRequest, agent_chat

                response = agent_chat(AgentRequest(
                    session_id=st.session_state.session_id,
                    message=question,
                ))
            st.markdown(response.answer)
            st.session_state.messages.extend([
                {"role": "user", "content": question},
                {"role": "assistant", "content": response.answer},
            ])
            st.rerun()
        except Exception:
            st.error("Unable to get an answer. Check the server logs and try again.")
            logging.getLogger(__name__).exception("Chat request failed")
