from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / '.env')


@dataclass
class Settings:
    app_name: str = 'University Assistant'
    app_env: str = 'development'
    debug: bool = True
    api_host: str = '0.0.0.0'
    api_port: int = 8000
    streamlit_port: int = 8501
    mongodb_uri: str = 'mongodb://localhost:27017'
    mongodb_db: str = 'university_assistant'
    llm_provider: str = 'demo'
    llm_api_key: str = ''
    llm_model: str = ''
    embedding_model: str = 'sentence-transformers/all-MiniLM-L6-v2'
    max_retrieved_chunks: int = 5
    min_relevance_score: float = 0.2
    max_upload_size_mb: int = 10
    allowed_extensions: tuple[str, ...] = ('.pdf', '.docx', '.txt', '.csv')
    data_dir: str = str(Path(__file__).resolve().parents[1] / 'data')
    uploads_dir: str = str(Path(__file__).resolve().parents[1] / 'data' / 'uploads')
    processed_dir: str = str(Path(__file__).resolve().parents[1] / 'data' / 'processed')

    @classmethod
    def from_env(cls) -> 'Settings':
        raw = {
            'app_name': os.getenv('APP_NAME', 'University Assistant'),
            'app_env': os.getenv('APP_ENV', 'development'),
            'debug': os.getenv('DEBUG', 'true').lower() == 'true',
            'api_host': os.getenv('API_HOST', '0.0.0.0'),
            'api_port': int(os.getenv('API_PORT', '8000')),
            'streamlit_port': int(os.getenv('STREAMLIT_PORT', '8501')),
            'mongodb_uri': os.getenv('MONGODB_URI', 'mongodb://localhost:27017'),
            'mongodb_db': os.getenv('MONGODB_DB', 'university_assistant'),
            'llm_provider': os.getenv('LLM_PROVIDER', 'demo'),
            'llm_api_key': os.getenv('LLM_API_KEY', ''),
            'llm_model': os.getenv('LLM_MODEL', ''),
            'embedding_model': os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2'),
            'max_retrieved_chunks': int(os.getenv('MAX_RETRIEVED_CHUNKS', '5')),
            'min_relevance_score': float(os.getenv('MIN_RELEVANCE_SCORE', '0.2')),
            'max_upload_size_mb': int(os.getenv('MAX_UPLOAD_SIZE_MB', '10')),
            'allowed_extensions': tuple(ext.strip() for ext in os.getenv('ALLOWED_EXTENSIONS', '.pdf,.docx,.txt,.csv').split(',') if ext.strip()),
        }
        return cls(**raw)


settings = Settings.from_env()
