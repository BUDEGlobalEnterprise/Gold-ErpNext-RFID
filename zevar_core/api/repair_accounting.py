"""
Accounting Integration API - Repair System Integration (Phase 11.3)

This module provides accounting-related functionality:
- Revenue recognition for repairs
- Cost of materials consumed
- Technician commission tracking
- Payment reconciliation
- Accounting period close
"""

from datetime import datetime, timedelta
from typing import Any

import frappe
from frappe import _
from frappe.utils import add_to_date, flt, fmt_money, get_datetime_str, getdate, now, nowdate


@frappe.whitelist()
def get_revenue_recognition(
    start_date: str,
    end_date: str,
    warehouse: str | None = None,
    group_by: str = "repair_type",
) -> dict[str, Any]:
    """
    Get revenue recognition report for repairs within a date period.

    Revenue is recognized when repairs are delivered (not when received).

    Args:
        start_date: Start date for reporting period
        end_date: End date for reporting period
        warehouse: Filter by warehouse/store
        group_by: How to group data (repair_type, warehouse, technician, daily)

    Returns:
        Revenue recognition report with recognized, deferred, and pending revenue
    """
    if not frappe.has_permission("Repair Order", "read"):
        frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

    # Get delivered repairs in period (recognized revenue)
    delivered_filters = [
        ["delivered_date", "between", [start_date, end_date]],
        ["status", "=", "Delivered"]
    ]
    if warehouse:
        delivered_filters.append(["warehouse", "=", warehouse])

    delivered_repairs = frappe.get_all(
        "Repair Order",
        filters=delivered_filters,
        fields=[
            "name", "delivered_date", "total_cost", "labor_cost",
            "material_cost", "warehouse", "repair_type", "handled_by"
        ]
    )

    # Get work in progress (deferred/unbilled revenue)
    wip_filters = [
        ["status", "not in", ["Delivered", "Cancelled", "Draft"]],
        ["received_date", "<=", end_date]
    ]
    if warehouse:
        wip_filters.append(["warehouse", "=", warehouse])

    wip_repairs = frappe.get_all(
        "Repair Order",
        filters=wip_filters,
        fields=[
            "name", "status", "total_cost", "labor_cost",
            "material_cost", "warehouse", "repair_type", "promised_date"
        ]
    )

    # Calculate totals
    report = {
        "period": {"start": start_date, "end": end_date},
        "warehouse": warehouse,
        "group_by": group_by,
        "summary": {
            "recognized_revenue": 0,
            "recognized_labor": 0,
            "recognized_materials": 0,
            "recognized_count": len(delivered_repairs),
            "deferred_revenue": 0,
            "wip_count": len(wip_repairs),
            "avg_repair_value": 0,
        },
        "details": {},
    }

    # Process delivered repairs (recognized revenue)
    for repair in delivered_repairs:
        total = flt(repair.get("total_cost", 0))
        labor = flt(repair.get("labor_cost", 0))
        material = flt(repair.get("material_cost", 0))

        report["summary"]["recognized_revenue"] += total
        report["summary"]["recognized_labor"] += labor
        report["summary"]["recognized_materials"] += material

        # Group by specified field
        group_key = _get_group_key(repair, group_by)
        if group_key not in report["details"]:
            report["details"][group_key] = {
                "recognized_revenue": 0,
                "recognized_labor": 0,
                "recognized_materials": 0,
                "recognized_count": 0,
                "deferred_revenue": 0,
                "wip_count": 0,
            }

        report["details"][group_key]["recognized_revenue"] += total
        report["details"][group_key]["recognized_labor"] += labor
        report["details"][group_key]["recognized_materials"] += material
        report["details"][group_key]["recognized_count"] += 1

    # Process WIP repairs (deferred revenue)
    for repair in wip_repairs:
        total = flt(repair.get("total_cost", 0))
        report["summary"]["deferred_revenue"] += total

        group_key = _get_group_key(repair, group_by)
        if group_key not in report["details"]:
            report["details"][group_key] = {
                "recognized_revenue": 0,
                "recognized_labor": 0,
                "recognized_materials": 0,
                "recognized_count": 0,
                "deferred_revenue": 0,
                "wip_count": 0,
            }

        report["details"][group_key]["deferred_revenue"] += total
        report["details"][group_key]["wip_count"] += 1

    # Calculate average repair value
    if report["summary"]["recognized_count"] > 0:
        report["summary"]["avg_repair_value"] = (
            report["summary"]["recognized_revenue"] / report["summary"]["recognized_count"]
        )

    return report


def _get_group_key(repair: dict, group_by: str) -> str:
    """Helper to get grouping key for reports."""
    if group_by == "repair_type":
        return repair.get("repair_type") or "Unspecified"
    elif group_by == "warehouse":
        return repair.get("warehouse") or "Unspecified"
    elif group_by == "technician":
        return repair.get("handled_by") or "Unassigned"
    elif group_by == "daily":
        return str(repair.get("delivered_date", "Unknown"))[:10]
    else:
        return "Other"


@frappe.whitelist()
def get_materials_consumed(
    start_date: str,
    end_date: str,
    warehouse: str | None = None,
) -> dict[str, Any]:
    """
    Get cost of materials consumed for repairs within a date period.

    This tracks actual materials used from inventory (via Stock Entries).

    Args:
        start_date: Start date for reporting period
        end_date: End date for reporting period
        warehouse: Filter by warehouse/store

    Returns:
        Materials consumed report with cost breakdown
    """
    if not frappe.has_permission("Repair Order", "read"):
        frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

    # Get delivered repairs that consumed materials
    delivered_filters = [
        ["delivered_date", "between", [start_date, end_date]],
        ["status", "=", "Delivered"],
        ["parts_stock_created", "=", 1]
    ]
    if warehouse:
        delivered_filters.append(["warehouse", "=", warehouse])

    repairs = frappe.get_all(
        "Repair Order",
        filters=delivered_filters,
        fields=["name", "material_cost"]
    )

    # Get all parts used
    parts_used = {}
    total_cost = 0

    for repair_name in [r["name"] for r in repairs]:
        repair_doc = frappe.get_doc("Repair Order", repair_name)

        if repair_doc.parts:
            for part in repair_doc.parts:
                item_code = part.item_code
                qty = flt(part.qty or 0)
                flt(part.rate or 0)
                amount = flt(part.amount or 0)

                if item_code not in parts_used:
                    # Get item details
                    item_details = frappe.db.get_value(
                        "Item",
                        item_code,
                        ["item_name", "item_group", "stock_uom"],
                        as_dict=True
                    ) or {}

                    parts_used[item_code] = {
                        "item_code": item_code,
                        "item_name": item_details.get("item_name", item_code),
                        "item_group": item_details.get("item_group", "Unknown"),
                        "uom": item_details.get("stock_uom", "Nos"),
                        "total_qty": 0,
                        "total_cost": 0,
                        "repairs": [],
                    }

                parts_used[item_code]["total_qty"] += qty
                parts_used[item_code]["total_cost"] += amount
                parts_used[item_code]["repairs"].append(repair_name)
                total_cost += amount

    return {
        "period": {"start": start_date, "end": end_date},
        "warehouse": warehouse,
        "summary": {
            "total_cost": total_cost,
            "total_repairs": len(repairs),
            "unique_items": len(parts_used),
        },
        "items": sorted(
            parts_used.values(),
            key=lambda x: x["total_cost"],
            reverse=True
        ),
    }


@frappe.whitelist()
def get_technician_commission(
    technician: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict[str, Any]]:
    """
    Calculate technician commissions for repairs.

    Commission is typically based on:
    - Labor revenue (percentage of labor cost)
    - Or flat rate per repair type
    - Or bonus for completing repairs on time

    Args:
        technician: Filter by specific technician (None = all)
        start_date: Start date for commission period
        end_date: End date for commission period

    Returns:
        Commission report by technician
    """
    if not frappe.has_permission("Repair Order", "read"):
        frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

    # Default to current month if no dates provided
    if not start_date:
        start_date = getdate(nowdate()).replace(day=1).strftime("%Y-%m-%d")
    if not end_date:
        end_date = nowdate()

    # Get commission settings
    commission_settings = frappe.get_single("Repair Commission Settings", cache=True)
    if not commission_settings:
        commission_settings = frappe.new_doc("Repair Commission Settings")
        commission_settings.commission_rate_labor_pct = 20.0
        commission_settings.bonus_on_time_pct = 5.0
        commission_settings.penalty_late_days = 0.5

    # Get completed/delivered repairs
    filters = [
        ["assigned_to", "!=", ""],
        ["delivered_date", "between", [start_date, end_date]],
        ["status", "=", "Delivered"]
    ]

    if technician:
        filters.append(["assigned_to", "=", technician])

    repairs = frappe.get_all(
        "Repair Order",
        filters=filters,
        fields=[
            "name", "assigned_to", "delivered_date", "promised_date",
            "received_date", "repair_type", "labor_cost", "total_cost",
            "warehouse"
        ]
    )

    # Calculate commission per technician
    commission_data = {}

    for repair in repairs:
        tech = repair["assigned_to"]
        if not tech:
            continue

        if tech not in commission_data:
            tech_name = frappe.db.get_value("User", tech, "full_name")
            commission_data[tech] = {
                "technician": tech,
                "technician_name": tech_name,
                "repairs": [],
                "total_labor_revenue": 0,
                "total_revenue": 0,
                "base_commission": 0,
                "on_time_bonus": 0,
                "late_penalty": 0,
                "total_commission": 0,
            }

        labor_cost = flt(repair.get("labor_cost", 0))
        total_cost = flt(repair.get("total_cost", 0))

        # Calculate commission
        commission_rate = flt(commission_settings.get("commission_rate_labor_pct", 20)) / 100
        base_commission = labor_cost * commission_rate

        # Check if on time (delivered on or before promised date)
        bonus = 0
        penalty = 0

        if repair.get("promised_date") and repair.get("delivered_date"):
            promised = getdate(repair["promised_date"])
            delivered = getdate(repair["delivered_date"])

            if delivered <= promised:
                # On-time bonus
                bonus_rate = flt(commission_settings.get("bonus_on_time_pct", 5)) / 100
                bonus = base_commission * bonus_rate
            else:
                # Late penalty
                days_late = (delivered - promised).days
                penalty_rate = flt(commission_settings.get("penalty_late_days", 0.5)) / 100
                penalty = base_commission * penalty_rate * days_late

        repair_commission = {
            "repair_order": repair["name"],
            "repair_type": repair.get("repair_type"),
            "labor_cost": labor_cost,
            "total_cost": total_cost,
            "delivered_date": str(repair["delivered_date"]),
            "promised_date": str(repair.get("promised_date", "")),
            "on_time": delivered <= promised if repair.get("promised_date") else None,
            "base_commission": base_commission,
            "bonus": bonus,
            "penalty": penalty,
            "net_commission": base_commission + bonus - penalty,
        }

        commission_data[tech]["repairs"].append(repair_commission)
        commission_data[tech]["total_labor_revenue"] += labor_cost
        commission_data[tech]["total_revenue"] += total_cost
        commission_data[tech]["base_commission"] += base_commission
        commission_data[tech]["on_time_bonus"] += bonus
        commission_data[tech]["late_penalty"] += penalty

    # Calculate totals
    for tech in commission_data.values():
        tech["total_commission"] = tech["base_commission"] + tech["on_time_bonus"] - tech["late_penalty"]

    return sorted(commission_data.values(), key=lambda x: x["total_commission"], reverse=True)


@frappe.whitelist()
def get_payment_reconciliation(
    start_date: str,
    end_date: str,
    warehouse: str | None = None,
) -> dict[str, Any]:
    """
    Reconcile payments against repair orders.

    Shows deposits, payments, and outstanding balances.

    Args:
        start_date: Start date for reporting period
        end_date: End date for reporting period
        warehouse: Filter by warehouse/store

    Returns:
        Payment reconciliation report
    """
    if not frappe.has_permission("Repair Order", "read"):
        frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

    # Get repairs with activity in period
    [
        [
            {"key": "received_date", "value": "between " + start_date + " and " + end_date},
            "or",
            {"key": "delivered_date", "value": "between " + start_date + " and " + end_date},
            "or",
            {"key": "deposit_date", "value": "between " + start_date + " and " + end_date},
        ]
    ]

    # Build proper filters
    or_filters = [
        {"received_date": ["between", [start_date, end_date]]},
        {"delivered_date": ["between", [start_date, end_date]]},
        {"deposit_date": ["between", [start_date, end_date]]},
    ]

    if warehouse:
        for f in or_filters:
            f["warehouse"] = warehouse

    repairs = frappe.get_all(
        "Repair Order",
        or_filters=or_filters,
        fields=[
            "name", "customer", "status", "total_cost", "deposit_amount",
            "deposit_date", "payment_status", "balance_due", "sales_invoice",
            "received_date", "delivered_date"
        ]
    )

    reconciliation = {
        "period": {"start": start_date, "end": end_date},
        "warehouse": warehouse,
        "summary": {
            "total_repair_value": 0,
            "total_deposits": 0,
            "total_collected": 0,
            "total_outstanding": 0,
            "invoice_coverage": 0,
        },
        "by_status": {
            "paid": {"count": 0, "amount": 0},
            "partial": {"count": 0, "amount": 0},
            "unpaid": {"count": 0, "amount": 0},
        },
        "details": [],
    }

    for repair in repairs:
        total = flt(repair.get("total_cost", 0))
        deposit = flt(repair.get("deposit_amount", 0))
        balance = flt(repair.get("balance_due", 0))

        reconciliation["summary"]["total_repair_value"] += total
        reconciliation["summary"]["total_deposits"] += deposit
        reconciliation["summary"]["total_outstanding"] += balance

        # Get total paid
        paid = 0
        if repair["payment_status"] == "Paid":
            paid = total
            reconciliation["by_status"]["paid"]["count"] += 1
            reconciliation["by_status"]["paid"]["amount"] += total
        elif repair["payment_status"] == "Partial":
            paid = total - balance
            reconciliation["by_status"]["partial"]["count"] += 1
            reconciliation["by_status"]["partial"]["amount"] += paid
        else:
            reconciliation["by_status"]["unpaid"]["count"] += 1
            reconciliation["by_status"]["unpaid"]["amount"] += total

        reconciliation["summary"]["total_collected"] += paid

        # Track invoice coverage
        if repair.get("sales_invoice"):
            reconciliation["summary"]["invoice_coverage"] += total

        customer_name = frappe.db.get_value(
            "Customer", repair["customer"], "customer_name"
        ) if repair.get("customer") else ""

        reconciliation["details"].append({
            "repair_order": repair["name"],
            "customer": customer_name,
            "status": repair["status"],
            "received_date": str(repair.get("received_date", ""))[:10],
            "delivered_date": str(repair.get("delivered_date", ""))[:10],
            "total_cost": total,
            "deposit": deposit,
            "paid": paid,
            "balance_due": balance,
            "payment_status": repair["payment_status"],
            "invoice": repair.get("sales_invoice"),
        })

    return reconciliation


@frappe.whitelist()
def create_journal_entry_for_repair(repair_order: str) -> dict[str, Any]:
    """
    Create a journal entry for revenue recognition when repair is delivered.

    This debits the customer account and credits repair revenue.

    Args:
        repair_order: The repair order to recognize revenue for

    Returns:
        Journal entry creation result
    """
    if not frappe.has_permission("Repair Order", "write", doc=repair_order):
        frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

    doc = frappe.get_doc("Repair Order", repair_order)

    if doc.status != "Delivered":
        return {"success": False, "message": "Can only recognize revenue for delivered repairs"}

    if doc.total_cost <= 0:
        return {"success": False, "message": "No cost to recognize"}

    # Check if journal entry already exists
    existing_je = frappe.db.get_value("Journal Entry", {
        "reference_name": repair_order,
        "reference_type": "Repair Order",
        "docstatus": ["!=", 2]
    })

    if existing_je:
        return {"success": False, "message": f"Journal Entry already exists: {existing_je}"}

    company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
        "Global Defaults", "default_company"
    )

    if not company:
        return {"success": False, "message": "No company configured"}

    # Get accounting settings
    repair_revenue_account = frappe.db.get_value(
        "Repair Accounting Settings", None,
        "repair_revenue_account"
    ) or "Repair Revenue - {}".format(frappe.db.get_value("Company", company, "abbr"))

    receivable_account = frappe.db.get_value(
        "Account", {"account_type": "Receivable", "company": company}
    )

    if not receivable_account:
        return {"success": False, "message": "No receivable account found for company"}

    try:
        je = frappe.new_doc("Journal Entry")
        je.company = company
        je.posting_date = doc.delivered_date.split(" ")[0] if doc.delivered_date else nowdate()
        je.user_remark = f"Revenue recognition for repair order {repair_order}"
        je.reference_type = "Repair Order"
        je.reference_name = repair_order

        # Debit: Accounts Receivable (Customer)
        je.append("accounts", {
            "account": receivable_account,
            "party_type": "Customer",
            "party": doc.customer,
            "debit_in_account_currency": doc.total_cost,
            "credit_in_account_currency": 0,
            "reference_type": "Repair Order",
            "reference_name": repair_order,
        })

        # Credit: Repair Revenue
        je.append("accounts", {
            "account": repair_revenue_account,
            "debit_in_account_currency": 0,
            "credit_in_account_currency": doc.total_cost,
            "reference_type": "Repair Order",
            "reference_name": repair_order,
        })

        je.flags.ignore_permissions = True
        je.submit()

        # Link journal entry to repair order
        doc.db_set("journal_entry", je.name)

        return {
            "success": True,
            "message": f"Journal Entry {je.name} created successfully",
            "journal_entry": je.name,
        }

    except Exception as e:
        frappe.log_error(f"Journal Entry creation failed for {repair_order}: {e}")
        return {
            "success": False,
            "message": f"Failed to create Journal Entry: {e!s}"
        }


@frappe.whitelist()
def get_profitability_report(
    start_date: str,
    end_date: str,
    warehouse: str | None = None,
) -> dict[str, Any]:
    """
    Generate profitability report for repairs.

    Shows revenue, cost of materials, and gross margin.

    Args:
        start_date: Start date for reporting period
        end_date: End date for reporting period
        warehouse: Filter by warehouse/store

    Returns:
        Profitability report
    """
    if not frappe.has_permission("Repair Order", "read"):
        frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

    # Get delivered repairs
    filters = [
        ["delivered_date", "between", [start_date, end_date]],
        ["status", "=", "Delivered"]
    ]
    if warehouse:
        filters.append(["warehouse", "=", warehouse])

    repairs = frappe.get_all(
        "Repair Order",
        filters=filters,
        fields=[
            "name", "total_cost", "labor_cost", "material_cost",
            "warehouse", "repair_type"
        ]
    )

    report = {
        "period": {"start": start_date, "end": end_date},
        "warehouse": warehouse,
        "summary": {
            "total_revenue": 0,
            "total_labor_cost": 0,
            "total_material_cost": 0,
            "total_cost": 0,
            "gross_profit": 0,
            "gross_margin_pct": 0,
            "repair_count": len(repairs),
        },
        "by_repair_type": {},
        "by_warehouse": {},
    }

    for repair in repairs:
        revenue = flt(repair.get("total_cost", 0))
        labor = flt(repair.get("labor_cost", 0))
        material = flt(repair.get("material_cost", 0))
        labor + material  # Material cost is tracked, labor is pure profit

        # Labor is typically 100% margin (pure service)
        # Materials cost is what was tracked in parts
        report["summary"]["total_revenue"] += revenue
        report["summary"]["total_labor_cost"] += labor
        report["summary"]["total_material_cost"] += material
        report["summary"]["total_cost"] += material
        report["summary"]["gross_profit"] += (revenue - material)

        # Group by repair type
        rt = repair.get("repair_type") or "Other"
        if rt not in report["by_repair_type"]:
            report["by_repair_type"][rt] = {
                "count": 0,
                "revenue": 0,
                "material_cost": 0,
                "gross_profit": 0,
            }

        report["by_repair_type"][rt]["count"] += 1
        report["by_repair_type"][rt]["revenue"] += revenue
        report["by_repair_type"][rt]["material_cost"] += material
        report["by_repair_type"][rt]["gross_profit"] += (revenue - material)

        # Group by warehouse
        wh = repair.get("warehouse") or "Unspecified"
        if wh not in report["by_warehouse"]:
            report["by_warehouse"][wh] = {
                "count": 0,
                "revenue": 0,
                "material_cost": 0,
                "gross_profit": 0,
            }

        report["by_warehouse"][wh]["count"] += 1
        report["by_warehouse"][wh]["revenue"] += revenue
        report["by_warehouse"][wh]["material_cost"] += material
        report["by_warehouse"][wh]["gross_profit"] += (revenue - material)

    # Calculate margin
    if report["summary"]["total_revenue"] > 0:
        report["summary"]["gross_margin_pct"] = (
            report["summary"]["gross_profit"] / report["summary"]["total_revenue"] * 100
        )

    return report


@frappe.whitelist()
def process_commission_payment(
    technician: str,
    start_date: str,
    end_date: str,
    payment_method: str = "Bank Transfer",
) -> dict[str, Any]:
    """
    Process commission payment for a technician.

    Creates a payment entry based on calculated commissions.

    Args:
        technician: User ID of the technician
        start_date: Commission period start date
        end_date: Commission period end date
        payment_method: Method of payment

    Returns:
        Payment entry result
    """
    if not frappe.has_permission("Payment Entry", "create"):
        frappe.throw(_("Insufficient permissions to create payments"), frappe.PermissionError)

    # Calculate commission
    commissions = get_technician_commission(technician, start_date, end_date)

    if not commissions:
        return {"success": False, "message": "No commission found for period"}

    tech_commission = commissions[0]  # First result for this technician
    commission_amount = tech_commission["total_commission"]

    if commission_amount <= 0:
        return {"success": False, "message": f"No commission payable. Amount: {commission_amount}"}

    company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
        "Global Defaults", "default_company"
    )

    if not company:
        return {"success": False, "message": "No company configured"}

    # Get technician employee record
    employee = frappe.db.get_value("Employee", {"user_id": technician})
    if not employee:
        return {"success": False, "message": "No employee record found for technician"}

    try:
        from frappe.utils import nowdate

        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = "Pay"
        pe.company = company
        pe.party_type = "Employee"
        pe.party = employee
        pe.paid_amount = commission_amount
        pe.paid_to = frappe.db.get_value("Account", {
            "account_type": "Payable",
            "company": company
        })
        pe.payment_type = "Pay"
        pe.reference_no = f"Commission-{start_date}_to_{end_date}"
        pe.reference_date = nowdate()
        pe.remarks = f"Commission payment for {tech_commission['technician_name']} for period {start_date} to {end_date}"

        pe.flags.ignore_permissions = True
        pe.submit()

        return {
            "success": True,
            "message": f"Payment Entry {pe.name} created successfully",
            "payment_entry": pe.name,
            "amount": commission_amount,
        }

    except Exception as e:
        frappe.log_error(f"Commission payment failed for {technician}: {e}")
        return {
            "success": False,
            "message": f"Failed to create Payment Entry: {e!s}"
        }
