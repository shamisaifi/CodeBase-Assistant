
from sqlalchemy import select

from ai.chunking import chunk_multiple_files
from ai.vectordb import store_chunks
from db.session import SessionLocal
from models.file import CodeFile


async def process_files_for_rag (file_data: list[tuple[int, str]]):
    async with SessionLocal() as db:
        file_ids = [fd[0] for fd in file_data]
        file_paths = [fd[1] for fd in file_data]

        chunks_result = await chunk_multiple_files(file_paths)

        result = await db.execute(select(CodeFile).where(CodeFile.id.in_(file_ids)))
        files = result.scalars().all()

        for file in files:
            chunk = chunks_result.get(file.file_path, [])
            await store_chunks(chunk, file.id, file.chat_session_id, db)

            file.is_processed = True

        await db.commit()
