# Triển khai KG-1 đến KG-4

## Cấu trúc code

- `src/graph.py`: bốn entry point của lab; giữ helper HINT để benchmark đối chứng.
- `src/graph_ontology.py`: parser luật/ngưỡng, kiểm tra JSON và bằng chứng, dựng 11 label và truy xuất nhiều bước theo ontology.
- `data/entity_registry.json`: bảng đối chiếu nguồn cho cùng vụ/người; không chứa đáp án benchmark, mức án hay khối lượng để thay thế trích xuất.
- `tests/test_ontology.py`: 15 regression test bổ sung, không sửa test có sẵn.
- `scripts/inspect_kg.py`: xuất số liệu graph và context Q1–Q6, không gọi LLM.
- `scripts/audit_kg.py`: truy vấn chỉ đọc Q-A–Q-D, lượng thiếu, tội chưa nối, nhóm vụ MDMA; lưu Cypher và kết quả vào `report/graph_audit.json` để tái kiểm chứng báo cáo.

## Cách chạy trên PowerShell

Kích hoạt Docker Desktop và container Neo4j trước. API key nằm trong `.env` được gitignore; không đưa key vào code hoặc báo cáo.

```powershell
$env:PYTHONIOENCODING = 'utf-8'
$env:KG_ONTOLOGY = 'custom'
.venv/Scripts/python.exe -m pytest tests/test_base.py tests/test_graph.py -q
.venv/Scripts/python.exe -m pytest tests/test_ontology.py -q
.venv/Scripts/python.exe bench_kg.py --check
.venv/Scripts/python.exe bench_kg.py --judge
.venv/Scripts/python.exe scripts/inspect_kg.py
.venv/Scripts/python.exe scripts/audit_kg.py
```

`KG_ONTOLOGY` mặc định là `custom`. Khi benchmark đối chứng:

```powershell
$env:KG_ONTOLOGY = 'hint'
.venv/Scripts/python.exe bench_kg.py --judge --out ket_qua_benchmark_kg.hint.txt
$env:KG_ONTOLOGY = 'custom'
.venv/Scripts/python.exe bench_kg.py --judge
```

Mỗi lệnh benchmark/build/check xóa và dựng lại graph trong container của lab. Chạy custom cuối cùng để graph đang mở khớp ontology mới. Dùng cùng provider/model/top-k/chunk-size cho hai lần so sánh.

## Kiểm tra đã thực hiện

Test nền và test graph gốc:

```text
48 passed
```

Regression bổ sung:

```text
15 passed
```

Lần check sau khi sửa cơ chế bằng chứng và quy thuộc lượng đạt đủ 7 dòng OK, 440 node / 981 cạnh, đường xuyên KB dài 2 cạnh. Output ở `CHECK_KG.txt`. Đây là graph luật + một bài kiểm tra, không phải số lượng graph đầy đủ.

Benchmark cuối đã hoàn tất: graph đầy đủ 558 node / 1148 cạnh; Graph recall 1,00, judge 2,00; Flat recall 0,43, judge 1,00. File kết quả ở `../ket_qua_benchmark_kg.txt`, snapshot ở `graph_contexts.json`, so sánh đối chứng và các hạn chế còn lại ở `COMPARISON_KG.md`.

## Giới hạn triển khai

- Evidence phải tồn tại nguyên văn trong nguồn, nhưng điều này chưa đảm bảo LLM gán đúng câu cho đúng người; cần đối chiếu các trường hợp phức tạp.
- Quy thuộc lượng cần tên/bí danh hoặc tên ngắn duy nhất trong đoạn nguồn. Bằng chứng nói rõ “trong chuyên án” được giữ ở operation_total và không gán cho một người. Đây là kiểm tra bảo thủ; có thể bỏ mất quy thuộc đúng nếu nguồn chỉ dùng đại từ.
- Các đoạn nguồn được đánh mã S0001…; LLM chọn mã, code lấy lại nguyên văn, tránh lỗi chép lại dấu/Unicode. Nếu LLM trả trực tiếp một quote thì vẫn phải khớp nguyên văn nguồn.
- Schema/bằng chứng sai được thử lại tối đa một lần rồi dừng build. Toàn bộ trích xuất được kiểm tra trước khi ghi graph; không bỏ bài im lặng. Bài hợp lệ không có vụ cụ thể có thể trả cases rỗng. Finding chưa biết tên chất bị bỏ với cảnh báo, giữ nội dung ở Case; không tạo chất giả.
- Ngưỡng hỗn hợp nhiều chất giữ nguyên văn, chưa tự quy đổi. Lượng xấp xỉ hoặc khoảng không đủ chắc chắn không được tự gán khoản.
- Bảng định danh chỉ nhóm các nguồn/vụ có căn cứ; các nguồn chưa đối chiếu giữ canonical ID cục bộ, có thể còn đếm trùng.
- Hint mode giữ hành vi trích xuất và lọc khoản của gợi ý làm baseline; không dùng nó làm ontology mặc định.
- Báo cáo `REPORT_KG.md` đã hoàn thiện theo benchmark mới nhất; ảnh Neo4j do người thực hiện tự chụp theo `BROWSER_QUERIES.md`, hiện chưa có ảnh trong repo. Chưa xác nhận nộp Vlearn.
