import hashlib
import json 
import re
from langchain_core.documents import Document

class DocumentProcessor:

    @staticmethod
    def clean_text(text:str)->str:
        """Clean and standardise document text."""
        
        if not text:
            return ""
        
        text = re.sub(r"\s+"," ",text)

        return text.strip()

    @staticmethod
    def generate_source_id(url:str,title:str)->str:
        """Generate a stable ID for each source"""

        identifier = url or title

        return hashlib.sha256(identifier.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def prepare_metadata(source:dict)->dict:
        """Prepare metadat compatible with ChromaDB"""

        metadata = dict(source.get("metadata") or {})
        metadata["title"] = source.get("title","")
        metadata["url"] = source.get("url") or ""
        metadata["source_type"] = source.get("source_type","unknown")
        metadata["source_types"] = ",".join(source.get("source_types",[]))

        clean_metadata = {}

        for key,value in metadata.items():
            if value is None:
                continue
            if isinstance(value,(list,dict)):
                value = json.dumps(value,ensure_ascii = False)
            if isinstance(value,(str,int,float,bool)):
                clean_metadata[key] = value

        return clean_metadata

    def process(self,sources:list[dict]) -> list[Document]:
        documents = []

        for source in sources:
            title = self.clean_text(source.get("title",""))

            content = self.clean_text(source.get("content",""))

            if not content:
                continue

            url = source.get("url") or ""

            metadata = self.prepare_metadata(source)
            metadata["source_id"] = self.generate_source_id(url,title)
            page_content = f"title: {title}\n\n{content}"
            document = Document(
                page_content = page_content,
                metadata = metadata
            )

            documents.append(document)
        return documents