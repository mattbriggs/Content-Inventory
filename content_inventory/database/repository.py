# content_inventory/database/repository.py
import sqlite3

class Repository:
    """Handles all database interactions (CRUD) with SQLite."""

    def __init__(self, db_path, logger):
        self.logger = logger
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY,
            filename TEXT,
            summary TEXT,
            word_count INTEGER,
            sentiment REAL
        );
        CREATE TABLE IF NOT EXISTS entities (
            id INTEGER PRIMARY KEY,
            entity TEXT,
            count INTEGER
        );
        CREATE TABLE IF NOT EXISTS duplicates (
            id INTEGER PRIMARY KEY,
            doc1 TEXT,
            doc2 TEXT,
            similarity REAL
        );
        """)
        self.conn.commit()
        self.logger.info("SQLite tables created or verified.")

    def insert_document(self, doc):
        self.conn.execute(
            "INSERT INTO documents (filename, summary, word_count, sentiment) VALUES (?, ?, ?, ?)",
            (doc['filename'], doc['summary'], doc['word_count'], doc['sentiment']['compound'])
        )
        self.conn.commit()

    def insert_entities(self, entities):
        for e, c in entities.items():
            self.conn.execute("INSERT INTO entities (entity, count) VALUES (?, ?)", (e, c))
        self.conn.commit()

    def insert_duplicates(self, duplicates):
        for d in duplicates:
            self.conn.execute(
                "INSERT INTO duplicates (doc1, doc2, similarity) VALUES (?, ?, ?)",
                (d['doc1'], d['doc2'], d['similarity'])
            )
        self.conn.commit()

    def close(self):
        self.conn.close()