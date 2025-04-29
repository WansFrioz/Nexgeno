# import streamlit as st
# from langchain.document_loaders import WebBaseLoader, TextLoader, PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.vectorstores import Chroma
# from langchain.embeddings import HuggingFaceEmbeddings
# from sentence_transformers import SentenceTransformer
# from youtube_transcript_api import YouTubeTranscriptApi
# from langchain.schema import Document
# from urllib.parse import urlparse, parse_qs
# import tempfile
# import os

# # === CONFIG ===
# EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# CHROMA_DB_DIR = "db/chroma"

# # === Set up Embeddings and DB ===
# embedding = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
# vectorstore = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embedding)

# # === Utility Functions ===
# def process_documents(docs, metadata=None):
#     if metadata:
#         for d in docs:
#             d.metadata.update(metadata)

#     splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
#     chunks = splitter.split_documents(docs)
#     vectorstore.add_documents(chunks)
#     vectorstore.persist()

# def extract_youtube_id(url):
#     parsed = urlparse(url)
#     if 'youtube' in parsed.netloc:
#         return parse_qs(parsed.query)['v'][0]
#     elif 'youtu.be' in parsed.netloc:
#         return parsed.path.lstrip('/')
#     return None

# def ingest_website(url):
#     loader = WebBaseLoader(url)
#     docs = loader.load()
#     process_documents(docs, metadata={"source": url, "type": "website"})

# def ingest_youtube(url):
#     video_id = extract_youtube_id(url)
#     transcript = YouTubeTranscriptApi.get_transcript(video_id)
#     text = "\n".join([t['text'] for t in transcript])
#     doc = Document(page_content=text, metadata={"source": url, "type": "youtube"})
#     process_documents([doc])

# def ingest_text(text, title="Custom Note"):
#     doc = Document(page_content=text, metadata={"source": title, "type": "custom"})
#     process_documents([doc])

# def ingest_file(uploaded_file):
#     suffix = uploaded_file.name.split(".")[-1].lower()
#     with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp_file:
#         tmp_file.write(uploaded_file.getvalue())
#         tmp_path = tmp_file.name

#     if suffix == "pdf":
#         loader = PyPDFLoader(tmp_path)
#     elif suffix in ["txt", "md"]:
#         loader = TextLoader(tmp_path)
#     else:
#         st.error("Unsupported file type.")
#         return

#     docs = loader.load()
#     process_documents(docs, metadata={"source": uploaded_file.name, "type": "file"})
#     os.remove(tmp_path)

# # === Streamlit UI ===
# st.set_page_config(page_title="Admin Data Ingestion", layout="centered")
# st.title("🧠 NexBuddy Admin — Data Ingestion")

# with st.expander("🌐 Add Website URL"):
#     url = st.text_input("Enter website URL")
#     if st.button("Ingest Website") and url:
#         ingest_website(url)
#         st.success("Website data ingested!")

# with st.expander("📺 Add YouTube Video"):
#     yt_url = st.text_input("Enter YouTube URL")
#     if st.button("Ingest YouTube") and yt_url:
#         ingest_youtube(yt_url)
#         st.success("YouTube transcript ingested!")

# with st.expander("📄 Upload Document"):
#     file = st.file_uploader("Upload .pdf, .txt, or .md", type=["pdf", "txt", "md"])
#     if st.button("Ingest File") and file:
#         ingest_file(file)
#         st.success("File ingested!")

# with st.expander("📝 Add Custom Note"):
#     note_title = st.text_input("Note title")
#     note_text = st.text_area("Enter text")
#     if st.button("Ingest Note") and note_text:
#         ingest_text(note_text, title=note_title or "Note")
#         st.success("Custom text ingested!")



# from sentence_transformers import SentenceTransformer

# # Test loading the model
# model = SentenceTransformer('all-MiniLM-L6-v2')
# print("Model loaded successfully.")

import streamlit as st
import pandas as pd
import numpy as np
import time
st.set_page_config(layout="wide")
# Sample data for the home page
def get_sample_data():
    data = {
        'users': 150,
        'total_prompts': 5000,
        'api_usage': 12000,
        'active_models': 10
    }
    return data
# Sample time-based data for the line graph
def get_time_based_data():
    np.random.seed(0)
    dates = pd.date_range(start='1/1/2023', end='12/31/2023')
    usage = np.random.randint(50, 200, len(dates))
    return pd.DataFrame({'Date': dates, 'Usage': usage})
# Sample API usage distribution data for the pie chart
def get_api_usage_data():
    data = {
        'Model': ['Model A', 'Model B', 'Model C', 'Model D'],
        'Usage': [30, 25, 20, 25]
    }
    return pd.DataFrame(data)
# Sample data for the Excel-like table
def get_table_data():
    data = {
        'Name': ['User 1', 'User 2', 'User 3', 'User 4'],
        'Limit Left': [100, 50, 200, 150],
        'Model Used': ['Model A', 'Model B', 'Model A', 'Model C']
    }
    return pd.DataFrame(data)
# Home page
def home_page():
    st.title("Home")
    data = get_sample_data()
    time_based_data = get_time_based_data()
    api_usage_data = get_api_usage_data()
    table_data = get_table_data()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Number of Users", value=data['users'])
    with col2:
        st.metric(label="Total Prompts", value=data['total_prompts'])
    with col3:
        st.metric(label="Total API Usage", value=data['api_usage'])
    with col4:
        st.metric(label="Active Models", value=data['active_models'])
    st.subheader("Usage Over Time")
    st.line_chart(data=time_based_data, x='Date', y='Usage')
    st.subheader("API Usage Distribution")
    st.dataframe(api_usage_data)
    st.subheader("User Table")
    st.dataframe(table_data)
# Train AI page
def train_ai_page():
    st.title("Train AI")
    with st.form("training_form"):
        tone = st.selectbox("Tone", ["Formal", "Casual", "Friendly", "Professional"])
        ai_role = st.text_input("AI Role")
        about_ai = st.text_area("About the AI")
        share_links = st.text_input("Share Links (comma-separated)")
        uploaded_file = st.file_uploader("Upload Knowledge Base", type=["csv", "xlsx", "txt"])
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.success("Training initiated! Please wait...")
            time.sleep(2)
            st.write("Tone: ", tone)
            st.write("AI role: ", ai_role)
            st.write("About: ", about_ai)
            st.write("Links: ", share_links)
            if uploaded_file:
                st.write("Uploaded file name:", uploaded_file.name)
# History page
def history_page():
    st.title("History")
    st.write("History")
# Main app
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Train AI", "History"])
    if page == "Home":
        home_page()
    elif page == "Train AI":
        train_ai_page()
    elif page == "History":
        history_page()
if __name__ == '__main__':
    main() 