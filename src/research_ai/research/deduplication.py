
import re
from urllib.parse import urlparse, urlunparse
from typing import Any

from langchain_core.documents import Document


class SourceDeduplicator:

    @staticmethod
    def _normalise_title(title: str) -> str:
        """Normalise titles for duplicate detection."""
        title = title.lower().strip()
        title = re.sub(r"[^a-z0-9\s]", "", title)
        return " ".join(title.split())

    @staticmethod
    def _normalise_url(url: str | None) -> str | None:
        """Normalise URLs to avoid duplicates caused by URL variations."""
        if not url:
            return None

        parsed = urlparse(url.strip())

        if not parsed.netloc:
            return url.strip().rstrip("/").lower()

        domain = parsed.netloc.lower().removeprefix("www.")
        path = parsed.path.rstrip("/")

        # Treat arXiv abstract and PDF URLs as the same paper.
        if "arxiv.org" in domain:
            path = re.sub(r"^/(abs|pdf)/", "/", path)
            path = path.removesuffix(".pdf")
            return f"arxiv:{path.strip('/').lower()}"

        return urlunparse((
            "https",
            domain,
            path,
            "",
            "",
            ""
        )).lower()

    def _normalise_web_results(self,results: Any) -> list[dict]:

        # Tavily may return a dictionary containing "results".
        if isinstance(results, dict):
            results = results.get("results", [])

        documents = []

        for result in results or []:
            documents.append({
                "source_type": "web",
                "title": result.get("title", ""),
                "content": (
                    result.get("content")
                    or result.get("raw_content")
                    or ""
                ),
                "url": result.get("url"),
                "metadata": {
                    key: value
                    for key, value in result.items()
                    if key not in {
                        "title", "content", "raw_content", "url"
                    }
                }
            })

        return documents

    def _normalise_academic_results(self,results: list[Document]) -> list[dict]:

        documents = []

        for result in results:
            metadata = dict(result.metadata)

            documents.append({
                "source_type": "academic",
                "title": metadata.get("title", ""),
                "content": result.page_content,
                "url": metadata.get("url"),
                "metadata": metadata
            })

        return documents

    def deduplicate(self,web_results: Any,academic_results: list[Document]) -> list[dict]:

        web_documents = self._normalise_web_results(web_results)
        academic_documents = self._normalise_academic_results( academic_results)

        # Process academic results first so paper abstracts are preserved.
        all_documents = academic_documents + web_documents

        unique_documents = []
        url_index = {}
        title_index = {}

        for document in all_documents:

            url_key = self._normalise_url(document["url"])
            title_key = self._normalise_title(document["title"])

            # Identify a duplicate by URL or normalised title.
            existing_index = None

            if url_key:
                existing_index = url_index.get(url_key)

            if existing_index is None and title_key:
                existing_index = title_index.get(title_key)

            if existing_index is not None:
                existing = unique_documents[existing_index]

                # Preserve the provenance of both sources.
                source_types = existing["source_types"]

                if document["source_type"] not in source_types:
                    source_types.append(document["source_type"])

                # Merge metadata without overwriting existing values.
                existing["metadata"].update({
                    key: value
                    for key, value in document["metadata"].items()
                    if key not in existing["metadata"]
                })

                # Prefer academic abstracts over web snippets.
                if document["source_type"] == "academic":
                    existing["content"] = document["content"]

                continue

            document["source_types"] = [document["source_type"]]

            index = len(unique_documents)
            unique_documents.append(document)

            if url_key:
                url_index[url_key] = index

            if title_key:
                title_index[title_key] = index

        return unique_documents
