import os
import re

from duckduckgo_search import DDGS

from .utils import clean_sources, is_trusted_source


class FactChecker:
    def __init__(self) -> None:
        self.model_name = os.getenv("OLLAMA_MODEL", "mistral")
        self.enabled = os.getenv("ENABLE_FACT_CHECKING", "true").lower() == "true"

    def check(self, text: str) -> tuple[str, list[dict[str, str]]]:
        if not self.enabled:
            return "AI fact checking is disabled for this server.", []

        claim = self._extract_claim(text)
        results = self._search(claim)
        sources = self._rank_sources(claim, results)
        if not sources:
            return "No relevant search sources were available to compare this claim.", []

        explanation = self._summarize(claim, sources)
        return explanation, sources

    @staticmethod
    def _extract_claim(text: str) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return max(sentences, key=len)[:500] if sentences else text[:500]

    @staticmethod
    def _search(claim: str) -> list[dict]:
        try:
            with DDGS() as search:
                return list(search.text(claim, max_results=8))
        except Exception:
            return []

    def _rank_sources(self, claim: str, results: list[dict]) -> list[dict[str, str]]:
        sources = clean_sources(results, limit=8)
        if not sources:
            return []

        try:
            return self._semantic_rank(claim, sources)
        except Exception:
            return sorted(
                sources,
                key=lambda source: is_trusted_source(source["url"]),
                reverse=True,
            )[:4]

    @staticmethod
    def _semantic_rank(claim: str, sources: list[dict[str, str]]) -> list[dict[str, str]]:
        import faiss
        from sentence_transformers import SentenceTransformer

        encoder = SentenceTransformer("all-MiniLM-L6-v2")
        documents = [f"{source['title']} {source['url']}" for source in sources]
        embeddings = encoder.encode([claim, *documents], normalize_embeddings=True)
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings[1:].astype("float32"))
        _, matches = index.search(embeddings[0:1].astype("float32"), min(4, len(sources)))
        ranked = [sources[index] for index in matches[0]]
        return sorted(ranked, key=lambda source: is_trusted_source(source["url"]), reverse=True)

    def _summarize(self, claim: str, sources: list[dict[str, str]]) -> str:
        source_text = "\n".join(f"- {source['title']}: {source['url']}" for source in sources)
        prompt = f"""You are a careful fact-checking assistant.
Claim: {claim}
Search results:
{source_text}

Explain in two or three sentences whether these results support, contradict, or are insufficient
to verify the claim. Do not claim that a search result proves something you cannot read. State
uncertainty clearly and refer to the sources by title."""
        try:
            from langchain_ollama import ChatOllama

            response = ChatOllama(model=self.model_name, temperature=0).invoke(prompt)
            return str(response.content).strip()
        except Exception:
            return (
                "Relevant sources were found, but the local Ollama model was unavailable to "
                "compare them. Review the linked sources directly."
            )
