# ai/chunking.py

import asyncio
import os

import aiofiles
from fastapi import HTTPException
from tree_sitter_languages import get_language, get_parser

text_file_types = {'.txt', '.md'}

code_file_types = {
    '.agda', '.sh', '.bash', '.bats',
    '.c', '.h', '.cc', '.cpp', '.cxx', '.c++', '.hh', '.hpp', '.hxx',
    '.cs', '.css', '.go', '.hs', '.lhs', '.html', '.htm',
    '.java', '.js', '.mjs', '.cjs', '.json', '.jl',
    '.ml', '.mli', '.php', '.php3', '.php4', '.php5', '.phtml',
    '.py', '.pyw', '.pyi', '.rb', '.rake', '.gemspec',
    '.rs', '.scala', '.sc', '.ts', '.tsx',
    '.v', '.vh', '.sv', '.svh',
}

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

# node types that represent meaningful code units across languages
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


async def chunk_file(file_path: str) -> list[str]:
    try:
        ext = os.path.splitext(file_path)[1].lower()

        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            content = await f.read()

        if not content.strip():
            return []

        if ext in text_file_types:
            return chunk_text_file(content)
        elif ext in code_file_types:
            return chunk_code_file(content, ext)
        else:
            return chunk_text_file(content)

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


def chunk_code_file(content: str, ext: str) -> list[str]:
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
                chunk = "\n".join(lines[start:end + 1])
                if chunk.strip():
                    chunks.append(chunk)

        if not chunks:
            return chunk_text_file(content)

        return chunks

    except Exception:
        return chunk_text_file(content)


def chunk_text_file(
    content: str,
    max_chunk_size: int = 1500,
    overlap: int = 200
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