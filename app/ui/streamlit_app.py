from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from app.config import settings
from app.core.document_loader import extract_text_from_file
from app.services.chat_service import chat_service
from app.services.document_service import document_service


def ensure_initialized() -> None:
    if 'messages' not in st.session_state:
        st.session_state.messages = []


st.set_page_config(page_title='University Assistant', layout='wide')
ensure_initialized()

st.title('University Assistant')
st.caption(f'Mode: {settings.app_env} | LLM: {settings.llm_provider}')

with st.sidebar:
    st.header('Documents')
    uploaded_files = st.file_uploader('Upload academic documents', accept_multiple_files=True)
    if uploaded_files:
        for uploaded in uploaded_files:
            file_path = Path(settings.uploads_dir) / uploaded.name
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(uploaded.read())
            try:
                metadata = document_service.ingest_document(file_path)
                st.success(f'Loaded {metadata.get("file_name", uploaded.name)}')
            except Exception as exc:  # pragma: no cover
                st.warning(f'Could not index {uploaded.name}: {exc}')

    if st.button('Re-index uploaded documents'):
        upload_dir = Path(settings.uploads_dir)
        count = 0
        if upload_dir.exists():
            for file_path in sorted(upload_dir.iterdir()):
                if file_path.is_file() and file_path.suffix.lower() in settings.allowed_extensions:
                    try:
                        document_service.ingest_document(file_path)
                        count += 1
                    except Exception:
                        continue
        st.success(f'Re-indexed {count} documents.')

    if st.button('New conversation'):
        st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

question = st.chat_input('اسأل بالعربية أو الإنجليزية عن جامعة القاهرة')
if question:
    with st.chat_message('user'):
        st.markdown(question)
    st.session_state.messages.append({'role': 'user', 'content': question})

    response = chat_service.answer_question(question)
    with st.chat_message('assistant'):
        st.markdown(response['answer'])
        if response.get('sources'):
            st.subheader('Sources')
            for source in response['sources']:
                page = source.get('page_number') or 'n/a'
                st.write(f"- {source.get('file_name')} — page {page}")
    st.session_state.messages.append({'role': 'assistant', 'content': response['answer']})
