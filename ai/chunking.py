import asyncio
import os

import aiofiles
from fastapi import HTTPException
from tree_sitter_languages import get_parser

text_file_types = {'.txt', '.md'}

code_file_types = [
    '.agda', '.sh', '.bash', '.bats',
    '.c', '.h', '.cc', '.cpp', '.cxx', '.c++', '.hh', '.hpp', '.hxx',
    '.cs', '.css', '.go', '.hs', '.lhs', '.html', '.htm',
    '.java', '.js', '.mjs', '.cjs', '.json', '.jl',
    '.ml', '.mli', '.php', '.php3', '.php4', '.php5', '.phtml',
    '.py', '.pyw', '.pyi', '.rb', '.rake', '.gemspec',
    '.rs', '.scala', '.sc', '.ts', '.tsx',
    '.v', '.vh', '.sv', '.svh',
]

EXTENSION_TO_LANGUAGE = {
    '.agda': 'agda', '.sh': 'bash', '.bash': 'bash', '.bats': 'bash',
    '.c': 'c', '.h': 'c', '.cc': 'cpp', '.cpp': 'cpp', '.cxx': 'cpp',
    '.c++': 'cpp', '.hh': 'cpp', '.hpp': 'cpp', '.hxx': 'cpp',
    '.cs': 'c_sharp', '.css': 'css', '.go': 'go',
    '.hs': 'haskell', '.lhs': 'haskell',
    '.html': 'html', '.htm': 'html',
    '.java': 'java', '.js': 'javascript', '.mjs': 'javascript', '.cjs': 'javascript',
    '.json': 'json', '.jl': 'julia',
    '.ml': 'ocaml', '.mli': 'ocaml',
    '.php': 'php', '.php3': 'php', '.php4': 'php', '.php5': 'php', '.phtml': 'php',
    '.py': 'python', '.pyw': 'python', '.pyi': 'python',
    '.rb': 'ruby', '.rake': 'ruby', '.gemspec': 'ruby',
    '.rs': 'rust', '.scala': 'scala', '.sc': 'scala',
    '.ts': 'typescript', '.tsx': 'tsx',
    '.v': 'verilog', '.vh': 'verilog', '.sv': 'verilog', '.svh': 'verilog',
}

CHUNK_NODE_TYPES = {
    'function_definition',
    'class_definition',
    'function_declaration',
    'class_declaration',
    'method_declaration',
    'method_definition',
    'func_literal',
    'function_item',
    'impl_item',
    'def',
    'class',
}

MAX_CHUNK_SIZE = 1200  # characters — keep chunks focused
OVERLAP_SIZE = 150


async def chunk_file(file_path: str) -> list[str]:
    try:
        ext = os.path.splitext(file_path)[1].lower()

        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            content = await f.read()

        if not content.strip():
            return []

        # inject filename into content so LLM knows which file each chunk is from
        file_name = os.path.basename(file_path)
        content_with_header = f"# File: {file_name}\n\n{content}"

        if ext in text_file_types:
            return chunk_text_file(content_with_header)
        elif ext in code_file_types:
            return chunk_code_file(content, ext, file_name)
        else:
            return chunk_text_file(content_with_header)

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File contains unreadable characters")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to chunk file: {str(e)}")


async def chunk_multiple_files(file_paths: list[str]) -> dict[str, list[str]]:
    async def chunk_with_path(path: str):
        chunks = await chunk_file(path)
        return path, chunks

    results = await asyncio.gather(
        *(chunk_with_path(path) for path in file_paths),
        return_exceptions=True
    )

    output = {}
    for result in results:
        if isinstance(result, Exception):
            continue
        path, chunks = result
        output[path] = chunks

    return output


def chunk_code_file(content: str, ext: str, file_name: str = "") -> list[str]:
    language_name = EXTENSION_TO_LANGUAGE.get(ext)
    if not language_name:
        return chunk_text_file(content)

    try:
        parser = get_parser(language_name)
        tree = parser.parse(bytes(content, "utf-8"))
        root = tree.root_node
        lines = content.split("\n")
        chunks = []

        for node in root.children:
            if node.type in CHUNK_NODE_TYPES:
                start = node.start_point[0]
                end = node.end_point[0]
                raw_chunk = "\n".join(lines[start:end + 1])

                if not raw_chunk.strip():
                    continue

                header = f"# File: {file_name}\n" if file_name else ""
                chunk_with_header = header + raw_chunk

                if len(chunk_with_header) > MAX_CHUNK_SIZE:
                    sub_chunks = _split_large_function(raw_chunk, file_name)
                    chunks.extend(sub_chunks)
                else:
                    chunks.append(chunk_with_header)

        if not chunks:
            return chunk_text_file(content)

        return chunks

    except Exception:
        return chunk_text_file(content)


def _split_large_function(raw_chunk: str, file_name: str) -> list[str]:
    lines = raw_chunk.split("\n")
    
    # function signature = first 1-3 lines (def line + decorators above it)
    signature_lines = lines[:3]
    signature = "\n".join(signature_lines)
    header = f"# File: {file_name}\n" if file_name else ""

    body_lines = lines[3:]
    body = "\n".join(body_lines)

    # split body using text chunker
    body_chunks = chunk_text_file(body, max_chunk_size=MAX_CHUNK_SIZE - len(signature) - 50, overlap=OVERLAP_SIZE)

    result = []
    for i, body_chunk in enumerate(body_chunks):
        # every sub-chunk gets: header + signature + [continued] marker + body piece
        label = f"# [Part {i+1} of {len(body_chunks)}]\n" if len(body_chunks) > 1 else ""
        result.append(f"{header}{label}{signature}\n...\n{body_chunk}")

    return result if result else [f"{header}{raw_chunk}"]


def chunk_text_file(
    content: str,
    max_chunk_size: int = MAX_CHUNK_SIZE,
    overlap: int = OVERLAP_SIZE
) -> list[str]:
    chunk_list = []
    current_chunk = ""
    overlap_text = ""

    paragraphs = content.split("\n\n")

    for para in paragraphs:
        if not para.strip():
            continue

        if len(current_chunk) + len(para) <= max_chunk_size:
            current_chunk += para + "\n\n"
            overlap_text = para[-overlap:]
        else:
            if current_chunk.strip():
                chunk_list.append(current_chunk.strip())
            current_chunk = overlap_text + "\n\n" + para + "\n\n"
            overlap_text = para[-overlap:]

    if current_chunk.strip():
        chunk_list.append(current_chunk.strip())

    return chunk_list
