"""Read-only Neo4j audit for lab steps 8.1, 8.3 and error evidence; no LLM calls."""
import sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
from bench_kg import connect_graph
load_dotenv(ROOT / '.env')
queries = {
    'QA': 'MATCH (n) RETURN labels(n)[0] AS label, count(*) AS n ORDER BY n DESC',
    'QB': '''MATCH (p:Person)-[:HAS_PARTICIPATION]->(pt:Participation)-[:IN_CASE]->(k:Case)-[:CHARGED_WITH]->(c:Crime)<-[:DEFINES]-(a:Article) RETURN p.name AS person, k.name AS case_name, c.name AS crime, a.name AS article LIMIT 25''',
    'QC': '''MATCH (a:Article {doc_id:'blhs-dieu-251'})-[:HAS_CLAUSE]->(cl:Clause) RETURN a.name AS article, cl.number AS clause, cl.penalty_text AS penalty ORDER BY clause''',
    'QD': '''MATCH (p:Person {name:'Cái Quang Huy'})-[:HAS_PARTICIPATION]->(pt:Participation)-[:IN_CASE]->(k:Case), (pt)-[:CHARGED_WITH]->(c:Crime)<-[:DEFINES]-(a:Article) RETURN p.name AS person, pt.status AS status, c.name AS crime, a.name AS article, k.doc_id AS source''',
    'Q5_findings': '''MATCH (p:Person {name:'Cái Quang Huy'})-[:HAS_PARTICIPATION]->(:Participation)-[:IN_CASE]->(k:Case)-[:HAS_FINDING]->(f:DrugFinding)-[:OF_SUBSTANCE]->(s:Substance) RETURN DISTINCT s.name AS substance, f.amount_text AS amount, f.qualifier AS qualifier, f.scope AS scope, f.evidence_text AS evidence, f.doc_id AS source''',
    'missing_quantities': '''MATCH (k:Case)-[:HAS_FINDING]->(f:DrugFinding)-[:OF_SUBSTANCE]->(s:Substance) WHERE f.amount_text = '' RETURN k.name AS case_name, s.name AS substance, f.amount_text AS amount, f.value AS value, f.qualifier AS qualifier, f.evidence_text AS evidence, f.doc_id AS source ORDER BY source, substance''',
    'missing_charges': '''MATCH (p:Person)-[:HAS_PARTICIPATION]->(pt:Participation)-[:IN_CASE]->(k:Case) WHERE NOT (pt)-[:CHARGED_WITH]->(:Crime) RETURN p.name AS person, pt.charge_raw AS charge, pt.status AS status, pt.evidence_text AS evidence, k.doc_id AS source''',
    'relationships': 'MATCH ()-[r]->() RETURN type(r) AS rel, count(*) AS n ORDER BY n DESC',
    'MDMA_cases': '''MATCH (k:Case)-[:HAS_FINDING]->(:DrugFinding)-[:OF_SUBSTANCE]->(:Substance {name:'MDMA'}) RETURN k.canonical_case_id AS case_id, collect(DISTINCT k.name) AS names, collect(DISTINCT k.doc_id) AS sources ORDER BY case_id''',
}
g = connect_graph()
try:
    results = {key: {'cypher': query, 'rows': g.run(query)} for key, query in queries.items()}
    (ROOT / 'report/graph_audit.json').write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Saved report/graph_audit.json: ' + ', '.join(f'{key}={len(value["rows"])} rows' for key, value in results.items()))
finally:
    g.close()
