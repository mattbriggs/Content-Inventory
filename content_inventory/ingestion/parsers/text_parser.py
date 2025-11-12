from content_inventory.analysis.summary_luhn import LuhnSummarizer
from nltk.sentiment import SentimentIntensityAnalyzer

class TextParser:
    def __init__(self, logger):
        self.logger = logger
        self.summarizer = LuhnSummarizer(logger)
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def parse(self, filepath):
        self.logger.info(f"Parsing file: {filepath}")
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()

        summary = self.summarizer.summarize(text)
        words = summary.split()
        sentiment = self.sentiment_analyzer.polarity_scores(text)

        return {
            "filename": filepath.split("/")[-1],
            "path": filepath,
            "word_count": len(words),
            "summary": summary,
            "text": text,
            "sentiment": sentiment
        }