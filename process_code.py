import os
from pathlib import Path
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader

load_dotenv()

# 🌟 Fast + cheap LLM for summarization
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.2
)

def load_and_embed_repo(repo_path: str, db_path: str = "faiss_index"):
    # ⚡ Load precomputed FAISS if exists
    if os.path.exists(db_path):
        print("🧠 Loading existing FAISS index...")
        vectorstore = FAISS.load_local(
            db_path,
            GoogleGenerativeAIEmbeddings(model="models/embedding-001"),
            allow_dangerous_deserialization=True
        )
        return vectorstore, None

    print("📚 Loading and embedding repository files...")

    allowed_ext = [".py", ".md", ".txt", ".json", ".js", ".ts", ".java", ".c", ".cpp"]

    # ✅ Smart loader using pathlib
    docs = []
    for filepath in Path(repo_path).rglob("*"):
        if filepath.suffix.lower() in allowed_ext and "__pycache__" not in str(filepath).lower():
            try:
                loader = TextLoader(str(filepath), autodetect_encoding=True)
                docs.extend(loader.load())
            except Exception as e:
                print(f"❌ Error loading {filepath}: {e}")

    if not docs:
        raise ValueError("🚨 No valid documents found in the repo!")

    # 🔍 Extract README.md specifically
    readme_docs = [doc for doc in docs if "readme" in doc.metadata['source'].lower()]
    print("📄 README files found:", [doc.metadata['source'] for doc in readme_docs])
    readme_content = None
    readme_path = Path(repo_path) / "README.md"

    if readme_path.exists():
        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                readme_content = f.read().strip()
                print("📜 README Preview:", readme_content[:300])
        except Exception as e:
            print(f"❌ Could not read README.md: {e}")
    else:
        print("❌ README.md not found in repo.")

    summary = None
    if readme_content:
        prompt = f"Summarize the GitHub project using this README:\n\n{readme_content}"
        response = llm.invoke(prompt)
        summary = response.content if hasattr(response, "content") else str(response)
        print("🧾 README Summary:\n", summary)
    else:
        print("⚠️ README content empty or unreadable.")



    # 📦 Chunk all docs for embedding
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=300,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(docs)

    # 🧠 Embed using Gemini
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(db_path)

    print(f"✅ Vectorstore saved at: {db_path}")
    return vectorstore, summary
