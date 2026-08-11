
from sqlalchemy import select

from ai.chunking import chunk_multiple_files
from ai.embeddings import embed_chunks, embed_query
from models.file import CodeFile


async def process_files_for_rag (file_data: list[tuple[int, str]], db):
    file_ids = [fd[0] for fd in file_data]
    file_paths = [fd[1] for fd in file_data]

    chunks_result = await chunk_multiple_files(file_paths)
    # print("chunks for embedd: ", chunks_result)

    result = await db.execute(select(CodeFile).where(CodeFile.id.in_(file_ids)))
    files = result.scalars().all()

    for file in files:
        chunk = chunks_result.get(file.file_path, [])
        embedded = embed_chunks(chunk)
        file.is_processed = True

    await db.commit()