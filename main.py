import streamlit as st
from clone_repo import clone_repo
from process_code import load_and_embed_repo
from qa_bot import ask_question

st.set_page_config(page_title="Git-RAG AI", layout="wide")

st.title("🚀 Git-RAG AI – Decode Any GitHub Repo with Gemini")
st.markdown("Give me a GitHub repo and ask me *anything* about it.")

# Store state across reruns
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None
if 'repo_path' not in st.session_state:
    st.session_state.repo_path = None

# Input GitHub repo
repo_url = st.text_input("🔗 Enter GitHub Repo URL:")

if repo_url and st.session_state.repo_path != repo_url:
    with st.spinner("Cloning repo..."):
        repo_path = clone_repo(repo_url)
        st.session_state.repo_path = repo_url

    with st.spinner("Processing and embedding code..."):
        vectorstore, readme_summary = load_and_embed_repo(repo_path)
        st.session_state.vectorstore = vectorstore
        st.session_state.readme_summary = readme_summary

    st.success("✅ Repo ready! Ask a question now 👇")

# Show README summary if available
if 'readme_summary' in st.session_state:
    st.markdown(f"### 🧾 README Summary:\n{st.session_state.readme_summary}")

# Ask questions only when vectorstore is ready
if st.session_state.vectorstore:
    user_question = st.text_input("❓ Ask something about the code:")
    if user_question:
        with st.spinner("Thinking with Gemini...🧠"):
            answer = ask_question(user_question, st.session_state.vectorstore)
        st.markdown(f"**Answer:** {answer}")
