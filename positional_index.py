import re
from collections import defaultdict
import sys

sys.stdout.reconfigure(encoding="utf-8")


FILE_PATH = "IITB.en-hi.hi"
NUM_DOCUMENTS = 10
LINES_PER_DOCUMENT = 20


def read_dataset(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    required_lines = NUM_DOCUMENTS * LINES_PER_DOCUMENT

    if len(lines) < required_lines:
        raise ValueError(
            f"Dataset contains only {len(lines)} non-empty lines. "
            f"{required_lines} lines are required."
        )

    return lines[:required_lines]


def create_documents(lines):
    documents = {}

    for i in range(NUM_DOCUMENTS):
        start = i * LINES_PER_DOCUMENT
        end = start + LINES_PER_DOCUMENT

        documents[i + 1] = lines[start:end]

    return documents


def tokenize(text):
    return re.findall(r"\S+", text)


def build_positional_index(documents):
    positional_index = defaultdict(lambda: defaultdict(list))

    for doc_id, lines in documents.items():

        position = 1

        for line in lines:
            tokens = tokenize(line)

            for token in tokens:
                positional_index[token][doc_id].append(position)
                position += 1

    return positional_index


def print_documents(documents):
    print("\n" + "=" * 70)
    print("DOCUMENT COLLECTION")
    print("=" * 70)

    for doc_id, lines in documents.items():

        print(f"\nDOCUMENT {doc_id}")
        print("-" * 70)

        for line_number, line in enumerate(lines, start=1):
            print(f"{line_number:02d}. {line}")


def print_positional_index(positional_index):
    print("\n" + "=" * 70)
    print("POSITIONAL INVERTED INDEX")
    print("=" * 70)

    for term in sorted(positional_index.keys()):

        postings = []

        for doc_id in sorted(positional_index[term].keys()):
            positions = positional_index[term][doc_id]
            postings.append(
                f"D{doc_id}: {positions}"
            )

        print(f"{term} -> " + ", ".join(postings))


def search_term(positional_index, term):
    if term in positional_index:
        return positional_index[term]

    return None


def show_term_search(positional_index):
    print("\n" + "=" * 70)
    print("TERM SEARCH")
    print("=" * 70)

    while True:

        term = input(
            "\nEnter a Hindi term to search "
            "(or type 'exit' to stop): "
        ).strip()

        if term.lower() == "exit":
            break

        result = search_term(positional_index, term)

        if result is None:
            print("Term not found in the positional index.")

        else:
            print(f"\nTerm: {term}")
            print("Occurrences:")

            for doc_id in sorted(result.keys()):
                print(
                    f"  Document {doc_id}: "
                    f"positions {result[doc_id]}"
                )


def save_index(positional_index, file_name):
    with open(file_name, "w", encoding="utf-8") as file:

        file.write("POSITIONAL INVERTED INDEX\n")
        file.write("=" * 70 + "\n\n")

        for term in sorted(positional_index.keys()):

            postings = []

            for doc_id in sorted(positional_index[term].keys()):

                positions = positional_index[term][doc_id]

                postings.append(
                    f"D{doc_id}: {positions}"
                )

            file.write(
                f"{term} -> "
                + ", ".join(postings)
                + "\n"
            )


def main():

    print("=" * 70)
    print("HINDI POSITIONAL INDEXING SYSTEM")
    print("=" * 70)

    print("\nReading dataset...")

    lines = read_dataset(FILE_PATH)

    print(f"Total lines used: {len(lines)}")
    print(f"Number of documents: {NUM_DOCUMENTS}")
    print(f"Lines per document: {LINES_PER_DOCUMENT}")

    documents = create_documents(lines)

    print_documents(documents)

    print("\nBuilding positional index...")

    positional_index = build_positional_index(documents)

    print(
        f"\nTotal unique terms: "
        f"{len(positional_index)}"
    )

    print_positional_index(positional_index)

    save_index(
        positional_index,
        "output.txt"
    )

    print("\n" + "=" * 70)
    print("INDEX SAVED TO output.txt")
    print("=" * 70)

    show_term_search(positional_index)


if __name__ == "__main__":
    main()