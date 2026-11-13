"""
CẤU HÌNH DỮ LIỆU DANH MỤC SẢN PHẨM, TỒN KHO, BẢNG GIÁ VÀ CHÍNH SÁCH NGHIỆP VỤ
Công ty Công nghệ & Dịch vụ Doanh nghiệp Minh An (B2B)
"""

# 1. DANH MỤC SẢN PHẨM & DỊCH VỤ NIÊM YẾT (PRODUCT & SERVICE CATALOG)
# Bao gồm: Mã SP, Tên sản phẩm, Đơn vị, Giá niêm yết (VNĐ), Tồn kho khả dụng, Lead-time nhập hàng (ngày)
PRODUCT_CATALOG = {
    "SP01": {
        "name": "Máy chủ Server Dell PowerEdge R750",
        "category": "Thiết bị phần cứng",
        "unit": "Hệ thống",
        "list_price": 95_000_000,
        "stock_available": 8,
        "restock_lead_days": 14,
        "description": "2x Intel Xeon Gold 5318Y, 64GB RAM, 2x 480GB SSD SAS, Dual PSU"
    },
    "SP02": {
        "name": "Switch Cisco Catalyst 24 Port C9200L-24T-4G",
        "category": "Thiết bị mạng",
        "unit": "Chiếc",
        "list_price": 28_000_000,
        "stock_available": 15,
        "restock_lead_days": 7,
        "description": "Switch Layer 3 quản lý, 24 port 1G, 4x 1G SFP uplink"
    },
    "SP03": {
        "name": "Laptop Doanh nghiệp Dell Latitude 5540",
        "category": "Máy tính cá nhân",
        "unit": "Chiếc",
        "list_price": 26_500_000,
        "stock_available": 25,
        "restock_lead_days": 5,
        "description": "Intel Core i7-1365U, 16GB RAM, 512GB SSD, 15.6 inch FHD"
    },
    "SP04": {
        "name": "Màn hình Dell UltraSharp 27 inch U2724D",
        "category": "Màn hình chuyên dụng",
        "unit": "Chiếc",
        "list_price": 9_200_000,
        "stock_available": 40,
        "restock_lead_days": 3,
        "description": "27 inch IPS Black 2K QHD 120Hz, 100% sRGB, Type-C 90W"
    },
    "SP05": {
        "name": "Tường lửa Firewall Fortinet FortiGate 60F",
        "category": "Thiết bị an ninh mạng",
        "unit": "Thiết bị",
        "list_price": 18_500_000,
        "stock_available": 12,
        "restock_lead_days": 10,
        "description": "Firewall bảo mật mạng doanh nghiệp 10-100 người, UTM License 1 năm"
    },
    "SP06": {
        "name": "Dịch vụ Cài đặt & Triển khai Hệ thống Onsite",
        "category": "Dịch vụ kỹ thuật",
        "unit": "Gói",
        "list_price": 15_000_000,
        "stock_available": 999,  # Dịch vụ luôn sẵn sàng
        "restock_lead_days": 1,
        "description": "Triển khai lắp đặt tủ rack, cấu hình mạng, ảo hóa và tối ưu hóa hệ thống"
    },
    "SP07": {
        "name": "Dịch vụ Bảo trì & Hỗ trợ Kỹ thuật 24/7 (1 Năm)",
        "category": "Dịch vụ kỹ thuật",
        "unit": "Gói/Năm",
        "list_price": 24_000_000,
        "stock_available": 999,
        "restock_lead_days": 1,
        "description": "Hỗ trợ sự cố khẩn cấp 24/7 trong 2 giờ, bảo dưỡng định kỳ hàng quý"
    }
}

# 2. CHÍNH SÁCH THỜI HẠN GIAO HÀNG & TRIỂN KHAI (LEAD TIME POLICY)
# Nếu hàng có sẵn trong kho: 2 ngày làm việc (kiểm tra xuất kho và đóng gói vận chuyển)
DEFAULT_IN_STOCK_LEAD_DAYS = 2

# 3. CHÍNH SÁCH CHIẾT KHẤU & PHÂN ĐỊNH THẨM QUYỀN (DISCOUNT & APPROVAL POLICY)
DISCOUNT_TIERS = [
    {
        "min_val": 0,
        "max_val": 50_000_000,
        "standard_discount_pct": 0.0,
        "sales_rep_max_pct": 3.0,
        "description": "Đơn hàng nhỏ (< 50 triệu): Không chiết khấu chuẩn, NVKD tối đa 3%"
    },
    {
        "min_val": 50_000_000,
        "max_val": 150_000_000,
        "standard_discount_pct": 3.0,
        "sales_rep_max_pct": 5.0,
        "description": "Đơn hàng vừa (50M - 150M): Chiết khấu chuẩn 3%, NVKD tối đa 5%"
    },
    {
        "min_val": 150_000_000,
        "max_val": 300_000_000,
        "standard_discount_pct": 5.0,
        "sales_rep_max_pct": 8.0,
        "description": "Đơn hàng lớn (150M - 300M): Chiết khấu chuẩn 5%, NVKD tối đa 8%"
    },
    {
        "min_val": 300_000_000,
        "max_val": float("inf"),
        "standard_discount_pct": 8.0,
        "sales_rep_max_pct": 10.0,
        "description": "Đơn hàng trọng điểm (> 300M): Chiết khấu chuẩn 8%, NVKD tối đa 10%"
    }
]

# Trần chiết khấu tối đa công ty cho phép (Trưởng phòng duyệt)
MANAGER_MAX_DISCOUNT_PCT = 15.0

# Ngưỡng lệch ngân sách cho phép xem xét hỗ trợ giá
BUDGET_TOLERANCE_PCT = 5.0

# 4. DANH SÁCH NHÂN VIÊN KINH DOANH PHỤ TRÁCH (SALES REPS)
SALES_REPRESENTATIVES = [
    {"id": "NV01", "name": "Nguyễn Văn An", "email": "an.nguyen@minhan.com.vn", "phone": "0912.345.671"},
    {"id": "NV02", "name": "Trần Thị Bình", "email": "binh.tran@minhan.com.vn", "phone": "0912.345.672"},
    {"id": "NV03", "name": "Lê Hoàng Cường", "email": "cuong.le@minhan.com.vn", "phone": "0912.345.673"},
    {"id": "NV04", "name": "Phạm Thị Dung", "email": "dung.pham@minhan.com.vn", "phone": "0912.345.674"},
    {"id": "NV05", "name": "Vũ Minh Đức", "email": "duc.vu@minhan.com.vn", "phone": "0912.345.675"},
    {"id": "NV06", "name": "Đỗ Thu Hà", "email": "ha.do@minhan.com.vn", "phone": "0912.345.676"},
]

# 5. TRƯỞNG PHÒNG KINH DOANH (APPROVER)
SALES_MANAGER = {
    "name": "Hoàng Minh Trí",
    "title": "Trưởng phòng Kinh doanh Doanh nghiệp",
    "email": "tri.hoang@minhan.com.vn"
}

