from docx import Document
from content_inventory.analysis.summary_luhn import LuhnSummarizer
from nltk.sentiment import SentimentIntensityAnalyzer

class DocxParser:
    """Parses .docx files and generates structured document data."""

    def __init__(self, logger):
        self.logger = logger
        self.summarizer = LuhnSummarizer(logger)
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def parse(self, filepath):
        """Read and summarize a DOCX file."""
        self.logger.info(f"Parsing DOCX: {filepath}")
        try:
            doc = Document(filepath)
            text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())

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
            self.logger.error(f"Failed to parse DOCX file {filepath}: {e}")
            return {
                "filename": filepath.split("/")[-1],
                "path": filepath,
                "text": "",
                "summary": "",
                "word_count": 0,
                "sentiment": {"compound": 0.0}
            }