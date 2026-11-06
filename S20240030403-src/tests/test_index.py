import sys, tempfile, unittest, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from preprocessing import tokenize, normalize_text
from indexer import build_index
from query_processor import PositionalIndex

class IndexTests(unittest.TestCase):
    def build(self, docs, tmp):
        build_index(docs, tmp, block_posting_limit=1)
        return PositionalIndex(tmp)

    def test_tokenization_punctuation(self):
        self.assertEqual(tokenize("भारत, weather मौसम! विभाग।"), ["भारत", "weather", "मौसम", "विभाग"])

    def test_unicode_nfc(self):
        self.assertEqual(normalize_text("e" + chr(0x0301)), "é")
        self.assertEqual(normalize_text("  भारत    मौसम  "), "भारत मौसम")

    def test_cf_df_positions_and_multiple_occurrences(self):
        with tempfile.TemporaryDirectory() as tmp:
            idx = self.build([{"doc_id":"A","text":"भारत भारत मौसम"},
                              {"doc_id":"B","text":"भारत मौसम विभाग"}], tmp)
            got = idx.lookup("भारत")
            self.assertEqual((got["cf"], got["df"]), (3, 2))
            self.assertEqual(got["postings"], [
                {"doc_id":"A","positions":[1,2]}, {"doc_id":"B","positions":[1]}])

    def test_term_in_multiple_documents(self):
        with tempfile.TemporaryDirectory() as tmp:
            idx = self.build([{"doc_id":"A","text":"नदी जल"},
                              {"doc_id":"B","text":"जल नदी"}], tmp)
            self.assertEqual(idx.lookup("नदी")["df"], 2)

    def test_exact_phrase_and_positions(self):
        with tempfile.TemporaryDirectory() as tmp:
            idx = self.build([{"doc_id":"A","text":"जलवायु परिवर्तन भारत जलवायु परिवर्तन"},
                              {"doc_id":"B","text":"परिवर्तन जलवायु"}], tmp)
            self.assertEqual(idx.phrase_search(["जलवायु","परिवर्तन"]),
                [{"doc_id":"A","positions":[1,4]}])
            self.assertEqual(idx.phrase_search(["जलवायु","भारत"]), [])

    def test_missing_term_and_phrase(self):
        with tempfile.TemporaryDirectory() as tmp:
            idx = self.build([{"doc_id":"A","text":"भारत मौसम"}], tmp)
            self.assertIsNone(idx.lookup("अनुपलब्ध"))
            self.assertEqual(idx.phrase_search(["भारत","अनुपलब्ध"]), [])

    def test_disk_offsets_read_only_relevant_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            idx = self.build([{"doc_id":"A","text":"भारत मौसम"}], tmp)
            entry = idx.vocabulary["भारत"]["postings"]
            self.assertGreater(entry["length"], 0)
            self.assertEqual(idx.lookup("भारत")["postings"][0]["positions"], [1])
            self.assertTrue((Path(tmp)/"postings.jsonl").exists())


    def test_actual_dataset_document_count_and_hindi_content(self):
        from dataset_loader import load_documents
        from preprocessing import tokenize
        docs = load_documents(ROOT / "dataset" / "documents")
        self.assertEqual(len(docs), 5)
        self.assertTrue(all(tokenize(d["text"]) for d in docs))

    def test_actual_index_rare_term_statistics(self):
        idx = PositionalIndex(ROOT / "index")
        result = idx.lookup("कॉन्फ़िगरेशन")
        self.assertIsNotNone(result)
        self.assertEqual((result["cf"], result["df"]), (1, 1))
        self.assertEqual(result["postings"], [{"doc_id":"doc00","positions":[14014]}])

    def test_vocabulary_postings_consistency(self):
        with tempfile.TemporaryDirectory() as tmp:
            vocab = build_index([{"doc_id":"A","text":"भारत भारत मौसम"},
                                 {"doc_id":"B","text":"भारत"}], tmp, block_posting_limit=1)
            idx = PositionalIndex(tmp)
            for term, entry in vocab.items():
                p = idx.lookup(term)["postings"]
                self.assertEqual(entry["cf"], sum(len(x["positions"]) for x in p))
                self.assertEqual(entry["df"], len(p))

    def test_bilingual_tokenization_and_positions(self):
        self.assertEqual(tokenize("हिंदी search engine 2026 भारत"),
                         ["हिंदी", "search", "engine", "भारत"])
        with tempfile.TemporaryDirectory() as tmp:
            idx = self.build([{"doc_id":"A","text":"हिंदी search engine भारत"}], tmp)
            self.assertEqual(idx.lookup("search")["postings"],
                             [{"doc_id":"A","positions":[2]}])
            self.assertEqual(idx.lookup("भारत")["postings"],
                             [{"doc_id":"A","positions":[4]}])

    def test_top_cf_df_rankings(self):
        with tempfile.TemporaryDirectory() as tmp:
            idx = self.build([{"doc_id":"A","text":"भारत भारत मौसम"},
                              {"doc_id":"B","text":"भारत मौसम मौसम"}], tmp)
            self.assertEqual(idx.top_terms("cf", 1)[0]["term"], "भारत")
            self.assertEqual(idx.top_terms("df", 1)[0]["df"], 2)

    def test_bm25_document_ranking(self):
        with tempfile.TemporaryDirectory() as tmp:
            idx = self.build([{"doc_id":"A","text":"भारत मौसम भारत"},
                              {"doc_id":"B","text":"भारत नदी"},
                              {"doc_id":"C","text":"समुद्र पर्वत"}], tmp)
            ranked = idx.rank_documents("भारत मौसम", 5)
            self.assertEqual(ranked[0]["doc_id"], "A")
            self.assertGreater(ranked[0]["score"], ranked[1]["score"])

if __name__ == "__main__":
    unittest.main()
