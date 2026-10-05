"""Save graph counts, source coverage and context facts without any LLM calls.

Run from the repository root after bench_kg.py --judge or --build.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
from bench_kg import connect_graph


def main():
    load_dotenv(ROOT / ".env")
    graph = connect_graph()
    try:
        questions = json.loads((ROOT / "data/benchmark_kg.json").read_text(encoding="utf-8"))
        result = {
            "context_note": "Contexts below use doc_ids=[]: named entities, terms and global aggregation only. Q2 needs vector-search doc_ids in the real GraphRAG pipeline; these snapshots do not reproduce vector retrieval.",
            "stats": graph.stats(),
            "labels": graph.run("MATCH (n) RETURN labels(n)[0] AS label, count(*) AS count ORDER BY label"),
            "relationships": graph.run("MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS count ORDER BY type"),
            "source_coverage": graph.run("MATCH (n) WHERE n.doc_id IS NOT NULL RETURN n.doc_id AS doc_id, count(*) AS count ORDER BY doc_id"),
            "questions": [{"id": q["id"], "question": q["question"],
                           "facts": graph.context(q["question"], [])} for q in questions],
        }
        output = ROOT / "report/graph_contexts.json"
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Saved {output}: {result['stats']}")
    finally:
        graph.close()


if __name__ == "__main__":
    main()
