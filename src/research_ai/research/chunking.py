from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class DocumentChunker:
    def __init__(self,chunk_size :int =1000,chunk_overlap:int = 200):
        if chunk_size <= 0:
            raise ValueError("Chunk size must be positive.")

        if chunk_overlap < 0:
            raise ValueError("Chunk overlap cannot be negative.")

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class DocumentChunker:

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):

        if chunk_size <= 0:
            raise ValueError("Chunk size must be positive.")

        if chunk_overlap < 0:
            raise ValueError("Chunk overlap cannot be negative.")

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "Chunk overlap must be smaller than chunk size."
            )

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ],
            length_function=len,
            add_start_index=True
        )

    def split_documents(
        self,
        documents: list[Document]
    ) -> list[Document]:

        if not documents:
            return []

        chunks = self.splitter.split_documents(documents)
        for index, chunk in enumerate(chunks):

            source_id = chunk.metadata.get(
                "source_id",
                "unknown"
            )

            start_index = chunk.metadata.get(
                "start_index",
                0
            )

            chunk.metadata["chunk_id"] = (
                f"{source_id}_{start_index}"
            )

        return chunks


