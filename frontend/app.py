import streamlit as st
import requests
from PIL import Image
import json
import os

st.set_page_config(
    page_title=" Titanic Chatbot",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
body {
    background-color: #f7f7f8;
}
.chat-wrapper {
    max-width: 800px;
    margin: auto;
    padding-bottom: 120px;
}
.user-bubble {
    background-color: #DCF8C6;
    padding: 14px 18px;
    border-radius: 14px;
    margin: 10px 0;
    text-align: right;
    font-size: 16px;
}
.bot-bubble {
    background-color: #FFFFFF;
    padding: 14px 18px;
    border-radius: 14px;
    margin: 10px 0;
    font-size: 16px;
    border: 1px solid #e0e0e0;
}
.plot-box {
    background-color: #ffffff;
    padding: 12px;
    border-radius: 12px;
    border: 1px solid #e0e0e0;
    margin-bottom: 16px;
}
.input-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background-color: #ffffff;
    padding: 12px 0;
    border-top: 1px solid #ddd;
    z-index: 999;
}
.input-inner {
    max-width: 800px;
    margin: auto;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center;'> Titanic Dataset Chatbot</h2>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:gray;'>Ask analytical questions and get insights with visualizations</p>",
    unsafe_allow_html=True
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

st.markdown("<div class='chat-wrapper'>", unsafe_allow_html=True)

for entry in st.session_state.chat_history:
   
    if entry[0] == "user":
        st.markdown(
            f"<div class='user-bubble'>{entry[1]}</div>",
            unsafe_allow_html=True
        )

    
    else:
        st.markdown(
            f"<div class='bot-bubble'>{entry[1]}</div>",
            unsafe_allow_html=True
        )

        
        if len(entry) > 2 and entry[2]:
            plot_path = os.path.join(PROJECT_ROOT, entry[2])

            if os.path.exists(plot_path):
                st.markdown("<div class='plot-box'>", unsafe_allow_html=True)

                img = Image.open(plot_path)
                img.thumbnail((700, 400))
                st.image(img)

                st.markdown("</div>", unsafe_allow_html=True)

                try:
                    os.remove(plot_path)
                except Exception:
                    pass

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='input-bar'>", unsafe_allow_html=True)
st.markdown("<div class='input-inner'>", unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=True):
    question = st.text_input(
        "",
        placeholder="Ask about Titanic passengers, survival rates, distributions..."
    )
    send = st.form_submit_button("Send ")

st.markdown("</div></div>", unsafe_allow_html=True)

if send and question.strip():
    st.session_state.chat_history.append(("user", question))

    with st.spinner("Analyzing Titanic dataset..."):
        try:
            response = requests.post(
                "https://titanic-dataset-chatbot-339w5j5kr-adityas-projects-1fcb2206.vercel.app/chat",
                json={"question": question},
                timeout=120
            )

            if not response.text.strip():
                answer = " Backend returned empty response."
                plot = None
            else:
                try:
                    data = response.json()
                    answer = data.get("answer", "No answer returned.")
                    plot = data.get("plot")
                except json.JSONDecodeError:
                    answer = " Invalid response from backend."
                    plot = None

            st.session_state.chat_history.append(("bot", answer, plot))

        except requests.exceptions.ConnectionError:
            st.session_state.chat_history.append(
                ("bot", " Backend is not running. Start FastAPI first.", None)
            )

    st.rerun()