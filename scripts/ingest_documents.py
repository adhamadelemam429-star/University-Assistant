from __future__ import annotations

import argparse
from pathlib import Path

from app.config import settings
from app.services.document_service import document_service


def ingest_folder(folder_path: str | Path) -> int:
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f'Folder not found: {folder}')

    count = 0
    for file_path in sorted(folder.iterdir()):
        if file_path.is_file() and file_path.suffix.lower() in settings.allowed_extensions:
            metadata = document_service.ingest_document(file_path)
            count += 1
            print(f'Indexed {metadata.get("file_name")} -> {metadata.get("chunk_count", 0)} chunks')
    return count


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest university documents into the local index.')
    parser.add_argument('folder', nargs='?', default=settings.uploads_dir, help='Folder containing PDF, DOCX, TXT, or CSV files.')
    args = parser.parse_args()

    processed = ingest_folder(args.folder)
    print(f'Finished ingesting {processed} documents.')
