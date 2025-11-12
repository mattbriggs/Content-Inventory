# Content Inventory — Design Overview

This project ingests a folder of mixed content types (TXT, MD, HTML, XML, DOCX, PDF), extracts structured metadata and linguistic insights, and stores results in both SQLite and CSV/Markdown reports. It combines modular software design patterns, NLTK-based NLP analysis, and extensible content processing.



## System Architecture

```
Files → Ingestion → Database → Analysis → Reports
```

1. **Ingestion Layer**
   - Scans directories recursively.
   - Identifies file type and selects appropriate parser (Text, DOCX, PDF).
   - Extracts full text, word count, sentiment, and summary.
   - Produces structured document objects for downstream use.

2. **Analysis Layer**
   - Performs entity extraction using NLTK (noun phrase identification via POS tagging).
   - Detects duplicate text segments using `difflib.SequenceMatcher`.
   - Generates extractive summaries using *Luhn’s 1958 algorithm* for frequency-based sentence ranking.
   - Computes document- and corpus-level sentiment via NLTK VADER.

3. **Persistence Layer (Repository Pattern)**
   - Handles SQLite interaction for persistent storage of:
     - Documents (`filename`, `summary`, `word_count`, `sentiment`)
     - Entities (`entity`, `count`)
     - Duplicates (`doc1`, `doc2`, `similarity`)
   - Designed for extensibility to alternative databases.
   - Encapsulates all SQL operations via a single repository class.

4. **Reporting Layer**
   - Exports CSVs for:
     - Inventory (filename, word count, summary)
     - Entities and counts
     - Duplicate pairs
   - Generates a Markdown summary with:
     - Total files and total words
     - Top 50 entities
     - Top 10 duplicate clusters
   - Provides easily ingestible data for analytics or dashboards.



## Key Design Patterns

| Pattern | Role | Example |
|----------|------|----------|
| **Factory** | Dynamically instantiates the correct parser based on file extension. | `FileIngestor` chooses between `TextParser`, `PDFParser`, and `DocxParser`. |
| **Strategy** | Encapsulates summarization and sentiment logic, enabling interchangeable NLP strategies. | `LuhnSummarizer` and `SentimentIntensityAnalyzer`. |
| **Repository** | Centralizes SQLite persistence logic. | `Repository` in `database/repository.py`. |
| **Observer (Logging)** | Provides progress feedback and error tracking across modules. | `Logger` utility emits verbose progress and error messages. |



## Core Components

### 1. FileIngestor
- Scans the source folder and delegates file handling to appropriate parsers.
- Logs all operations and errors.
- Returns a unified list of structured document dictionaries.

### 2. Parsers
- **TextParser**, **DocxParser**, and **PDFParser** each extract raw text.
- Each applies **LuhnSummarizer** for extractive summaries and NLTK VADER for sentiment.
- Future formats (e.g., HTML, XML) can be added by subclassing `BaseParser`.

### 3. LuhnSummarizer
- Implements H. P. Luhn’s 1958 frequency-based summarization algorithm.
- Identifies high-value sentences by word frequency and proximity.
- Produces concise, representative summaries of unstructured text.

### 4. EntityExtractor
- Uses NLTK POS tagging to extract noun phrases.
- Aggregates results into a corpus-level frequency distribution.

### 5. DuplicateDetector
- Compares documents pairwise using `SequenceMatcher`.
- Reports duplicate segments and similarity ratios above 0.8.

### 6. Repository
- Initializes and manages a SQLite database.
- Handles creation and insertion for all tables.
- Designed to support future queries for analytics or dashboards.

### 7. Reports
- **CSVExporter:** Creates structured CSV outputs for inventory, entities, and duplicates.
- **MarkdownReport:** Builds a human-readable summary with corpus stats and top entities.

### 8. Logger
- Provides a consistent verbose logging interface across all modules.
- Supports informational, warning, success, and error messages with timestamps.



## Iteration & Extension Guide

1. **Add a new parser**
   - Subclass `BaseParser` (planned module).
   - Implement `parse(filepath)` returning the same dictionary keys.
   - Register it in `FileIngestor`.

2. **Add new analysis features**
   - Create a module in `analysis/` and integrate it into `main.py`.
   - Examples: topic modeling, readability scoring, named entity linking.

3. **Switch summarization algorithms**
   - Implement a new summarizer class (e.g., TextRank or GPT-based).
   - Replace `LuhnSummarizer` in parser constructors.

4. **Expand persistence**
   - Add schema tables in `repository.py`.
   - Extend `insert_` methods and regenerate `docs` using Sphinx.

5. **Regenerate Documentation**
   ```bash
   cd docs
   sphinx-build -b html . _build/html
   ```



## Design Principles

- **Single Responsibility:** Each class handles one logical function (e.g., parsing, summarizing, reporting).
- **Loose Coupling:** Modules communicate via lightweight dictionaries, not class dependencies.
- **Extensibility:** New parsers or analysis components can be added without modifying the existing flow.
- **Transparency:** Verbose logging ensures visibility into all processing stages.



## Future Enhancements

- Add HTML/XML parsing using BeautifulSoup or lxml.
- Incorporate fuzzy duplicate detection via text embeddings.
- Implement BaseParser inheritance to reduce repeated logic.
- Add a web dashboard to visualize inventory and duplication.
- Integrate asynchronous I/O for faster ingestion of large corpora.



## Summary

The **Content Inventory Project** is a scalable, modular NLP pipeline for analyzing, summarizing, and reporting on diverse content sets.  
Its design balances *readability, extensibility, and linguistic depth*—using modern Python architecture while honoring classic NLP foundations such as Luhn's summarization model.
