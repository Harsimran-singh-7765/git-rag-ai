import streamlit as st
from clone_repo import clone_repo
from process_code import load_and_embed_repo
from qa_bot import ask_question

# 🎨 Page setup
st.set_page_config(page_title="Git-RAG AI", layout="wide")
st.title("🚀 Git-RAG AI –  GitHub Repo ")

# Sidebar Navigation
st.sidebar.title("🚀 Git-RAG AI ")
page = st.sidebar.radio("Go to", ["🏠 Home", "🤖 Chatbot"])

# 🧠 Persistent session state
for key in ["vectorstore", "repo_url", "chat_history", "readme_summary", "readme_raw"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "chat_history" else []

# 🏠 HOME PAGE (Repo Input + README display)
if page == "🏠 Home":
    st.subheader("🔗 Enter GitHub Repo URL:")
    repo_url = st.text_input(" ")

    if repo_url and st.session_state.repo_url != repo_url:
        with st.spinner("🔄 Cloning repo..."):
            repo_path = clone_repo(repo_url)
            st.session_state.repo_url = repo_url

        with st.spinner("📦 Processing and embedding repo..."):
            vectorstore, summary, readme_content = load_and_embed_repo(repo_path)
            st.session_state.vectorstore = vectorstore
            st.session_state.readme_summary = summary
            st.session_state.readme_raw = readme_content
            st.session_state.chat_history = []  # reset chat

        st.success("✅ Repo processed successfully! Switch to Chatbot tab to ask questions.")

    if st.session_state.readme_summary:
        with st.expander("📖 README Summary", expanded=True):
            st.markdown(st.session_state.readme_summary)

    if st.session_state.readme_raw:
        with st.expander("📝 Full README.md"):
            st.code(st.session_state.readme_raw, language="markdown")


# 🤖 CHATBOT PAGE
elif page == "🤖 Chatbot":
    if st.session_state.vectorstore:
        user_query = st.chat_input("Ask something about this repo...")

        if user_query:
            # Show user message
            st.session_state.chat_history.append(("user", user_query))
            

            # Gemini response
            with st.spinner("🤖 Thinking with Gemini..."):
                response = ask_question(user_query, st.session_state.vectorstore,readme_text=st.session_state.readme_raw)

            st.session_state.chat_history.append(("ai", response))


        # Show full history (so new messages appear above old ones)
        for role, msg in st.session_state.chat_history:
            with st.chat_message(role):
                st.markdown(msg)

    else:
        st.warning("⚠️ Please load a repository first from the Home page.")
