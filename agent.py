"""
AI AGENT ĐIỀU PHỐI ĐA KỸ NĂNG XỬ LÝ CƠ HỘI BÁN HÀNG B2B (MINH AN SALES AGENT)
Tích hợp:
1. Kỹ năng Trích xuất & Thẩm định tính đầy đủ (Skill 1)
2. Kỹ năng Thẩm định Tồn kho & Lead-time (Skill 2)
3. Kỹ năng Áp giá & Chính sách Chiết khấu (Skill 3)
4. Kỹ năng Soạn thảo Hồ sơ, Email & Phiếu trình duyệt (Skill 4)
5. Hệ thống Nhật ký Truy vết Thực thi (Audit Trail Logger)
"""

import datetime
from typing import Dict, List, Any, Optional
from config import SALES_REPRESENTATIVES, SALES_MANAGER
from tools import (
    validate_request_completeness,
    check_inventory_and_leadtime,
    calculate_pricing_and_discount,
    generate_customer_email,
    generate_approval_ticket,
    format_currency_vnd
)


class AuditLogger:
    """Hệ thống ghi nhận và lưu vết nhật ký thực thi của Agent (Audit Trail)"""
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []

    def record(self, step: str, action: str, details: Dict[str, Any], rule: Optional[str] = None):
        entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "step": step,
            "action": action,
            "rule": rule or "Quy chế vận hành chuẩn Minh An",
            "details": details
        }
        self.logs.append(entry)

    def get_logs(self) -> List[Dict[str, Any]]:
        return self.logs

    def to_readable_text(self) -> str:
        lines = []
        for idx, log in enumerate(self.logs, 1):
            lines.append(f"[{log['timestamp']}] BƯỚC {idx}: {log['step']} -> {log['action']}")
            if log.get("rule"):
                lines.append(f"   * Căn cứ quy tắc: {log['rule']}")
            lines.append(f"   * Chi tiết: {log['details']}")
        return "\n".join(lines)


class SalesOpportunityAgent:
    """
    AI Agent đa kỹ năng xử lý tự động cơ hội bán hàng B2B theo đúng quy trình To-Be
    """
    def __init__(self):
        self.rep_index = 0

    def _assign_sales_rep(self, request_id: str) -> Dict[str, Any]:
        """Phân bổ công bằng luân phiên cho 1 trong 6 NVKD theo quy trình To-Be"""
        # Dùng hash mã để gán nhất quán hoặc round-robin
        idx = abs(hash(str(request_id))) % len(SALES_REPRESENTATIVES)
        return SALES_REPRESENTATIVES[idx]

    def process_opportunity(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Quy trình xử lý hoàn chỉnh từ yêu cầu thô đến Hồ sơ Cơ hội và Đề xuất
        """
        logger = AuditLogger()
        now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        req_id = request_data.get("request_id") or f"OPP-{datetime.datetime.now().strftime('%y%m%d%H%M%S')}"

        logger.record(
            step="Tiếp nhận Yêu cầu",
            action="Khởi tạo phiên xử lý cơ hội B2B",
            details={"request_id": req_id, "customer_name": request_data.get("customer_name")},
            rule="Quy trình Tiếp nhận & Chuẩn hóa đầu vào To-Be"
        )

        # -------------------------------------------------------------
        # BƯỚC 1: PHÂN LOẠI & KIỂM TRA THÔNG TIN (SKILL 1)
        # -------------------------------------------------------------
        val_result = validate_request_completeness(request_data)

        logger.record(
            step="Phân loại & Kiểm tra thông tin",
            action="Kiểm tra tính đầy đủ của các trường dữ liệu",
            details={
                "is_complete": val_result["is_complete"],
                "missing_fields": val_result["missing_fields"],
                "missing_count": val_result["missing_count"]
            },
            rule="Checklist thẩm định thông tin tối thiểu (Sản phẩm, Số lượng, Ngân sách, Thời hạn)"
        )

        # Gán NVKD phụ trách
        sales_rep = self._assign_sales_rep(req_id)

        # Nếu THIẾU THÔNG TIN -> Dừng và sinh email làm rõ theo quy định "Không tự xác nhận bán hàng khi chưa đủ dữ kiện"
        if not val_result["is_complete"]:
            final_status = "CẦN BỔ SUNG THÔNG TIN"
            dossier = {
                "opportunity_id": req_id,
                "created_at": now_str,
                "customer_name": request_data.get("customer_name", "Chưa rõ tên"),
                "contact": request_data.get("contact", "Chưa rõ liên hệ"),
                "sales_rep": sales_rep,
                "final_status": final_status,
                "can_proceed": False,
                "requires_approval": False,
                "is_infeasible": False,
                "needs_info": True,
                "eligible_value": 0.0,
                "missing_fields": val_result["missing_fields"],
                "clarification_questions": val_result["clarification_questions"],
                "infeasible_reason": "Thiếu các trường thông tin quan trọng để thẩm định giá và thời hạn.",
                "next_action": f"NVKD {sales_rep['name']} gửi email yêu cầu khách hàng bổ sung các thông tin còn thiếu.",
                "audit_logs": logger.get_logs()
            }
            dossier["customer_email_draft"] = generate_customer_email(dossier)
            dossier["approval_ticket"] = "Không áp dụng (Yêu cầu chưa đủ dữ liệu để trình duyệt)"
            return dossier

        # -------------------------------------------------------------
        # BƯỚC 2: TẠO HỒ SƠ CƠ HỘI & GẮN NGƯỜI PHỤ TRÁCH
        # -------------------------------------------------------------
        logger.record(
            step="Tạo Hồ sơ Cơ hội",
            action=f"Khởi tạo hồ sơ #{req_id} và gán người phụ trách",
            details={"sales_rep_id": sales_rep["id"], "sales_rep_name": sales_rep["name"]},
            rule="Phân bổ trách nhiệm tự động (RACI Step 3)"
        )

        # -------------------------------------------------------------
        # BƯỚC 3: THẨM ĐỊNH TỒN KHO & TIẾN ĐỘ (SKILL 2)
        # -------------------------------------------------------------
        items = request_data.get("items", [])
        requested_lead_days = request_data.get("requested_lead_days")

        inv_result = check_inventory_and_leadtime(items, requested_lead_days)

        logger.record(
            step="Thẩm định tồn kho & giá",
            action="Đối chiếu tồn kho khả dụng và tính toán Lead-time khả thi",
            details={
                "all_in_stock": inv_result["all_in_stock"],
                "feasible_days": inv_result["feasible_days"],
                "lead_time_feasible": inv_result["lead_time_feasible"],
                "lead_time_basis": inv_result["lead_time_basis"]
            },
            rule="Quy tắc Lead-time: 2 ngày nếu đủ kho; Max(Restock) + 2 ngày nếu thiếu hàng"
        )

        # -------------------------------------------------------------
        # BƯỚC 4: TÍNH TOÁN BÁO GIÁ & CHÍNH SÁCH CHIẾT KHẤU (SKILL 3)
        # -------------------------------------------------------------
        req_discount = request_data.get("requested_discount_pct", 0.0)
        budget = request_data.get("budget", 0.0)

        pricing_result = calculate_pricing_and_discount(items, req_discount, budget)

        logger.record(
            step="Lập Báo giá & Dự thảo đề xuất",
            action="Áp bảng giá niêm yết hiện hành và tính toán chiết khấu",
            details={
                "total_list_price": pricing_result["total_list_price"],
                "applied_discount_pct": pricing_result["applied_discount_pct"],
                "final_proposed_price": pricing_result["final_proposed_price"],
                "discount_scenario": pricing_result["discount_scenario"],
                "requires_manager_approval": pricing_result["requires_manager_approval"],
                "budget_status": pricing_result["budget_status"]
            },
            rule="Chính sách chiết khấu bậc thang theo doanh số & Hạn mức phân quyền NVKD/TPKD"
        )

        # -------------------------------------------------------------
        # BƯỚC 5: XÁC ĐỊNH TRẠNG THÁI CUỐI CÙNG & ĐIỀU KIỆN CHUYỂN XỬ LÝ
        # -------------------------------------------------------------
        # Điều kiện 1: Vượt trần công ty hoặc không khả thi nghiêm trọng
        if pricing_result["exceeds_policy_ceiling"]:
            final_status = "CHƯA ĐÁP ỨNG"
            infeasible_reason = f"Mức chiết khấu khách hàng yêu cầu ({req_discount}%) vượt quá trần tối đa công ty cho phép ({pricing_result['manager_max_pct']}%)."
            next_action = f"NVKD {sales_rep['name']} liên hệ khách hàng đàm phán lại mức chiết khấu theo khung tối đa của công ty."
            can_proceed = False
            requires_approval = False
            eligible_value = 0.0

        elif pricing_result["budget_status"] == "INFEASIBLE":
            final_status = "CHƯA ĐÁP ỨNG"
            deficit = abs(pricing_result["budget_variance"])
            infeasible_reason = f"Ngân sách khách hàng ({format_currency_vnd(budget)}) không đủ chi trả cho gói giải pháp (thiếu {format_currency_vnd(deficit)})."
            next_action = f"NVKD {sales_rep['name']} tư vấn khách hàng giảm bớt số lượng thiết bị hoặc đổi sang phân khúc tương đương."
            can_proceed = False
            requires_approval = False
            eligible_value = 0.0

        elif not inv_result["lead_time_feasible"]:
            final_status = "CHƯA ĐÁP ỨNG"
            gap = abs(inv_result["gap_days"])
            infeasible_reason = f"Thời hạn khách yêu cầu giao trong {requested_lead_days} ngày không khả thi vì kho cần tối thiểu {inv_result['feasible_days']} ngày nhập hàng."
            next_action = f"NVKD {sales_rep['name']} đàm phán với khách hàng kéo dài tiến độ lên {inv_result['feasible_days']} ngày hoặc giao hàng làm 2 đợt."
            can_proceed = False
            requires_approval = False
            eligible_value = 0.0

        # Điều kiện 2: Vượt thẩm quyền NVKD -> Chờ Trưởng phòng duyệt
        elif pricing_result["requires_manager_approval"]:
            final_status = "CHỜ DUYỆT"
            infeasible_reason = ""
            next_action = f"Trình Trưởng phòng {SALES_MANAGER['name']} phê duyệt Phiếu chiết khấu/hỗ trợ ngân sách đặc biệt."
            can_proceed = True  # Đủ điều kiện tiếp tục nếu được duyệt
            requires_approval = True
            eligible_value = pricing_result["final_proposed_price"]

        # Điều kiện 3: Hoàn toàn hợp lệ trong thẩm quyền
        else:
            final_status = "CÓ THỂ TIẾP TỤC"
            infeasible_reason = ""
            next_action = f"NVKD {sales_rep['name']} rà soát bản nháp đề xuất và gửi báo giá chính thức cho khách hàng."
            can_proceed = True
            requires_approval = False
            eligible_value = pricing_result["final_proposed_price"]

        logger.record(
            step="Kết luận Xử lý Cơ hội",
            action=f"Xác định trạng thái: {final_status}",
            details={
                "final_status": final_status,
                "eligible_value": eligible_value,
                "requires_approval": requires_approval,
                "next_action": next_action
            },
            rule="Quy tắc phân loại To-Be (Có thể tiếp tục / Cần bổ sung / Chưa đáp ứng / Chờ duyệt)"
        )

        dossier = {
            "opportunity_id": req_id,
            "created_at": now_str,
            "customer_name": request_data.get("customer_name"),
            "contact": request_data.get("contact"),
            "sales_rep": sales_rep,
            "final_status": final_status,
            "can_proceed": can_proceed,
            "requires_approval": requires_approval,
            "is_infeasible": (final_status == "CHƯA ĐÁP ỨNG"),
            "needs_info": False,
            "eligible_value": eligible_value,
            "requested_lead_days": requested_lead_days,
            "customer_budget": budget,
            "inventory": inv_result,
            "pricing": pricing_result,
            "infeasible_reason": infeasible_reason,
            "next_action": next_action,
            "audit_logs": logger.get_logs()
        }

        # -------------------------------------------------------------
        # BƯỚC 6: SOẠN THẢO BẢN NHÁP EMAIL & PHIẾU TRÌNH DUYỆT (SKILL 4)
        # -------------------------------------------------------------
        dossier["customer_email_draft"] = generate_customer_email(dossier)

        if requires_approval or final_status == "CHỜ DUYỆT":
            dossier["approval_ticket"] = generate_approval_ticket(dossier)
        else:
            dossier["approval_ticket"] = "Không cần trình duyệt (Nằm hoàn toàn trong hạn mức thẩm quyền của NVKD)"

        return dossier

    def process_batch(self, batch_requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Xử lý hàng loạt danh sách yêu cầu (từ File Excel, CSV hoặc Google Sheet)
        và tổng hợp số liệu theo đúng yêu cầu đề bài.
        """
        dossiers = []
        counts = {
            "CÓ THỂ TIẾP TỤC": 0,
            "CẦN BỔ SUNG THÔNG TIN": 0,
            "CHƯA ĐÁP ỨNG": 0,
            "CHỜ DUYỆT": 0
        }
        total_eligible_value = 0.0

        for req in batch_requests:
            dossier = self.process_opportunity(req)
            dossiers.append(dossier)

            st = dossier["final_status"]
            if st in counts:
                counts[st] += 1

            # Tính riêng tổng giá trị các cơ hội đủ điều kiện tiếp tục hoặc chờ duyệt
            if st in ["CÓ THỂ TIẾP TỤC", "CHỜ DUYỆT"]:
                total_eligible_value += dossier.get("eligible_value", 0.0)

        return {
            "total_requests": len(batch_requests),
            "counts": counts,
            "total_eligible_value": total_eligible_value,
            "dossiers": dossiers
        }

