# Đối chứng ontology gợi ý và ontology mới

Nguồn: `ket_qua_benchmark_kg.hint.txt` (hint) và `ket_qua_benchmark_kg.txt` (custom mới nhất), đều do `bench_kg.py --judge` sinh ra. Cấu hình chung: gpt-4o-mini, text-embedding-3-small, top_k=3, chunk_size=800, 176 chunk. Graph hiện tại khớp custom; snapshot lấy bằng truy vấn chỉ đọc sau benchmark.

## Kết quả GraphRAG

| Chỉ số | Ontology gợi ý | Ontology mới |
| --- | --- | --- |
| Node / cạnh | 202 / 382 | 558 / 1148 |
| Recall trung bình | 0,74 | 1,00 |
| Judge trung bình (0–2) | 1,50 | 2,00 |
| Indexing USD | 0,00935 | 0,01463 |
| Indexing giây | 204,7 | 326,5 |
| Query USD trung bình | 0,00050 | 0,00040 |
| Query input token trung bình | 3039 | 2360 |
| Query giây trung bình | 3,30 | 5,15 |

Chi phí index custom khoảng 1,565 lần hint; chi phí query khoảng 0,80 lần hint. Tuy nhiên custom vẫn đắt hơn Flat ở lần chạy mới (0,00040 so với 0,00012 USD/câu). Timing biến động API/mạng: cùng 176 lượt embedding nhưng Flat ở run hint mất 115,8 giây, run custom mới mất 214,3 giây. Không quy toàn bộ khác biệt thời gian cho ontology. USD là ước tính theo token, giá trị đã làm tròn; chi phí máy chủ và judge chưa nằm trong so sánh trả lời.

## Từng câu

| Câu | Hint Graph recall / judge | Custom Graph recall / judge | Flat ở run custom |
| --- | --- | --- | --- |
| Q1 | 1.00 / 2 | 1.00 / 2 | 1.00 / 2 |
| Q2 | 1.00 / 2 | 1.00 / 2 | 1.00 / 2 |
| Q3 | 1.00 / 2 | 1.00 / 2 | 0.00 / 0 |
| Q4 | 0.33 / 1 | 1.00 / 2 | 0.00 / 0 |
| Q5 | 0.80 / 1 | 1.00 / 2 | 0.60 / 1 |
| Q6 | 0.33 / 1 | 1.00 / 2 | 0.00 / 1 |

## Bằng chứng cải thiện

Q4 hint trả lời:

> Giang hồ 'Hoàng Nato' bị bắt về hành vi tổ chức sử dụng trái phép chất ma túy. Tuy nhiên, trong ngữ cảnh hiện tại không đủ thông tin để xác định mức phạt tù tối đa cho hành vi này theo Bộ luật Hình sự.

Q4 custom trả lời:

> Giang hồ 'Hoàng Nato' (Dương Minh Tuấn) bị bắt về hành vi "tổ chức sử dụng trái phép chất ma túy". Hành vi này có thể bị phạt tù tối đa theo Điều 255 Bộ luật Hình sự, với mức án là 20 năm hoặc tù chung thân nếu phạm tội thuộc một trong các trường hợp quy định tại khoản 4 của điều luật này.

Context Q4 trong `graph_contexts.json` có khoản 4 Điều 255. Khung cao nhất của tội không phải án đã tuyên cho Hoàng Nato. Từ câu trả lời hint chưa xác định duy nhất thiếu luật do seed, linking hay lọc khoản; không còn snapshot hint để tách các nguyên nhân.

Q5 hint trả lời:

> Cái Quang Huy bị truy tố về tội vận chuyển trái phép chất ma túy với loại ma túy là MDMA. Với khối lượng MDMA trong vụ này là hơn 9,6kg, khoản áp dụng tương ứng là khoản 4 của Điều 251 BLHS, trong đó quy định rằng phạm tội thuộc trường hợp có khối lượng MDMA từ 100 gam trở lên sẽ bị phạt tù 20 năm, tù chung thân hoặc tử hình.

Q5 custom trả lời:

> Cái Quang Huy bị truy tố về tội vận chuyển trái phép chất ma túy, cụ thể là ma túy MDMA. Với tổng khối lượng MDMA là hơn 9,6kg, khoản áp dụng tương ứng là khoản 4 của Điều 250 Bộ luật Hình sự (BLHS), với khung hình phạt là 20 năm, tù chung thân hoặc tử hình.

Custom dẫn đúng Điều 250 khoản 4; hint dẫn Điều 251 cho tội vận chuyển. Ontology mới chọn điều theo Crime, sau đó xét Rule/chất/đơn vị. Trước/sau đồng thời thay ontology, prompt trích xuất và truy vấn; chưa chứng minh riêng tác động của từng thay đổi.

Q6 hint liệt kê thêm vụ hơn 36kg có MDMA; custom liệt kê ba nhóm vụ. Truy vấn `MDMA_cases` trong `graph_audit.json` hiện nhóm ra ba vụ: Huy–Đạt, Thành, Viện Pháp y tâm thần. Kết quả mới Graph recall=1,00 và judge=2; không tiếp tục dùng judge=1 của lần chạy cũ làm số liệu hiện tại.

## Lỗi còn lại

Q5 custom vẫn bỏ Ketamine dù đạt recall=1,00/judge=2. Graph hiện tại chỉ có một finding MDMA gần 4,3kg trong vụ Huy–Đạt; thiếu hai finding hơn 9,6kg MDMA và khoảng 406g Ketamine trong nguồn. Vector chunks/evidence có thể giúp trả lời đúng lượng ngay khi graph thiếu bản ghi có cấu trúc. Hai lỗi E4/E6 và bằng chứng Cypher, nguyên nhân, đề xuất sửa nằm ở [REPORT_KG.md](REPORT_KG.md).

Các finding không có lượng cũng xuất hiện ở Viện Pháp y tâm thần; câu nguồn chỉ liệt kê tên chất nên để unknown hợp lý. Việc evidence nằm nguyên văn trong nguồn chưa bảo đảm gán đúng người/scope hoặc trích đủ dữ kiện. Kết quả trên sáu câu chưa chứng minh chất lượng tổng quát.
