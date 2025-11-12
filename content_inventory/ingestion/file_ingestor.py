import os
import concurrent.futures
import multiprocessing
from tqdm import tqdm
from content_inventory.utils.logger import Logger
from content_inventory.ingestion.parsers.text_parser import TextParser
from content_inventory.ingestion.parsers.pdf_parser import PDFParser
from content_inventory.ingestion.parsers.docx_parser import DocxParser

class FileIngestor:
    """Scans folders for supported files and parses them concurrently."""

    def __init__(self, logger: Logger):
        self.logger = logger
        # Detect number of CPU cores (Apple Silicon friendly)
        self.cpu_count = multiprocessing.cpu_count()
        self.logger.info(f"Detected {self.cpu_count} CPU cores available.")

    def _parse_file(self, filepath):
        """Internal helper to parse a single file safely."""
        parser = None
        file = os.path.basename(filepath)

        try:
            # Choose parser by file extension
            if file.lower().endswith(('.txt', '.md', '.html', '.xml')):
                parser = TextParser(self.logger)
            elif file.lower().endswith('.pdf'):
                parser = PDFParser(self.logger)
            elif file.lower().endswith('.docx'):
                parser = DocxParser(self.logger)
            else:
                return None  # unsupported

            parsed = parser.parse(filepath)
            self.logger.info(f"Parsed: {file} ({parsed['word_count']} words)")
            return parsed

        except Exception as e:
            self.logger.error(f"Failed to parse {file}: {e}")
            return None

    def ingest_folder(self, path):
        """Ingest all supported files in a directory using multithreading."""
        corpus = []
        self.logger.info(f"Scanning folder: {path}")

        # Gather all supported files
        filepaths = []
        for root, _, files in os.walk(path):
            for file in files:
                if file.lower().endswith(('.txt', '.md', '.html', '.xml', '.pdf', '.docx')):
                    filepaths.append(os.path.join(root, file))

        if not filepaths:
            self.logger.warn("No supported files found.")
            return corpus

        self.logger.info(f"Discovered {len(filepaths)} supported files.")
        max_workers = min(self.cpu_count, 8)  # reasonable cap
        self.logger.info(f"Processing files with {max_workers} concurrent threads...")

        # Multithreaded parsing with progress bar
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            for result in tqdm(
                executor.map(self._parse_file, filepaths),
                total=len(filepaths),
                desc="Parsing files",
                unit="file"
            ):
                if result:
                    corpus.append(result)

        self.logger.success(f"Ingested {len(corpus)} files total.")
        return corpus