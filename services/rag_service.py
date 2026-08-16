
import asyncio

from groq import Groq
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.chunking import chunk_multiple_files
from ai.embeddings import embed_query
from ai.vectordb import search_chunks, store_chunks
from config.settings import settings
from db.session import SessionLocal
from models.file import CodeFile

client = Groq(api_key=settings.GROQ_API_KEY)

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

async def rag_search(
    question: str,
    session_id: int,
    db: AsyncSession
) -> str:
    query_vector = embed_query(question)

    relevant_chunks = await search_chunks(query_vector, session_id, db)

    if not relevant_chunks:
        return "No relevant code found. Please upload code files first."

    context = "\n---\n".join([chunk.content for chunk in relevant_chunks])

    system_prompt = """You are a helpful code assistant. 
        Answer the user's question based ONLY on the code context provided.
        If the answer is not in the context, say "I cannot find this in the provided code."
        Be specific and reference actual function names and code from the context.
    """
    user_prompt = f"""CONTEXT: 
        ------
        {context}
        ------

        USER QUESTION:
        {question}"""

    response = await asyncio.to_thread(
        client.chat.completions.create,
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,
        max_tokens=1000,
    )

    return response.choices[0].message.content