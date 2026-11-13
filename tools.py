"""
BỘ CÔNG CỤ NGHIỆP VỤ (BUSINESS TOOLS) CHO AI AGENT XỬ LÝ CƠ HỘI BÁN HÀNG B2B
Công ty Công nghệ Minh An
"""

import math
from typing import Dict, List, Any, Tuple
from config import (
    PRODUCT_CATALOG,
    DEFAULT_IN_STOCK_LEAD_DAYS,
    DISCOUNT_TIERS,
    MANAGER_MAX_DISCOUNT_PCT,
    BUDGET_TOLERANCE_PCT,
    SALES_REPRESENTATIVES,
    SALES_MANAGER
)


def format_currency_vnd(amount: float) -> str:
    """Định dạng tiền tệ VNĐ chuẩn có dấu chấm phân cách hàng nghìn"""
    if amount is None or math.isnan(amount):
        return "Chưa xác định"
    return f"{int(round(amount)):,} VNĐ".replace(",", ".")


def validate_request_completeness(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Kỹ năng 1 (Tool): Kiểm tra tính đầy đủ của dữ liệu yêu cầu ban đầu.
    Xác định các trường còn thiếu: Tên khách hàng, liên hệ, danh mục sản phẩm, số lượng, ngân sách, thời hạn.
    """
    missing_fields = []
    clarification_questions = []

    # 1. Kiểm tra thông tin định danh khách hàng
    customer_name = request_data.get("customer_name")
    if not customer_name or str(customer_name).strip() == "":
        missing_fields.append("Tên doanh nghiệp / Khách hàng")
        clarification_questions.append("Quý khách vui lòng cung cấp Tên công ty/doanh nghiệp tiếp nhận báo giá.")

    contact = request_data.get("contact")
    if not contact or str(contact).strip() == "":
        missing_fields.append("Thông tin liên hệ (Email/Số điện thoại)")
        clarification_questions.append("Quý khách vui lòng để lại địa chỉ Email hoặc Số điện thoại để nhân viên phụ trách gửi hồ sơ đề xuất.")

    # 2. Kiểm tra danh mục sản phẩm và số lượng
    items = request_data.get("items", [])
    if not items or len(items) == 0:
        missing_fields.append("Danh sách sản phẩm / dịch vụ")
        clarification_questions.append("Quý khách vui lòng chỉ định cụ thể các mã sản phẩm hoặc thiết bị/dịch vụ cần triển khai.")
    else:
        for idx, item in enumerate(items, 1):
            qty = item.get("quantity")
            p_id = item.get("product_id")
            if qty is None or qty <= 0:
                missing_fields.append(f"Số lượng cho hạng mục #{idx} ({p_id or 'Chưa rõ mã'})")
                clarification_questions.append(f"Quý khách vui lòng xác nhận số lượng dự kiến cho thiết bị {p_id or 'ở dòng ' + str(idx)}.")

    # 3. Kiểm tra ngân sách
    budget = request_data.get("budget")
    if budget is None or budget <= 0:
        missing_fields.append("Ngân sách dự kiến (Budget)")
        clarification_questions.append("Quý khách vui lòng chia sẻ dải ngân sách dự kiến để Minh An cân đối gói giải pháp và chính sách giá phù hợp nhất.")

    # 4. Kiểm tra thời hạn mong muốn
    lead_days = request_data.get("requested_lead_days")
    if lead_days is None or lead_days <= 0:
        missing_fields.append("Thời hạn triển khai / ngày cần giao (Lead-time)")
        clarification_questions.append("Quý khách cần hoàn thành giao hàng và triển khai hệ thống trong bao nhiêu ngày kể từ ngày ký hợp đồng?")

    is_complete = (len(missing_fields) == 0)

    return {
        "is_complete": is_complete,
        "missing_fields": missing_fields,
        "clarification_questions": clarification_questions,
        "missing_count": len(missing_fields)
    }


def check_inventory_and_leadtime(items: List[Dict[str, Any]], requested_lead_days: int) -> Dict[str, Any]:
    """
    Kỹ năng 2 (Tool): Thẩm định tồn kho khả dụng và tính toán khả năng đáp ứng thời hạn.
    Đối chiếu số lượng với CSDL kho, tính thời gian nhập hàng nếu thiếu hàng.
    """
    item_analysis = []
    all_in_stock = True
    max_restock_lead = 0
    unknown_products = []

    for item in items:
        p_id = item.get("product_id", "").strip().upper()
        req_qty = item.get("quantity", 0)

        catalog_entry = PRODUCT_CATALOG.get(p_id)
        if not catalog_entry:
            unknown_products.append(p_id)
            item_analysis.append({
                "product_id": p_id,
                "product_name": "Sản phẩm không có trong danh mục niêm yết",
                "unit": "-",
                "requested_qty": req_qty,
                "stock_available": 0,
                "is_in_stock": False,
                "shortage_qty": req_qty,
                "restock_lead_days": 30,
                "note": "Cần Vận hành tra cứu nguồn hàng đặc thù"
            })
            all_in_stock = False
            max_restock_lead = max(max_restock_lead, 30)
            continue

        stock_avail = catalog_entry["stock_available"]
        restock_lead = catalog_entry["restock_lead_days"]
        is_in_stock = (stock_avail >= req_qty)
        shortage = max(0, req_qty - stock_avail)

        if not is_in_stock:
            all_in_stock = False
            max_restock_lead = max(max_restock_lead, restock_lead)

        item_analysis.append({
            "product_id": p_id,
            "product_name": catalog_entry["name"],
            "unit": catalog_entry["unit"],
            "requested_qty": req_qty,
            "stock_available": stock_avail,
            "is_in_stock": is_in_stock,
            "shortage_qty": shortage,
            "restock_lead_days": restock_lead,
            "note": "Đủ tồn kho khả dụng" if is_in_stock else f"Thiếu {shortage} {catalog_entry['unit']}, cần {restock_lead} ngày nhập kho"
        })

    # Tính toán thời hạn khả thi thực tế
    if all_in_stock:
        feasible_days = DEFAULT_IN_STOCK_LEAD_DAYS
        lead_time_basis = f"Tất cả sản phẩm có sẵn trong kho Minh An -> Thời gian xuất kho và giao nhận: {DEFAULT_IN_STOCK_LEAD_DAYS} ngày làm việc."
    else:
        feasible_days = max_restock_lead + DEFAULT_IN_STOCK_LEAD_DAYS
        lead_time_basis = f"Có sản phẩm thiếu kho -> Cần nhập hàng tối đa {max_restock_lead} ngày + {DEFAULT_IN_STOCK_LEAD_DAYS} ngày xuất kho = {feasible_days} ngày làm việc."

    # So sánh với thời hạn khách yêu cầu
    if requested_lead_days is not None and requested_lead_days > 0:
        lead_time_feasible = (feasible_days <= requested_lead_days)
        gap_days = requested_lead_days - feasible_days
        if lead_time_feasible:
            fulfillment_verdict = f"ĐÁP ỨNG TIẾN ĐỘ: Khách cần trong {requested_lead_days} ngày, Minh An giao trong {feasible_days} ngày."
        else:
            fulfillment_verdict = f"KHÔNG ĐÁP ỨNG TIẾN ĐỘ: Khách cần gấp trong {requested_lead_days} ngày nhưng Minh An cần tối thiểu {feasible_days} ngày (chậm {abs(gap_days)} ngày)."
    else:
        lead_time_feasible = True
        gap_days = 0
        fulfillment_verdict = f"Khách chưa xác định ngày giao, thời gian bàn giao dự kiến khả thi là {feasible_days} ngày làm việc."

    return {
        "all_in_stock": all_in_stock,
        "feasible_days": feasible_days,
        "requested_lead_days": requested_lead_days,
        "lead_time_feasible": lead_time_feasible,
        "gap_days": gap_days,
        "fulfillment_verdict": fulfillment_verdict,
        "lead_time_basis": lead_time_basis,
        "item_analysis": item_analysis,
        "unknown_products": unknown_products
    }


def calculate_pricing_and_discount(
    items: List[Dict[str, Any]],
    requested_discount_pct: float,
    customer_budget: float
) -> Dict[str, Any]:
    """
    Kỹ năng 3 (Tool): Áp bảng giá niêm yết, tính chiết khấu theo chính sách bậc thang và kiểm tra thẩm quyền.
    So sánh giá trị đề xuất với ngân sách khách hàng.
    """
    detailed_lines = []
    total_list_price = 0.0

    for item in items:
        p_id = item.get("product_id", "").strip().upper()
        qty = item.get("quantity", 0)
        catalog_entry = PRODUCT_CATALOG.get(p_id)

        if catalog_entry:
            unit_price = catalog_entry["list_price"]
            p_name = catalog_entry["name"]
            unit = catalog_entry["unit"]
        else:
            unit_price = 0.0
            p_name = f"Sản phẩm {p_id} (chưa có giá niêm yết)"
            unit = "Gói"

        line_total = unit_price * qty
        total_list_price += line_total

        detailed_lines.append({
            "product_id": p_id,
            "product_name": p_name,
            "unit": unit,
            "quantity": qty,
            "unit_price": unit_price,
            "line_total": line_total
        })

    # 1. Xác định khung chiết khấu tiêu chuẩn theo nấc giá trị đơn hàng
    matched_tier = None
    for tier in DISCOUNT_TIERS:
        if tier["min_val"] <= total_list_price < tier["max_val"]:
            matched_tier = tier
            break

    if not matched_tier:
        matched_tier = DISCOUNT_TIERS[-1]

    standard_discount_pct = matched_tier["standard_discount_pct"]
    sales_rep_max_pct = matched_tier["sales_rep_max_pct"]

    # 2. Xử lý yêu cầu chiết khấu của khách hàng
    if requested_discount_pct is None or requested_discount_pct <= 0:
        applied_discount_pct = standard_discount_pct
        discount_scenario = "Khách không yêu cầu chiết khấu riêng -> Áp dụng chiết khấu tiêu chuẩn theo quy chế."
        requires_manager_approval = False
        exceeds_policy_ceiling = False
    elif requested_discount_pct <= sales_rep_max_pct:
        applied_discount_pct = requested_discount_pct
        discount_scenario = f"Khách đề nghị {requested_discount_pct}% (nằm trong hạn mức NVKD tối đa {sales_rep_max_pct}%)."
        requires_manager_approval = False
        exceeds_policy_ceiling = False
    elif requested_discount_pct <= MANAGER_MAX_DISCOUNT_PCT:
        applied_discount_pct = requested_discount_pct
        discount_scenario = f"Khách đề nghị {requested_discount_pct}% (vượt thẩm quyền NVKD {sales_rep_max_pct}%, trong trần TPKD {MANAGER_MAX_DISCOUNT_PCT}%)."
        requires_manager_approval = True
        exceeds_policy_ceiling = False
    else:
        applied_discount_pct = MANAGER_MAX_DISCOUNT_PCT
        discount_scenario = f"Khách đề nghị {requested_discount_pct}% vượt trần tối đa toàn công ty ({MANAGER_MAX_DISCOUNT_PCT}%)."
        requires_manager_approval = True
        exceeds_policy_ceiling = True

    discount_amount = total_list_price * (applied_discount_pct / 100.0)
    final_proposed_price = total_list_price - discount_amount

    # 3. So sánh với ngân sách của khách hàng
    if customer_budget is not None and customer_budget > 0:
        budget_variance = customer_budget - final_proposed_price
        budget_variance_pct = (budget_variance / final_proposed_price) * 100.0

        if final_proposed_price <= customer_budget:
            budget_status = "FEASIBLE"
            budget_verdict = f"Ngân sách ĐẠT: Ngân sách khách ({format_currency_vnd(customer_budget)}) dư {format_currency_vnd(budget_variance)} so với giá đề xuất."
        elif abs(budget_variance) / customer_budget * 100.0 <= BUDGET_TOLERANCE_PCT:
            budget_status = "MARGINAL_DEFICIT"
            budget_verdict = f"Thiếu ngân sách nhẹ (hụt {format_currency_vnd(abs(budget_variance))}, ~{abs(budget_variance_pct):.1f}% <= {BUDGET_TOLERANCE_PCT}%). Cần TPKD hỗ trợ giá hoặc xin khách bổ sung."
            requires_manager_approval = True
        else:
            budget_status = "INFEASIBLE"
            budget_verdict = f"Vượt quá ngân sách (hụt {format_currency_vnd(abs(budget_variance))}, ~{abs(budget_variance_pct):.1f}% > {BUDGET_TOLERANCE_PCT}%). Không thể đáp ứng bằng chiết khấu thông thường."
    else:
        budget_status = "UNKNOWN"
        budget_variance = 0.0
        budget_variance_pct = 0.0
        budget_verdict = "Chưa có thông tin ngân sách từ khách hàng."

    return {
        "total_list_price": total_list_price,
        "standard_discount_pct": standard_discount_pct,
        "sales_rep_max_pct": sales_rep_max_pct,
        "manager_max_pct": MANAGER_MAX_DISCOUNT_PCT,
        "requested_discount_pct": requested_discount_pct or 0.0,
        "applied_discount_pct": applied_discount_pct,
        "discount_amount": discount_amount,
        "final_proposed_price": final_proposed_price,
        "discount_scenario": discount_scenario,
        "requires_manager_approval": requires_manager_approval,
        "exceeds_policy_ceiling": exceeds_policy_ceiling,
        "customer_budget": customer_budget,
        "budget_variance": budget_variance,
        "budget_variance_pct": budget_variance_pct,
        "budget_status": budget_status,
        "budget_verdict": budget_verdict,
        "detailed_lines": detailed_lines
    }


def generate_customer_email(dossier: Dict[str, Any]) -> str:
    """
    Kỹ năng 4 (Tool): Tạo bản nháp email phản hồi khách hàng theo từng trạng thái nghiệp vụ.
    """
    status = dossier.get("final_status")
    c_name = dossier.get("customer_name", "Quý khách hàng")
    rep = dossier.get("sales_rep", {})
    req_id = dossier.get("opportunity_id", "REQ-MINHAN")

    rep_signature = f"""
Trân trọng,
{rep.get('name', 'Phòng Kinh doanh Doanh nghiệp')}
Chuyên viên Tư vấn Giải pháp B2B | Công ty Công nghệ Minh An
Hotline/Zalo: {rep.get('phone', '0912.345.678')}
Email: {rep.get('email', 'kd@minhan.com.vn')}
Địa chỉ: Tòa nhà Minh An Tower, Khu Công nghệ cao, Hà Nội
Website: https://minhan.com.vn
"""

    if status == "CẦN BỔ SUNG THÔNG TIN":
        questions = "\n".join([f"  {idx}. {q}" for idx, q in enumerate(dossier.get("clarification_questions", []), 1)])
        return f"""Kính gửi Quý Công ty {c_name},

Lời đầu tiên, Công ty Công nghệ Minh An xin gửi lời chào trân trọng và cảm ơn Quý công ty đã quan tâm đến giải pháp thiết bị công nghệ của chúng tôi (Mã cơ hội: #{req_id}).

Để có thể lập Bảng dự thảo giải pháp tối ưu và chính xác nhất về mặt kỹ thuật, ngân sách cũng như cam kết tiến độ bàn giao, chúng tôi kính đề nghị Quý công ty vui lòng làm rõ hoặc bổ sung một số điểm sau:

{questions}

Ngay khi nhận được phản hồi từ Quý công ty, chuyên viên phụ trách của chúng tôi sẽ hoàn thiện Hồ sơ đề xuất chính thức và gửi lại trong vòng 2 giờ làm việc.

Rất mong sớm nhận được thông tin từ Quý công ty!

{rep_signature}"""

    elif status in ["CÓ THỂ TIẾP TỤC", "CHỜ DUYỆT"]:
        price = dossier.get("pricing", {})
        inv = dossier.get("inventory", {})

        table_rows = []
        for idx, line in enumerate(price.get("detailed_lines", []), 1):
            table_rows.append(
                f"  {idx}. {line['product_name']} ({line['product_id']}) | SL: {line['quantity']} {line['unit']} | Đơn giá niêm yết: {format_currency_vnd(line['unit_price'])} | Thành tiền: {format_currency_vnd(line['line_total'])}"
            )
        table_str = "\n".join(table_rows)

        discount_note = ""
        if price.get("applied_discount_pct", 0) > 0:
            discount_note = f"\n- Mức chiết khấu doanh nghiệp áp dụng: {price['applied_discount_pct']}% (-{format_currency_vnd(price['discount_amount'])})"

        approval_tag = ""
        if status == "CHỜ DUYỆT":
            approval_tag = "\n*(Lưu ý nội bộ: Báo giá bao gồm chính sách chiết khấu đặc biệt đang được trình Trưởng phòng Kinh doanh ký duyệt chính thức trước khi gửi đi)*\n"

        return f"""Kính gửi Quý Công ty {c_name},

Công ty Công nghệ Minh An xin chân thành cảm ơn Quý công ty đã tin tưởng lựa chọn chúng tôi làm đối tác cung cấp thiết bị và giải pháp công nghệ.

Căn cứ trên yêu cầu của Quý công ty, Minh An xin trân trọng gửi Bản dự thảo Báo giá và Phương án triển khai chi tiết (Mã cơ hội: #{req_id}) như sau:

I. DANH MỤC THIẾT BỊ VÀ DỊCH VỤ DỰ KIẾN:
{table_str}

II. TỔNG HỢP GIÁ TRỊ VÀ CHÍNH SÁCH ƯU ĐÃI:
- Tổng giá trị niêm yết: {format_currency_vnd(price.get('total_list_price', 0))}{discount_note}
- TỔNG GIÁ TRỊ ĐỀ XUẤT (Chưa VAT): {format_currency_vnd(price.get('final_proposed_price', 0))}
- Tiến độ bàn giao và triển khai: Cam kết hoàn thành trong {inv.get('feasible_days', 2)} ngày làm việc kể từ ngày hoàn tất thủ tục hợp đồng.
{approval_tag}
III. CAM KẾT CHẤT LƯỢNG & BẢO HÀNH:
- Thiết bị nhập khẩu chính hãng mới 100%, có đầy đủ chứng chỉ CO/CQ.
- Hỗ trợ kỹ thuật onsite tiêu chuẩn và gói bảo trì định kỳ.

Quý công ty vui lòng xem xét bản dự thảo trên. Chuyên viên {rep.get('name')} sẽ chủ động liên hệ với Quý công ty để hỗ trợ các thủ tục tiếp theo.

{rep_signature}"""

    else:  # CHƯA ĐÁP ỨNG
        reason = dossier.get("infeasible_reason", "Chưa đáp ứng được yêu cầu về tiến độ hoặc ngân sách hiện hành.")
        return f"""Kính gửi Quý Công ty {c_name},

Công ty Công nghệ Minh An trân trọng cảm ơn Quý công ty đã quan tâm và gửi yêu cầu hợp tác đến chúng tôi (Mã cơ hội: #{req_id}).

Sau khi đối chiếu kỹ lưỡng khả năng đáp ứng kỹ thuật, tồn kho khả dụng và chính sách thương mại, chúng tôi rất tiếc phải thông báo hiện tại Minh An chưa thể đáp ứng đầy đủ 100% điều kiện ban đầu của Quý công ty vì lý do:
-> {reason}

ĐỀ XUẤT PHƯƠNG ÁN THAY THẾ TỪ MINH AN:
- Về tiến độ: Chúng tôi có thể phân kỳ giao trước các thiết bị có sẵn trong kho, phần còn lại sẽ giao ngay sau khi hoàn tất nhập kho.
- Về cấu hình/ngân sách: Minh An sẵn sàng cử chuyên gia tư vấn dòng sản phẩm tương đương về hiệu năng nhằm tối ưu hóa chi phí khớp với ngân sách của Quý công ty.

Chuyên viên {rep.get('name')} ({rep.get('phone')}) sẽ liên hệ lại với Quý công ty trong ngày hôm nay để cùng trao đổi phương án điều chỉnh phù hợp nhất.

{rep_signature}"""


def generate_approval_ticket(dossier: Dict[str, Any]) -> str:
    """
    Kỹ năng 4 (Tool): Tạo Phiếu chuyển duyệt nội bộ (Approval Ticket) cho Trưởng phòng Kinh doanh.
    """
    req_id = dossier.get("opportunity_id", "REQ-MINHAN")
    c_name = dossier.get("customer_name", "Doanh nghiệp")
    rep = dossier.get("sales_rep", {})
    price = dossier.get("pricing", {})
    inv = dossier.get("inventory", {})

    return f"""================================================================================
PHIẾU CHUYỂN DUYỆT VƯỢT THẨM QUYỀN / CHIẾT KHẤU ĐẶC BIỆT
Mã hồ sơ: #{req_id} | Ngày tạo: {dossier.get('created_at', 'Hôm nay')}
Người đề xuất: {rep.get('name')} ({rep.get('id')}) | Bộ phận: Kinh doanh B2B
Người phê duyệt: {SALES_MANAGER['name']} - {SALES_MANAGER['title']}
================================================================================

1. THÔNG TIN KHÁCH HÀNG & CƠ HỘI:
   - Doanh nghiệp: {c_name}
   - Người liên hệ: {dossier.get('contact', 'Chưa rõ')}
   - Tiến độ yêu cầu: {dossier.get('requested_lead_days', 'Chưa rõ')} ngày (Tiến độ kho đáp ứng: {inv.get('feasible_days')} ngày)

2. THẨM ĐỊNH TÀI CHÍNH & CHÍNH SÁCH GIÁ:
   - Tổng giá niêm yết (List Price): {format_currency_vnd(price.get('total_list_price', 0))}
   - Mức chiết khấu tiêu chuẩn quy định: {price.get('standard_discount_pct', 0)}%
   - Hạn mức tự quyết tối đa của NVKD: {price.get('sales_rep_max_pct', 0)}%
   - MỨC CHIẾT KHẤU KHÁCH YÊU CẦU: {price.get('requested_discount_pct', 0)}% (VƯỢT QUYỀN NVKD)
   - Tiền chiết khấu đề nghị: -{format_currency_vnd(price.get('discount_amount', 0))}
   - GIÁ TRỊ SAU CHIẾT KHẤU ĐỀ XUẤT: {format_currency_vnd(price.get('final_proposed_price', 0))}
   - Ngân sách của khách hàng: {format_currency_vnd(price.get('customer_budget', 0))}
   - Tình trạng ngân sách: {price.get('budget_verdict')}

3. CĂN CỨ VÀ ĐỀ XUẤT CỦA AI AGENT:
   - Tồn kho khả dụng: {'Tất cả có sẵn' if inv.get('all_in_stock') else 'Cần nhập thêm một số linh kiện'}
   - Đánh giá biên lợi nhuận: Nằm trong khung cho phép của Trưởng phòng (<= {price.get('manager_max_pct')}%)
   - Khuyến nghị: ĐỒNG Ý PHÊ DUYỆT để chốt deal chiến lược với khách hàng doanh nghiệp.

================================================================================
HÀNH ĐỘNG CỦA TRƯỞNG PHÒNG KINH DOANH:
[  ] PHÊ DUYỆT (Chấp thuận mức chiết khấu đề xuất)
[  ] YÊU CẦU ĐIỀU CHỈNH (Mức chiết khấu tối đa cho phép: ..... %)
[  ] TỪ CHỐI (Không chấp thuận chính sách giá đặc biệt)
Ý kiến phê duyệt: ................................................................
================================================================================
"""

