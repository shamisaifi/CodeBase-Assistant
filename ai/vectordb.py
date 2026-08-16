from sqlalchemy import select
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

    # chunk_with_context = f"# File: {file.file_name}\n\n{chunk}"
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

async def search_chunks(
        query_vector: list[float],
        session_id: int,
        db: AsyncSession,
        limit: int = 10
) -> list[CodeChunk]:
    result = await db.execute(
        select(CodeChunk)
        .where(CodeChunk.session_id == session_id)
        .order_by(CodeChunk.embedding.cosine_distance(query_vector))
        .limit(limit)
    )

    chunks = result.scalars().all()
    return chunks

