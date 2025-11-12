# Content Inventory Project

A modular Python tool for building a **content inventory** from mixed document sources (TXT, MD, HTML, XML, DOCX, PDF).  
It extracts **summaries**, **entities**, **sentiment**, and **duplicates**, then exports structured data to **SQLite**, **CSV**, and **Markdown** reports.

## Features

- **Multi-format ingestion:** TXT, Markdown, HTML/XML, PDF, and DOCX  
- **Automatic summarization:** Implements H. P. Luhn's 1958 algorithm for extractive text summarization  
- **Entity extraction:** Identifies key noun phrases across the corpus  
- **Sentiment analysis:** Computes compound sentiment scores using NLTK's VADER  
- **Duplicate detection:** Finds overlapping or near-identical text between documents  
- **SQLite persistence:** Stores structured document, entity, and duplication data  
- **Structured reporting:**  
  - CSV exports for inventory, entities, and duplicates  
  - Markdown corpus summary report  
- **Verbose logging:** Detailed progress messages during ingestion, analysis, and export  
- **Extensible design:** Easily add new parsers, analyses, or output formats  

## System Architecture

```
Files → Ingestion → Analysis → Database → Reports
```

| Layer | Description |
|-------|--------------|
| **Ingestion** | Detects file types and extracts text using specialized parsers. |
| **Analysis** | Summarizes content (Luhn), identifies entities, detects duplicates, and scores sentiment. |
| **Database** | Stores processed data in SQLite for later retrieval. |
| **Reports** | Produces Markdown and CSV output for review or visualization. |

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/content_inventory.git
cd content_inventory
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Download required NLTK resources
```bash
python -m nltk.downloader punkt vader_lexicon averaged_perceptron_tagger stopwords
```

## Usage

Run the main script from the project root:

```bash
python -m content_inventory.main \
  --source "/path/to/source_folder" \
  --output "./output"
```

**Example:**
```bash
python -m content_inventory.main \
  --source "/Users/mattbriggs/Desktop/UnisonCorpus-Reduce" \
  --output "./output"
```

### Command-line Arguments

| Argument | Description |
|-----------|-------------|
| `--source` | Path to the folder containing input documents. |
| `--output` | Path to the folder where reports and the SQLite database will be written. |

## Output

After processing, the output folder contains:

| File | Description |
|------|--------------|
| `inventory.db` | SQLite database of documents, entities, and duplicates. |
| `inventory.csv` | File-level summaries (filename, word count, summary). |
| `entities.csv` | List of extracted noun phrases with frequency counts. |
| `duplicates.csv` | List of duplicate text pairs with similarity scores. |
| `report.md` | Markdown summary with top entities and duplicate statistics. |

## Processing Workflow

1. **FileIngestor** scans the source directory recursively, selecting the appropriate parser (Text, PDF, or DOCX).  
2. Each parser extracts text, summarizes it using **Luhn's algorithm**, and performs **sentiment analysis**.  
3. **EntityExtractor** collects and counts noun phrases across the corpus.  
4. **DuplicateDetector** compares documents pairwise for overlap and similarity.  
5. **Repository** persists results to SQLite.  
6. **CSVExporter** and **MarkdownReport** generate structured outputs.

## Example Markdown Summary

```
# Content Inventory Summary

**Total Files:** 812  
**Total Words:** 1,452,300  
**Duplicate Pairs:** 63  

## Top 10 Entities
- project: 214  
- server: 189  
- configuration: 172  
- update: 161  
- user: 150  
```

## Architecture Highlights

- **Factory Pattern** -- dynamically selects the parser based on file extension.  
- **Strategy Pattern** -- Luhn summarization and sentiment analysis implemented as interchangeable strategies.  
- **Repository Pattern** -- central SQLite interface for data persistence.  
- **Observer Pattern** -- unified verbose logging system with timestamps.  

## Extending the Project

| Task | Steps |
|------|-------|
| Add a new file type | Implement a new parser in `ingestion/parsers/` and register it in `FileIngestor`. |
| Use a different summarizer | Replace `LuhnSummarizer` in `analysis/summary_luhn.py` with your own algorithm. |
| Add custom analytics | Extend `Repository` and `MarkdownReport` modules. |
| Integrate into a web app | Connect `inventory.db` to a dashboard or API. |

## Documentation

To generate HTML documentation using Sphinx:

```bash
cd docs
sphinx-build -b html . _build/html
```

Open:
```
_build/html/index.html
```

## Requirements

- Python 3.10 or later  
- macOS, Linux, or Windows  

See `requirements.txt` for full dependencies:
- NLTK  
- pdfminer.six  
- python-docx  
- pandas, numpy  
- tqdm  
- PyYAML  
- prettytable  

## Setting Up NLTK in a Virtual Environment

This project uses the Natural Language Toolkit (**NLTK**) for tokenization, part-of-speech tagging, lemmatization, and sentiment analysis. 
 
When you run it inside a virtual environment, you need to download the required NLTK data packages once for that environment.

### 1. Activate your virtual environment
Make sure your environment is active before downloading the NLTK data.

```bash
# Example for macOS or Linux
source venv/bin/activate

# Example for Windows
venv\Scripts\activate
```

### 2. Run the NLTK downloader
Use the following command to download all required resources into your active virtual environment:

```bash
python -m nltk.downloader punkt vader_lexicon averaged_perceptron_tagger wordnet omw-1.4 stopwords
```

This installs:
- `punkt` -- sentence and word tokenization  
- `vader_lexicon` -- sentiment analysis  
- `averaged_perceptron_tagger` -- part-of-speech tagging  
- `wordnet` and `omw-1.4` -- lemmatization and multilingual support  
- `stopwords` -- for filtering common words during entity extraction

### 3. Verify installation
You can confirm that NLTK data has been downloaded correctly:

```bash
python -m nltk.downloader -d ~/nltk_data list
```

This lists all installed datasets. You should see the above packages marked as “installed.”

### 4. Optional: Specify a custom data directory
If your organization or environment restricts downloads, you can specify a local path:

```bash
python -m nltk.downloader -d ./nltk_data punkt vader_lexicon averaged_perceptron_tagger wordnet omw-1.4 stopwords
```

Then, set the environment variable so your code finds it:

```bash
export NLTK_DATA=./nltk_data
```

### 5. Troubleshooting (macOS Certificate Issue)
If you see SSL errors when downloading data, run this command once:

```bash
/Applications/Python\ 3*/Install\ Certificates.command
```

This updates your certificate store so the downloader can access NLTK’s data servers.

## License

This project is licensed under the MIT License.  
You may use, modify, and distribute it with attribution.
