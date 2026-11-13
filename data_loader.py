"""
MODULE NẠP VÀ TIỀN XỬ LÝ DỮ LIỆU ĐẦU VÀO
Hỗ trợ:
- File tải lên: CSV, XLSX
- Đường dẫn Google Sheet (tự động export CSV)
- Văn bản yêu cầu tự do (Raw text / Email)
- Sinh bộ dữ liệu kiểm thử mẫu chuẩn hóa (Sample Test Suite)
"""

import re
import json
import io
from typing import List, Dict, Any, Union
import pandas as pd
import requests


def normalize_col_name(col: str) -> str:
    """Chuẩn hóa tên cột để dễ mapping"""
    c = str(col).lower().strip()
    c = re.sub(r"[àáạảãâầấậẩẫăằắặẳẵ]", "a", c)
    c = re.sub(r"[èéẹẻẽêềếệểễ]", "e", c)
    c = re.sub(r"[ìíịỉĩ]", "i", c)
    c = re.sub(r"[òóọỏõôồốộổỗơờớợởỡ]", "o", c)
    c = re.sub(r"[ùúụủũưừứựửữ]", "u", c)
    c = re.sub(r"[ỳýỵỷỹ]", "y", c)
    c = re.sub(r"[đ]", "d", c)
    c = re.sub(r"[^a-z0-9]", "_", c)
    return c


def parse_items_string(items_val: Any) -> List[Dict[str, Any]]:
    """
    Phân tích chuỗi sản phẩm đa dạng:
    - JSON: '[{"product_id": "SP01", "quantity": 2}]'
    - Text: 'SP01: 2, SP02: 5' hoặc 'SP01(2); SP03(1)' hoặc '2x SP01, 1x SP06'
    """
    if not items_val or pd.isna(items_val):
        return []

    # Nếu đã là list
    if isinstance(items_val, list):
        return items_val

    s = str(items_val).strip()

    # Thử parse JSON
    if s.startswith("[") and s.endswith("]"):
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass

    # Phân tích theo regex pattern
    items = []
    # Pattern 1: SP01: 2 hoặc SP01:2 hoặc SP01 - 2
    p1 = re.findall(r"(SP\d+)\s*[:\-\(]\s*(\d+)\s*\)?", s, re.IGNORECASE)
    if p1:
        for pid, qty in p1:
            items.append({"product_id": pid.upper(), "quantity": int(qty)})
        return items

    # Pattern 2: 2x SP01 hoặc 2 SP01
    p2 = re.findall(r"(\d+)\s*(?:x\s*)?(SP\d+)", s, re.IGNORECASE)
    if p2:
        for qty, pid in p2:
            items.append({"product_id": pid.upper(), "quantity": int(qty)})
        return items

    # Pattern 3: Chỉ có mã sản phẩm đơn lẻ (mặc định số lượng 1 nếu không ghi)
    p3 = re.findall(r"(SP\d+)", s, re.IGNORECASE)
    if p3:
        for pid in p3:
            items.append({"product_id": pid.upper(), "quantity": 1})
        return items

    return items


def dataframe_to_request_list(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Chuyển đổi DataFrame từ Excel/CSV sang danh sách yêu cầu chuẩn hóa"""
    normalized_cols = {col: normalize_col_name(col) for col in df.columns}
    df_renamed = df.rename(columns=normalized_cols)

    # Tìm các cột tương ứng
    def find_col(candidates):
        for col in df_renamed.columns:
            for cand in candidates:
                if cand in col:
                    return col
        return None

    id_col = find_col(["request_id", "ma_yeu_cau", "ma_co_hoi", "id"])
    customer_col = find_col(["khach_hang", "customer", "ten_cong_ty", "doanh_nghiep"])
    contact_col = find_col(["lien_he", "contact", "email", "sdt", "phone"])
    items_col = find_col(["san_pham", "items", "hang_muc", "ma_sp", "danh_muc"])
    qty_col = find_col(["so_luong", "quantity", "qty"])
    budget_col = find_col(["ngan_sach", "budget", "gia_tri"])
    lead_col = find_col(["thoi_han", "lead_time", "lead_days", "tien_do", "ngay_giao"])
    discount_col = find_col(["chiet_khau", "discount", "giam_gia", "de_nghi_chiet_khau"])

    # Nếu cấu trúc file có 1 dòng cho mỗi sản phẩm của cùng 1 request_id -> Group by
    if id_col and items_col and qty_col and not id_col == items_col:
        # Kiểm tra xem ID có trùng lặp không
        if df_renamed[id_col].duplicated().any():
            requests_map = {}
            for _, row in df_renamed.iterrows():
                r_id = str(row[id_col]).strip()
                if r_id not in requests_map:
                    requests_map[r_id] = {
                        "request_id": r_id,
                        "customer_name": str(row[customer_col]) if customer_col and not pd.isna(row[customer_col]) else "Chưa rõ",
                        "contact": str(row[contact_col]) if contact_col and not pd.isna(row[contact_col]) else "",
                        "budget": float(row[budget_col]) if budget_col and not pd.isna(row[budget_col]) else None,
                        "requested_lead_days": int(row[lead_col]) if lead_col and not pd.isna(row[lead_col]) else None,
                        "requested_discount_pct": float(row[discount_col]) if discount_col and not pd.isna(row[discount_col]) else 0.0,
                        "items": []
                    }
                p_id = str(row[items_col]).strip().upper()
                q_val = row[qty_col] if not pd.isna(row[qty_col]) else 0
                requests_map[r_id]["items"].append({"product_id": p_id, "quantity": int(q_val)})
            return list(requests_map.values())

    # Cấu trúc mỗi dòng là một yêu cầu độc lập (items nằm trong 1 cột hoặc parse chuỗi)
    result = []
    for idx, row in df_renamed.iterrows():
        r_id = str(row[id_col]).strip() if id_col and not pd.isna(row[id_col]) else f"REQ-{idx+1:03d}"
        c_name = str(row[customer_col]).strip() if customer_col and not pd.isna(row[customer_col]) else f"Khách hàng #{idx+1}"
        contact = str(row[contact_col]).strip() if contact_col and not pd.isna(row[contact_col]) else "contact@enterprise.vn"

        # Ngân sách
        b_val = None
        if budget_col and not pd.isna(row[budget_col]):
            try:
                b_val = float(row[budget_col])
            except Exception:
                try:
                    # Làm sạch chuỗi tiền nếu có dấu phẩy hoặc chữ VNĐ
                    clean_b = re.sub(r"[^\d]", "", str(row[budget_col]))
                    b_val = float(clean_b) if clean_b else None
                except Exception:
                    b_val = None

        # Thời hạn
        l_val = None
        if lead_col and not pd.isna(row[lead_col]):
            try:
                l_val = int(float(str(row[lead_col]).strip()))
            except Exception:
                try:
                    clean_l = re.sub(r"[^\d]", "", str(row[lead_col]))
                    l_val = int(clean_l) if clean_l else None
                except Exception:
                    l_val = None

        # Chiết khấu
        d_val = 0.0
        if discount_col and not pd.isna(row[discount_col]):
            try:
                d_val = float(row[discount_col])
            except Exception:
                try:
                    clean_d = re.sub(r"[^\d.]", "", str(row[discount_col]))
                    d_val = float(clean_d) if clean_d else 0.0
                except Exception:
                    d_val = 0.0

        # Danh mục sản phẩm
        items = []
        if items_col and not pd.isna(row[items_col]):
            raw_items = row[items_col]
            items = parse_items_string(raw_items)
            # Nếu có cột số lượng riêng và items chỉ có 1 mã SP
            if qty_col and not pd.isna(row[qty_col]) and len(items) == 1:
                try:
                    items[0]["quantity"] = int(row[qty_col])
                except Exception:
                    pass

        result.append({
            "request_id": r_id,
            "customer_name": c_name,
            "contact": contact,
            "budget": b_val,
            "requested_lead_days": l_val,
            "requested_discount_pct": d_val,
            "items": items
        })

    return result


def load_google_sheet(sheet_url: str) -> List[Dict[str, Any]]:
    """
    Tải dữ liệu từ đường dẫn Google Sheets công khai.
    Tự động trích xuất Document ID và tải định dạng CSV.
    """
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", sheet_url)
    if not match:
        raise ValueError("Đường dẫn Google Sheets không hợp lệ. Vui lòng kiểm tra lại định dạng link.")

    sheet_id = match.group(1)

    # Lấy gid nếu có (chỉ định sheet cụ thể)
    gid_match = re.search(r"[#&]gid=([0-9]+)", sheet_url)
    gid = gid_match.group(1) if gid_match else "0"

    export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    response = requests.get(export_url, timeout=15)
    if response.status_code != 200:
        raise ConnectionError(f"Không thể tải Google Sheet (Mã lỗi {response.status_code}). Vui lòng đảm bảo Sheet đã được chia sẻ công khai ('Bất kỳ ai có liên kết đều có thể xem').")

    csv_data = response.content.decode("utf-8")
    df = pd.read_csv(io.StringIO(csv_data))
    return dataframe_to_request_list(df)


def load_from_file(file_content, filename: str) -> List[Dict[str, Any]]:
    """Nạp dữ liệu từ file CSV hoặc XLSX"""
    fn = filename.lower()
    if fn.endswith(".csv"):
        df = pd.read_csv(file_content)
    elif fn.endswith(".xlsx") or fn.endswith(".xls"):
        df = pd.read_excel(file_content)
    else:
        raise ValueError("Chỉ hỗ trợ file định dạng .csv hoặc .xlsx")

    return dataframe_to_request_list(df)


def parse_unstructured_text(raw_text: str) -> Dict[str, Any]:
    """
    Kỹ năng xử lý văn bản tự do: Bóc tách thực thể từ email hoặc mô tả yêu cầu thô
    """
    # 1. Tìm tên khách hàng
    name_match = re.search(r"(?:công ty|doanh nghiệp|khách hàng|kính gửi|đơn vị)\s*[:\-]?\s*([A-Za-z0-9\s\.\&]+?)(?:\n|,|\.|\-|$)", raw_text, re.IGNORECASE)
    customer_name = name_match.group(1).strip() if name_match else "Khách hàng Doanh nghiệp"

    # 2. Tìm liên hệ
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", raw_text)
    phone_match = re.search(r"(?:0|\+84)\d{9,10}", raw_text)
    contact = email_match.group(0) if email_match else (phone_match.group(0) if phone_match else "contact@enterprise.vn")

    # 3. Tìm sản phẩm và số lượng
    items = parse_items_string(raw_text)

    # 4. Tìm ngân sách
    budget = None
    budget_match = re.search(r"(?:ngân sách|budget|tài chính|dự toán)\s*[:\-]?\s*([\d\.\,]+)\s*(?:tr|triệu|trieu|vnđ|vnd|đ)?", raw_text, re.IGNORECASE)
    if budget_match:
        val_str = budget_match.group(1).replace(".", "").replace(",", "")
        try:
            val_num = float(val_str)
            # Nếu nhập 150 tr -> 150,000,000
            if "tr" in raw_text.lower() or "triệu" in raw_text.lower() or val_num < 10000:
                val_num = val_num * 1_000_000
            budget = val_num
        except Exception:
            budget = None

    # 5. Tìm thời hạn
    lead_days = None
    lead_match = re.search(r"(?:thời hạn|tiến độ|giao hàng trong|hoàn thành trong|lead\s*time)\s*[:\-]?\s*(\d+)\s*(?:ngày|day)?", raw_text, re.IGNORECASE)
    if lead_match:
        lead_days = int(lead_match.group(1))

    # 6. Tìm chiết khấu
    discount_pct = 0.0
    disc_match = re.search(r"(?:chiết khấu|giảm giá|discount)\s*[:\-]?\s*([\d\.]+)\s*%", raw_text, re.IGNORECASE)
    if disc_match:
        discount_pct = float(disc_match.group(1))

    return {
        "request_id": f"RAW-{datetime.datetime.now().strftime('%H%M%S')}",
        "customer_name": customer_name,
        "contact": contact,
        "budget": budget,
        "requested_lead_days": lead_days,
        "requested_discount_pct": discount_pct,
        "items": items
    }


def create_sample_dataset() -> pd.DataFrame:
    """
    Tạo bộ dữ liệu kiểm thử 10 trường hợp thực tế phủ kín toàn bộ các ranh giới quy tắc:
    1. Thông thường (Có thể tiếp tục)
    2. Thiếu dữ liệu ngân sách (Cần bổ sung thông tin)
    3. Thiếu dữ liệu thời hạn (Cần bổ sung thông tin)
    4. Thiếu số lượng sản phẩm (Cần bổ sung thông tin)
    5. Vượt quyền NVKD: Xin chiết khấu 10% (Chờ duyệt)
    6. Hụt ngân sách nhẹ 3% (Chờ duyệt)
    7. Không đáp ứng tiến độ kho: Cần 2 ngày nhưng kho hết hàng cần 16 ngày (Chưa đáp ứng)
    8. Vượt trần chiết khấu công ty: Đòi 25% > 15% (Chưa đáp ứng)
    9. Ngân sách quá thấp: Đơn 200M mà ngân sách 80M (Chưa đáp ứng)
    10. Ranh giới chuẩn: Vừa khít 150M và chiết khấu đúng 5% trần NVKD (Có thể tiếp tục)
    """
    records = [
        {
            "Mã yêu cầu": "REQ-001",
            "Tên khách hàng": "Công ty Cổ phần Công nghệ EcoTech",
            "Liên hệ": "tuan.le@ecotech.vn",
            "Hạng mục sản phẩm": "SP02: 2, SP04: 5",
            "Ngân sách (VNĐ)": 120_000_000,
            "Thời hạn yêu cầu (Ngày)": 5,
            "Chiết khấu đề nghị (%)": 3.0,
            "Kịch bản kiểm thử": "Trường hợp thông thường (Đầy đủ dữ liệu, kho đủ hàng, trong ngân sách)"
        },
        {
            "Mã yêu cầu": "REQ-002",
            "Tên khách hàng": "Tập đoàn Xây dựng An Thịnh",
            "Liên hệ": "kinhdoanh@anthinhgroup.vn",
            "Hạng mục sản phẩm": "SP01: 1, SP06: 1",
            "Ngân sách (VNĐ)": None,  # THIẾU NGÂN SÁCH
            "Thời hạn yêu cầu (Ngày)": 15,
            "Chiết khấu đề nghị (%)": 0.0,
            "Kịch bản kiểm thử": "Thiếu dữ liệu: Khách không cung cấp ngân sách"
        },
        {
            "Mã yêu cầu": "REQ-003",
            "Tên khách hàng": "Bệnh viện Đa khoa Quốc tế Trí Đức",
            "Liên hệ": "it@triduchospital.com",
            "Hạng mục sản phẩm": "SP03: 10, SP05: 2",
            "Ngân sách (VNĐ)": 350_000_000,
            "Thời hạn yêu cầu (Ngày)": None,  # THIẾU THỜI HẠN
            "Chiết khấu đề nghị (%)": 5.0,
            "Kịch bản kiểm thử": "Thiếu dữ liệu: Khách không nêu rõ thời hạn giao hàng"
        },
        {
            "Mã yêu cầu": "REQ-004",
            "Tên khách hàng": "Trường Quốc tế Horizon Academy",
            "Liên hệ": "procurement@horizon.edu.vn",
            "Hạng mục sản phẩm": "SP04: 0, SP03: 5",  # THIẾU SỐ LƯỢNG MÀN HÌNH
            "Ngân sách (VNĐ)": 150_000_000,
            "Thời hạn yêu cầu (Ngày)": 7,
            "Chiết khấu đề nghị (%)": 0.0,
            "Kịch bản kiểm thử": "Thiếu dữ liệu: Số lượng sản phẩm không hợp lệ (=0)"
        },
        {
            "Mã yêu cầu": "REQ-005",
            "Tên khách hàng": "Ngân hàng Thương mại Á Châu SmartBank",
            "Liên hệ": "tech.buying@smartbank.com.vn",
            "Hạng mục sản phẩm": "SP01: 2, SP02: 4, SP06: 2",
            "Ngân sách (VNĐ)": 320_000_000,
            "Thời hạn yêu cầu (Ngày)": 10,
            "Chiết khấu đề nghị (%)": 12.0,  # VƯỢT QUYỀN NVKD (NVKD tối đa 10%, TPKD duyệt tối đa 15%)
            "Kịch bản kiểm thử": "Vượt thẩm quyền: Khách đòi chiết khấu 12% (Cần Trưởng phòng duyệt)"
        },
        {
            "Mã yêu cầu": "REQ-006",
            "Tên khách hàng": "Công ty Logistics Vận tải Biển Đông",
            "Liên hệ": "dieuhanh@biendonglogistics.vn",
            "Hạng mục sản phẩm": "SP03: 4, SP04: 4",
            "Ngân sách (VNĐ)": 135_000_000,  # Hụt nhẹ ~3.5% so với giá đề xuất
            "Thời hạn yêu cầu (Ngày)": 6,
            "Chiết khấu đề nghị (%)": 4.0,
            "Kịch bản kiểm thử": "Ranh giới ngân sách: Hụt ngân sách nhẹ <= 5% (Trình TPKD hỗ trợ giá)"
        },
        {
            "Mã yêu cầu": "REQ-007",
            "Tên khách hàng": "Công ty Cổ phần Chứng khoán Thăng Long",
            "Liên hệ": "system@thanglongsec.com.vn",
            "Hạng mục sản phẩm": "SP01: 15, SP05: 1",  # KHO CHỈ CÓ 8 MÁY CHỦ -> THIẾU 7 MÁY, CẦN 14+2=16 NGÀY
            "Ngân sách (VNĐ)": 1_500_000_000,
            "Thời hạn yêu cầu (Ngày)": 2,  # ĐÒI GIAO TRONG 2 NGÀY (KHÔNG KHẢ THI)
            "Chiết khấu đề nghị (%)": 8.0,
            "Kịch bản kiểm thử": "Không khả thi tồn kho & thời hạn: Đòi giao 2 ngày nhưng kho thiếu hàng cần 16 ngày"
        },
        {
            "Mã yêu cầu": "REQ-008",
            "Tên khách hàng": "Công ty Truyền thông MediaStar",
            "Liên hệ": "contact@mediastar.vn",
            "Hạng mục sản phẩm": "SP03: 6, SP04: 6",
            "Ngân sách (VNĐ)": 250_000_000,
            "Thời hạn yêu cầu (Ngày)": 10,
            "Chiết khấu đề nghị (%)": 25.0,  # VƯỢT TRẦN TOÀN CÔNG TY (TRẦN LÀ 15%)
            "Kịch bản kiểm thử": "Vượt trần chính sách: Đòi chiết khấu 25% (Vượt trần 15% của TPKD)"
        },
        {
            "Mã yêu cầu": "REQ-009",
            "Tên khách hàng": "Chuỗi Khách sạn Grand Palace",
            "Liên hệ": "admin@grandpalace.vn",
            "Hạng mục sản phẩm": "SP01: 1, SP02: 2, SP05: 2",  # TỔNG NIÊM YẾT: 188 TRIỆU
            "Ngân sách (VNĐ)": 80_000_000,  # NGÂN SÁCH QUÁ THẤP (THIẾU HƠN 50%)
            "Thời hạn yêu cầu (Ngày)": 15,
            "Chiết khấu đề nghị (%)": 5.0,
            "Kịch bản kiểm thử": "Không khả thi ngân sách: Ngân sách khách hàng chỉ bằng 45% giá trị giải pháp"
        },
        {
            "Mã yêu cầu": "REQ-010",
            "Tên khách hàng": "Công ty Phần mềm Sáng Tạo FinTech Việt",
            "Liên hệ": "ceo@fintechviet.io",
            "Hạng mục sản phẩm": "SP03: 5, SP07: 1",  # TỔNG NIÊM YẾT: 156.5 TRIỆU (NẤC 150M-300M)
            "Ngân sách (VNĐ)": 160_000_000,
            "Thời hạn yêu cầu (Ngày)": 7,
            "Chiết khấu đề nghị (%)": 5.0,  # ĐÚNG BẰNG CHIẾT KHẤU CHUẨN VÀ TRONG QUYỀN NVKD
            "Kịch bản kiểm thử": "Ranh giới quy tắc: Đơn hàng nấc > 150M, chiết khấu 5% vừa khớp quyền NVKD"
        }
    ]

    return pd.DataFrame(records)
