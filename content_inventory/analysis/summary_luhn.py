import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from heapq import nlargest


class LuhnSummarizer:
    """Improved Luhn-based summarizer tuned for procedural and policy documents."""

    BOILERPLATE_PATTERNS = [
        r'continued on next page',
        r'summary of document changes',
        r'issue version number.*',
        r'published date.*',
        r'data classification.*',
        r'contact your supervisor',
        r'stop –',
        r'uncontrolled when printed',
        r'appendix [a-z]',
        r'©\d{4}',
        r'\btable \d+\b',
        r'\bfigure \d+\b',
        r'next review due.*',
        r'definitions/abbreviations',
        r'document purpose',
        r'overview, continued',
    ]

    def __init__(self, logger, max_sentences=7):
        self.logger = logger
        self.max_sentences = max_sentences
        nltk.download("punkt", quiet=True)
        nltk.download("stopwords", quiet=True)
        nltk.download("averaged_perceptron_tagger", quiet=True)
        self.stop_words = set(stopwords.words("english"))

    # --------------------------------------------------------------
    # Cleaning utilities
    # --------------------------------------------------------------
    def _clean_boilerplate(self, text):
        """Remove metadata, headings, and repeated procedural boilerplate."""
        text = re.sub(r"\s+", " ", text)
        for pat in self.BOILERPLATE_PATTERNS:
            text = re.sub(pat, " ", text, flags=re.IGNORECASE)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _is_informative(self, sentence):
        """Return True if the sentence is likely to contain useful information."""
        words = word_tokenize(sentence)
        # Ignore short, list-like, or table-style sentences
        if len(words) < 8 or len(words) > 40:
            return False
        # Must contain a verb
        tags = nltk.pos_tag(words)
        if not any(tag.startswith("VB") for _, tag in tags):
            return False
        # Skip headings or repeated patterns
        if re.search(r"(table|appendix|figure|continued|copyright)", sentence, re.I):
            return False
        return True

    # --------------------------------------------------------------
    # Core summarization
    # --------------------------------------------------------------
    def summarize(self, text):
        """Generate a 7-sentence readable summary paragraph."""
        if not text or len(text.split()) < 50:
            return text.strip()

        clean_text = self._clean_boilerplate(text)
        sentences = [s.strip() for s in sent_tokenize(clean_text) if self._is_informative(s)]

        # Fallback if filtering removed everything
        if not sentences:
            self.logger.debug("No informative sentences found; using fallback summary.")
            raw = " ".join(sent_tokenize(clean_text)[:3])
            return self._finalize_summary(raw)

        words = word_tokenize(clean_text.lower())
        freq = {}
        for word in words:
            if word not in self.stop_words and word not in string.punctuation:
                freq[word] = freq.get(word, 0) + 1

        if not freq:
            return self._finalize_summary(" ".join(sentences[:self.max_sentences]))

        max_freq = max(freq.values())
        for w in freq:
            freq[w] /= max_freq

        # Score informative sentences by average term frequency
        sentence_scores = {}
        for sent in sentences:
            sent_words = word_tokenize(sent.lower())
            score = sum(freq.get(w, 0) for w in sent_words)
            if score > 0:
                sentence_scores[sent] = score / len(sent_words)

        # Select top 7 (or fewer) sentences
        top_sents = nlargest(self.max_sentences, sentence_scores, key=sentence_scores.get)

        # Preserve original order for readability
        ordered = [s for s in sentences if s in top_sents]
        summary = " ".join(ordered[:self.max_sentences])
        return self._finalize_summary(summary)

    # --------------------------------------------------------------
    # Post-processing for readability
    # --------------------------------------------------------------
    def _finalize_summary(self, text):
        """Polish output into a single coherent paragraph."""
        text = re.sub(r"\s+([.,;:!?])", r"\1", text)
        text = re.sub(r"\s+", " ", text)
        text = text.strip()
        if not text.endswith("."):
            text += "."
        # Capitalize first letter if necessary
        if text and not text[0].isupper():
            text = text[0].upper() + text[1:]
        return text