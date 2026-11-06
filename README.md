# HINDI-ENGLISH DISK-BASED POSITIONAL INVERTED INDEX

Student roll number : S20240030403
Project             : Disk-Based Positional Inverted Index with Ranking
Programming language: Python 3.10+
Indexed scripts     : Hindi (Devanagari) and English (Latin)
Dataset archive     : dataset_ir.zip (provided by the student)

## READ THIS FIRST
This guide assumes you are new to Information Retrieval and Python projects.
Follow the steps in order. You can run the project before understanding every
technical detail. The project is a small search engine: it reads the supplied
text files, creates an index, searches words and phrases, ranks frequent terms,
and ranks documents for a search query.

## DATASET CONTEXT AND SCOPE
You have explained that the five supplied text files are a sample taken from
a much larger IIT Bombay Hindi-English (Hi-En) and English-Hindi (En-Hi)
dataset. This project indexes the five files actually present in dataset_ir.zip.
It does NOT contain or claim to index the complete large IIT Bombay corpus.
The supplied ZIP itself does not include a formal citation, release/version,
licence, source URL, or alignment metadata. The IIT Bombay relationship is
therefore recorded as student-provided dataset context, not independently
verified corpus provenance. Use the exact citation supplied by your instructor
or dataset provider if a formal bibliography entry is required.

The index now includes both Hindi Devanagari words and English Latin-script
words found in the sample. This expands the vocabulary based on actual text;
no artificial or fabricated words are added. The current five-file index has
2,491 unique terms, compared with 2,048 when only Devanagari words were indexed.

---
# 1. WHAT DOES THIS PROJECT DO?

Suppose you have five text files and want to find a word. One simple approach
is to open every file and scan it each time you search. That becomes slow as
the collection grows.

An inverted index prepares a lookup structure in advance. Instead of storing
only documents and their words, it stores each word and the documents/positions
where it occurs.

Example (illustrative only):

    "भारत" -> doc00: positions 2, 9; doc02: position 8
    "weather" -> doc01: positions 4, 20

This is a POSITIONAL inverted index because it stores exact token positions,
not just document IDs. Positions allow exact phrase searching.

The project provides these features:
  1. Read the five supplied UTF-8 text files.
  2. Normalize Unicode text.
  3. Tokenize Hindi and English words.
  4. Assign stable document IDs and 1-indexed token positions.
  5. Build a vocabulary of unique terms.
  6. Calculate Collection Frequency (CF) and Document Frequency (DF).
  7. Store all term occurrences in disk-based postings records.
  8. Keep the vocabulary and postings pointers in main memory during queries.
  9. Read only the requested postings record from disk using byte offsets.
 10. Search individual words and exact phrases.
 11. Display the top five terms by CF and by DF.
 12. Rank documents for a user query using BM25.

---
# 2. IMPORTANT TERMS EXPLAINED SIMPLY

DOCUMENT
    One input file. doc00.txt is one document; doc01.txt is another.

TOKEN
    A word-like unit produced by the tokenizer. Hindi and English words are
    indexed. Punctuation, whitespace, symbols and numerals separate tokens.

TERM
    A unique token stored in the vocabulary. If a word occurs 100 times, it
    still has one vocabulary entry, with CF and DF describing its occurrences.

VOCABULARY
    The collection of all unique indexed terms, with their statistics and a
    pointer to the term's postings record on disk.

POSTING
    A record identifying a document and the positions of a term in that file.
    Example: doc00, positions [2, 9, 18].

COLLECTION FREQUENCY (CF)
    The total number of times a term occurs across every document.
    Example: 3 occurrences in doc00 and 2 in doc01 gives CF = 5.

DOCUMENT FREQUENCY (DF)
    The number of different documents that contain a term at least once.
    If a term occurs 50 times in doc00 and once in doc01, DF = 2.

CF and DF are different: CF counts occurrences; DF counts documents.

POSITION
    The token number within one document. Positions start at 1 and restart
    at 1 for each new document. In this bilingual version, both Hindi and
    English words count toward positions. Punctuation and numerals do not.
    Positions are token positions, not line numbers, character offsets or
    byte offsets.

PHRASE QUERY
    A search for words in the exact order at consecutive token positions.
    For example, "भारत का मौसम" matches only if the positions are n, n+1,
    and n+2 in that order.

BM25
    A widely used lexical document-ranking formula. It scores documents using
    query-term frequency, how rare each query term is across the collection,
    and document length. Higher scores mean a stronger match for that query.
    BM25 scores are query-dependent; they are not permanent document quality
    ratings.

MAIN MEMORY (RAM)
    The computer's working memory. The vocabulary is loaded into RAM so the
    program can quickly find a term's disk pointer.

SECONDARY STORAGE
    The SSD/HDD where files are saved. The complete postings collection stays
    in index/postings.jsonl and is not loaded all at once for a term lookup.

BYTE OFFSET AND LENGTH
    A byte offset identifies a location in a file. The vocabulary stores the
    byte offset and byte length of each postings record. A query seeks to that
    location and reads only that record.

---
# 3. WHAT IS IN THE ACTUAL DATASET?

The authoritative input is dataset_ir.zip. It contains five TXT files:

    dataset_ir/
        doc00.txt
        doc01.txt
        doc02.txt
        doc03.txt
        doc04.txt

Inspection of the supplied archive:
  - 5 document files; all 5 are usable.
  - Format: plain text (.txt).
  - Encoding: UTF-8.
  - Empty documents: 0.
  - UTF-8 decoding failures: 0.
  - Nested document directories: none in the supplied archive.
  - All five files contain substantial Devanagari text.
  - Some Latin-script English technical/UI terms are also present.

Indexed dataset statistics after bilingual tokenization:

    Documents                              5
    Hindi tokens                      75,965
    English tokens                    11,159
    Total indexed tokens              87,124
    Unique vocabulary terms            2,491

Per-document token counts:

    Document     Hindi tokens    English tokens    Total tokens
    doc00            19,100            2,055           21,155
    doc01            14,020            4,450           18,470
    doc02            13,987            1,615           15,602
    doc03            14,426            1,524           15,950
    doc04            14,432            1,515           15,947

These are statistics for the five supplied files only, not for the complete
large IIT Bombay Hi-En/En-Hi collection. See dataset/dataset_statistics.json
for machine-readable details and dataset/sources.json for the provenance note.
No web-crawl results or missing source URLs have been invented.

---
# 4. PROJECT FOLDER STRUCTURE

S20240030403-src/
  dataset/
    documents/                 Original five input TXT files
    dataset_statistics.json    Inspection and token statistics
    sources.json               Dataset provenance note
  src/
    dataset_loader.py           Finds and reads input documents
    preprocessing.py            Unicode normalization and tokenization
    indexer.py                  SPIMI-style index construction
    storage.py                  Disk postings read/write by byte offset
    query_processor.py          Term, phrase, term-ranking and BM25 search
    main.py                     Command-line interface
    crawler.py                  Optional legacy crawler; not used by this build
  index/
    vocabulary.json             Unique terms, CF, DF, language and disk pointers
    postings.jsonl              Disk-resident positional postings
    index_metadata.json         Build, token and document-length statistics
  tests/
    test_index.py               Automated tests
  output/
    test_cases.txt              Five test cases, ten rare Hindi terms
    rare_terms_output.txt       CF, DF, document IDs and positions
    top_terms_report.txt        Top five terms by CF and by DF
    document_ranking_example.txt Example BM25 query ranking
    test_results.txt            Saved test-run summary
  README.txt                    This guide
  requirements.txt              Optional crawler dependencies

All commands below must be run from the project root: the folder containing
README.txt and the src folder.

---
# 5. SOFTWARE YOU NEED

Required:
  - Windows, Linux or macOS.
  - Python 3.10 or newer.
  - The extracted project folder.
  - PowerShell/Command Prompt on Windows, or Terminal on Linux/macOS.

Recommended but optional:
  - Visual Studio Code, for viewing Python, JSON and Hindi text files.

The indexer, query program and tests use Python's standard library. No GPU,
Jupyter Notebook, database server or internet connection is required.
The packages in requirements.txt are for the optional legacy crawler only.

---
# 6. STEP BY STEP: EXTRACT AND OPEN THE PROJECT

1. Download S20240030403-src.zip.
2. On Windows, right-click it and choose "Extract All...". Extract it to a
   convenient location such as Documents.
3. Open Visual Studio Code (or another editor).
4. Choose File -> Open Folder.
5. Select the extracted S20240030403-src folder.
6. Open Terminal -> New Terminal in VS Code.
7. Check that the terminal is at the project root:

   PowerShell:
       Get-Location

   Linux/macOS:
       pwd

The path should end in S20240030403-src. Do not run the commands from inside
src or tests.

---
# 7. STEP BY STEP: CHECK PYTHON AND PREPARE THE ENVIRONMENT

1. Check Python:

   Windows:
       python --version

   Linux/macOS:
       python3 --version

The version should be 3.10 or newer. If Python is not found, install it and
reopen the terminal. On Windows, enable the option to add Python to PATH.

2. Create a virtual environment (recommended):

   Windows:
       python -m venv .venv

   Linux/macOS:
       python3 -m venv .venv

3. Activate it:

   PowerShell:
       .venv\Scripts\Activate.ps1

   Windows Command Prompt:
       .venv\Scripts\activate.bat

   Linux/macOS:
       source .venv/bin/activate

You should see (.venv) at the start of the terminal prompt. If PowerShell
blocks activation, use Command Prompt or run this in PowerShell first:

       Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
       .venv\Scripts\Activate.ps1

4. Package installation is not required for indexing or tests. The optional
   crawler dependencies can be installed with:

       python -m pip install -r requirements.txt

---
# 8. STEP BY STEP: BUILD THE INDEX

What does "build" mean?
    The program reads the documents, tokenizes them, records every term's
    position, calculates CF and DF, and writes the search index to index/.

1. Make sure the terminal is at the project root.
2. Run:

       python src/main.py

   On some Linux/macOS systems, use python3 instead of python.

3. The program will:
   a. Find the TXT files in dataset/documents/.
   b. Read each file as UTF-8.
   c. Normalize Unicode using NFC.
   d. Extract Hindi Devanagari and English Latin-script tokens.
   e. Assign 1-indexed positions over the combined bilingual token stream.
   f. Build bounded SPIMI-style blocks and flush them to temporary disk runs.
   g. Merge the runs and write postings records to disk.
   h. Calculate CF and DF and write the vocabulary.
   i. Save document lengths and build metadata.

4. Expected completion message for the supplied dataset:

       Indexed 5 documents; bilingual vocabulary size = 2491

5. Open the index folder. It should contain:

       index/vocabulary.json
       index/postings.jsonl
       index/index_metadata.json

Running python src/main.py rebuilds and overwrites the generated index files.
Use --no-build for searches against the existing index.

Optional: use a smaller block limit to make the builder flush more frequently:

       python src/main.py --block-limit 1000

The block limit affects construction, not the logical search results.
It is an approximate posting-entry limit, not a strict byte-level RAM cap.

---
# 9. SEARCH FOR ONE HINDI OR ENGLISH WORD

1. Build the index first (Section 8).
2. Run a Hindi term lookup:

       python src/main.py --no-build --query कॉन्फ़िगरेशन

3. Or search an English term that actually occurs in the corpus, for example:

       python src/main.py --no-build --query project

The result includes:
  - term: the normalized token searched.
  - language: hi (Devanagari) or en (Latin script).
  - cf: total occurrences in the collection.
  - df: number of documents containing the term.
  - postings: each document ID and exact positions.

If a term is not present, the program reports "Term not found". A term lookup
expects exactly one token.

---
# 10. SEARCH FOR AN EXACT PHRASE

A phrase search checks that every word appears in order at consecutive
positions. It works across Hindi and English tokens.

Run:

    python src/main.py --no-build --phrase "परियोजना में जोड़ें"

Keep quotation marks around a multiword phrase so the shell passes it as one
argument. If a phrase starts at position 100 and has three terms, the required
positions are 100, 101 and 102. A different order or an intervening token is
not a match. If no exact phrase occurs, the result is an empty list [].

---
# 11. TOP FIVE TERMS BY CF AND DF

The program can rank vocabulary terms by collection frequency or document
frequency. This is a vocabulary-level ranking, not a document ranking.

Top five by CF:

    python src/main.py --no-build --top-cf

Top five by DF:

    python src/main.py --no-build --top-df

Display both commands separately to make the two rankings easy to explain.
The program sorts by the requested metric in descending order. If two terms
tie, it sorts by the other frequency metric in descending order, then by term
alphabetically/Unicode order for deterministic output.

For the current five-document sample, the top five are:

    Term       CF       DF
    को         2748      5
    करें       1940      5
    के         1930      5
    का         1837      5
    फ़ाइल      1753      5

These same five terms top both CF and DF in this sample. Each occurs in all
five documents (DF=5), and the CF values determine their order. This does not
mean CF and DF are interchangeable; they measure different things.

A formatted copy is saved in output/top_terms_report.txt.

---
# 12. RANK DOCUMENTS FOR A QUERY USING BM25

Term rankings answer: "Which words occur most often?"
Document ranking answers: "Which documents are most relevant to my search?"

This project uses BM25, a standard lexical retrieval ranking function. It
considers:
  - TF: how many times each query term occurs in a document (from positions).
  - IDF: how informative/rare the query term is across the collection.
  - Document length: long documents are normalized so they do not win only
    because they contain more words.

To rank the top five documents for a query, run:

    python src/main.py --no-build --rank "परियोजना में जोड़ें"

To request the top three instead:

    python src/main.py --no-build --rank "परियोजना में जोड़ें" --top-k 3

For English:

    python src/main.py --no-build --rank "project configuration" --top-k 5

The result contains:
  - rank: 1 is the highest-scoring matching document.
  - doc_id: the matching document.
  - score: BM25 score (higher is better for this query).
  - matched_terms: query terms found in that document.
  - document_length: number of indexed Hindi-English tokens in the document.

Only documents containing at least one query term are returned. If none of
the query terms exist, the result is an empty list. Relevance scores are
specific to the query; do not compare scores from unrelated queries as if
they were universal document-quality scores.

A reproducible example is saved in output/document_ranking_example.txt.

---
# 13. HOW THE SOURCE MODULES WORK

src/dataset_loader.py
    Finds TXT files recursively, reads UTF-8 text, assigns document IDs from
    relative paths, and rejects empty documents rather than silently skipping.

src/preprocessing.py
    Applies NFC normalization and extracts Devanagari Hindi and Latin English
    lexical tokens. Script changes, punctuation, whitespace, symbols and
    numerals delimit tokens. It does not stem, lemmatize or remove stop words.

src/indexer.py
    Builds SPIMI-style sorted temporary runs. Each document is tokenized and
    its term positions are collected. Bounded term-document blocks are flushed
    to disk. Sorted runs are merged by term, one term at a time. The final
    postings record is written to disk and its byte pointer is stored in the
    vocabulary. CF and DF are calculated from the merged postings. Metadata
    includes document lengths and language token counts.

src/storage.py
    Writes each term's postings as a UTF-8 JSONL record. It returns byte offset
    and byte length. During a lookup it seeks to that offset and reads exactly
    that record, rather than loading the entire postings file.

src/query_processor.py
    Loads vocabulary and metadata into RAM. It implements term lookup, exact
    positional phrase search, top-CF/DF term rankings, and BM25 document
    ranking. Posting positions are used to calculate term frequency.

src/main.py
    Parses command-line arguments and connects the loader, indexer and query
    processor.

src/crawler.py
    Optional legacy crawler retained from the starter project. It is not used
    to build this supplied dataset. Do not run it for this assignment unless
    you have a separate approved crawling task and have checked website rules.

tests/test_index.py
    Automated tests for tokenization, Unicode normalization, CF/DF, positions,
    phrase search, disk access, bilingual indexing, term rankings and BM25.

---
# 14. HOW DISK STORAGE AND SPIMI WORK

The vocabulary is relatively small and used for every query, so it is loaded
into RAM. The full postings data can be much larger, so it stays in
index/postings.jsonl.

The vocabulary contains one entry per term, including CF, DF, language and a
postings pointer. The pointer has an offset and length. The query processor
uses those values to seek to the correct record in postings.jsonl.

SPIMI-style construction works like this:

    Read a document
          |
          v
    Tokenize and record positions
          |
          v
    Add term/document postings to current block
          |
          v
    Block limit reached? -- no --> continue reading
          |
         yes
          v
    Sort block and flush a temporary run to disk
          |
          v
    Read remaining documents and flush remaining block
          |
          v
    Merge sorted runs by term
          |
          v
    Write each final term postings record to postings.jsonl
          |
          v
    Write vocabulary pointers and metadata

This reduces the need to hold the entire collection's postings dictionary in
RAM. It is not a strict fixed-memory guarantee: the vocabulary is retained,
one document is tokenized in memory, and a term's postings are assembled
while that term is merged. A production-scale full corpus may require further
streaming, compression, parallelization and strict memory-budget controls.

---
# 15. ASSIGNMENT OUTPUT: FIVE TEST CASES AND TEN RARE HINDI TERMS

The assignment asks for five test cases with two rare terms each. The project
provides:

    output/test_cases.txt
    output/rare_terms_output.txt

The ten selected terms are actual Hindi terms in the supplied documents.
Each has CF=1 and DF=1, the minimum possible positive frequencies. Each entry
shows the term, CF, DF, document ID and exact position. Positions now count the
complete Hindi-English token stream, so they can differ from the earlier
Hindi-only index version.

Open the files in a UTF-8-capable editor such as VS Code. The underlying source
of truth is the generated vocabulary and postings files.

---
# 16. RUN AUTOMATED TESTS

From the project root, run:

    python -m unittest discover -s tests -v

The current suite contains 13 tests. It checks:
  - Hindi and English tokenization and punctuation boundaries.
  - Unicode NFC normalization.
  - CF and DF calculations.
  - Multiple occurrences in one document.
  - Terms appearing in multiple documents.
  - Exact phrase matching and phrase starting positions.
  - Missing terms and phrases.
  - Disk postings retrieval by byte offset and length.
  - Actual dataset loading.
  - Bilingual token positions.
  - Top-CF and top-DF ranking.
  - BM25 document ranking.
  - Vocabulary/postings consistency.

A passing run ends with a summary similar to:

    Ran 13 tests
    OK

The saved report is output/test_results.txt. Always run the command yourself
before claiming a new test run passed; the saved report is only a record of
the last packaged run.

---
# 17. QUICK COMMAND REFERENCE

Build/rebuild:
    python src/main.py

Build with smaller SPIMI blocks:
    python src/main.py --block-limit 1000

Search Hindi word:
    python src/main.py --no-build --query कॉन्फ़िगरेशन

Search English word:
    python src/main.py --no-build --query project

Exact phrase:
    python src/main.py --no-build --phrase "परियोजना में जोड़ें"

Top five by CF:
    python src/main.py --no-build --top-cf

Top five by DF:
    python src/main.py --no-build --top-df

Top five documents for a query:
    python src/main.py --no-build --rank "परियोजना में जोड़ें"

Top three documents for a query:
    python src/main.py --no-build --rank "project configuration" --top-k 3

Command-line help:
    python src/main.py --help

Automated tests:
    python -m unittest discover -s tests -v

---
# 18. TROUBLESHOOTING

"python is not recognized" / "python: command not found"
    Install Python 3.10+ and reopen the terminal. Try python3 on Linux/macOS.

"Document directory does not exist"
    Run from the project root and check dataset/documents/ exists.

"vocabulary.json" or "postings.jsonl" does not exist
    Build the index first using python src/main.py.

"Term not found"
    Check spelling and script. Only Hindi Devanagari and English Latin words
    are indexed. Numerals and punctuation are not searchable terms.

Hindi appears as boxes or question marks
    Open files as UTF-8 and use a terminal/editor with Unicode font support.

Phrase query returns []
    The exact sequence may not exist. Every term must be at consecutive
    positions in the same order. Phrase search does not skip intervening words.

Ranking returns fewer than five documents
    Only documents containing at least one query term are returned. Try a
    broader query or terms known to occur in more documents.

Results changed after editing documents
    Rebuild the index after any source-document or tokenizer change.

PowerShell blocks virtual-environment activation
    Use Command Prompt activation or the temporary process policy in Section 7.

---
# 19. ADD MORE DOCUMENTS

The loader searches recursively for .txt files under dataset/documents/.
To add more data:
  1. Add a UTF-8 .txt file under dataset/documents/.
  2. Give it a unique name, for example doc05.txt.
  3. Run python src/main.py to rebuild.
  4. Search words from the new file.

The document ID is its relative path without the .txt extension. A nested
file dataset/documents/train/doc05.txt receives ID train/doc05.

This version supports UTF-8 plain text only. PDF, DOCX, XML and HTML extraction
are not implemented. Do not simply rename another format to .txt.

---
# 20. LIMITATIONS AND FUTURE IMPROVEMENTS

1. The packaged collection contains five sample documents, not the complete
   IIT Bombay Hi-En/En-Hi corpus. To index the full corpus, obtain and add its
   actual files, subject to its licence and the assignment's data rules.
2. The ZIP does not provide a formal corpus release citation or sentence
   alignment metadata. This project does not create bilingual sentence pairs.
3. Hindi and English are indexed as separate script tokens. Transliteration,
   stemming, lemmatization, stop-word removal and language-specific morphology
   are not implemented.
4. Token positions count both Hindi and English tokens. They are not Hindi-only
   positions and are not positions in a parallel sentence alignment.
5. The tokenizer is practical, not a full linguistic analyzer. Apostrophes,
   hyphens and many symbols split tokens; numerals are excluded.
6. The builder uses disk-flushed blocks but does not impose a strict total RAM
   ceiling. The vocabulary is kept in memory and each document is tokenized
   in memory.
7. BM25 is lexical ranking. It does not understand semantic similarity,
   synonyms, translation equivalence or meaning beyond matching terms.
8. The current command-line interface is not a graphical web application.
9. The current source loader supports TXT files, not PDF/DOCX/XML/HTML.

Possible future extensions include full-corpus ingestion, compressed postings,
fielded indexing, stemming/lemmatization, stop-word-aware ranking, bilingual
query translation, phrase boosts in BM25, and a graphical search interface.

---
# 21. REPRODUCIBILITY AND DATA INTEGRITY

The five files in dataset/documents/ are the files supplied in dataset_ir.zip.
The original document boundaries and filenames are retained. The current
vocabulary, CF/DF values, postings, top-term rankings, BM25 example and rare
term examples are generated from those files using the tokenizer described
above.

The six-document demonstration corpus from the starter project is not used.
No additional documents, crawl results, source URLs, positions or dataset
statistics have been fabricated. The student's statement that these files
come from a larger IIT Bombay bilingual dataset is preserved as context, but
the complete corpus is not included in this submission.

For a fresh build and verification, run:

    python src/main.py
    python -m unittest discover -s tests -v

END OF README
