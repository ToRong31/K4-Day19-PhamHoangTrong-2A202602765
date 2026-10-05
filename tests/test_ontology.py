"""Additional regressions for evidence, legal thresholds and identity isolation.

The provided lab tests are unchanged. These tests require no API or Neo4j.
"""
import unittest
import unicodedata

from src.graph import load_markdown_docs
from src.graph_ontology import (
    GraphRows, add_law, add_news, linked_crime, parse_quantity, parse_rule,
    quantity_fits, sentence, substances, validate_extraction, evidence_passages, resolve_evidence, supported_attribution,
)
from src.models import Document


class TestLegalThresholds(unittest.TestCase):
    def test_exclusive_upper_boundary(self):
        rule = parse_rule("MDMA có khối lượng từ 05 gam đến dưới 30 gam")
        self.assertTrue(quantity_fits(parse_quantity("5 gam"), rule))
        self.assertFalse(quantity_fits(parse_quantity("30 gam"), rule))

    def test_kg_and_open_ended_report(self):
        rule = parse_rule("MDMA có khối lượng 100 gam trở lên")
        self.assertTrue(quantity_fits(parse_quantity("hơn 9,6kg"), rule))
        self.assertFalse(quantity_fits(parse_quantity("khoảng 100g"), rule))

    def test_count_is_not_mass_and_multiple_quantities_not_guessed(self):
        rule = parse_rule("MDMA có khối lượng 100 gam trở lên")
        self.assertFalse(quantity_fits(parse_quantity("5 viên"), rule))
        self.assertNotIn("value", parse_quantity("5g MDMA và 6g Ketamine"))

    def test_unbounded_quantity_not_assigned_to_bounded_rule(self):
        self.assertFalse(quantity_fits(parse_quantity("hơn 5 gam"), parse_rule("từ 05 gam đến dưới 30 gam")))

    def test_mixture_rule_is_not_single_substance_rule(self):
        self.assertEqual(parse_rule("Có 02 chất ma túy trở lên mà tổng khối lượng tương đương 100 gam trở lên")["parse_status"], "text_only")

    def test_compound_names_do_not_match_substrings(self):
        self.assertEqual(substances("Methamphetamine"), ["Methamphetamine"])

    def test_parse_corpus_law_and_definition(self):
        rows = GraphRows()
        docs = {d.id: d for d in load_markdown_docs("data/drug_law")}
        add_law(rows, docs["blhs-dieu-250"])
        add_law(rows, docs["blhs-dieu-255"])
        add_law(rows, docs["pcmt-dieu-2"])
        rule = rows.nodes["Rule"]["blhs-dieu-250:article:clause:4:rule:b"]
        self.assertEqual(rule["min_value"], 100)
        clause = rows.nodes["Clause"]["blhs-dieu-255:article:clause:4"]
        self.assertTrue(clause["life_allowed"])
        self.assertFalse(clause["death_allowed"])
        self.assertIn("term:tiền chất", rows.nodes["Term"])

    def test_sentence_units_and_missing_sentence(self):
        self.assertEqual(sentence("8 năm 6 tháng tù")["sentence_months"], 102)
        self.assertNotIn("sentence_months", sentence(""))


class TestSourceIntegrity(unittest.TestCase):
    def test_amount_not_attributed_to_another_person(self):
        nodes = {"h": {"name": "Cái Quang Huy", "aliases": []},
                 "d": {"name": "Nguyễn Tiến Đạt", "aliases": []}}
        names = {"huy": "h", "đạt": "d"}
        self.assertTrue(supported_attribution("h", "Huy vận chuyển 5kg MDMA.", nodes, names))
        self.assertFalse(supported_attribution("d", "Huy vận chuyển 5kg MDMA.", nodes, names))

    def test_paragraph_id_resolves_to_exact_source(self):
        doc = Document("n", "# Tiêu đề\n\nNgười A bị bắt.\n\nNgười B được thả.")
        value = {"cases": [{"evidence_text": "S0002", "people": [], "findings": []}]}
        resolved = resolve_evidence(value, evidence_passages(doc))
        self.assertEqual(resolved["cases"][0]["evidence_text"], "Người A bị bắt.")

    def test_unknown_paragraph_id_is_not_guessed(self):
        doc = Document("n", "Nguồn thật")
        case = {"name": "Vụ A", "evidence_text": "S0999", "people": [], "findings": [], "locations": []}
        with self.assertRaises(ValueError):
            validate_extraction(resolve_evidence({"cases": [case]}, evidence_passages(doc)), doc)

    def test_wrong_conduct_not_fuzzy_linked(self):
        self.assertIsNone(linked_crime("tàng trữ trái phép chất ma túy", ["vận chuyển trái phép chất ma túy"]))

    def test_invalid_schema_is_not_silently_empty(self):
        with self.assertRaises(ValueError):
            validate_extraction({"cases": "wrong"})

    def test_unicode_evidence_and_withdrawn_charge(self):
        content = "Nguyễn Văn A được hủy quyết định khởi tố về tội vận chuyển trái phép chất ma túy."
        doc = Document("news-test", unicodedata.normalize("NFD", content))
        case = {"name": "Vụ thử", "evidence_text": content, "people": [{
            "name": "Nguyễn Văn A", "aliases": [], "participations": [{
                "status": "withdrawn", "stage": "prosecution", "charge": "vận chuyển trái phép chất ma túy",
                "sentence": "20 năm tù", "evidence_text": content}]}], "locations": [], "findings": []}
        rows = GraphRows()
        rows.node("Crime", "crime:test", name="vận chuyển trái phép chất ma túy", source_doc_ids=[])
        add_news(rows, case, doc, {"vận chuyển trái phép chất ma túy": "crime:test"}, {"case_groups": [], "people": []})
        pt = next(iter(rows.nodes["Participation"].values()))
        self.assertEqual(pt["sentence_text"], "")
        self.assertFalse(rows.edges[("Case", "CHARGED_WITH", "Crime")])

    def test_fabricated_case_evidence_fails(self):
        with self.assertRaises(ValueError):
            add_news(GraphRows(), {"evidence_text": "invented"}, Document("n", "real source"), {}, {})


if __name__ == "__main__":
    unittest.main()
