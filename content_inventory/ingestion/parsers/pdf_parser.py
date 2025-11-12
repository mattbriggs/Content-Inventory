from pdfminer.high_level import extract_text
from content_inventory.analysis.summary_luhn import LuhnSummarizer
from nltk.sentiment import SentimentIntensityAnalyzer

class PDFParser:
    """Parses PDF files, summarizes them using Luhn's algorithm, and extracts sentiment."""

    def __init__(self, logger):
        self.logger = logger
        self.summarizer = LuhnSummarizer(logger)
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def parse(self, filepath):
        """Read and summarize a PDF file."""
        self.logger.info(f"Parsing PDF: {filepath}")
        try:
            text = extract_text(filepath) or ""
            if not text.strip():
                self.logger.warn(f"No extractable text in {filepath}")
                return {
                    "filename": filepath.split("/")[-1],
                    "path": filepath,
                    "text": "",
                    "summary": "",
                    "word_count": 0,
                    "sentiment": {"compound": 0.0}
                }

            summary = self.summarizer.summarize(text)
            sentiment = self.sentiment_analyzer.polarity_scores(text)

            return {
                "filename": filepath.split("/")[-1],
                "path": filepath,
                "text": text,
                "summary": summary,
                "word_count": len(text.split()),
                "sentiment": sentiment
            }

        except Exception as e:
            self.logger.error(f"Failed to parse PDF {filepath}: {e}")
            return {
                "filename": filepath.split("/")[-1],
                "path": filepath,
                "text": "",
                "summary": "",
                "word_count": 0,
                "sentiment": {"compound": 0.0}
            }