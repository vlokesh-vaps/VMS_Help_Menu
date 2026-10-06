"""Build the vector database from PDF using pymupdf4llm for Markdown extraction."""

import shutil

import pymupdf4llm
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import MarkdownTextSplitter

from src.config import (
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    OLLAMA_BASE_URL,
    PDF_CHUNK_OVERLAP,
    PDF_CHUNK_SIZE,
    PDF_PATH,
    PERSIST_DIRECTORY,
)


def load_pdf_documents() -> list[Document]:
    """
    Extract text from PDF as Markdown using pymupdf4llm.

    pymupdf4llm converts each page into structured Markdown,
    preserving headings, tables, lists, and code blocks — which
    results in semantically cleaner chunks compared to raw text.

    Returns:
        List of LangChain Documents, one per PDF page.

    Raises:
        FileNotFoundError: If PDF file doesn't exist.
        ValueError: If no content could be extracted from PDF.
    """
    PERSIST_DIRECTORY.parent.mkdir(parents=True, exist_ok=True)

    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"PDF file not found at: {PDF_PATH}. "
            "Add your PDF content and run again."
        )

    # pymupdf4llm.to_markdown returns a list of dicts, one per page:
    # [{"metadata": {"page": 0, "file_path": "..."}, "text": "<markdown>"}]
    pages = pymupdf4llm.to_markdown(str(PDF_PATH), page_chunks=True)

    if not pages:
        raise ValueError(f"No content could be extracted from {PDF_PATH}")

    documents: list[Document] = []
    for page in pages:
        md_text: str = page.get("text", "").strip()
        if not md_text:
            continue

        # page index in pymupdf4llm is 0-based; convert to 1-based for metadata
        page_num: int = page.get("metadata", {}).get("page", 0) + 1

        documents.append(
            Document(
                page_content=md_text,
                metadata={
                    "source": str(PDF_PATH),
                    "page": page_num,
                },
            )
        )

    if not documents:
        raise ValueError(f"All pages were empty in {PDF_PATH}")

    return documents


def build_vector_store() -> None:
    """
    Build and persist the vector database from PDF.

    Uses pymupdf4llm for Markdown-aware extraction, MarkdownTextSplitter
    for structure-preserving chunking, OllamaEmbeddings for vectors,
    and Chroma for persistence.
    """
    PERSIST_DIRECTORY.parent.mkdir(parents=True, exist_ok=True)
    documents = load_pdf_documents()

    # MarkdownTextSplitter respects Markdown heading boundaries,
    # producing chunks that don't split mid-section.
    text_splitter = MarkdownTextSplitter(
        chunk_size=PDF_CHUNK_SIZE,
        chunk_overlap=PDF_CHUNK_OVERLAP,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Loaded {len(documents)} pages -> created {len(chunks)} chunks.")

    embedding_model = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)

    if PERSIST_DIRECTORY.exists():
        shutil.rmtree(PERSIST_DIRECTORY)
    PERSIST_DIRECTORY.mkdir(parents=True, exist_ok=True)

    Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        collection_name=COLLECTION_NAME,
        persist_directory=str(PERSIST_DIRECTORY),
    )

    print(
        f"[OK] Vector DB saved to {PERSIST_DIRECTORY.resolve()} "
        f"in collection '{COLLECTION_NAME}'."
    )


if __name__ == "__main__":
    build_vector_store()
