# Truy vấn Neo4j Browser để tự chụp ảnh

Graph hiện tại sau benchmark mới nhất: **558 node / 1.148 cạnh**. Các truy vấn tương đương đã kiểm tra qua Neo4j driver; xem `graph_audit.json`. Người thực hiện tự chạy trên Browser và tự chụp ảnh. Không chạy lại `--check` trước khi chụp vì nó thay graph đầy đủ bằng graph nhỏ.

Mở http://localhost:7474, kết nối `neo4j://localhost:7687` bằng tài khoản lab. Gõ `:clear` và chạy trước **mỗi** truy vấn chụp ảnh. Chụp toàn bộ cửa sổ trình duyệt, thấy ô truy vấn, kết quả và Results overview; không cắt hoặc chỉnh sửa ảnh.

## Q-A — Đếm node, lưu `report/img/kg_count.png`

```cypher
MATCH (n)
RETURN labels(n)[0] AS label, count(*) AS n
ORDER BY n DESC;
```

Chọn tab **Table**, đủ 11 dòng: Rule 267; Clause 99; Participation 44; Person 40; Substance 19; Article 18; DrugFinding 17; Case 14; Term 14; Crime 13; Location 13. Tổng 558. Nếu số khác, có thể graph đã được dựng lại; cần cập nhật benchmark/snapshot/báo cáo tương ứng.

## Q-B — Cầu nối báo chí sang luật, lưu `report/img/kg_cross_kb.png`

```cypher
MATCH p=(:Person)-[:HAS_PARTICIPATION]->(:Participation)
          -[:IN_CASE]->(:Case)-[:CHARGED_WITH]->(:Crime)
          <-[:DEFINES]-(:Article)
RETURN p LIMIT 25;
```

Chọn tab **Graph**. Results overview cần có Person, Participation, Case, Crime, Article và các cạnh HAS_PARTICIPATION, IN_CASE, CHARGED_WITH, DEFINES. Crime là node cầu nối; Case–CHARGED_WITH là chỉ mục tội của vụ, không khẳng định mọi người trong vụ đều phạm mọi tội. Q-D dùng trực tiếp tội trên Participation để tránh suy luận đó.

## Q-C — Kiểm tra Điều 251, không bắt buộc chụp ảnh nộp

```cypher
MATCH p=(:Article {doc_id:'blhs-dieu-251'})
          -[:HAS_CLAUSE]->(:Clause)-[:MENTIONS]->(:Substance)
RETURN p;
```

Xem Điều 251 nối tới các khoản và chất. Khi cần xem cả khoản không nhắc chất:

```cypher
MATCH (a:Article {doc_id:'blhs-dieu-251'})-[:HAS_CLAUSE]->(cl:Clause)
RETURN a.name, cl.number, cl.penalty_text ORDER BY cl.number;
```

## Q-D — Cái Quang Huy, lưu `report/img/kg_my_case.png`

Người chuẩn bị trong báo cáo là **Cái Quang Huy**, khác Lê Minh Thành. Nếu tự chọn người khác, sửa tên ở truy vấn và ở `REPORT_KG.md`.

```cypher
MATCH p=(person:Person {name:'Cái Quang Huy'})
          -[:HAS_PARTICIPATION]->(pt:Participation)
          -[:CHARGED_WITH]->(:Crime)<-[:DEFINES]-(:Article)
MATCH q=(pt)-[:IN_CASE]->(k:Case)
OPTIONAL MATCH f=(k)-[:HAS_FINDING]->(:DrugFinding)
                      -[:OF_SUBSTANCE]->(:Substance)
OPTIONAL MATCH l=(k)-[:LOCATED_IN]->(:Location)
RETURN p, q, f, l;
```

Chọn tab **Graph**, thấy đường Cái Quang Huy → Participation → tội vận chuyển → Điều 250 BLHS, kèm vụ/chất/địa điểm nếu có. Finding của vụ không tự động là lượng riêng của Huy: lượng gần 4,3kg trong bài thuộc Nguyễn Tiến Đạt; lỗi thiếu finding của Huy đã phân tích ở E6 trong báo cáo.

## Bước 8.3 — Đếm cạnh

```cypher
MATCH ()-[r]->()
RETURN type(r) AS rel, count(*) AS n ORDER BY n DESC;
```

Kết quả đầy đủ: 13 loại, tổng 1.148 cạnh; xem bảng trong `REPORT_KG.md`.

## Sau khi tự chụp

Lưu đúng ba tên file trên rồi chạy:

```powershell
git add report/img/kg_count.png report/img/kg_cross_kb.png report/img/kg_my_case.png
git commit -m "docs: add Neo4j lab screenshots"
git push origin main
```

Nộp link repo lên trang Vlearn Day 19: https://github.com/ToRong31/K4-Day19-PhamHoangTrong-2A202602765. Khi chụp xong và không dùng Neo4j nữa, có thể tắt container bằng `docker stop neo4j-drug-kg`.
