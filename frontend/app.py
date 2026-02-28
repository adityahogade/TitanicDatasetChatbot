import streamlit as st
import requests

# =========================
# CONFIG
# =========================
BACKEND_URL = "https://titanic-dataset-chatbot.vercel.app/chat"

st.set_page_config(
    page_title="Titanic CSV Chatbot",
    page_icon="🚢",
    layout="centered"
)

# =========================
# UI HEADER
# =========================
st.title("🚢 Titanic Dataset Chatbot")
st.write(
    "Ask natural language questions about the Titanic passenger dataset. "
    "The backend analyzes the CSV and may generate insights and plots."
)

# =========================
# INPUT (FIXED LABEL WARNING)
# =========================
question = st.text_input(
    "Ask a question about the Titanic dataset",
    placeholder="e.g. What is the survival rate of women in first class?",
    label_visibility="collapsed"
)

# =========================
# SUBMIT BUTTON
# =========================
submit = st.button("Ask")

# =========================
# HANDLE QUERY
# =========================
if submit and question.strip():
    with st.spinner("Analyzing Titanic data..."):
        try:
            response = requests.post(
                BACKEND_URL,
                params={"question": question},
                timeout=120
            )

            if response.status_code == 200:
                data = response.json()

                # ---- Answer ----
                st.subheader("Answer")
                st.write(data.get("answer", "No answer returned."))

                # ---- Plot (if exists) ----
                plot_path = data.get("plot")
                if plot_path:
                    st.subheader("Visualization")
                    st.image(
                        f"https://titanic-dataset-chatbot.vercel.app{plot_path}",
                        use_container_width=True
                    )
            else:
                st.error(f"Backend error: {response.status_code}")

        except requests.exceptions.RequestException as e:
            st.error("Could not connect to backend.")
            st.error(str(e))

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("Powered by LangChain, FastAPI, Streamlit & Titanic Dataset")