# Bước 1 — Đọc dữ liệu và câu hỏi

Ghi chép dựa trên dữ liệu lưu trong repo. Các khung hình phạt dưới đây mô tả phiên bản văn bản trong bộ dữ liệu lab. Chưa triển khai code, chưa chạy benchmark; nhận định về Flat RAG là dự đoán từ cấu trúc dữ liệu.

## 1. Tài liệu đã đọc

- Luật chính: [Điều 251 BLHS](../data/drug_law/blhs-dieu-251.md).
- Bốn bài tin chính:
  1. [Lê Minh Thành và ba thanh niên kháng cáo](../data/drug_news/news-100260918080821054.md).
  2. [Cái Quang Huy vận chuyển ma túy từ Đức](../data/drug_news/news-100260917203001265.md).
  3. [Hoàng Nato và Phannhibeauty sử dụng pod chill](../data/drug_news/news-100260924095400982.md).
  4. [Đường dây mua bán hơn 36kg ma túy](../data/drug_news/news-100260928173914514.md).
- [Sáu câu hỏi benchmark](../data/benchmark_kg.json).
- Đối chiếu bổ sung: [Điều 2 Luật PCMT](../data/drug_law/pcmt-dieu-2.md), [Điều 250 BLHS](../data/drug_law/blhs-dieu-250.md), [Điều 255 BLHS](../data/drug_law/blhs-dieu-255.md), và đoạn thu giữ MDMA trong [bài về Viện Pháp y tâm thần Trung ương](../data/drug_news/news-100260924105118645.md).

## 2. Cấu trúc Điều 251

Đầu file là metadata: `doc_id`, `title`, `source_url`, `retrieved_at`, `document_version`, `kb`, `law`, `article`, `language`. Đây là thông tin nguồn, không phải nội dung một khoản luật. Ngày thu thập cũng không phải ngày xảy ra vụ việc.

Tiêu đề Markdown và dòng `Điều 251. Tội mua bán trái phép chất ma túy` cùng chỉ một điều luật; khi trích xuất không nên tạo hai điều khác nhau.

| Thành phần | Nội dung quan sát |
| --- | --- |
| Điều | Điều 251 BLHS, định nghĩa tội mua bán trái phép chất ma túy |
| Khoản 1 | Khung cơ bản: tù từ 02 năm đến 07 năm |
| Khoản 2 | Tù từ 07 năm đến 15 năm; các điểm a–q nêu tình tiết và ngưỡng chất |
| Khoản 3 | Tù từ 15 năm đến 20 năm; các điểm a–h nêu điều kiện |
| Khoản 4 | Tù 20 năm, tù chung thân hoặc tử hình; các điểm a–h nêu điều kiện |
| Khoản 5 | Hình phạt bổ sung: tiền, cấm chức vụ/hành nghề và tịch thu tài sản |

Ví dụ với MDMA:

| Vị trí | Ngưỡng khối lượng | Khung hình phạt |
| --- | --- | --- |
| Khoản 2, điểm i | Từ 05 gam đến dưới 30 gam | 07–15 năm tù |
| Khoản 3, điểm b | Từ 30 gam đến dưới 100 gam | 15–20 năm tù |
| Khoản 4, điểm b | Từ 100 gam trở lên | 20 năm tù, chung thân hoặc tử hình |

Các điểm còn chứa điều kiện không dựa vào khối lượng, như có tổ chức, qua biên giới, tái phạm nguy hiểm. Có cả đơn vị gam, kilôgam, mililít và quy tắc cho nhiều chất; không thể chỉ tìm tên chất để xác định đầy đủ điều kiện của khoản.

Không phải khoản nào cũng có mẫu “thì bị phạt tù từ … đến …”: khoản 4 có chung thân/tử hình, khoản 5 là hình phạt bổ sung. File Điều 251 đang đọc không có chú thích `[2]`; đây là dạng cần lưu ý nếu gặp ở tài liệu khác, không phải một khoản hay một thực thể mới.

## 3. Kết quả đọc bốn bài tin

| Bài | Người và vai trò | Tội danh/hành vi | Chất, lượng và địa điểm | Mức án/giai đoạn |
| --- | --- | --- | --- | --- |
| Lê Minh Thành | Thành; Trịnh Vũ Kiên, Kim Xuân Tuấn, Nguyễn Quang Hưng là đồng phạm giúp sức theo bản án sơ thẩm | Mua bán trái phép chất ma túy | 5 viên được giám định là MDMA; ketamine được đề cập trong việc mua; Ngọc Thụy, phường Bồ Đề, Hà Nội | Thành 36 tháng tù; ba người còn lại mỗi người 24 tháng; phiên phúc thẩm bị hoãn |
| Cái Quang Huy | Huy, Nguyễn Tiến Đạt; Nguyễn Hữu Đức từng bị khởi tố nhưng quyết định đã bị hủy | Vận chuyển trái phép chất ma túy | Huy: hơn 9,6kg MDMA, khoảng 406g Ketamine; Đạt: gần 4,3kg MDMA; Đức/Berlin, Nội Bài, Hà Nội, Nghệ An | Truy tố, chuẩn bị xét xử; Huy bị truy nã; chưa có mức án được tuyên trong bài |
| Hoàng Nato | Dương Minh Tuấn = Hoàng Nato; Phan Kim Nhi = TikToker Phannhibeauty | Tổ chức sử dụng ma túy; bài còn nhắc đầy đủ hành vi tổ chức sử dụng trái phép chất ma túy trong chuyên án | Etomidate trong pod chill; 5 ống mỗi lần được kể; Gia Định, TP.HCM | Bị bắt, đang điều tra; chưa có mức án được tuyên |
| Hơn 36kg ma túy | Trần Thanh Tuấn, Trần Minh Tâm, Đỗ Thị Ngọc Yến, Võ Nữ Minh Thư, Đinh Đức Tuấn, Trần Ngọc Thảo | Bốn người đầu: mua bán trái phép chất ma túy; hai người cuối: tổ chức sử dụng trái phép chất ma túy | Hơn 36kg ma túy các loại thuộc trách nhiệm của Tuấn/Tâm; bài không nêu tên hóa học cụ thể; TP.HCM, tuyến Campuchia–Việt Nam | Tuấn/Tâm tử hình; Yến 8 năm 6 tháng; Thư 8 năm; Đinh Đức Tuấn/Thảo mỗi người 2 năm 6 tháng |

### Tên tội trong báo có thống nhất với luật không?

- Cụm “mua bán trái phép chất ma túy” trong bài Thành và bài hơn 36kg phù hợp tên tội tại Điều 251, sau khi bỏ tiền tố “Tội” và chuẩn hóa chữ hoa/thường, Unicode.
- “Vận chuyển trái phép chất ma túy” là tội khác, cần nối với Điều 250; không nối vào Điều 251 chỉ vì cùng có ma túy.
- Bài Hoàng Nato có cách diễn đạt rút gọn “tổ chức sử dụng ma túy loại etomidate”. Cần đối chiếu ngữ cảnh và tên chuẩn “tổ chức sử dụng trái phép chất ma túy” ở Điều 255.
- “Mua ma túy để sử dụng”, lời khai phủ nhận, cáo trạng và kết luận của tòa là những thông tin khác nhau. Không tự suy ra tội danh từ một động từ trong lời kể.
- Một vụ có nhiều tội danh và mức án theo từng người. Chỉ lưu một tội/mức án chung cho cả vụ có thể gán nhầm thông tin.

### Thông tin lặp lại và các nguy cơ trích xuất

- MDMA và ketamine xuất hiện ở cả bài Thành lẫn bài Huy. Hà Nội cũng lặp lại nhưng là địa điểm của nhiều vụ khác nhau.
- Tội mua bán trái phép chất ma túy lặp ở bài Thành và bài hơn 36kg; tổ chức sử dụng trái phép chất ma túy xuất hiện ở bài Hoàng Nato và bài hơn 36kg.
- Tên Cái Quang Huy xuất hiện trong bài riêng và đoạn giới thiệu ở cuối bài Thành. Đoạn cuối này nói về vụ khác; không được gán hơn 9,6kg MDMA của Huy cho vụ Thành.
- Dương Minh Tuấn/Hoàng Nato và Phan Kim Nhi/Phannhibeauty là các cặp tên–bí danh của cùng người.
- “Tuấn” có thể chỉ Kim Xuân Tuấn, Trần Thanh Tuấn, Đinh Đức Tuấn hoặc Dương Minh Tuấn. Không gộp người bằng tên gọi ngắn.
- 24 tháng = 2 năm; 36 tháng = 3 năm. Chuẩn hóa để so sánh nhưng giữ cách ghi gốc để đối chiếu nguồn.
- “5 viên”, “5 ống”, “nửa chỉ” không tự động chuyển thành gam nếu thiếu căn cứ. Hơn 1.000 đầu pod thu giữ trong toàn chuyên án không phải lượng riêng của Hoàng Nato.
- Không cộng hơn 5,3kg, gần 4,3kg và hơn 9,6kg thành ba lần lượng độc lập: hơn 9,6kg là tổng của Huy. Cần phân biệt lượng từng đợt, từng người và tổng vụ.
- Bị bắt/truy tố không có nghĩa đã bị tuyên án. Mức án thiếu trong bài Huy và Hoàng Nato là thiếu hợp lý.

## 4. Thực thể và quan hệ trong hai KB

Đây là danh sách khái niệm quan sát được, chưa phải quyết định bắt buộc khái niệm nào cũng phải thành node. Cách chọn node/property thuộc Bước 2.

| Nhóm thực thể/khái niệm | KB luật | KB tin tức | Ví dụ |
| --- | --- | --- | --- |
| Văn bản luật, điều, khoản, điểm | Có cấu trúc đầy đủ | Có thể được viện dẫn, thường không đủ nội dung | BLHS, Điều 251; bài Thành viện dẫn Điều 16 |
| Tội danh/hành vi | Định nghĩa và điều kiện | Cáo buộc, truy tố, kết luận xét xử | Mua bán; vận chuyển; tổ chức sử dụng trái phép chất ma túy |
| Chất/nhóm chất | Tên chất và ngưỡng | Tang vật, chất được mua/sử dụng/vận chuyển | MDMA, Methamphetamine; ketamine/etomidate được nêu trong tin |
| Người | Chủ thể khái quát: “người nào”, “người phạm tội” | Cá nhân có tên và bí danh | Lê Minh Thành, Cái Quang Huy |
| Vụ án/vụ việc | Không có vụ cụ thể trong các điều đang xét | Có | Vụ Thành, vụ Huy, vụ hơn 36kg |
| Địa điểm, cơ quan | Quy định/nhắc cơ quan hoặc điều kiện địa lý khái quát | Địa điểm và cơ quan cụ thể | Nội Bài, TP.HCM, TAND TP Hà Nội |
| Hình phạt | Khung có thể áp dụng | Mức án thực tế theo người, giai đoạn | 02–07 năm; 36 tháng; tử hình |
| Lượng, đơn vị, điều kiện | Ngưỡng và khoảng | Lượng ghi nhận, đôi khi xấp xỉ | MDMA từ 100 gam; hơn 9,6kg MDMA |
| Sự kiện/giai đoạn, ngày | Quy định tổng quát | Bắt, truy tố, sơ thẩm, phúc thẩm | Phiên phúc thẩm bị hoãn; ngày xét xử 28-9 |

Quan hệ quan sát được:

| KB | Quan hệ | Ví dụ |
| --- | --- | --- |
| Luật | Văn bản chứa điều; điều chứa khoản; khoản chứa điểm | BLHS → Điều 251 → khoản 4 → điểm b |
| Luật | Điều định nghĩa tội danh | Điều 251 → mua bán trái phép chất ma túy |
| Luật | Khoản/điểm quy định điều kiện, chất, ngưỡng và hình phạt | Khoản 4, điểm b → MDMA ≥ 100g; khoản 4 → 20 năm/chung thân/tử hình |
| Tin | Người tham gia vụ với vai trò | Kiên → vụ Thành, vai trò đồng phạm giúp sức theo án sơ thẩm |
| Tin | Người bị cáo buộc/truy tố/tuyên án về tội trong vụ | Thành → mua bán trái phép chất ma túy, 36 tháng sơ thẩm |
| Tin | Vụ liên quan chất và lượng | Vụ Huy → MDMA, hơn 9,6kg thuộc trách nhiệm của Huy |
| Tin | Vụ xảy ra tại/đi qua địa điểm, do cơ quan xử lý | Vụ Huy → Nội Bài; vụ hơn 36kg → TAND TP.HCM |
| Tin | Người có tên khác/bí danh | Dương Minh Tuấn ↔ Hoàng Nato |
| Cả hai | Dữ kiện có nguồn tài liệu | Nội dung luật/tin → `doc_id`, URL và phiên bản nguồn |

**Thực thể cầu nối rõ nhất là tội danh và chất ma túy.** Tội danh nối một vụ cụ thể với điều luật; chất giúp liên kết vụ với các khoản nhắc chất đó. Khung hình phạt và mức án cùng thuộc nhóm hình phạt nhưng không phải cùng một dữ kiện. Cá nhân có tên trong tin không phải “người nào” trong luật.

Ví dụ đường nối khái niệm:

```text
Lê Minh Thành → vụ Thành → mua bán trái phép chất ma túy ← Điều 251 → khoản 1
Cái Quang Huy → vụ Huy → vận chuyển trái phép chất ma túy ← Điều 250
                         └→ MDMA, hơn 9,6kg → đối chiếu khoản 4, điểm b
```

Chất MDMA đơn lẻ chưa đủ xác định đúng điều luật: cùng chất đó nhưng hành vi mua bán và vận chuyển đi tới hai điều khác nhau.

## 5. Đối chiếu sáu câu benchmark

| Câu | KB và dữ kiện cần lấy | Kết quả theo dữ liệu lab | Flat RAG có thể lấy đủ không? |
| --- | --- | --- | --- |
| Q1 — Tiền chất là gì? | Chỉ KB luật: khoản 4 Điều 2 Luật PCMT | Hóa chất không thể thiếu trong điều chế, sản xuất chất ma túy, được quy định trong danh mục tiền chất do Chính phủ ban hành | Khả năng cao nếu tìm đúng chunk định nghĩa; không cần nối vụ với luật |
| Q2 — Ai bị tử hình trong vụ hơn 36kg? | Chỉ KB tin: bài `news-100260928173914514` | Trần Thanh Tuấn và Trần Minh Tâm | Khả năng cao: tên, mức án và vụ nằm ngay cùng đoạn mở đầu |
| Q3 — Mức án Thành, tội, điều và khung cơ bản? | Tin về Thành + khoản 1 Điều 251 | 36 tháng tù; mua bán trái phép chất ma túy; Điều 251; 02–07 năm | Có thể đủ nếu top-k chứa cả bài và khoản luật; dễ thiếu luật vì tên Thành chỉ có trong tin |
| Q4 — Hoàng Nato bị bắt vì hành vi gì, khung tối đa? | Tin về bí danh/hành vi + khoản 4 Điều 255 | Dương Minh Tuấn/Hoàng Nato; tổ chức sử dụng trái phép chất ma túy; khung cao nhất 20 năm hoặc chung thân | Có thể đủ nếu lấy được cả tin và khoản cao nhất; dễ nhầm với hành vi sử dụng hoặc chỉ lấy khung cơ bản. Khung tối đa của tội không phải mức án đã tuyên cho người này |
| Q5 — Tội, chất, lượng của Huy và khoản tương ứng? | Tin Huy + khoản 4, điểm b Điều 250; đối chiếu đơn vị | Vận chuyển trái phép chất ma túy; hơn 9,6kg MDMA, khoảng 406g Ketamine; ngưỡng MDMA ≥ 100g tại khoản 4; 20 năm/chung thân/tử hình | Khó hơn: phải nối nhiều dữ kiện, đổi kg sang g và giữ đúng loại tội; không được dùng Điều 251 chỉ vì có cùng MDMA |
| Q6 — Những vụ nào liên quan MDMA? | Chỉ KB tin nhưng phải tổng hợp nhiều tài liệu | Đáp án benchmark liệt kê vụ Huy, vụ Thành và vụ Viện Pháp y tâm thần Trung ương | Có thể tìm một số vụ nhưng top-k không đảm bảo đủ; nhiều chunk từ cùng vụ có thể chiếm chỗ, và nhiều bài về cùng vụ cần gộp |

Q6 được đối chiếu thêm bằng đoạn bài Viện Pháp y nêu việc thu giữ MDMA, ketamine, methamphetamine và cần sa. Ba vụ trên là các vụ trong đáp án chuẩn benchmark, không phải kết luận đã rà soát toàn bộ corpus để chứng minh chỉ có đúng ba vụ.

Nhận định chung: Q1–Q2 phù hợp truy xuất một nguồn; Q3–Q5 cần nối hai KB; Q6 cần truy xuất nhiều bài và gộp theo vụ. Flat RAG vẫn có thể trả lời đầy đủ khi lấy đúng ngữ cảnh. Chưa có số liệu để kết luận GraphRAG thắng; graph cũng có thể thiếu hoặc nối sai nếu ontology, trích xuất hay truy vấn chưa phù hợp.

## 6. Tự kiểm hoàn thành Bước 1

- [x] Đọc Điều 251, nhận diện điều/khoản/điểm, hình phạt, chất và ngưỡng.
- [x] Đọc bốn bài tin, đối chiếu tội danh và các thông tin lặp.
- [x] Phân loại nguồn dữ liệu và dự đoán khả năng Flat RAG cho Q1–Q6.
- [x] Liệt kê thực thể và quan hệ trong hai KB.
- [x] Chỉ ra tội danh và chất là các thực thể dùng chung có thể nối hai KB.

Bước tiếp theo là thiết kế ontology dựa trên các quan sát này, đặc biệt lưu ý bí danh, nhiều tội trong một vụ, giai đoạn tố tụng, lượng theo người/đợt và nguồn gốc dữ kiện.
