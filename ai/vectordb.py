from sqlalchemy.ext.asyncio import AsyncSession

from ai.embeddings import embed_chunks
from models.chunk import CodeChunk


async def store_chunks(
    chunks: list[str],
    file_id: int,
    session_id: int,
    db: AsyncSession
) -> None:
    if not chunks:
        return

    vectors = embed_chunks(chunks)

    for chunk, vector in zip(chunks, vectors):
        code_chunk = CodeChunk(
            content = chunk,
            embedding = vector,
            file_id = file_id,
            session_id = session_id
        )

        db.add(code_chunk)

    await db.commit()