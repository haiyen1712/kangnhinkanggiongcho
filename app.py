"""
HỆ THỐNG AI AGENT XỬ LÝ CƠ HỘI BÁN HÀNG B2B - CÔNG TY MINH AN
Giao diện Phong Cách Neo-Brutalist / Webflow "Ghosts" Landing Page
Đồng bộ màu sắc: Pastel Lavender, Coral Pink, Deep Purple, Mint Green, Cyber Yellow
Hiệu ứng mượt mà: Hard Drop Shadow, Pop-out Badges, Floating Dark Pill Nav, Smooth Hover
"""

import io
import os
import datetime
import pandas as pd
import streamlit as st

from config import (
    PRODUCT_CATALOG,
    DISCOUNT_TIERS,
    MANAGER_MAX_DISCOUNT_PCT,
    SALES_REPRESENTATIVES,
    SALES_MANAGER
)
from tools import format_currency_vnd
from agent import SalesOpportunityAgent
from data_loader import (
    load_google_sheet,
    load_from_file,
    parse_unstructured_text,
    create_sample_dataset,
    dataframe_to_request_list
)

# 1. CẤU HÌNH TRANG STREAMLIT
st.set_page_config(
    page_title="Minh An AI Agent • Ghosts Edition",
    page_icon="👻",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CSS NEO-BRUTALIST / GHOSTS STYLE ĐỒNG BỘ 100% THEO CÁC SLIDE HÌNH ẢNH
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800;900&family=Space+Grotesk:wght@600;700&family=Space+Mono:wght@400;700&display=swap');

    /* Nền chung Lavender Pastel của Slide 1 */
    .stApp {
        background-color: #837be7 !important;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
        color: #111827 !important;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1200px !important;
    }

    /* Floating Dark Capsule Navbar (Slide 1) */
    .ghost-nav {
        background-color: #181824;
        border: 3px solid #000000;
        border-radius: 9999px;
        box-shadow: 4px 4px 0px #000000;
        padding: 10px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 0 auto 28px auto;
        max-width: 820px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .ghost-nav:hover {
        transform: translate(-2px, -2px);
        box-shadow: 6px 6px 0px #000000;
    }
    .ghost-logo {
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 800;
        color: #ffffff;
        font-size: 16px;
        letter-spacing: 0.5px;
    }
    .ghost-nav-links {
        display: flex;
        gap: 20px;
        font-size: 13px;
        font-weight: 700;
    }
    .ghost-nav-links a {
        color: #cbd5e1;
        text-decoration: none;
        transition: color 0.15s;
    }
    .ghost-nav-links a:hover {
        color: #55efc4;
    }
    .ghost-nav-btn {
        background-color: #ff4757;
        color: white !important;
        border: 2px solid #000000;
        border-radius: 9999px;
        padding: 6px 16px;
        font-size: 12px;
        font-weight: 800;
        box-shadow: 2px 2px 0px #000000;
        text-decoration: none;
    }

    /* Hero Section (Slide 1: Giant typography + Mint Button) */
    .hero-banner {
        text-align: center;
        padding: 30px 20px 40px 20px;
        position: relative;
    }
    .hero-big-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(48px, 8vw, 84px);
        font-weight: 900;
        color: #ffffff;
        text-transform: uppercase;
        letter-spacing: 2px;
        line-height: 1.05;
        margin: 0 auto 12px auto;
        text-shadow: 4px 4px 0px #000000, 7px 7px 0px #000000;
    }
    .hero-tagline {
        background-color: #ffeaa7;
        color: #000000;
        display: inline-block;
        font-weight: 800;
        font-size: 14px;
        padding: 6px 16px;
        border: 2.5px solid #000000;
        border-radius: 9999px;
        box-shadow: 3px 3px 0px #000000;
        margin-bottom: 24px;
    }

    /* Neo-brutalist Mint Button (View on OpenSea style) */
    .btn-neo-mint {
        display: inline-block;
        background-color: #55efc4;
        color: #000000 !important;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 17px;
        font-weight: 800;
        padding: 14px 38px;
        border: 3px solid #000000;
        border-radius: 12px;
        box-shadow: 5px 5px 0px #000000;
        text-decoration: none;
        cursor: pointer;
        transition: all 0.15s ease;
    }
    .btn-neo-mint:hover {
        transform: translate(-3px, -3px);
        box-shadow: 8px 8px 0px #000000;
        background-color: #00b894;
    }

    /* Thẻ trắng Neo-Brutalist (Slide 2: "Get Your Ghosts") */
    .neo-card {
        background-color: #ffffff;
        border: 3px solid #000000;
        border-radius: 20px;
        box-shadow: 6px 6px 0px #000000;
        padding: 28px;
        margin-bottom: 24px;
        position: relative;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .neo-card:hover {
        transform: translate(-2px, -2px);
        box-shadow: 9px 9px 0px #000000;
    }

    /* Pop-out Avatar Circle ở đỉnh card (Slide 2) */
    .card-top-avatar {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        background-color: #837be7;
        border: 3px solid #000000;
        box-shadow: 3px 3px 0px #000000;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
        position: absolute;
        top: -32px;
        left: 50%;
        transform: translateX(-50%);
    }

    .neo-card-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 22px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #000000;
        text-align: center;
        margin-top: 14px;
        margin-bottom: 8px;
    }

    /* 4 Thẻ Phân Loại Trạng Thái Màu Sắc Rực Rỡ */
    .status-tile {
        border: 3px solid #000000;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 5px 5px 0px #000000;
        color: #000000;
        height: 100%;
        transition: all 0.2s ease;
    }
    .status-tile:hover {
        transform: translate(-3px, -3px);
        box-shadow: 8px 8px 0px #000000;
    }
    .tile-mint { background-color: #55efc4; }
    .tile-yellow { background-color: #ffeaa7; }
    .tile-orange { background-color: #fab1a0; }
    .tile-coral { background-color: #ff7675; }

    .tile-num {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 38px;
        font-weight: 900;
        margin-bottom: 2px;
        line-height: 1;
    }
    .tile-label {
        font-size: 13px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }

    /* Banner Tổng Doanh Số Tiềm Năng (Slide 2 style Coral background) */
    .coral-banner {
        background-color: #ff6b6b;
        border: 3.5px solid #000000;
        border-radius: 18px;
        box-shadow: 6px 6px 0px #000000;
        padding: 24px 30px;
        color: #ffffff;
        margin: 24px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }
    .coral-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 15px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #ffeaa7;
    }
    .coral-val {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 36px;
        font-weight: 900;
        color: #ffffff;
        text-shadow: 3px 3px 0px #000000;
    }

    /* Rarity Card / Deep Purple Section (Slide 4) */
    .rarity-container {
        background-color: #480ca8;
        border: 3.5px solid #000000;
        border-radius: 20px;
        box-shadow: 7px 7px 0px #000000;
        padding: 30px;
        margin: 28px 0;
        color: #ffffff;
    }
    .rarity-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 26px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #55efc4;
        text-shadow: 2px 2px 0px #000000;
        margin-bottom: 6px;
    }

    /* Roadmap Section (Slide 5: Soft Blue) */
    .roadmap-box {
        background-color: #d0f0fd;
        border: 3.5px solid #000000;
        border-radius: 20px;
        box-shadow: 6px 6px 0px #000000;
        padding: 30px;
        margin: 28px 0;
        color: #000000;
    }

    /* Footer Banner (Slide 6: Dark "Thank You") */
    .footer-dark {
        background-color: #111827;
        border: 3.5px solid #000000;
        border-radius: 20px;
        box-shadow: 7px 7px 0px #000000;
        padding: 40px 20px;
        text-align: center;
        color: #ffffff;
        margin-top: 40px;
    }
    .footer-huge-text {
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(28px, 5vw, 54px);
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 2px;
        line-height: 1.1;
        margin-bottom: 12px;
        text-shadow: 3px 3px 0px #837be7;
    }

    /* Neo-Brutalist Form Inputs */
    div[data-baseweb="input"] input {
        background-color: #ffffff !important;
        border: 2.5px solid #000000 !important;
        color: #000000 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        box-shadow: 3px 3px 0px #000000 !important;
    }
    div[data-baseweb="select"] {
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    .stTextArea textarea {
        background-color: #ffffff !important;
        border: 2.5px solid #000000 !important;
        color: #000000 !important;
        border-radius: 12px !important;
        box-shadow: 3px 3px 0px #000000 !important;
        font-family: 'Space Mono', monospace !important;
        font-weight: 600 !important;
    }

    /* Buttons inside Streamlit */
    .stButton>button {
        border: 2.5px solid #000000 !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        box-shadow: 3px 3px 0px #000000 !important;
        transition: all 0.15s ease !important;
    }
    .stButton>button:hover {
        transform: translate(-2px, -2px) !important;
        box-shadow: 5px 5px 0px #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. KHỞI TẠO SESSION STATE
if "batch_result" not in st.session_state:
    st.session_state.batch_result = None
if "selected_opp_id" not in st.session_state:
    st.session_state.selected_opp_id = "REQ-001"
if "approval_decisions" not in st.session_state:
    st.session_state.approval_decisions = {}

agent = SalesOpportunityAgent()

# Nạp sẵn 10 mẫu chuẩn nếu chưa có dữ liệu
if st.session_state.batch_result is None:
    df_sample = create_sample_dataset()
    requests_to_process = dataframe_to_request_list(df_sample)
    st.session_state.batch_result = agent.process_batch(requests_to_process)

batch_res = st.session_state.batch_result
counts = batch_res["counts"]
dossiers = batch_res["dossiers"]

# 4. FLOATING DARK CAPSULE NAVBAR (SLIDE 1 MOCKUP)
st.markdown("""
<div class="ghost-nav">
    <div class="ghost-logo">
        <span style="font-size: 20px;">👻</span>
        <span>MINH AN AGENT</span>
    </div>
    <div class="ghost-nav-links">
        <a href="#pipeline">Cơ Hội</a>
        <a href="#rarity">Thẩm Định</a>
        <a href="#team">Đội Ngũ</a>
        <a href="#roadmap">Quy Trình</a>
    </div>
    <a href="#input-data" class="ghost-nav-btn">⚡ Nạp Yêu Cầu</a>
</div>
""", unsafe_allow_html=True)

# 5. HERO BANNER POP-ART (SLIDE 1: GIANT TITLE + MINT CTA)
st.markdown("""
<div class="hero-banner">
    <div class="hero-tagline">AI301 • ĐỀ 01 • CÔNG TY CÔNG NGHỆ MINH AN</div>
    <div class="hero-big-title">MINH AN AI</div>
    <div style="font-size: 20px; font-weight: 800; color: #ffeaa7; margin-bottom: 24px; text-shadow: 2px 2px 0px #000;">
        HỆ THỐNG AI AGENT ĐA KỸ NĂNG XỬ LÝ CƠ HỘI BÁN HÀNG B2B
    </div>
    <a href="#input-data" class="btn-neo-mint">⚡ BẮT ĐẦU XỬ LÝ CƠ HỘI B2B</a>
</div>
""", unsafe_allow_html=True)

# 6. KHỐI TIẾP NHẬN YÊU CẦU & NẠP DỮ LIỆU ("GET YOUR GHOSTS" CARD - SLIDE 2)
st.markdown('<div id="input-data"></div>', unsafe_allow_html=True)

col_input_left, col_input_right = st.columns([1.1, 1], gap="large")

with col_input_left:
    st.markdown("""
    <div class="neo-card" style="padding-top: 42px;">
        <div class="card-top-avatar">📥</div>
        <div class="neo-card-title">TIẾP NHẬN YÊU CẦU ĐA KÊNH</div>
        <div style="text-align: center; color: #4b5563; font-size: 13px; font-weight: 600; margin-bottom: 18px;">
            Hỗ trợ nạp qua file CSV, Excel .xlsx hoặc link Google Sheets trực tiếp:
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tab con nạp file và link sheet
    tab_f, tab_gs, tab_sm = st.tabs(["📊 Nạp File CSV/XLSX", "🔗 Link Google Sheets", "🔄 10 Kịch Bản Mẫu"])

    with tab_f:
        up_file = st.file_uploader("Kéo thả file CSV hoặc Excel:", type=["csv", "xlsx", "xls"], key="up_neo")
        if up_file:
            if st.button("🚀 Xử Lý File Này", type="primary", use_container_width=True):
                try:
                    loaded = load_from_file(up_file, up_file.name)
                    st.session_state.batch_result = agent.process_batch(loaded)
                    st.toast(f"Đã xử lý xong {len(loaded)} yêu cầu từ file!", icon="✔")
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi đọc file: {str(e)}")

    with tab_gs:
        gs_url = st.text_input("Dán link Google Sheet:", placeholder="https://docs.google.com/spreadsheets/d/.../edit?usp=sharing", key="gs_neo")
        if st.button("📥 Nạp Dữ Liệu Từ Google Sheet", type="primary", use_container_width=True):
            if gs_url:
                with st.spinner("Đang tải dữ liệu từ Google Sheet..."):
                    try:
                        gs_reqs = load_google_sheet(gs_url)
                        st.session_state.batch_result = agent.process_batch(gs_reqs)
                        st.toast(f"Đã xử lý xong {len(gs_reqs)} yêu cầu từ Google Sheet!", icon="✔")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi kết nối: {str(e)}")

    with tab_sm:
        st.info("Nạp bộ 10 kịch bản kiểm thử ranh giới chuẩn AI301 (Thông thường, Thiếu dữ liệu, Vượt quyền, Thiếu kho).")
        c_s1, c_s2 = st.columns(2)
        with c_s1:
            if st.button("🔄 Nạp Lại 10 Mẫu", type="primary", use_container_width=True):
                df_s = create_sample_dataset()
                st.session_state.batch_result = agent.process_batch(dataframe_to_request_list(df_s))
                st.toast("Đã nạp lại 10 kịch bản mẫu!", icon="🚀")
                st.rerun()
        with c_s2:
            df_sample = create_sample_dataset()
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                df_sample.to_excel(writer, index=False, sheet_name="Data")
            st.download_button(
                label="⬇️ Tải Excel Mẫu",
                data=buf.getvalue(),
                file_name="MinhAn_10_Opportunities.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

with col_input_right:
    # FORM NHẬP TRỰC TIẾP (POP CARD STYLE)
    st.markdown("""
    <div class="neo-card" style="padding-top: 42px;">
        <div class="card-top-avatar" style="background-color: #55efc4;">✍️</div>
        <div class="neo-card-title">TẠO CƠ HỘI MỚI TRỰC TIẾP</div>
        <div style="text-align: center; color: #4b5563; font-size: 13px; font-weight: 600; margin-bottom: 10px;">
            Nhập yêu cầu để AI Agent thẩm định kho, tính giá & ra kết luận ngay:
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("neo_quick_form"):
        c_nm, c_ct = st.columns(2)
        with c_nm:
            f_name = st.text_input("Tên doanh nghiệp:", value="Công ty Công nghệ Alpha Việt Nam")
        with c_ct:
            f_contact = st.text_input("Email / SĐT:", value="contact@alphatech.vn")

        c_p, c_q = st.columns([3, 2])
        with c_p:
            p_sel = st.selectbox("Chọn thiết bị:", list(PRODUCT_CATALOG.keys()), format_func=lambda k: f"{k} - {PRODUCT_CATALOG[k]['name'][:22]}")
        with c_q:
            p_qty = st.number_input("Số lượng:", min_value=1, value=2, step=1)

        c_b, c_l, c_d = st.columns(3)
        with c_b:
            f_budget = st.number_input("Ngân sách (VNĐ):", min_value=0, value=200_000_000, step=10_000_000)
        with c_l:
            f_lead = st.number_input("Hạn giao (ngày):", min_value=1, value=5, step=1)
        with c_d:
            f_disc = st.number_input("Chiết khấu (%):", min_value=0.0, max_value=30.0, value=3.0, step=0.5)

        if st.form_submit_button("⚡ AI AGENT PHÂN TÍCH NGAY", use_container_width=True, type="primary"):
            new_item = {
                "request_id": f"OPP-{datetime.datetime.now().strftime('%H%M%S')}",
                "customer_name": f_name,
                "contact": f_contact,
                "budget": f_budget if f_budget > 0 else None,
                "requested_lead_days": f_lead,
                "requested_discount_pct": f_disc,
                "items": [{"product_id": p_sel, "quantity": p_qty}]
            }
            st.session_state.batch_result = agent.process_batch([new_item])
            st.toast("Đã thẩm định xong cơ hội vừa nhập!", icon="✔")
            st.rerun()

# 7. 4 TILES PHÂN LOẠI TRẠNG THÁI (NEO-BRUTALIST VIBRANT TILES)
st.markdown('<div id="pipeline" style="margin-top: 30px;"></div>', unsafe_allow_html=True)

col_t1, col_t2, col_t3, col_t4 = st.columns(4)

with col_t1:
    st.markdown(f"""
    <div class="status-tile tile-mint">
        <div style="font-size: 26px;">🟢</div>
        <div class="tile-num">{counts['CÓ THỂ TIẾP TỤC']}</div>
        <div class="tile-label">CÓ THỂ TIẾP TỤC</div>
        <div style="font-size: 12px; font-weight: 700; line-height: 1.4;">
            Đầy đủ dữ liệu, kho đủ hàng, chiết khấu trong quyền NVKD.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_t2:
    st.markdown(f"""
    <div class="status-tile tile-yellow">
        <div style="font-size: 26px;">🟡</div>
        <div class="tile-num">{counts['CHỜ DUYỆT']}</div>
        <div class="tile-label">CHỜ TRƯỞNG PHÒNG DUYỆT</div>
        <div style="font-size: 12px; font-weight: 700; line-height: 1.4;">
            Vượt quyền chiết khấu NVKD (> 5%) hoặc hụt ngân sách nhẹ (≤ 5%).
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_t3:
    st.markdown(f"""
    <div class="status-tile tile-orange">
        <div style="font-size: 26px;">🟠</div>
        <div class="tile-num">{counts['CẦN BỔ SUNG THÔNG TIN']}</div>
        <div class="tile-label">CẦN BỔ SUNG THÔNG TIN</div>
        <div style="font-size: 12px; font-weight: 700; line-height: 1.4;">
            Thiếu ngân sách, thời hạn giao hoặc số lượng hợp lệ.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_t4:
    st.markdown(f"""
    <div class="status-tile tile-coral">
        <div style="font-size: 26px;">🔴</div>
        <div class="tile-num">{counts['CHƯA ĐÁP ỨNG']}</div>
        <div class="tile-label">CHƯA ĐÁP ỨNG</div>
        <div style="font-size: 12px; font-weight: 700; line-height: 1.4;">
            Kho thiếu hàng gấp, vượt trần chiết khấu 15% hoặc hụt quá nhiều.
        </div>
    </div>
    """, unsafe_allow_html=True)

# BANNER TỔNG DOANH SỐ TIỀM NĂNG (SLIDE 2 STYLE CORAL BANNER)
st.markdown(f"""
<div class="coral-banner">
    <div>
        <div class="coral-title">💰 TỔNG GIÁ TRỊ CÁC CƠ HỘI ĐỦ ĐIỀU KIỆN TIẾP TỤC HOẶC CHỜ DUYỆT:</div>
        <div style="font-size: 13px; font-weight: 600; opacity: 0.95; margin-top: 4px;">
            Gồm {counts['CÓ THỂ TIẾP TỤC']} cơ hội Đạt chuẩn và {counts['CHỜ DUYỆT']} cơ hội Chờ duyệt. Không tự ý tính cơ hội thiếu dữ kiện.
        </div>
    </div>
    <div class="coral-val">
        {format_currency_vnd(batch_res['total_eligible_value'])}
    </div>
</div>
""", unsafe_allow_html=True)

# 8. BẢNG DỮ LIỆU ĐỐI CHIẾU "RARITY TABLE" (SLIDE 4 STYLE - DEEP PURPLE CONTAINER)
st.markdown("""
<div id="rarity" class="rarity-container">
    <div class="rarity-header">📊 BẢNG TỔNG HỢP & ĐỐI CHIẾU CƠ HỘI BÁN HÀNG B2B</div>
    <div style="font-size: 13px; color: #cbd5e1; margin-bottom: 20px; font-weight: 600;">
        Minh chứng đối chiếu khả năng đáp ứng tồn kho, tiến độ và chính sách chiết khấu từng cơ hội:
    </div>
""", unsafe_allow_html=True)

c_fil1, c_fil2 = st.columns([1, 2])
with c_fil1:
    f_filter = st.selectbox("Lọc theo nhóm trạng thái:", ["Tất cả", "CÓ THỂ TIẾP TỤC", "CHỜ DUYỆT", "CẦN BỔ SUNG THÔNG TIN", "CHƯA ĐÁP ỨNG"])
with c_fil2:
    f_search = st.text_input("🔍 Tìm theo tên doanh nghiệp hoặc mã:")

table_rows = []
for d in dossiers:
    if f_filter != "Tất cả" and d["final_status"] != f_filter:
        continue
    if f_search:
        if f_search.lower() not in d["opportunity_id"].lower() and f_search.lower() not in d["customer_name"].lower():
            continue

    p_val = d.get("pricing", {}).get("final_proposed_price") if d.get("pricing") else None
    b_val = d.get("customer_budget")
    lead = d.get("requested_lead_days")

    table_rows.append({
        "Mã cơ hội": d["opportunity_id"],
        "Doanh nghiệp": d["customer_name"],
        "NVKD phụ trách": f"{d['sales_rep']['name']} ({d['sales_rep']['id']})",
        "Trạng thái": d["final_status"],
        "Giá trị đề xuất": format_currency_vnd(p_val) if p_val else "Chưa xác định",
        "Ngân sách": format_currency_vnd(b_val) if b_val else "Chưa có",
        "Hạn giao": f"{lead} ngày" if lead else "Chưa rõ",
        "Hành động tiếp theo": d["next_action"]
    })

df_neo_table = pd.DataFrame(table_rows)

def color_neo_status(val):
    if val == "CÓ THỂ TIẾP TỤC":
        return "background-color: #55efc4; color: #000000; font-weight: 800; border: 1.5px solid #000;"
    elif val == "CHỜ DUYỆT":
        return "background-color: #ffeaa7; color: #000000; font-weight: 800; border: 1.5px solid #000;"
    elif val == "CẦN BỔ SUNG THÔNG TIN":
        return "background-color: #fab1a0; color: #000000; font-weight: 800; border: 1.5px solid #000;"
    elif val == "CHƯA ĐÁP ỨNG":
        return "background-color: #ff7675; color: #000000; font-weight: 800; border: 1.5px solid #000;"
    return ""

if not df_neo_table.empty:
    if hasattr(df_neo_table.style, "map"):
        styled_df = df_neo_table.style.map(color_neo_status, subset=["Trạng thái"])
    else:
        styled_df = df_neo_table.style.applymap(color_neo_status, subset=["Trạng thái"])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
else:
    st.info("Không có cơ hội nào khớp với bộ lọc.")

st.markdown("</div>", unsafe_allow_html=True)

# 9. KHỐI CHI TIẾT HỒ SƠ & PHÊ DUYỆT (WHITE POP CARD)
st.markdown("""
<div class="neo-card" style="margin-top: 28px;">
    <div class="card-top-avatar" style="background-color: #ffeaa7;">📋</div>
    <div class="neo-card-title">CHI TIẾT HỒ SƠ CƠ HỘI & PHÊ DUYỆT (HUMAN-IN-THE-LOOP)</div>
</div>
""", unsafe_allow_html=True)

opp_ids = [d["opportunity_id"] for d in dossiers]
selected_opp = st.selectbox("Chọn Mã cơ hội cần thẩm định chi tiết:", opp_ids, index=0)

if selected_opp:
    target_d = next((d for d in dossiers if d["opportunity_id"] == selected_opp), None)
    if target_d:
        col_dos_left, col_dos_right = st.columns([1.2, 1], gap="medium")

        with col_dos_left:
            st.markdown(f"### 📄 #{target_d['opportunity_id']} - {target_d['customer_name']}")
            st.markdown(f"- **Trạng thái:** `{target_d['final_status']}`")
            st.markdown(f"- **NVKD phụ trách:** `{target_d['sales_rep']['name']}` ({target_d['sales_rep']['phone']} - {target_d['sales_rep']['email']})")
            st.markdown(f"- **Bước tiếp theo:** **{target_d['next_action']}**")

            if target_d.get("inventory"):
                st.markdown("#### 📦 1. Thẩm định Tồn kho & Lead-time:")
                st.info(f"**Kết quả:** {target_d['inventory']['fulfillment_verdict']}\n\n*Căn cứ:* {target_d['inventory']['lead_time_basis']}")
                
                inv_items = []
                for it in target_d["inventory"].get("item_analysis", []):
                    inv_items.append({
                        "Mã": it["product_id"],
                        "Tên thiết bị": it["product_name"][:22],
                        "SL cần": it["requested_qty"],
                        "Tồn kho": it["stock_available"],
                        "Tình trạng": "Đủ hàng" if it["is_in_stock"] else f"Thiếu {it['shortage_qty']}"
                    })
                st.dataframe(pd.DataFrame(inv_items), hide_index=True, use_container_width=True)

            if target_d.get("pricing"):
                p = target_d["pricing"]
                st.markdown("#### 💰 2. Thẩm định Giá & Chiết khấu:")
                st.markdown(f"- Tổng giá niêm yết: `{format_currency_vnd(p.get('total_list_price'))}`")
                st.markdown(f"- Mức chiết khấu áp dụng: `{p.get('applied_discount_pct')}%` (-{format_currency_vnd(p.get('discount_amount'))})")
                st.markdown(f"- **GIÁ ĐỀ XUẤT CUỐI CÙNG:** `{format_currency_vnd(p.get('final_proposed_price'))}`")
                st.markdown(f"- Ngân sách khách hàng: `{format_currency_vnd(p.get('customer_budget'))}` ({p.get('budget_verdict')})")

        with col_dos_right:
            # Phiếu trình duyệt Trưởng phòng (Nếu Chờ duyệt)
            if target_d["final_status"] == "CHỜ DUYỆT" or target_d.get("requires_approval"):
                st.markdown("#### 📝 Phiếu Trình Duyệt Vượt Thẩm Quyền")
                st.text_area("Phiếu trình duyệt tự động:", target_d.get("approval_ticket", ""), height=220)

                b_ap, b_re = st.columns(2)
                with b_ap:
                    if st.button("✅ PHÊ DUYỆT (APPROVE)", key=f"neo_app_{selected_opp}", type="primary", use_container_width=True):
                        st.session_state.approval_decisions[selected_opp] = "ĐÃ PHÊ DUYỆT"
                        st.success("Trưởng phòng Hoàng Minh Trí đã phê duyệt thành công!")
                with b_re:
                    if st.button("❌ TỪ CHỐI (REJECT)", key=f"neo_rej_{selected_opp}", use_container_width=True):
                        st.session_state.approval_decisions[selected_opp] = "TỪ CHỐI"
                        st.error("Trưởng phòng đã từ chối yêu cầu chiết khấu!")

                if selected_opp in st.session_state.approval_decisions:
                    st.info(f"📌 Quyết định của Quản lý: **{st.session_state.approval_decisions[selected_opp]}**")

            # Bản nháp email gửi khách
            st.markdown("#### ✉️ Bản Nháp Email Phản Hồi Khách Hàng")
            st.text_area("Nội dung thư phản hồi:", target_d.get("customer_email_draft", ""), height=260)

# 10. ĐỘI NGŨ 6 NVKD (SLIDE 3: CHARACTER LINEUP STYLE)
st.markdown('<div id="team" style="margin-top: 30px;"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="neo-card" style="padding-top: 40px;">
    <div class="card-top-avatar" style="background-color: #fab1a0;">👥</div>
    <div class="neo-card-title">ĐỘI NGŨ 6 NHÂN VIÊN KINH DOANH PHỤ TRÁCH</div>
    <div style="text-align: center; color: #4b5563; font-size: 13px; font-weight: 600; margin-bottom: 20px;">
        Hệ thống tự động phân bổ cơ hội luân phiên đảm bảo tính sở hữu (Ownership) rõ ràng:
    </div>
</div>
""", unsafe_allow_html=True)

col_rep1, col_rep2, col_rep3, col_rep4, col_rep5, col_rep6 = st.columns(6)
rep_cols = [col_rep1, col_rep2, col_rep3, col_rep4, col_rep5, col_rep6]
avatars = ["👻", "🎃", "🧙", "🧛", "🧟", "🤖"]

for i, r in enumerate(SALES_REPRESENTATIVES):
    c_count = len([d for d in dossiers if d["sales_rep"]["id"] == r["id"]])
    with rep_cols[i]:
        st.markdown(f"""
        <div style="background: white; border: 2.5px solid #000; border-radius: 14px; box-shadow: 4px 4px 0px #000; padding: 14px; text-align: center;">
            <div style="font-size: 32px; margin-bottom: 4px;">{avatars[i]}</div>
            <div style="font-size: 13px; font-weight: 900; color: #000;">{r['name']}</div>
            <div style="font-size: 11px; font-weight: 700; color: #4b5563;">{r['id']}</div>
            <div style="background: #ffeaa7; border: 1.5px solid #000; border-radius: 999px; padding: 2px 8px; font-size: 11px; font-weight: 800; margin-top: 6px;">
                {c_count} cơ hội
            </div>
        </div>
        """, unsafe_allow_html=True)

# 11. ROADMAP & QUY TRÌNH TO-BE (SLIDE 5 STYLE - SOFT BLUE ROADMAP)
st.markdown('<div id="roadmap"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="roadmap-box">
    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 26px; font-weight: 900; text-transform: uppercase; margin-bottom: 16px;">
        🚀 QUY TRÌNH TO-BE & THIẾT KẾ AI AGENT (TASK 1)
    </div>
    <div style="font-size: 14px; line-height: 1.8; font-weight: 600;">
        <b>• Bước 1 & 2: Trích xuất & Kiểm tra thông tin (AI Agent Skill 1):</b> Tự động bóc tách thực thể, phát hiện ngay thông tin thiếu để sinh email hỏi lại.<br>
        <b>• Bước 3: Tạo Hồ sơ Cơ hội & Gắn người phụ trách:</b> Gán tự động cho 1 trong 6 NVKD.<br>
        <b>• Bước 4: Thẩm định Tồn kho & Lead-time (AI Agent Skill 2):</b> Đối chiếu CSDL kho và tính toán tiến độ khả thi thực tế.<br>
        <b>• Bước 5: Tính Báo giá & Chiết khấu (AI Agent Skill 3):</b> Áp biểu giá niêm yết hiện hành, tính chiết khấu bậc thang theo doanh số.<br>
        <b>• Bước 6: Phê duyệt Vượt Thẩm quyền (Human Checkpoint 1):</b> Trưởng phòng Hoàng Minh Trí ký duyệt các ca chiết khấu > 5% hoặc hụt ngân sách nhẹ.<br>
        <b>• Bước 7 & 8: Soạn thảo Báo giá & Dispatch (Human Checkpoint 2):</b> NVKD rà soát lần cuối trước khi phát hành đề xuất chính thức.
    </div>
</div>
""", unsafe_allow_html=True)

# 12. AUDIT LOGS TRUY VẾT
with st.expander("🕵️ XEM NHẬT KÝ TRUY VẾT THỰC THI CỦA AGENT (AUDIT TRAIL)"):
    if selected_opp and target_d:
        for idx, l in enumerate(target_d.get("audit_logs", []), 1):
            st.markdown(f"**Bước {idx}:** `{l['step']}` ➔ `{l['action']}` (*{l['timestamp']}*)")
            st.caption(f"Căn cứ: {l['rule']}")
            st.json(l["details"])

# 13. FOOTER "THANK YOU FOR ATTENTION" (SLIDE 6 STYLE)
st.markdown("""
<div class="footer-dark">
    <div class="footer-huge-text">THANK YOU FOR ATTENTION</div>
    <div style="font-size: 14px; color: #94a3b8; font-weight: 700; margin-bottom: 20px;">
        DỰ ÁN XỬ LÝ CƠ HỘI BÁN HÀNG B2B • CÔNG TY MINH AN • HỌC PHẦN AI301 • ĐỀ 01
    </div>
    <a href="#pipeline" class="btn-neo-mint" style="font-size: 14px; padding: 10px 24px;">⬆️ VỀ ĐẦU TRANG DASHBOARD</a>
</div>
""", unsafe_allow_html=True)
