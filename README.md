# Hindi-English Positional Inverted Index

**Information Retrieval Assignment · M2026**  
**Student roll number:** `S20240030403`  
**Implementation:** Python 3.10+  
**Index type:** Disk-based positional inverted index

A Python text indexer for UTF-8 Hindi and English documents. It records each term's collection frequency (CF), document frequency (DF), and exact token positions. The vocabulary and postings pointers are held in main memory, while the complete positional postings data is stored on secondary storage and retrieved by byte offset.

---

## Contents

- [1. Quick start](#1-quick-start)
- [2. Project overview](#2-project-overview)
- [3. Dataset and submission scope](#3-dataset-and-submission-scope)
- [4. Project structure](#4-project-structure)
- [5. Requirements and setup](#5-requirements-and-setup)
- [6. Prepare the input documents](#6-prepare-the-input-documents)
- [7. Build the index](#7-build-the-index)
- [8. Search and query examples](#8-search-and-query-examples)
- [9. Index format and position convention](#9-index-format-and-position-convention)
- [10. Main memory and secondary storage](#10-main-memory-and-secondary-storage)
- [11. Collection statistics](#11-collection-statistics)
- [12. Test cases and rare-term output](#12-test-cases-and-rare-term-output)
- [13. Run the automated tests](#13-run-the-automated-tests)
- [14. Module descriptions](#14-module-descriptions)
- [15. Implementation notes](#15-implementation-notes)
- [16. Limitations](#16-limitations)
- [17. Troubleshooting](#17-troubleshooting)

---

## 1. Quick start

> **Before running:** the assignment ZIP intentionally excludes the original dataset and generated index. Place the five supplied UTF-8 `.txt` documents in `dataset/documents/` (or provide their location with `--docs`).

Open a terminal in the project root, the directory containing `README.md` and `src/`.

**Build the index** (default input and output paths):

```bash
python src/main.py
```

**Look up a term:**

```bash
python src/main.py --no-build --query "को"
```

**Search an exact phrase:**

```bash
python src/main.py --no-build --phrase "परियोजना में जोड़ें"
```

**Rank documents with BM25:**

```bash
python src/main.py --no-build --rank "परियोजना में जोड़ें" --top-k 5
```

**Run the tests:**

```bash
python -m unittest discover -s src/tests -v
```

The default generated index directory is `./index/`. Build the index once before using any `--no-build` query command.

---

## 2. Project overview

A conventional sequential search scans every document whenever a query is submitted. An inverted index prepares a term-to-document lookup structure in advance. A **positional** inverted index goes one step further: it stores the exact token positions of each term in each document.

For example, the following is an illustrative posting (not a claim about a particular corpus occurrence):

```text
भारत
  CF: 3
  DF: 2
  doc00: [2, 9]
  doc02: [8]
```

This project provides the following functionality:

1. Read UTF-8 text documents from a directory.
2. Normalize text using Unicode NFC normalization.
3. Tokenize Devanagari Hindi and Latin-script English words.
4. Assign document IDs and 1-indexed token positions.
5. Build a vocabulary of unique terms and calculate CF and DF.
6. Store positional postings on disk in JSON Lines format.
7. Keep the vocabulary and postings pointers in RAM during querying.
8. Retrieve an individual postings record using its byte offset and length.
9. Support single-term lookup and exact phrase search.
10. Display the top five terms by CF or DF.
11. Rank matching documents for a multi-term query using BM25.

## 3. Dataset and submission scope

The implementation was developed and tested with the five UTF-8 text documents supplied for this assignment. The supplied files were described by the student as a sample from a larger Hindi-English collection. The submitted archive does **not** contain the complete collection and does not claim to index it.

The supplied dataset archive did not include a formal citation, release/version, licence, source URL, or alignment metadata. Therefore, the relationship to the larger collection is recorded as student-provided context rather than independently verified provenance. If a formal citation is required, use the citation provided by the instructor or dataset provider.

The assignment instructions say not to include the entire dataset or generated index in the submission archive. Accordingly, neither the original documents nor the generated index files are bundled here. Keep the input documents separately and follow the setup instructions below.

## 4. Project structure

```text
S20240030403-A1-PostIndex-IR-M2026/
├── README.md
├── src/
│   ├── main.py
│   ├── dataset_loader.py
│   ├── preprocessing.py
│   ├── indexer.py
│   ├── storage.py
│   ├── query_processor.py
│   ├── crawler.py
│   ├── requirements.txt
│   └── tests/
│       └── test_index.py
└── output/
    ├── test_cases.txt
    ├── rare_terms_output.txt
    ├── top_terms_report.txt
    ├── document_ranking_example.txt
    └── test_results.txt
```

| Path | Purpose |
|---|---|
| `README.md` | Setup, execution guide, design explanation, and module reference |
| `src/main.py` | Command-line entry point for building and querying the index |
| `src/dataset_loader.py` | Finds and reads UTF-8 text documents |
| `src/preprocessing.py` | Unicode normalization and Hindi/English tokenization |
| `src/indexer.py` | SPIMI-style block construction, merge, CF/DF calculation, and vocabulary generation |
| `src/storage.py` | Writes postings records and reads records by byte offset and length |
| `src/query_processor.py` | Term lookup, phrase search, CF/DF ranking, and BM25 ranking |
| `src/crawler.py` | Optional web-crawling helper; not used to create the supplied sample corpus |
| `src/tests/test_index.py` | Automated tests using temporary documents |
| `src/requirements.txt` | Dependencies for the optional crawler; core indexing does not require them |
| `output/` | Five test cases, ten rare-term positional results, and supporting reports |

The `index/` directory is created when the index is built. It is intentionally absent from this submission package.

## 5. Requirements and setup

### Software requirements

- Python 3.10 or newer.
- Windows, Linux, or macOS.
- UTF-8 plain-text input documents (`.txt`).
- A terminal (PowerShell/Command Prompt on Windows, Terminal on Linux/macOS).

The indexer, query processor, and automated tests use only the Python standard library. No GPU, database server, or internet connection is required for indexing or querying. The packages in `src/requirements.txt` are only for the optional crawler.

### Check Python

Windows:

```powershell
python --version
```

Linux/macOS:

```bash
python3 --version
```

### (Recommended) Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

No package installation is needed for the core indexer. If you intend to use the optional crawler, install its dependencies from the project root:

```bash
python -m pip install -r src/requirements.txt
```

## 6. Prepare the input documents

Extract the five supplied dataset text files separately. The default directory expected by the program is `dataset/documents/`, relative to the project root.

```text
project-root/
├── README.md
├── src/
├── output/
└── dataset/
    └── documents/
        ├── doc00.txt
        ├── doc01.txt
        ├── doc02.txt
        ├── doc03.txt
        └── doc04.txt
```

The loader searches the specified directory recursively for `.txt` files, reads them as UTF-8, sorts their relative paths to assign deterministic document IDs, and rejects empty documents. If the documents are stored elsewhere, pass their folder path using `--docs` when building the index.

**Windows example:**

```powershell
python src/main.py --docs "C:\Users\YourName\Documents\dataset_ir"
```

**Linux/macOS example:**

```bash
python src/main.py --docs "/home/yourname/dataset_ir"
```

Replace the example paths with the actual folder containing the `.txt` files.

## 7. Build the index

From the project root, run:

```bash
python src/main.py
```

This uses the default input directory `dataset/documents/` and writes the generated index to `index/`.

To specify both paths:

```bash
python src/main.py --docs "PATH_TO_DOCUMENT_FOLDER" --index "PATH_TO_INDEX_FOLDER"
```

To change the maximum number of document-term postings accumulated in a block before it is flushed to a temporary sorted run:

```bash
python src/main.py --block-limit 1000
```

The build process performs the following operations:

1. Loads and tokenizes each input document.
2. Assigns positions starting at 1 for each document.
3. Accumulates term-to-document positional postings in bounded blocks.
4. Flushes sorted temporary runs to disk when the configured block limit is reached.
5. Merges the sorted runs term by term.
6. Calculates each term's CF and DF.
7. Writes positional postings records to `index/postings.jsonl`.
8. Writes the vocabulary and pointers to `index/vocabulary.json`.
9. Writes collection and document-length information to `index/index_metadata.json`.

The temporary runs are removed after the build completes.

## 8. Search and query examples

Run query commands from the project root after a successful build. The `--no-build` flag tells the program to use the existing index rather than rebuilding it. If a custom index directory was used during construction, pass the same directory with `--index` in every query command.

### Single-term lookup

```bash
python src/main.py --no-build --query "को"
```

Returns the term, language label, CF, DF, and postings. Each posting contains a document ID and its ordered list of token positions. An unknown term returns a `Term not found` message.

### Exact phrase search

```bash
python src/main.py --no-build --phrase "परियोजना में जोड़ें"
```

Returns documents where the phrase terms occur in the same document at consecutive positions and in the given order. The returned positions are the starting positions of matching phrases.

### Top terms by Collection Frequency

```bash
python src/main.py --no-build --top-cf
```

Displays the five terms with the highest total occurrence count across the collection.

### Top terms by Document Frequency

```bash
python src/main.py --no-build --top-df
```

Displays the five terms appearing in the largest number of distinct documents.

### BM25 document ranking

```bash
python src/main.py --no-build --rank "परियोजना में जोड़ें" --top-k 5
```

Ranks documents containing at least one query term. The output includes rank, document ID, BM25 score, matched terms, and document length. The default `--top-k` value is 5; it must be at least 1.

### Use a custom index directory

If the index was built in a directory other than `./index`, specify it explicitly:

```bash
python src/main.py --no-build --index "PATH_TO_INDEX_FOLDER" --query "को"
```

## 9. Index format and position convention

### Tokenization

- Text is normalized to Unicode NFC.
- Devanagari Hindi and Latin-script English lexical words are indexed.
- Punctuation, whitespace, symbols, and numerals act as token boundaries; numerals are not indexed as terms.
- Stop words are retained.
- Stemming and lemmatization are not performed.

### Position numbering

Positions are **1-indexed** and restart at 1 for every document. Hindi and English tokens are counted in the same token stream. Consequently, English tokens occurring before a Hindi term contribute to that Hindi term's position. Positions represent token numbers, not line numbers, character offsets, or byte offsets.

### CF, DF, and postings

For a vocabulary term `t`:

- **Collection Frequency (CF):** total number of occurrences of `t` across all documents.
- **Document Frequency (DF):** number of distinct documents containing `t` at least once.
- **Posting:** a document identifier and the ordered positions where `t` occurs in that document.

The sum of the lengths of all positional lists for a term equals its CF. The number of document postings for that term equals its DF.

### Phrase matching

A phrase matches only if all its terms occur in one document at consecutive positions in the specified order. For a three-term phrase beginning at position `p`, the terms must occur at `p`, `p + 1`, and `p + 2`.

### BM25 ranking

BM25 uses term frequency derived from the number of stored positions, document frequency, collection size, and document length. The implementation uses `k1 = 1.5` and `b = 0.75`. Scores depend on the query and the indexed collection; they are not fixed document-quality ratings.

## 10. Main memory and secondary storage

The storage design separates the vocabulary from the complete postings data:

- `vocabulary.json` contains each term's CF, DF, language label, and a pointer to its postings record.
- `postings.jsonl` contains the complete positional postings records on secondary storage.
- The pointer stores a byte `offset` and `length` for the corresponding record.

When a query is processed, the vocabulary metadata is loaded into RAM. For a term lookup, the storage layer seeks to the saved byte offset in `postings.jsonl` and reads the specified record length. It does not need to load the entire postings file into memory for that lookup.

The index builder uses temporary sorted runs to bound the in-memory construction block, then merges those runs into the final disk-resident postings file.

## 11. Collection statistics

For the five supplied documents, the bilingual tokenizer produced the following statistics:

| Measure | Count |
|---|---:|
| Documents | 5 |
| Hindi tokens | 75,965 |
| English tokens | 11,159 |
| Total indexed tokens | 87,124 |
| Unique vocabulary terms | 2,491 |

Per-document token counts:

| Document | Hindi tokens | English tokens | Total tokens |
|---|---:|---:|---:|
| `doc00` | 19,100 | 2,055 | 21,155 |
| `doc01` | 14,020 | 4,450 | 18,470 |
| `doc02` | 13,987 | 1,615 | 15,602 |
| `doc03` | 14,426 | 1,524 | 15,950 |
| `doc04` | 14,432 | 1,515 | 15,947 |

These figures describe only the five supplied sample files. They must not be interpreted as statistics for the larger collection from which the sample was described as originating.

## 12. Test cases and rare-term output

The `output/` directory contains the required five test cases and ten rare-term examples:

- `test_cases.txt` — five test cases, with two rare terms in each case.
- `rare_terms_output.txt` — the ten terms with their CF, DF, document IDs, and positional lists.

For the supplied five-document sample, each selected rare term has `CF = 1` and `DF = 1`. The listed positions use the same 1-indexed bilingual token convention as the index. These files are UTF-8; use an editor with UTF-8 support to view Devanagari characters correctly.

Additional output files:

- `top_terms_report.txt` — top terms by CF and DF from the sample index.
- `document_ranking_example.txt` — an example BM25 query and ranking.
- `test_results.txt` — saved summary of the automated test run.

## 13. Run the automated tests

The tests create small temporary collections and build temporary indexes. The original dataset and a prebuilt index are not required to run them.

From the project root:

```bash
python -m unittest discover -s src/tests -v
```

The suite covers:

- Hindi and English tokenization and punctuation handling.
- Unicode NFC normalization.
- CF and DF calculations.
- Exact 1-indexed positions and multiple occurrences.
- Phrase matching and non-matching phrases.
- Missing-term handling.
- Disk byte-offset postings retrieval.
- Vocabulary and postings consistency.
- UTF-8 document loading and deterministic document IDs.
- Top-CF and top-DF ranking.
- BM25 document ranking.

A successful run ends with `OK` and reports the number of tests executed.

## 14. Module descriptions

### `src/main.py`

Defines the command-line interface. It parses build and query options, loads documents when building, invokes the indexer, and routes term, phrase, frequency-ranking, and BM25 queries to the query processor.

### `src/dataset_loader.py`

Searches the input directory recursively for `.txt` files, sorts paths deterministically, reads each file as UTF-8, assigns document IDs from relative paths, and rejects empty documents.

### `src/preprocessing.py`

Applies Unicode NFC normalization and extracts Hindi Devanagari and English Latin-script lexical tokens. It also exposes token-language information used for collection statistics.

### `src/indexer.py`

Builds the index using bounded SPIMI-style blocks. It writes sorted temporary runs, merges terms across runs, combines document postings, calculates CF and DF, and writes vocabulary metadata and disk-resident positional postings.

### `src/storage.py`

Implements the postings storage interface. It serializes postings records to JSON Lines and retrieves an individual record using its byte offset and byte length.

### `src/query_processor.py`

Loads the vocabulary and index metadata, retrieves postings for a term, performs exact positional phrase search, ranks terms by CF or DF, and ranks matching documents with BM25.

### `src/crawler.py`

Contains an optional web-crawling helper retained from the starter project. It was not used to generate the five supplied input documents. Before crawling a website, follow its terms of service, robots instructions, rate limits, and applicable copyright rules.

### `src/tests/test_index.py`

Contains automated unit tests for tokenization, indexing, storage, positional retrieval, phrase matching, frequency statistics, and BM25 ranking.

## 15. Implementation notes

- Document IDs are derived from each input file's relative path without the `.txt` extension. For example, `nested/article.txt` becomes `nested/article`.
- Document paths are sorted before IDs are assigned, making the order deterministic for a fixed directory structure.
- Positions are assigned after tokenization, so punctuation and numerals do not occupy positions.
- Both Hindi and English terms share the same positional stream within a document.
- The vocabulary is serialized as UTF-8 JSON with non-ASCII characters preserved.
- Positional postings are serialized as UTF-8 JSON Lines records.
- Temporary build runs are removed after the merge completes.

## 16. Limitations

- The packaged example reports results for five sample documents, not the complete larger collection.
- The tokenizer is script-based and lexical. It does not perform Hindi morphological analysis, stemming, lemmatization, or stop-word removal.
- Numerals are treated as token boundaries and are not indexed.
- The optional crawler is not used to produce the supplied sample corpus.
- BM25 ranking is lexical and query-dependent; it is not a semantic search model.

## 17. Troubleshooting

| Problem | Suggested check |
|---|---|
| `Document directory does not exist` | Place the `.txt` files in `dataset/documents/` or pass the correct directory with `--docs`. |
| `No module named ...` when running a source file | Run commands from the project root using `python src/main.py ...`; do not run from inside `src/`. |
| Query reports that an index file is missing | Build the index first with `python src/main.py`, or pass the correct existing path with `--index`. |
| Query returns no result | Check spelling, tokenization, and whether the term exists in the indexed documents. Phrase search requires consecutive positions. |
| Hindi characters appear incorrectly | Open the files in a UTF-8-capable editor or terminal. |
| PowerShell blocks virtual-environment activation | You can skip activation and run `python src/main.py` directly, or use the Python launcher without a virtual environment. |

---

**End of README**
