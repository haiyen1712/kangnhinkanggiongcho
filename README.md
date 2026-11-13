# HỆ THỐNG AI AGENT XỬ LÝ CƠ HỘI BÁN HÀNG B2B - CÔNG TY MINH AN
**Học phần:** AI301 | Đề 01  
**Đơn vị:** Công ty Cổ phần Công nghệ & Dịch vụ Doanh nghiệp Minh An (Giả định)  

---

## 📌 TỔNG QUAN HỆ THỐNG

Dự án xây dựng giải pháp AI Agent đa kỹ năng (Multi-Skill AI Agent) tự động hóa quy trình xử lý cơ hội bán hàng B2B, giải quyết triệt để 4 vấn đề nhức nhối hiện nay của Công ty Minh An:
1. **Bỏ sót hạng mục** trong đề xuất giải pháp.
2. **Sử dụng bảng giá cũ, tính sai chiết khấu** gây thất thoát biên lợi nhuận.
3. **Hứa thời hạn triển khai ảo** không đáp ứng được do thiếu hàng trong kho.
4. **Tắc nghẽn quy trình**, yêu cầu thiếu thông tin/vượt quyền bị chuyển qua lại không người theo dõi.

Hệ thống được thiết kế theo nguyên tắc: **Tuyệt đối không tự ý xác nhận bán hàng khi chưa đủ dữ kiện hoặc vượt thẩm quyền** và tích hợp chặt chẽ cơ chế **Human-in-the-loop (Con người kiểm tra / phê duyệt)**.

---

## 🛠️ CẤU TRÚC MÃ NGUỒN

```
/Users/mac/môn mới/
├── config.py                 # CSDL Danh mục sản phẩm, bảng giá niêm yết, tồn kho, quy chế chiết khấu, phân quyền
├── tools.py                  # 4 Kỹ năng nghiệp vụ: Thẩm định thông tin, Thẩm định tồn kho/Lead-time, Báo giá, Soạn thảo
├── agent.py                  # Lớp AI Agent điều phối quy trình To-Be, hệ thống Audit Logger lưu vết thực thi
├── data_loader.py            # Xử lý nạp dữ liệu: Google Sheet link, File CSV/XLSX, Text tự do, sinh bộ dữ liệu mẫu
├── app.py                    # Giao diện Streamlit Web trực quan, Dashboard KPI, Chi tiết Dossier, Audit Trail
├── test_suite.py             # Kịch bản kiểm thử tự động 10 test cases (Standard, Missing, Boundary, Escalation, Infeasible)
├── sample_opportunities.xlsx # File dữ liệu mẫu Excel 10 trường hợp chuẩn hóa
├── sample_opportunities.csv  # File dữ liệu mẫu CSV
└── README.md                 # Tài liệu hướng dẫn hệ thống
```

---

## 🚀 HƯỚNG DẪN KHỞI CHẠY HỆ THỐNG

### 1. Khởi chạy ứng dụng Web (Streamlit UI)
Chạy lệnh sau trong thư mục dự án:
```bash
./.venv/bin/streamlit run app.py
```
Sau đó truy cập trình duyệt tại địa chỉ: `http://localhost:8501`

### 2. Chạy Kiểm Thử Tự Động (Automated Evaluation Test)
```bash
./.venv/bin/python test_suite.py
```
Toàn bộ 10 kịch bản kiểm thử (thông thường, thiếu dữ liệu, ranh giới quy tắc, vượt quyền, thiếu kho) sẽ được đánh giá tự động và in ra bảng tổng hợp chỉ số KPI.

---

## 📥 CÁC PHƯƠNG THỨC NẠP DỮ LIỆU ĐẦU VÀO

Tại thanh bên trái (Sidebar) của giao diện Web, người dùng có thể lựa chọn 4 cách nạp dữ liệu:
1. **⚡ Bộ dữ liệu mẫu Demo (10 Cases chuẩn):** Nhấn 1 nút để nạp ngay bộ dữ liệu thử nghiệm toàn diện.
2. **📊 Tải lên File (CSV / XLSX):** Tải file Excel hoặc CSV từ máy tính.
3. **🔗 Link Google Sheets:** Dán liên kết Google Sheet (bảng tính cần được chia sẻ quyền *'Bất kỳ ai có liên kết đều có thể xem'*). Hệ thống sẽ tự động trích xuất Document ID và nạp dữ liệu trực tiếp.
4. **✍️ Nhập văn bản yêu cầu tự do:** Dán trực tiếp email hoặc yêu cầu dạng text không cấu trúc, AI Agent sẽ tự động bóc tách thực thể và xử lý.

---

## 📊 KẾT QUẢ ĐẦU RA TRÊN GIAO DIỆN

Giao diện trực quan gồm 4 Tab chức năng chính:
- **Tab 1: Bảng Điều Khiển Tổng Quan (Pipeline Dashboard):**
  - Thống kê 5 chỉ số KPI: Tổng yêu cầu, Có thể tiếp tục, Chờ duyệt, Cần bổ sung thông tin, Chưa đáp ứng.
  - **Thẻ Doanh số tiềm năng:** Tính riêng tổng giá trị của các cơ hội *Có thể tiếp tục* + *Chờ duyệt*.
  - Bảng danh sách cơ hội có bộ lọc trạng thái và tìm kiếm.
  - Nút xuất báo cáo tổng hợp ra file CSV.
- **Tab 2: Chi Tiết Hồ Sơ Cơ Hội & Đề Xuất Kinh Doanh:**
  - Chọn bất kỳ cơ hội nào để xem toàn văn Hồ sơ Cơ hội (Dossier).
  - Bảng đối chiếu Tồn kho & Lead-time chi tiết từng linh kiện.
  - Bảng tính Báo giá, Chiết khấu và Đánh giá Ngân sách.
  - Bản nháp Email gửi khách hàng (theo từng trạng thái nghiệp vụ).
  - **Phiếu Trình Duyệt Trưởng Phòng:** Có nút tương tác *Phê duyệt* hoặc *Từ chối* (Human-in-the-loop).
- **Tab 3: Nhật Ký Truy Vết AI Agent (Audit & Trace Log):**
  - Hiển thị từng bước gọi tool, tham số vào/ra, quy tắc nghiệp vụ áp dụng.
  - Chứng minh Agent hoạt động bằng công cụ và quy tắc rõ ràng, không bịa đặt hoặc hardcode.
- **Tab 4: Báo Cáo Phân Tích & Thiết Kế Quy Trình (Task 1):**
  - Trình bày toàn văn phân tích As-Is, 4 vấn đề, Sơ đồ To-Be, 3 bước AI tự thực hiện, 2 chốt chặn con người.

---

## 🎯 GIẢI THÍCH 4 TRẠNG THÁI CƠ HỘI BÁN HÀNG

1. **CÓ THỂ TIẾP TỤC (Ready to proceed):**
   - Đầy đủ thông tin (khách hàng, thiết bị, số lượng, ngân sách, thời hạn).
   - Kho đáp ứng được tiến độ giao hàng.
   - Chiết khấu nằm trong hạn mức tự quyết của NVKD (<= 5% hoặc theo nấc).
   - Ngân sách của khách hàng đủ chi trả.
2. **CẦN BỔ SUNG THÔNG TIN (Need more info):**
   - Thiếu một trong các thông tin: Tên khách hàng, liên hệ, mã/số lượng sản phẩm, ngân sách, hoặc thời hạn.
   - Agent tự động sinh email hỏi làm rõ, tuyệt đối không tự ý xác nhận bán hàng.
3. **CHỜ DUYỆT (Pending approval):**
   - Khách hàng yêu cầu mức chiết khấu vượt quyền NVKD nhưng nằm trong trần Trưởng phòng duyệt (<= 15%), HOẶC ngân sách bị hụt nhẹ trong phạm vi tolerance 5%.
   - Agent tự động lập Phiếu chuyển duyệt (Approval Ticket) trình Trưởng phòng Hoàng Minh Trí.
4. **CHƯA ĐÁP ỨNG (Cannot fulfill):**
   - Tồn kho không đủ và thời gian nhập hàng vượt xa thời hạn gấp của khách, HOẶC chiết khấu đòi hỏi vượt trần công ty (> 15%), HOẶC ngân sách thiếu hụt quá lớn (> 5%).
   - Agent tạo email giải thích rõ căn cứ và đề xuất phương án thay thế (giao từng phần hoặc điều chỉnh cấu hình).

