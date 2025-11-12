"""
Main entry point for the Content Inventory project.
Handles ingestion, analysis, and reporting.
"""
import argparse
import os
from content_inventory.utils.logger import Logger
from content_inventory.ingestion.file_ingestor import FileIngestor
from content_inventory.analysis.entity_extractor import EntityExtractor
from content_inventory.analysis.duplicate_detector import DuplicateDetector
from content_inventory.reports.markdown_report import MarkdownReport
from content_inventory.reports.csv_exporter import CSVExporter
from content_inventory.database.repository import Repository 

def main():
    parser = argparse.ArgumentParser(description="Content Inventory Generator")
    parser.add_argument("--source", required=True, help="Path to folder with content files")
    parser.add_argument("--output", required=True, help="Path to output directory")
    args = parser.parse_args()

    logger = Logger(verbose=True)
    logger.info("Starting content inventory process...")

    # 1. Ingest
    ingestor = FileIngestor(logger)
    corpus = ingestor.ingest_folder(args.source)

    # 2. Analyze
    extractor = EntityExtractor(logger)
    extractor.process_corpus(corpus)

    dupe_detector = DuplicateDetector(logger)
    duplicates = dupe_detector.find_duplicates(corpus)

    # 3. Persist results in SQLite  ← ADD THIS BLOCK HERE
    repo = Repository(os.path.join(args.output, "inventory.db"), logger)
    for doc in corpus:
        repo.insert_document(doc)
    repo.insert_entities(extractor.entities)
    repo.insert_duplicates(duplicates)
    repo.close()

    # 4. Export reports
    csv_exporter = CSVExporter(args.output, logger)
    csv_exporter.export_inventory(corpus, duplicates)
    csv_exporter.export_entities(extractor.entities)
    csv_exporter.export_duplicates(duplicates)

    MarkdownReport(args.output, logger).generate_summary(corpus, extractor, duplicates)

    logger.success("Content inventory completed successfully.")

if __name__ == "__main__":
    main()
