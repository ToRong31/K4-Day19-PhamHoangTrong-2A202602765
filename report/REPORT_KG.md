# Báo cáo Day 19 — Flat RAG vs GraphRAG

**Họ tên:** Phạm Hoàng Trọng  **MSSV:** 2A202602765  **Ngày:** 05/10/2026

Nguồn số liệu: `ket_qua_benchmark_kg.txt` do `python bench_kg.py --judge` sinh ra ở lần chạy mới nhất. Chat: `openai:gpt-4o-mini`; embedding: `openai:text-embedding-3-small`; top_k=3; chunk_size=800; 176 chunk. Graph đầy đủ: **558 node / 1.148 cạnh**, 11 label và 13 loại quan hệ. Bản thiết kế ở [ONTOLOGY.md](ONTOLOGY.md); graph được kiểm tra chỉ đọc ở [graph_contexts.json](graph_contexts.json) và [graph_audit.json](graph_audit.json).

## 1. Chi phí

Hai bảng dưới đây sao chép nguyên văn từ file benchmark:

```text
== Indexing (one-off)
pipeline  calls    in_tok  out_tok       USD  seconds
flat        176     56072        0   0.00112    214.3
graph       197    106421     9922   0.01463    326.5

== Querying (mean per question)
pipeline  recall  judge   in_tok  out_tok       USD  seconds
flat        0.43   1.00      694       45   0.00012     4.55
graph       1.00   2.00     2360       84   0.00040     5.15
```

| Chỉ số | Flat | Graph | Graph / Flat |
| --- | --- | --- | --- |
| Indexing USD | 0.00112 | 0.01463 | ×13.063 |
| Indexing giây | 214.3 | 326.5 | ×1.524 |
| Mỗi câu: USD | 0.00012 | 0.00040 | ×3.333 |
| Mỗi câu: giây | 4.55 | 5.15 | ×1.132 |
| Mỗi câu: in_tok | 694 | 2360 | ×3.401 |

Graph index dùng cùng 176 lượt embedding của Flat và thêm 21 lượt chat trích xuất tin (20 bài, một lượt thử lại schema), nên tăng token đầu vào và có 9.922 token đầu ra. Khi trả lời, Graph đưa cả chunks và facts nhiều bước vào prompt, tăng input trung bình từ 694 lên 2.360 token; output cũng tăng từ 45 lên 84 token. Thời gian chịu ảnh hưởng API/mạng; số liệu một lần chạy chưa tách riêng được chi phí thời gian của ontology và dịch vụ.

USD là ước tính từ token và bảng giá `src/llm.py`, không phải hóa đơn; các tỉ lệ tính từ số đã làm tròn trong benchmark. Giá chuẩn kiểm tra ngày 05/10/2026: GPT-4o-mini input 0,15 USD và output 0,60 USD/1M token; embedding-3-small 0,02 USD/1M token. Nguồn: [GPT-4o-mini — OpenAI Docs](https://developers.openai.com/api/docs/models/gpt-4o-mini), [text-embedding-3-small — OpenAI Docs](https://developers.openai.com/api/docs/models/text-embedding-3-small). Phép tính trong code dùng giá input thông thường, chưa tách ưu đãi cached input; chi phí LLM judge không nằm trong số đo trả lời từng pipeline.

Ước tính với N câu và cùng corpus: `Flat(N) = 0.00112 + 0.00012N`, `Graph(N) = 0.01463 + 0.00040N` USD. Graph đắt hơn `0.01351 + 0.00028N` USD, nên **không có điểm hòa vốn về chi phí API so với Flat** theo số liệu này. Quyết định dùng KG phải dựa vào mức cải thiện chất lượng; công thức chưa tính máy chủ Neo4j, cập nhật dữ liệu và bảo trì.

## 2. Từng câu hỏi

| Câu | Loại | Flat recall / judge | Graph recall / judge | Thắng theo benchmark | Vì sao |
| --- | --- | --- | --- | --- | --- |
| Q1 | single-hop-law | 1.00 / 2 | 1.00 / 2 | Hòa | Định nghĩa nằm trong một khoản luật, cả hai lấy đủ. |
| Q2 | single-hop-news | 1.00 / 2 | 1.00 / 2 | Hòa | Hai người và mức án nằm trong cùng bài báo, Flat đủ. |
| Q3 | cross-kb | 0.00 / 0 | 1.00 / 2 | Graph | Graph nối án 36 tháng và tội mua bán với Điều 251, khung 02–07 năm. |
| Q4 | cross-kb | 0.00 / 0 | 1.00 / 2 | Graph | Graph nối bí danh Hoàng Nato với tội rồi lấy khung cao nhất Điều 255. |
| Q5 | cross-kb-multi-hop | 0.60 / 1 | 1.00 / 2 | Graph | Graph nêu đúng Điều 250 khoản 4; Flat thiếu điều và khoản chính xác. Cả hai còn bỏ Ketamine. |
| Q6 | aggregation | 0.00 / 1 | 1.00 / 2 | Graph | Graph nhóm toàn graph theo MDMA và vụ; Flat chỉ thấy top-k đoạn nên thiếu tên chuẩn/phạm vi. |

Trung bình: Flat recall **0,43**, judge **1,00/2**; Graph recall **1,00**, judge **2,00/2**. Q1–Q2 cho thấy Flat đủ khi dữ kiện nằm trong một đoạn; Q3–Q5 cần nối báo chí với luật, Q6 cần tổng hợp nhiều nguồn nên Graph có lợi. Đây là kết quả trên sáu câu lab; điểm tối đa chưa bảo đảm không thiếu dữ kiện, như lỗi E4 bên dưới.

## 3. Phân tích lỗi

### E4 — Phép đo cho điểm tối đa dù câu trả lời chưa đầy đủ

- **Hiện tượng:** Q5 Graph đạt recall=1,00 và judge=2 nhưng chỉ nêu MDMA, không nêu Ketamine trong khi câu hỏi hỏi loại ma túy và gold có cả hai chất.
- **Bằng chứng:** nguyên văn câu Q5 pipeline Graph trong `ket_qua_benchmark_kg.txt`:

> Cái Quang Huy bị truy tố về tội vận chuyển trái phép chất ma túy, cụ thể là ma túy MDMA. Với tổng khối lượng MDMA là hơn 9,6kg, khoản áp dụng tương ứng là khoản 4 của Điều 250 Bộ luật Hình sự (BLHS), với khung hình phạt là 20 năm, tù chung thân hoặc tử hình.

`data/benchmark_kg.json`, Q5 có gold ghi “hơn 9,6kg MDMA và khoảng 406g Ketamine”, nhưng `must_include` chỉ gồm `vận chuyển`, `MDMA`, `Điều 250`, `khoản 4`, `tử hình`; không có Ketamine. Bài `news-100260917203001265` có câu:

> Tổng khối lượng ma túy Huy phải chịu trách nhiệm hình sự là hơn 9,6kg ma túy MDMA và khoảng 406g Ketamine. Nguyễn Tiến Đạt phải chịu trách nhiệm hình sự đối với gần 4,3kg MDMA.

- **Nguyên nhân:** ở bước đánh giá, recall kiểm tra một tập từ khóa nên không phát hiện chất bị thiếu; LLM judge cũng bỏ sót yêu cầu liệt kê đủ chất ở lần chạy này. Vì thiếu chất đã có trong nguồn, không thể kết luận câu trả lời đầy đủ chỉ từ judge=2.
- **Đề xuất sửa:** xây dựng bộ đánh giá bổ sung riêng theo các ý bắt buộc (tội, từng chất/lượng, điều, khoản, mức phạt), chấm thiếu ý và kiểm tra mâu thuẫn với nguồn; thêm yêu cầu liệt kê đủ các chất vào prompt trả lời của `src/graph.py`. Giữ nguyên benchmark/test gốc để đối chứng. Đánh đổi: tốn công chuẩn hóa gold, có thể thêm token hoặc lượt judge; prompt dài hơn chưa tự sửa dữ liệu thiếu trong KG.

### E6 — Dữ liệu định lượng bị thiếu sau trích xuất và kiểm tra bằng chứng

- **Hiện tượng:** trong graph hiện tại, vụ Cái Quang Huy và Nguyễn Tiến Đạt chỉ có một DrugFinding MDMA “gần 4,3kg”; thiếu finding riêng cho hơn 9,6kg MDMA và khoảng 406g Ketamine được nêu rõ trong bài. Có các finding ở vụ khác không có lượng; phải phân biệt nguồn không nêu lượng với lỗi bỏ mất lượng đã được nêu.
- **Bằng chứng:** truy vấn trên graph đầy đủ sau benchmark; kết quả đầy đủ được lưu ở `graph_audit.json`, mục `Q5_findings`:

```cypher
MATCH (p:Person {name:'Cái Quang Huy'})-[:HAS_PARTICIPATION]->(:Participation)-[:IN_CASE]->(k:Case)-[:HAS_FINDING]->(f:DrugFinding)-[:OF_SUBSTANCE]->(s:Substance) RETURN DISTINCT s.name AS substance, f.amount_text AS amount, f.qualifier AS qualifier, f.scope AS scope, f.evidence_text AS evidence, f.doc_id AS source;
```

```text
substance | amount     | qualifier   | scope        | source
MDMA      | gần 4,3kg | approximate | person_total | news-100260917203001265
1 dòng
```

Truy vấn này lấy mọi finding trong vụ, chưa quy lượng 4,3kg cho Huy; bài nguồn ghi lượng đó của Nguyễn Tiến Đạt. Câu nguồn trích trong E4 chứng minh có cả hơn 9,6kg MDMA của Huy và khoảng 406g Ketamine, nên việc không có hai finding này là thiếu trích xuất. Log lần benchmark mới còn ghi hai cảnh báo `news-100260917203001265: omitted unsupported substance mention MDMA` và `... Ketamine`: code đã bỏ finding khi chất không có trong đoạn bằng chứng mà mô hình chọn.

Đối chứng trường rỗng hợp lý:

```cypher
MATCH (k:Case)-[:HAS_FINDING]->(f:DrugFinding)-[:OF_SUBSTANCE]->(s:Substance) WHERE f.amount_text = '' RETURN k.name AS case_name, s.name AS substance, f.amount_text AS amount, f.value AS value, f.qualifier AS qualifier, f.evidence_text AS evidence, f.doc_id AS source ORDER BY source, substance;
```

Trong kết quả `missing_quantities`, bốn dòng MDMA/Ketamine/Methamphetamine/cần sa của `news-100260924105118645` có `amount=''`, `value=null`, `qualifier='unknown'`. Bằng chứng là câu “Khi khám xét phòng của vợ chồng Mai Anh trong viện, công an tiếp tục thu giữ MDMA, ketamine, methamphetamine, cần sa và các dụng cụ sử dụng ma túy.” Câu này không nêu lượng nên để rỗng hợp lý; không được gán 0 hoặc lấy lượng ở đoạn khác mà chưa xác định cùng người/sự kiện.

- **Nguyên nhân:** ở bước LLM trích xuất và chọn đoạn chứng cứ, một số finding chọn đoạn không chứa chất/lượng cần chứng minh. `add_news()` trong `src/graph_ontology.py` loại chất không có trong evidence và xóa lượng không khớp nguyên văn. Cơ chế này chặn dữ kiện thiếu căn cứ nhưng chưa có lượt phục hồi các finding bị loại; khớp nguyên văn cũng chưa kiểm tra đầy đủ quan hệ người–chất–lượng. Câu trả lời Q5 vẫn đúng lượng MDMA nhờ văn bản nguồn trong pipeline lai, nên benchmark trả lời che khuất lỗi graph.
- **Đề xuất sửa:** lưu danh sách finding bị loại kèm lý do, chọn lại đoạn nguồn chứa đồng thời chất và lượng rồi kiểm tra người/phạm vi trước khi ghi; chỉ retry các finding lỗi trong `extract_cases()`/`add_news()`. Thêm kiểm tra độc lập cho bộ ba người–chất–lượng và độ bao phủ nguồn. Nếu không đủ căn cứ thì giữ unknown, không suy đoán. Đánh đổi: tăng lượt LLM/token, có thể bỏ sót khi nguồn dùng đại từ; cần tránh tạo finding trùng hoặc cộng lượng tổng với từng đợt.

## 4. Kết luận

Nên dùng KG khi có nhiều KB và câu hỏi yêu cầu nối người–tội–điều luật–khoản, đối chiếu ngưỡng hoặc tổng hợp nhiều vụ: Q3–Q6 của Graph đều đạt recall=1,00, trong khi Flat đạt lần lượt 0,00; 0,00; 0,60; 0,00. Với định nghĩa hoặc mức án trong một bài như Q1–Q2, Flat đã đạt recall=1,00 và judge=2, nên phù hợp khi cần triển khai đơn giản và chi phí thấp.

Trong lần chạy này, Graph tốn 0,01463 USD để index so với 0,00112 USD của Flat và 0,00040 USD/câu so với 0,00012 USD/câu; không có hòa vốn thuần chi phí API. KG phù hợp khi lợi ích trả lời xuyên nguồn đáng giá hơn chi phí dựng/bảo trì. Graph đạt judge trung bình 2,00/2 nhưng E4–E6 cho thấy vẫn phải đọc câu trả lời, kiểm tra nguồn và graph; chưa thể suy rộng sáu câu thành độ chính xác trên mọi câu hỏi hoặc coi đây là công cụ tư vấn pháp luật.

## 5. Tự kiểm

Output test chạy lại sau lần benchmark mới nhất; 63 test gồm 41 base + 7 graph gốc + 15 test ontology bổ sung:

```text
$ python -m pytest tests/ -q
...............................................................          [100%]
63 passed in 0.11s
```

Output `--check` đã chạy trước `--judge`, khớp log người thực hiện cung cấp và `CHECK_KG.txt`:

```text
$ python bench_kg.py --check
[OK] Dữ liệu: 18 điều luật, 20 bài báo
[OK] KG-1 link_entity
[OK] Neo4j kết nối được
[provider] chat = openai:gpt-4o-mini | embedding = openai:text-embedding-3-small
news-100260918080821054: removed attribution unsupported by cited passage
[OK] KG-2 build_graph: 440 node / 981 cạnh, đường xuyên 2 KB dài 2 cạnh
[OK] KG-3 context: 5 dữ kiện, có Điều 251
[OK] KG-4 GraphRAGAgent.answer
[OK] Chi phí check: 1 lần gọi LLM, $0.00095. Graph nhỏ (luật + 1 bài) vẫn còn trong Neo4j để bạn xem; chạy --judge để dựng graph đầy đủ.
```

Không chạy lại `--check` sau `--judge` vì lệnh đó thay graph đầy đủ bằng graph nhỏ. `python scripts/inspect_kg.py` xác nhận graph hiện tại **558 node / 1.148 cạnh**. Các truy vấn Q-A–Q-D và đếm cạnh đã chạy qua driver Neo4j (chỉ đọc), có kết quả trong `graph_audit.json`; phần kiểm tra giao diện/chụp ảnh do người thực hiện tự làm theo [BROWSER_QUERIES.md](BROWSER_QUERIES.md).

| Label | Node |
| --- | --- |
| Article | 18 |
| Case | 14 |
| Clause | 99 |
| Crime | 13 |
| DrugFinding | 17 |
| Location | 13 |
| Participation | 44 |
| Person | 40 |
| Rule | 267 |
| Substance | 19 |
| Term | 14 |

| Quan hệ | Cạnh |
| --- | --- |
| ATTRIBUTED_TO | 11 |
| CHARGED_WITH | 38 |
| DEFINES | 13 |
| DEFINES_TERM | 14 |
| FOR_SUBSTANCE | 291 |
| HAS_CLAUSE | 99 |
| HAS_FINDING | 17 |
| HAS_PARTICIPATION | 44 |
| HAS_RULE | 267 |
| IN_CASE | 44 |
| LOCATED_IN | 15 |
| MENTIONS | 278 |
| OF_SUBSTANCE | 17 |

Ảnh còn chờ người thực hiện tự chụp: `report/img/kg_count.png`, `report/img/kg_cross_kb.png`, `report/img/kg_my_case.png`. Người chuẩn bị cho Q-D: **Cái Quang Huy** (đã xác nhận có đường tới Điều 250 BLHS); nếu chọn người khác, cập nhật dòng này. Chưa xác nhận đã chụp ảnh hoặc nộp Vlearn.

## Vấn đề gặp phải

Lần `--judge` mới nhất hoàn tất và sinh file kết quả. Có cảnh báo loại finding/chất hoặc quy thuộc thiếu bằng chứng, xóa lượng không nguyên văn, và một lượt retry schema vì thiếu `evidence_text`; đây là kiểm soát dữ liệu, nhưng có thể làm graph thiếu dữ kiện như E6. Chưa sửa cơ chế phục hồi finding và lỗi đánh giá E4 trong lần benchmark này. Mở Neo4j đang giữ graph đầy đủ để chụp; khi xong có thể chạy `docker stop neo4j-drug-kg`.
