
import arxiv

from langchain_core.documents import Document


class AcademicResearcher:

    def __init__(self, max_results: int = 5):

        self.max_results = max_results

        self.client = arxiv.Client(
            page_size=max_results,
            delay_seconds=3,
            num_retries=3
        )

    def search(self, query: str) -> list[Document]:

        if not query.strip():
            raise ValueError("Search query cannot be empty")

        search = arxiv.Search(
            query=query,
            max_results=self.max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        documents = []

        try:
            results = self.client.results(search)

            for paper in results:

                document = Document(
                    page_content=paper.summary,
                    metadata={
                        "source_type": "academic",
                        "title": paper.title,
                        "authors": [
                            author.name for author in paper.authors
                        ],
                        "published": paper.published.isoformat(),
                        "updated": paper.updated.isoformat(),
                        "arxiv_id": paper.get_short_id(),
                        "url": paper.entry_id,
                        "pdf_url": paper.pdf_url,
                        "categories": paper.categories
                    }
                )

                documents.append(document)

        except arxiv.ArxivError as error:
            raise RuntimeError(
                f"arXiv search failed: {error}"
            ) from error

        return documents
