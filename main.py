import streamlit as st
from clone_repo import clone_repo
from process_code import load_and_embed_repo
from qa_bot import ask_question
from file_tree_utils import build_file_tree, describe_code_file

# 🎨 Page setup
st.set_page_config(page_title="Decodify ", layout="wide")
st.title("🚀 Decodify  –  GitHub Repo Decoded ")

# Sidebar Navigation
st.sidebar.title("🚀Decodify  ")
page = st.sidebar.radio("Go to", ["🏠 Home", "🤖 Chatbot", "📂 Decode"])


# 🧠 Persistent session state

for key in ["vectorstore", "repo_url", "repo_path", "chat_history", "readme_summary", "readme_raw", "selected_file_path"]:

    if key not in st.session_state:
        st.session_state[key] = None if key != "chat_history" else []

# 🏠 HOME PAGE (Repo Input + README display)
if page == "🏠 Home":
    st.subheader("🔗 Enter GitHub Repo URL:")
    repo_url = st.text_input(" ")

    if repo_url and st.session_state.repo_url != repo_url:
        with st.spinner("🔄 Cloning repo..."):
            repo_path = clone_repo(repo_url)
            if repo_path is None:
                st.error("❌ Failed to clone the repo. Please check the URL.")
            else:
                st.session_state.repo_url = repo_url
                st.session_state.repo_path = repo_path

        with st.spinner("📦 Processing and embedding repo..."):
            vectorstore, summary, readme_content = load_and_embed_repo(repo_path)
            st.session_state.vectorstore = vectorstore
            st.session_state.readme_summary = summary or None
            st.session_state.readme_raw = readme_content or None
            st.session_state.chat_history = []
            st.session_state.selected_file_path = None

        st.success("✅ Repo processed successfully! Switch to Chatbot tab to ask questions.")


    if st.session_state.readme_summary:
        with st.expander("📖 README Summary", expanded=True):
            st.markdown(st.session_state.readme_summary)
    elif st.session_state.repo_path:
        st.info("ℹ️ This repo doesn’t contain a valid README.md")
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
        
        
elif page == "📂 Decode":
    from utilis import analyze_languages  
    import matplotlib.pyplot as plt
    import os

    def render_tree(tree, parent_path=""):
        for name, value in tree.items():
            current_path = f"{parent_path}/{name}" if parent_path else name

            if isinstance(value, dict):
                st.markdown(f"📁 {name}", unsafe_allow_html=True)
                with st.container():
                    render_tree(value, current_path)
            else:
                if st.button(f"📄 {name}", key=current_path):
                    st.session_state.selected_file_path = value
                    st.session_state.show_project_info = False  # hide project info on file select

    if "show_project_info" not in st.session_state:
        st.session_state.show_project_info = False

    if st.session_state.get("repo_path"):
        from file_tree_utils import build_file_tree
        from qa_bot import ask_question

        repo_path = st.session_state.repo_path
        file_tree = build_file_tree(repo_path)

        col1, col2 = st.columns([1, 3])
        with col1:
            # ✅ Corrected condition
            if not st.session_state.selected_file_path:
                btn_label = "📊 Hide Project Info" if st.session_state.show_project_info else "📊 Show Project Info"
                if st.button(btn_label, key="toggle_info_btn"):
                    st.session_state.show_project_info = not st.session_state.show_project_info

            st.subheader("📂 Project Files")
            render_tree(file_tree)



        with col2:
            if "selected_file_path" in st.session_state and st.session_state.selected_file_path:

                selected = st.session_state.selected_file_path
                st.subheader(f"📄 {os.path.basename(selected)}")

                st.markdown(
                    """
                    <div style='text-align: right; margin-top: -35px; margin-bottom: 10px;'>
                        <a href="#ai-desc" style="
                            text-decoration: none;
                            background: rgba(0, 123, 255, 0.1);
                            padding: 5px 10px;
                            border-radius: 12px;
                            font-size: 0.85rem;
                            color: #007bff;
                            border: 1px solid #007bff;
                        ">
                            🔍 AI Description ⬇️
                        </a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                try:
                    with open(selected, "r", encoding="utf-8") as f:
                        code = f.read()

                    st.code(code, language="python" if selected.endswith(".py") else None)

                    st.markdown('<a name="ai-desc"></a>', unsafe_allow_html=True)
                    st.markdown("### 🧠 AI Description")
                    with st.spinner("Analyzing..."):
                        description = ask_question(
                            f"Explain what this file does and why it’s useful:\n\n{code[:4000]}",
                            st.session_state.vectorstore,
                            readme_text=st.session_state.readme_raw
                        )
                    st.markdown(description)

                except Exception as e:
                    st.error(f"❌ Could not read file: {e}")

            elif st.session_state.show_project_info:
                st.subheader("📊 Language Usage in Project")
                repo_path = st.session_state.get("repo_path", "cloned_repo")
                lang_data = analyze_languages(repo_path)

                
                if lang_data:
                    fig, ax = plt.subplots(figsize=(3, 3))
                    fig.patch.set_alpha(0)
                    ax.patch.set_alpha(0)

                    ax.pie(
                        lang_data.values(),
                        labels=lang_data.keys(),
                        autopct="%1.1f%%",
                        startangle=90,
                        textprops={"color": "white", "fontsize": 8},
                    )
                    ax.axis("equal")
                    st.pyplot(fig, use_container_width=True)
                else:
                    st.info("No recognizable languages found.")

                st.subheader("🧾 Project Summary")
                st.markdown(st.session_state.readme_summary or "*No summary available.*")

            else:
                st.info("👈 Select a file from left OR show project info.")

    else:
        st.warning("⚠️ Please load a repository first from the Home page.")

