from datetime import timedelta

import frappe
from frappe import _
from frappe.query_builder.functions import Coalesce, Count, Sum, CurDate, Now, Max
from frappe.utils import flt, cint, getdate, nowdate, add_days, get_datetime, now_datetime
from pypika.terms import CustomFunction

DATEDIFF = CustomFunction("DATEDIFF", ["date1", "date2"])

# ==============================================================================
# Aggregator Endpoint (get_hub_data)
# ==============================================================================

@frappe.whitelist(allow_guest=False)
def get_hub_data(store: str | None = None, date_from: str | None = None, date_to: str | None = None) -> dict:
    frappe.only_for(["System Manager", "Store Manager", "Sales Manager", "Sales User", "Accounts Manager"])
    
    # Implement cache layer
    user = frappe.session.user
    today_str = nowdate()
    cache_key = f"hub_data:{user}:{store or 'all'}:{today_str}"
    
    cached = frappe.cache().get_value(cache_key)
    if cached:
        return cached

    # Gather data from existing endpoints/sub-queries
    date_from_str = date_from or today_str
    date_to_str = date_to or today_str

    def _safe(fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            frappe.log_error(f"Hub sub-query {fn.__name__} failed: {e}", "AnalyticsHub")
            return {}

    payload = {
        "hero": {
            "sales": _safe(get_daily_revenue_breakdown, date_from_str, date_to_str, store),
            "layaway": _safe(get_layaway_health, store),
            "low_stock": {"total": 0, "stockout": 0},
            "cash_variance": _safe(get_cash_variance_today, store),
            "overdue_payments": _safe(get_overdue_payments, store, type="all"),
            "hold_queue": _safe(get_hold_queue, store),
        },
        "role": {
            "name": ", ".join(frappe.get_roles(user)),
            "is_owner": "Sales Owner" in frappe.get_roles(user) or "System Manager" in frappe.get_roles(user),
            "is_manager": "Sales Manager" in frappe.get_roles(user) or "Store Manager" in frappe.get_roles(user),
        },
        "as_of": str(frappe.utils.now_datetime())
    }

    # Fetch actual low stock for hero count
    try:
        payload["hero"]["low_stock"] = get_low_stock_detail(severity="all", limit=1)
    except Exception:
        pass

    # AI Brief (deterministic fallback)
    try:
        payload["ai_brief"] = _rag_deterministic_fallback("today", None)
    except Exception:
        payload["ai_brief"] = None

    # Set cache for 2 minutes
    frappe.cache().set_value(cache_key, payload, expires_in_sec=120)
    
    return payload


# ==============================================================================
# Individual Metric Endpoints
# ==============================================================================

@frappe.whitelist(allow_guest=False)
def get_daily_revenue_breakdown(date_from: str, date_to: str, store: str | None = None) -> dict:
    frappe.has_permission("Sales Invoice", ptype="read", throw=True)
    frappe.has_permission("Repair Order", ptype="read", throw=True)
    
    # Sales Revenue
    si = frappe.qb.DocType("Sales Invoice")
    q_sales = (
        frappe.qb.from_(si)
        .select(
            Coalesce(Sum(si.base_grand_total), 0).as_("sales_revenue"),
            Count(si.name).as_("sales_count")
        )
        .where(si.docstatus == 1)
        .where(si.is_pos == 1)
        .where(si.posting_date >= date_from)
        .where(si.posting_date <= date_to)
    )
    if store:
        q_sales = q_sales.where(si.cost_center == store)
    
    sales_res = q_sales.run(as_dict=True)
    s_rev = flt(sales_res[0].sales_revenue) if sales_res else 0.0
    s_cnt = cint(sales_res[0].sales_count) if sales_res else 0

    # Repair Revenue
    ro = frappe.qb.DocType("Repair Order")
    q_repair = (
        frappe.qb.from_(ro)
        .select(
            Coalesce(Sum(ro.total_cost), 0).as_("repair_revenue"),
            Count(ro.name).as_("repair_count")
        )
        .where(ro.docstatus == 1)
        .where(ro.status == 'Delivered')
        .where(ro.received_date >= date_from)
        .where(ro.received_date <= date_to)
    )
    if store:
        q_repair = q_repair.where(ro.branch == store)
        
    repair_res = q_repair.run(as_dict=True)
    r_rev = flt(repair_res[0].repair_revenue) if repair_res else 0.0
    r_cnt = cint(repair_res[0].repair_count) if repair_res else 0
    
    # Sparkline data (30 days)
    thirty_days_ago = add_days(date_to, -30)
    sparkline_data = frappe.db.sql("""
        SELECT 
            posting_date as date,
            SUM(base_grand_total) as sales,
            0 as repair
        FROM `tabSales Invoice`
        WHERE docstatus = 1 AND is_pos = 1 AND posting_date BETWEEN %s AND %s
        GROUP BY posting_date
        ORDER BY posting_date
    """, (thirty_days_ago, date_to), as_dict=True)

    return {
        "sales_revenue": s_rev,
        "repair_revenue": r_rev,
        "layaway_revenue": 0.0,
        "total_revenue": s_rev + r_rev,
        "sales_count": s_cnt,
        "repair_count": r_cnt,
        "sparkline_30d": sparkline_data
    }

@frappe.whitelist(allow_guest=False)
def get_layaway_health(store: str | None = None) -> dict:
    frappe.has_permission("Layaway Contract", ptype="read", throw=True)
    
    lc = frappe.qb.DocType("Layaway Contract")
    today_dt = getdate(nowdate())
    next_week = add_days(today_dt, 7)
    
    res = frappe.qb.from_(lc).select(
        Count(lc.name).as_("active"),
        Sum(lc.balance_amount).as_("total_outstanding"),
        Count(frappe.qb.terms.Case().when(lc.target_completion_date < today_dt, 1)).as_("overdue"),
        Count(frappe.qb.terms.Case().when((lc.target_completion_date >= today_dt) & (lc.target_completion_date <= next_week), 1)).as_("due_this_week")
    ).where(lc.docstatus == 1).where(lc.status == 'Active').run(as_dict=True)
    
    data = res[0] if res else {"active": 0, "total_outstanding": 0, "overdue": 0, "due_this_week": 0}
    active = cint(data.active)
    
    return {
        "active": active,
        "overdue": cint(data.overdue),
        "due_this_week": cint(data.due_this_week),
        "total_outstanding": flt(data.total_outstanding),
        "avg_ticket": flt(data.total_outstanding) / active if active > 0 else 0.0,
        "completion_rate_90d": 0.0
    }

@frappe.whitelist(allow_guest=False)
def get_low_stock_detail(severity: str = "all", category: str | None = None, limit: int = 50, offset: int = 0) -> dict:
    frappe.has_permission("Bin", ptype="read", throw=True)
    limit = _clamp_int(limit, 1, 200, 50)
    offset = max(cint(offset), 0)

    bin_tb = frappe.qb.DocType("Bin")
    item_tb = frappe.qb.DocType("Item")
    has_reorder_level = _has_column("Item", "reorder_level")
    reorder_level = item_tb.reorder_level if has_reorder_level else 2
    reorder_select = item_tb.reorder_level if has_reorder_level else (bin_tb.actual_qty * 0 + 2)

    query = (
        frappe.qb.from_(bin_tb)
        .join(item_tb).on(bin_tb.item_code == item_tb.name)
        .select(
            bin_tb.item_code,
            item_tb.item_name,
            bin_tb.actual_qty,
            reorder_select.as_("reorder_level"),
            bin_tb.warehouse,
            frappe.qb.terms.Case()
                .when(bin_tb.actual_qty == 0, 'stockout')
                .else_('low')
                .as_("severity")
        )
        .where((bin_tb.actual_qty <= reorder_level) | (bin_tb.actual_qty == 0))
    )

    total_query = (
        frappe.qb.from_(bin_tb)
        .join(item_tb).on(bin_tb.item_code == item_tb.name)
        .select(Count(bin_tb.name).as_("total"))
        .where((bin_tb.actual_qty <= reorder_level) | (bin_tb.actual_qty == 0))
    )

    if severity == "stockout":
        query = query.where(bin_tb.actual_qty == 0)
        total_query = total_query.where(bin_tb.actual_qty == 0)
    elif severity == "low":
        low_filter = (bin_tb.actual_qty <= reorder_level) & (bin_tb.actual_qty > 0)
        query = query.where(low_filter)
        total_query = total_query.where(low_filter)

    if category and _has_column("Item", "custom_jewelry_type"):
        query = query.where(item_tb.custom_jewelry_type == category)
        total_query = total_query.where(item_tb.custom_jewelry_type == category)

    count_res = total_query.run(as_dict=True)
    total = cint(count_res[0].total) if count_res else 0
    stockout_query = (
        frappe.qb.from_(bin_tb)
        .join(item_tb).on(bin_tb.item_code == item_tb.name)
        .select(Count(bin_tb.name).as_("total"))
        .where(bin_tb.actual_qty == 0)
    )
    if category and _has_column("Item", "custom_jewelry_type"):
        stockout_query = stockout_query.where(item_tb.custom_jewelry_type == category)
    stockout_res = stockout_query.run(as_dict=True)
    stockout = cint(stockout_res[0].total) if stockout_res else 0
    items = query.limit(limit).offset(offset).run(as_dict=True)

    return {"total": total, "stockout": stockout, "items": items}

@frappe.whitelist(allow_guest=False)
def get_cash_variance_today(store: str | None = None) -> dict:
    try:
        frappe.has_permission("POS Closing Entry", ptype="read", throw=True)
    except frappe.PermissionError:
        return {"sessions": [], "total_variance": 0, "worst_session": None, "within_tolerance": True}

    has_expected = _has_column("POS Closing Entry", "custom_expected_cash")
    has_counted = _has_column("POS Closing Entry", "custom_counted_cash")
    has_variance = _has_column("POS Closing Entry", "custom_variance")

    pos = frappe.qb.DocType("POS Closing Entry")
    today_dt = nowdate()

    expected_field = pos.custom_expected_cash if has_expected else Coalesce(Sum(pos.grand_total), 0)
    counted_field = pos.custom_counted_cash if has_counted else Coalesce(Sum(pos.grand_total), 0)
    variance_field = pos.custom_variance if has_variance else (counted_field - expected_field)

    q = (
        frappe.qb.from_(pos)
        .select(
            pos.name.as_("session_id"),
            pos.owner.as_("opened_by"),
            expected_field.as_("expected"),
            counted_field.as_("counted"),
            variance_field.as_("variance"),
            pos.status
        )
        .where(pos.posting_date == today_dt)
        .where(pos.docstatus == 1)
    )
    sessions = q.run(as_dict=True)

    total_variance = sum(flt(s.variance) for s in sessions)
    worst_session = min(sessions, key=lambda x: flt(x.variance)) if sessions else None

    return {
        "sessions": sessions,
        "total_variance": total_variance,
        "worst_session": worst_session,
        "within_tolerance": abs(total_variance) < 20.0
    }

@frappe.whitelist(allow_guest=False)
def get_overdue_payments(store: str | None = None, type: str = "all", overdue_days_threshold: int = 30) -> dict:
    repairs = []
    layaways = []
    total_amount = 0.0
    
    if type in ["all", "repair"]:
        frappe.has_permission("Repair Order", ptype="read", throw=True)
        ro = frappe.qb.DocType("Repair Order")
        repairs = (
            frappe.qb.from_(ro)
            .select(ro.name, ro.customer, ro.balance_due, ro.delivered_date)
            .where(ro.status.isin(['Ready for Pickup', 'Delivered']))
            .where(ro.balance_due > 0)
            .where(DATEDIFF(CurDate(), ro.delivered_date) > overdue_days_threshold)
        ).run(as_dict=True)
        total_amount += sum(flt(r.balance_due) for r in repairs)
        
    if type in ["all", "layaway"]:
        frappe.has_permission("Layaway Contract", ptype="read", throw=True)
        lc = frappe.qb.DocType("Layaway Contract")
        layaways = (
            frappe.qb.from_(lc)
            .select(lc.name, lc.customer, lc.balance_amount, lc.target_completion_date)
            .where(lc.docstatus == 1)
            .where(lc.status == 'Active')
            .where(lc.target_completion_date < CurDate())
        ).run(as_dict=True)
        total_amount += sum(flt(l.outstanding_amount) for l in layaways)
        
    return {
        "repairs": repairs,
        "layaways": layaways,
        "total_overdue_amount": total_amount,
        "count": len(repairs) + len(layaways)
    }

@frappe.whitelist(allow_guest=False)
def get_hold_queue(store: str | None = None) -> dict:
    frappe.has_permission("Stock Reservation", ptype="read", throw=True)

    sr = frappe.qb.DocType("Stock Reservation")
    q = (
        frappe.qb.from_(sr)
        .select(
            sr.name.as_("reservation"),
            sr.customer,
            sr.owner.as_("salesperson"),
            sr.item_code.as_("item"),
            sr.hold_until,
            sr.creation,
        )
        .where(sr.status == 'Active')
        .where(sr.hold_until > Now())
    )
    if _has_column("Stock Reservation", "reservation_type"):
        q = q.where(sr.reservation_type == 'Soft Hold')

    active_holds = q.run(as_dict=True)
    now_dt = get_datetime(now_datetime())
    one_hour_later = now_dt + timedelta(hours=1)

    expiring_soon = 0
    for hold in active_holds:
        hold_dt = get_datetime(hold.hold_until)
        created = get_datetime(hold.creation) if hold.get("creation") else now_dt
        hold["age_hours"] = flt((now_dt - created).total_seconds() / 3600, 1)
        if hold_dt and hold_dt <= one_hour_later:
            expiring_soon += 1

    return {
        "active_holds": active_holds,
        "total_count": len(active_holds),
        "expiring_soon_count": expiring_soon,
    }


# ==============================================================================
# Phase 8 — RAG P&L Prediction (§8.8 / §8.11)
# Wires the real RAG pipeline: kg_builder + ChromaDB COLLECTION_METRICS +
# Qwen3.6-35B with grounding validation and deterministic fallback.
# ==============================================================================

@frappe.whitelist(allow_guest=False)
def get_rag_insights(scope: str = "today", focus: str | None = None) -> dict:
    """§8.8 — RAG P&L insight generator.
    Permission: System Manager, Sales Owner, or Store Manager (per §14.3).
    """
    roles = frappe.get_roles()
    if not any(r in roles for r in ("System Manager", "Sales Owner", "Store Manager", "Sales Manager")):
        frappe.throw(_("You do not have permission to view AI insights."), frappe.PermissionError)

    try:
        from zevar_core.rag.generation.insight_generator import generate_pnl_insights
        return generate_pnl_insights(scope=scope, focus=focus)
    except ImportError:
        # Defensive: if RAG module not importable, return the deterministic fallback
        return _rag_deterministic_fallback(scope, focus)
    except Exception as e:
        frappe.log_error(f"get_rag_insights failed: {e}", "AnalyticsHub")
        return _rag_deterministic_fallback(scope, focus)


def _rag_deterministic_fallback(scope: str, focus: str | None) -> dict:
    """Per Plan §9.7 last paragraph — when the LLM path fails, return a
    deterministic rule-based summary built from the existing dashboard APIs.
    """
    sales = get_daily_revenue_breakdown(nowdate(), nowdate())
    layaway = get_layaway_health()
    variance = get_cash_variance_today()
    overdue = get_overdue_payments()

    sales_revenue = flt(sales.get("total_revenue", 0))
    sales_count = int(sales.get("sales_count", 0))
    repair_count = int(sales.get("repair_count", 0))
    overdue_count = int(overdue.get("count", 0))
    overdue_amount = flt(overdue.get("total_overdue_amount", 0))
    var_amount = flt(variance.get("total_variance", 0))
    in_tol = bool(variance.get("within_tolerance"))

    headline = f"Today: {sales_count} sales · {repair_count} repairs delivered"
    body = (
        f"Total revenue ${sales_revenue:,.2f}. "
        f"{layaway.get('active', 0)} active layaways, {layaway.get('overdue', 0)} overdue. "
        f"Cash variance ${var_amount:,.2f} "
        f"({'within' if in_tol else 'outside'} tolerance). "
        f"{overdue_count} overdue payments totaling ${overdue_amount:,.2f}."
    )

    insights = [
        {
            "id": f"sum-{frappe.utils.now_datetime().strftime('%Y%m%d%H')}",
            "category": "revenue",
            "severity": "info",
            "text": f"Total revenue today is ${sales_revenue:,.2f} across {sales_count} sales and {repair_count} repairs.",
            "grounded_numbers": [
                {"value": f"${sales_revenue:,.2f}", "label": "Total revenue",
                 "source_query": "get_daily_revenue_breakdown", "confidence": 1.0},
            ],
            "recommended_action": None,
        }
    ]
    if overdue_count > 0:
        insights.append({
            "id": f"od-{nowdate()}",
            "category": "finance",
            "severity": "warning" if overdue_amount > 1000 else "info",
            "text": f"{overdue_count} overdue payments totaling ${overdue_amount:,.2f} (repairs + layaways).",
            "grounded_numbers": [
                {"value": f"${overdue_amount:,.2f}", "label": "Overdue amount",
                 "source_query": "get_overdue_payments", "confidence": 1.0},
            ],
            "recommended_action": {
                "type": "follow_up",
                "description": "Run a follow-up sweep on overdue repairs and layaways.",
                "endpoint": None,
            },
        })
    if not in_tol:
        insights.append({
            "id": f"cv-{nowdate()}",
            "category": "finance",
            "severity": "critical" if abs(var_amount) >= 20 else "warning",
            "text": f"Cash variance ${var_amount:,.2f} is outside tolerance (≥$20).",
            "grounded_numbers": [
                {"value": f"${var_amount:,.2f}", "label": "Cash variance",
                 "source_query": "get_cash_variance_today", "confidence": 1.0},
            ],
            "recommended_action": {
                "type": "investigate",
                "description": "Review the POS closing session that contributed the variance.",
                "endpoint": None,
            },
        })

    return {
        "headline": headline,
        "body": body,
        "insights": insights,
        "generated_at": str(frappe.utils.now_datetime()),
        "model_version": "fallback",
        "prompt_hash": None,
    }


@frappe.whitelist(allow_guest=False)
def submit_insight_feedback(insight_id: str, rating: int, note: str = "") -> dict:
    """§8.11 — Persist user feedback on an insight to `tabRAG Insight Feedback`.
    Plan §9.9: weekly cron aggregates this for prompt template tuning.
    """
    if rating not in (-1, 0, 1):
        frappe.throw(_("rating must be -1, 0, or 1"))

    # Try to write to the DocType if it exists; fall back to a cache record.
    if frappe.db.exists("DocType", "RAG Insight Feedback"):
        doc = frappe.get_doc({
            "doctype": "RAG Insight Feedback",
            "insight_id": insight_id,
            "user": frappe.session.user,
            "rating": int(rating),
            "note": note or "",
        })
        doc.insert(ignore_permissions=True)
        return {"ok": True, "name": doc.name}

    key = f"rag_feedback:{insight_id}"
    existing = frappe.cache().get_value(key) or []
    existing.append({
        "insight_id": insight_id,
        "user": frappe.session.user,
        "rating": int(rating),
        "note": note or "",
        "created_at": str(frappe.utils.now_datetime()),
    })
    frappe.cache().set_value(key, existing, expires_in_sec=86400 * 30)
    return {"ok": True, "recorded": "cache"}


# ==============================================================================
# Phase 9 — Overage Clearance Workflow (§8.9 / §8.10)
# ==============================================================================

@frappe.whitelist(allow_guest=False)
def score_overage(days_threshold: int = 90, min_score: int = 50, limit: int = 100, offset: int = 0) -> dict:
    """Return scored dead-stock queue using stock age, velocity, and margin drag."""
    frappe.has_permission("Bin", ptype="read", throw=True)
    frappe.has_permission("Item", ptype="read", throw=True)

    days_threshold = _clamp_int(days_threshold, 30, 3650, 90)
    min_score = _clamp_int(min_score, 0, 100, 50)
    limit = _clamp_int(limit, 1, 200, 100)
    offset = max(cint(offset), 0)

    rows = _get_overage_candidates(days_threshold)
    if not rows:
        return {"items": [], "total": 0, "min_score": min_score, "days_threshold": days_threshold}

    item_codes = [row["item_code"] for row in rows]
    sales_90 = _get_recent_item_sales(item_codes, 90)
    sales_365 = _get_recent_item_sales(item_codes, 365)

    scored = []
    for row in rows:
        item = dict(row)
        item_code = item["item_code"]
        item["sales_90d"] = flt(sales_90.get(item_code, 0))
        item["sales_365d"] = flt(sales_365.get(item_code, 0))
        item["overage_score"] = _compute_overage_score(item)
        item["recommended_action"] = _recommended_overage_action(item["overage_score"])
        item["recommended_markdown_pct"] = _recommended_markdown_pct(item["overage_score"])
        if item["overage_score"] >= min_score:
            scored.append(item)

    scored.sort(key=lambda d: (d["overage_score"], d["days_in_inventory"]), reverse=True)
    total = len(scored)
    return {
        "items": scored[offset:offset + limit],
        "total": total,
        "min_score": min_score,
        "days_threshold": days_threshold,
    }


@frappe.whitelist(allow_guest=False)
def submit_overage_action(action_type: str, items: list[str] | str, params: dict | None = None) -> dict:
    """Execute a clearance action and track the outcome/audit trail."""
    frappe.has_permission("Item", ptype="read", throw=True)
    params = params or {}
    _require_overage_action_role(action_type, params)

    if isinstance(items, str):
        items = [items]
    if not isinstance(items, list) or not items:
        frappe.throw(_("Select at least one item."))
    items = [str(item).strip() for item in items if str(item).strip()]
    if not items:
        frappe.throw(_("Select at least one item."))

    if action_type not in ("markdown", "bundle", "vault_sale", "vendor_return", "repurpose", "trade_up"):
        frappe.throw(_("Unknown action_type: {0}").format(action_type))

    if action_type == "markdown":
        results = _submit_markdown_action(action_type, items, params)
    else:
        results = _submit_note_action(action_type, items, params)

    _log_overage_action(action_type, items, params, results)
    return {"ok": True, "action_type": action_type, "items": items, "results": results}


def _has_column(doctype: str, fieldname: str) -> bool:
    try:
        return bool(frappe.db.has_column(doctype, fieldname))
    except Exception:
        return False


def _clamp_int(value, low: int, high: int, default: int) -> int:
    try:
        value = cint(value)
    except Exception:
        value = default
    return min(max(value or default, low), high)


def _get_overage_candidates(days_threshold: int) -> list[dict]:
    bin_tb = frappe.qb.DocType("Bin")
    item_tb = frappe.qb.DocType("Item")
    sle = frappe.qb.DocType("Stock Ledger Entry")
    last_moves = (
        frappe.qb.from_(sle)
        .select(sle.item_code, Max(sle.posting_date).as_("last_move"))
        .where(sle.docstatus == 1)
        .groupby(sle.item_code)
    ).run(as_dict=True)
    last_move_by_item = {r.item_code: r.last_move for r in last_moves if r.item_code}

    price_field = item_tb.custom_msrp if _has_column("Item", "custom_msrp") else item_tb.standard_rate
    cost_field = item_tb.custom_cost_price if _has_column("Item", "custom_cost_price") else item_tb.valuation_rate
    category_field = item_tb.custom_jewelry_type if _has_column("Item", "custom_jewelry_type") else item_tb.item_group

    rows = (
        frappe.qb.from_(bin_tb)
        .join(item_tb).on(bin_tb.item_code == item_tb.name)
        .select(
            bin_tb.item_code,
            item_tb.item_name,
            item_tb.item_group,
            category_field.as_("category"),
            Sum(bin_tb.actual_qty).as_("actual_qty"),
            Sum(bin_tb.stock_value).as_("stock_value"),
            Coalesce(price_field, 0).as_("current_price"),
            Coalesce(cost_field, 0).as_("cost_basis"),
            Max(bin_tb.valuation_rate).as_("valuation_rate"),
        )
        .where(bin_tb.actual_qty > 0)
        .where(item_tb.disabled == 0)
        .groupby(bin_tb.item_code)
        .limit(1000)
    ).run(as_dict=True)

    today = getdate(nowdate())
    candidates = []
    for row in rows:
        last_move = last_move_by_item.get(row.item_code)
        if not last_move:
            continue
        days = (today - getdate(last_move)).days
        if days < days_threshold:
            continue
        qty = flt(row.actual_qty) or 1
        stock_value = flt(row.stock_value)
        row["days_in_inventory"] = days
        row["age_bucket"] = _age_bucket(days)
        row["last_movement_date"] = str(last_move)
        row["cost_basis"] = flt(row.cost_basis) or flt(row.valuation_rate) or flt(stock_value / qty)
        row["stock_value"] = stock_value
        candidates.append(row)
    return candidates


def _get_recent_item_sales(item_codes: list[str], days: int) -> dict[str, float]:
    if not item_codes:
        return {}
    sii = frappe.qb.DocType("Sales Invoice Item")
    si = frappe.qb.DocType("Sales Invoice")
    rows = (
        frappe.qb.from_(sii)
        .join(si).on(sii.parent == si.name)
        .select(sii.item_code, Sum(sii.qty).as_("qty"))
        .where(si.docstatus == 1)
        .where(si.posting_date >= add_days(nowdate(), -days))
        .where(sii.item_code.isin(item_codes))
        .groupby(sii.item_code)
    ).run(as_dict=True)
    return {r.item_code: flt(r.qty) for r in rows}


def _compute_overage_score(item: dict) -> int:
    days = cint(item.get("days_in_inventory"))
    age_score = min(40, max(0, (days - 45) / 685 * 40))
    sales_90 = flt(item.get("sales_90d"))
    sales_365 = flt(item.get("sales_365d"))
    expected_90 = max(sales_365 / 4, 1)
    velocity_score = min(20, max(0, (1 - min(sales_90 / expected_90, 1)) * 20))
    price = flt(item.get("current_price"))
    cost = flt(item.get("cost_basis"))
    margin_pct = ((price - cost) / price * 100) if price else 0
    margin_score = min(20, max(0, (55 - margin_pct) / 55 * 20))
    carrying_score = min(10, flt(item.get("stock_value")) / 10000 * 10)
    seasonality_adjustment = 10 if _has_q4_lift(item) else 0
    return cint(min(100, max(0, round(age_score + velocity_score + margin_score + carrying_score - seasonality_adjustment))))


def _has_q4_lift(item: dict) -> bool:
    category = (item.get("category") or item.get("item_group") or "").lower()
    return any(token in category for token in ("bridal", "diamond", "engagement", "holiday"))


def _age_bucket(days: int) -> str:
    if days >= 730:
        return "730+"
    if days >= 365:
        return "365-729"
    if days >= 180:
        return "180-364"
    if days >= 90:
        return "90-179"
    return "0-89"


def _recommended_overage_action(score: int) -> str:
    if score >= 95:
        return "vendor_return_or_repurpose"
    if score >= 85:
        return "vault_sale"
    if score >= 75:
        return "markdown"
    if score >= 65:
        return "bounty_markdown"
    return "bundle"


def _recommended_markdown_pct(score: int) -> int:
    if score >= 95:
        return 45
    if score >= 85:
        return 35
    if score >= 75:
        return 25
    if score >= 65:
        return 15
    return 0


def _require_overage_action_role(action_type: str, params: dict) -> None:
    roles = set(frappe.get_roles())
    markdown_pct = flt(params.get("markdown_pct"))
    if action_type in ("vendor_return", "repurpose") and "System Manager" not in roles:
        frappe.throw(_("Only System Manager can execute this clearance action."), frappe.PermissionError)
    if action_type == "markdown" and markdown_pct > 30 and not roles.intersection({"System Manager", "Sales Manager", "Store Manager"}):
        frappe.throw(_("Manager approval is required for markdowns over 30%."), frappe.PermissionError)
    if not roles.intersection({"System Manager", "Sales Manager", "Store Manager", "Stock Manager", "Inventory Manager"}):
        frappe.throw(_("You do not have permission to execute overage actions."), frappe.PermissionError)


def _item_value_fields() -> list[str]:
    fields = ["item_name", "standard_rate", "valuation_rate"]
    for fieldname in ("custom_msrp", "custom_cost_price"):
        if _has_column("Item", fieldname):
            fields.append(fieldname)
    return fields


def _submit_markdown_action(action_type: str, items: list[str], params: dict) -> list[dict]:
    if not frappe.db.exists("DocType", "Pricing Recommendation"):
        frappe.throw(_("Pricing Recommendation is not installed on this site."))
    frappe.has_permission("Pricing Recommendation", ptype="create", throw=True)
    markdown_pct = _clamp_int(params.get("markdown_pct"), 1, 90, 15)
    results = []
    for item_code in items:
        if not frappe.db.exists("Item", item_code):
            frappe.throw(_("Item not found: {0}").format(item_code))
        item = frappe.db.get_value("Item", item_code, _item_value_fields(), as_dict=True) or {}
        current_price = flt(item.get("custom_msrp")) or flt(item.get("standard_rate"))
        cost = flt(item.get("custom_cost_price")) or flt(item.get("valuation_rate"))
        recommended_price = flt(current_price * (1 - markdown_pct / 100), 2)
        doc = frappe.get_doc({
            "doctype": "Pricing Recommendation",
            "recommendation_type": "Clearance",
            "item_code": item_code,
            "current_price": current_price,
            "current_margin_pct": _margin_pct(current_price, cost),
            "recommended_price": recommended_price,
            "projected_margin_pct": _margin_pct(recommended_price, cost),
            "confidence_level": "Medium",
            "reasoning": params.get("reasoning") or f"Overage clearance markdown of {markdown_pct}%.",
            "generated_by": "Analytics Hub",
            "generation_method": "manual",
            "status": "Pending Review" if markdown_pct > 30 else "Draft",
            "valid_until": params.get("valid_until") or add_days(nowdate(), 30),
            "notes": params.get("notes") or "",
        })
        doc.insert()
        outcome = _track_clearance_outcome(item_code, action_type, markdown_pct, doc.name)
        results.append({"item_code": item_code, "pricing_recommendation": doc.name, "clearance_outcome": outcome})
    return results


def _submit_note_action(action_type: str, items: list[str], params: dict) -> list[dict]:
    results = []
    for item_code in items:
        if not frappe.db.exists("Item", item_code):
            frappe.throw(_("Item not found: {0}").format(item_code))
        outcome = _track_clearance_outcome(item_code, action_type, flt(params.get("markdown_pct")), None, params)
        results.append({"item_code": item_code, "clearance_outcome": outcome})
    return results


def _margin_pct(price: float, cost: float) -> float:
    return flt(((price - cost) / price * 100) if price else 0, 2)


def _track_clearance_outcome(
    item_code: str,
    action_type: str,
    markdown_pct: float = 0,
    reference_doc: str | None = None,
    params: dict | None = None,
) -> str | None:
    if not frappe.db.exists("DocType", "Clearance Outcome"):
        return None
    item = frappe.db.get_value("Item", item_code, _item_value_fields(), as_dict=True) or {}
    doc = frappe.get_doc({
        "doctype": "Clearance Outcome",
        "item_code": item_code,
        "action_type": action_type,
        "applied_at": now_datetime(),
        "applied_by": frappe.session.user,
        "markdown_pct": flt(markdown_pct),
        "cost_basis": flt(item.get("custom_cost_price")) or flt(item.get("valuation_rate")),
        "reference_doctype": "Pricing Recommendation" if reference_doc else None,
        "reference_name": reference_doc,
        "feedback_notes": frappe.as_json(params or {}) if params else "",
    })
    doc.insert(ignore_permissions=True)
    return doc.name


def _log_overage_action(action_type: str, items: list[str], params: dict, results: list[dict]) -> None:
    try:
        from zevar_core.api.audit_log import log_event_safely
        log_event_safely(
            "stock_adjusted",
            {
                "source": "analytics_hub",
                "action_type": action_type,
                "items": items,
                "params": params,
                "results": results,
            },
            reference_document=", ".join(items[:5]),
            reference_type="Item",
        )
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Analytics Hub overage audit failed")
