"""
Page 5 – AI Resume Chatbot
"""
import streamlit as st
from utils.resume_parser import extract_text
from utils.ai_engine import _get_model


def render():
    st.title("💬 AI Resume Chatbot")
    st.markdown("Apne resume ke baare mein kuch bhi pucho — AI jawab dega!")

    # ── Resume load ───────────────────────────────────────────────────────────
    resume_text = st.session_state.get("resume_text", "")
    if not resume_text:
        uploaded = st.file_uploader("Resume upload karo", type=["pdf", "docx", "txt"], key="chat_upload")
        if uploaded:
            resume_text = extract_text(uploaded)
            st.session_state["resume_text"] = resume_text

    if not resume_text:
        st.info("👆 Pehle resume upload karo — phir chatbot se baat karo!")
        return

    st.success("✅ Resume loaded! Ab kuch bhi pucho.")

    # ── Chat history ──────────────────────────────────────────────────────────
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [
            {"role": "assistant", "content": "Namaste! 👋 Main tumhara AI resume assistant hoon. Resume ke baare mein kuch bhi pucho!"}
        ]

    # Display chat history
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # ── Quick questions ───────────────────────────────────────────────────────
    st.markdown("**Quick Questions:**")
    col1, col2, col3 = st.columns(3)
    quick_q = None
    with col1:
        if st.button("💰 Salary kitni honi chahiye?"):
            quick_q = "Mere resume ke hisaab se meri salary kitni honi chahiye?"
    with col2:
        if st.button("🎯 Konsi job suits karti hai?"):
            quick_q = "Mere resume ke hisaab se konsi job role best suited hai?"
    with col3:
        if st.button("📈 Kaise improve karoon?"):
            quick_q = "Mera resume improve karne ke liye kya karna chahiye?"

    # ── User input ────────────────────────────────────────────────────────────
    user_input = st.chat_input("Apna sawaal likho...")
    
    if quick_q:
        user_input = quick_q

    if user_input:
        # Add user message
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.write(user_input)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Soch raha hoon..."):
                try:
                    model = _get_model()
                    prompt = f"""
You are a helpful AI resume assistant. Answer questions about the candidate's resume.
Be helpful, friendly, and give practical advice. Answer in the same language as the question.

Resume:
{resume_text[:3000]}

User Question: {user_input}

Give a helpful, concise answer.
"""
                    response = model.generate_content(prompt)
                    answer = response.text
                    st.write(answer)
                    st.session_state["chat_history"].append({"role": "assistant", "content": answer})
                except Exception as e:
                    err = "Sorry, kuch error aayi. Dobara try karo!"
                    st.error(err)
                    st.session_state["chat_history"].append({"role": "assistant", "content": err})

    # Clear chat button
    if st.button("🗑️ Chat Clear Karo"):
        st.session_state["chat_history"] = [
            {"role": "assistant", "content": "Namaste! 👋 Main tumhara AI resume assistant hoon. Resume ke baare mein kuch bhi pucho!"}
        ]
        st.rerun()
