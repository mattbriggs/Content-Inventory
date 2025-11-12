import csv
import os

class CSVExporter:
    def __init__(self, output_dir, logger):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.logger = logger

    def export_inventory(self, corpus, duplicates):
        self.logger.info("Exporting inventory CSV...")
        path = os.path.join(self.output_dir, "inventory.csv")
        with open(path, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Filename", "Word Count", "Summary"])
            for doc in corpus:
                writer.writerow([doc["filename"], doc["word_count"], doc["summary"]])

    def export_entities(self, entities):
        self.logger.info("Exporting entities CSV...")
        path = os.path.join(self.output_dir, "entities.csv")
        with open(path, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Entity", "Count"])
            for entity, count in entities.items():
                writer.writerow([entity, count])

    def export_duplicates(self, duplicates):
        self.logger.info("Exporting duplicates CSV...")
        path = os.path.join(self.output_dir, "duplicates.csv")
        with open(path, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Doc1", "Doc2", "Similarity"])
            for dupe in duplicates:
                writer.writerow([dupe["doc1"], dupe["doc2"], dupe["similarity"]])
