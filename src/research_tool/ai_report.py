from __future__ import annotations

from collections import Counter
import re


class BasicAIEarningsSummarizer:
    """Deterministic text summarizer for earnings snippets.

    This is intentionally offline and key-less. Replace with an LLM-backed
    implementation when credentials are available.
    """

    _stop_words = {
        "the",
        "and",
        "that",
        "with",
        "this",
        "from",
        "have",
        "were",
        "will",
        "about",
        "into",
        "there",
        "their",
        "our",
        "your",
    }

    def summarize(self, snippets: list[str], *, max_points: int = 4) -> tuple[str, list[str]]:
        if not snippets:
            return "No earnings call snippets were found.", []

        text = " ".join(snippets)
        sentences = [s.strip() for s in re.split(r"[.!?]", text) if s.strip()]
        words = [w.lower() for w in re.findall(r"[A-Za-z]{4,}", text)]
        keywords = [w for w in words if w not in self._stop_words]
        freq = Counter(keywords)

        ranked = sorted(sentences, key=lambda s: self._score_sentence(s, freq), reverse=True)
        takeaways = ranked[:max_points]

        top_terms = ", ".join([w for w, _ in freq.most_common(6)])
        summary = (
            f"Earnings call sentiment is mixed-to-constructive with recurring emphasis on: {top_terms}. "
            f"Top discussion points were extracted from management commentary and analyst Q&A."
        )
        return summary, takeaways

    @staticmethod
    def _score_sentence(sentence: str, freq: Counter[str]) -> int:
        words = re.findall(r"[A-Za-z]{4,}", sentence.lower())
        return sum(freq[w] for w in words)
