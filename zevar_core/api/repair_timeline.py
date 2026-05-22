"""
Repair Timeline API — Status history, predictive ETA, and technician workload
"""

from typing import Any

import frappe
from frappe import _
from frappe.utils import (
    add_days,
    cint,
    date_diff,
    flt,
    getdate,
    now,
    nowdate,
    today,
)


# ──────────────────────────────────────────────────
# 1. Status Timeline
# ──────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_repair_timeline(repair_order: str) -> list[dict[str, Any]]:
    """Return the ordered status change history for a repair order.

    Each entry has: status, timestamp, user, user_name, notes.
    Falls back to creation/modification dates if no explicit log exists.
    """
    frappe.has_permission("Repair Order", ptype="read", doc=repair_order, throw=True)

    # Try the explicit status log first (new child table)
    logs = frappe.get_all(
        "Repair Status Log",
        filters={"parent": repair_order, "parenttype": "Repair Order"},
        fields=["status", "timestamp", "changed_by", "notes"],
        order_by="timestamp asc",
    )

    if logs:
        for log in logs:
            if log.get("changed_by"):
                log["user"] = log["changed_by"]
                log["user_name"] = frappe.db.get_value("User", log["changed_by"], "full_name") or log["changed_by"]
            else:
                log["user"] = ""
                log["user_name"] = ""
        return logs

    # Fallback: parse communications audit trail
    doc = frappe.get_doc("Repair Order", repair_order)
    timeline: list[dict[str, Any]] = []

    # Always include "Received" as the first event
    timeline.append(
        {
            "status": "Received",
            "timestamp": str(doc.received_date or doc.creation),
            "user": doc.handled_by or doc.owner,
            "user_name": _get_user_name(doc.handled_by or doc.owner),
            "notes": "",
        }
    )

    # Parse audit entries from communications child table
    for comm in doc.communications or []:
        if comm.communication_type == "Audit" and "status changed" in (comm.content or "").lower():
            # Extract new status from message like "Status changed from 'X' to 'Y'"
            content = comm.content or ""
            new_status = _extract_status_from_audit(content)
            if new_status and new_status != "Received":
                timeline.append(
                    {
                        "status": new_status,
                        "timestamp": str(comm.timestamp or comm.creation),
                        "user": comm.user or "",
                        "user_name": _get_user_name(comm.user) if comm.user else "",
                        "notes": "",
                    }
                )

    # If current status isn't in timeline, add it
    current = doc.status
    if current and not any(t["status"] == current for t in timeline):
        timeline.append(
            {
                "status": current,
                "timestamp": str(doc.modified),
                "user": doc.modified_by or "",
                "user_name": _get_user_name(doc.modified_by) if doc.modified_by else "",
                "notes": "",
            }
        )

    return timeline


def _extract_status_from_audit(content: str) -> str:
    """Extract the target status from an audit message."""
    import re

    match = re.search(r"to '([^']+)'", content)
    if match:
        return match.group(1)
    return ""


def _get_user_name(user: str) -> str:
    """Get full name for a user, with caching."""
    if not user:
        return ""
    return frappe.db.get_value("User", user, "full_name") or user


@frappe.whitelist(allow_guest=False)
def log_status_change(
    repair_order: str,
    new_status: str,
    notes: str | None = None,
) -> dict[str, Any]:
    """Explicitly log a status change event (called from update_repair_status)."""
    frappe.has_permission("Repair Order", ptype="write", doc=repair_order, throw=True)

    doc = frappe.get_doc("Repair Order", repair_order)
    doc.append(
        "status_log",
        {
            "status": new_status,
            "timestamp": now(),
            "changed_by": frappe.session.user,
            "notes": notes or "",
        },
    )
    doc.save(ignore_permissions=True)
    return {"success": True}


# ──────────────────────────────────────────────────
# 2. Predictive ETA Engine
# ──────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def predict_repair_eta(repair_order: str) -> dict[str, Any]:
    """Calculate a predicted completion date based on historical data.

    Uses:
    - Average turnaround for this repair type
    - Current status position in the workflow
    - Priority multiplier
    - Technician's historical performance
    """
    frappe.has_permission("Repair Order", ptype="read", doc=repair_order, throw=True)

    doc = frappe.get_doc("Repair Order", repair_order)

    # If already delivered, return actual date
    if doc.status == "Delivered":
        return {
            "predicted_date": str(doc.delivered_date) if doc.delivered_date else str(doc.completed_date or ""),
            "confidence": "high",
            "days_remaining": 0,
            "method": "actual",
        }

    # If already has a promised date, use that as base
    if doc.promised_date:
        days_remaining = max(0, date_diff(doc.promised_date, today()))
        return {
            "predicted_date": str(doc.promised_date),
            "confidence": "high",
            "days_remaining": days_remaining,
            "method": "promised",
        }

    # Calculate from historical data
    repair_type = doc.repair_type
    priority = doc.priority or "Medium"

    # 1. Get average turnaround for this repair type (completed repairs)
    avg_days = _get_avg_turnaround(repair_type)

    # 2. Priority multiplier
    priority_multipliers = {
        "Low": 1.3,
        "Medium": 1.0,
        "High": 0.7,
        "Urgent": 0.4,
    }
    multiplier = priority_multipliers.get(priority, 1.0)

    # 3. Status progress — reduce remaining days based on progress
    status_progress = {
        "Received": 0.0,
        "Estimated": 0.1,
        "Approved": 0.15,
        "In Progress": 0.4,
        "Waiting for Parts": 0.5,
        "Quality Check": 0.85,
        "Ready for Pickup": 0.95,
    }
    progress = status_progress.get(doc.status, 0.0)

    # 4. Technician factor
    tech_factor = 1.0
    if doc.assigned_to:
        tech_avg = _get_technician_avg_days(doc.assigned_to, repair_type)
        if tech_avg and avg_days:
            tech_factor = tech_avg / avg_days if avg_days > 0 else 1.0
            tech_factor = max(0.5, min(tech_factor, 2.0))  # Clamp

    # Calculate estimated remaining days
    base_days = avg_days * multiplier * tech_factor
    remaining_days = max(1, int(base_days * (1.0 - progress)))

    received_date = getdate(doc.received_date or doc.creation)
    predicted_date = add_days(today(), remaining_days)

    # Confidence level
    sample_size = _get_sample_size(repair_type)
    if sample_size >= 20:
        confidence = "high"
    elif sample_size >= 5:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "predicted_date": str(predicted_date),
        "confidence": confidence,
        "days_remaining": remaining_days,
        "avg_turnaround": round(avg_days, 1),
        "sample_size": sample_size,
        "method": "predicted",
    }


def _get_avg_turnaround(repair_type: str | None) -> float:
    """Get average turnaround days for a repair type from completed repairs."""
    filters = {"status": "Delivered", "delivered_date": ["is", "set"], "received_date": ["is", "set"]}
    if repair_type:
        filters["repair_type"] = repair_type

    completed = frappe.get_all(
        "Repair Order",
        filters=filters,
        fields=["received_date", "delivered_date"],
        limit=100,
        order_by="delivered_date desc",
    )

    if not completed:
        # Fallback: try repair type estimated_days
        if repair_type:
            est_days = frappe.db.get_value("Repair Type", repair_type, "estimated_days")
            if est_days:
                return flt(est_days)
        return 5.0  # Default fallback

    total_days = 0
    count = 0
    for r in completed:
        if r.received_date and r.delivered_date:
            days = date_diff(r.delivered_date, r.received_date)
            if days >= 0:
                total_days += days
                count += 1

    return (total_days / count) if count > 0 else 5.0


def _get_technician_avg_days(user: str, repair_type: str | None = None) -> float | None:
    """Get a technician's average turnaround for a specific repair type."""
    filters = {
        "status": "Delivered",
        "assigned_to": user,
        "delivered_date": ["is", "set"],
        "received_date": ["is", "set"],
    }
    if repair_type:
        filters["repair_type"] = repair_type

    completed = frappe.get_all(
        "Repair Order",
        filters=filters,
        fields=["received_date", "delivered_date"],
        limit=50,
    )

    if len(completed) < 3:
        return None

    total_days = 0
    count = 0
    for r in completed:
        if r.received_date and r.delivered_date:
            days = date_diff(r.delivered_date, r.received_date)
            if days >= 0:
                total_days += days
                count += 1

    return (total_days / count) if count > 0 else None


def _get_sample_size(repair_type: str | None) -> int:
    """Get the number of completed repairs for confidence scoring."""
    filters = {"status": "Delivered"}
    if repair_type:
        filters["repair_type"] = repair_type
    return cint(frappe.db.count("Repair Order", filters=filters))


# ──────────────────────────────────────────────────
# 3. Technician Workload
# ──────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_technician_workload() -> list[dict[str, Any]]:
    """Get workload statistics for all technicians with active repairs.

    Returns per-technician: active jobs, capacity, avg turnaround,
    jobs by status, revenue generated.
    """
    frappe.has_permission("Repair Order", ptype="read", throw=True)

    # Get all users who have been assigned repairs
    active_statuses = ["Received", "Estimated", "Approved", "In Progress", "Waiting for Parts", "Quality Check"]

    assigned_users = frappe.db.sql(
        """
        SELECT DISTINCT assigned_to
        FROM `tabRepair Order`
        WHERE assigned_to IS NOT NULL
          AND assigned_to != ''
          AND status IN %(statuses)s
        """,
        {"statuses": active_statuses},
        as_dict=True,
    )

    technicians: list[dict[str, Any]] = []

    for row in assigned_users:
        user = row.assigned_to
        user_name = frappe.db.get_value("User", user, "full_name") or user

        # Active jobs by status
        status_counts = {}
        total_active = 0
        for status in active_statuses:
            count = frappe.db.count(
                "Repair Order",
                filters={"assigned_to": user, "status": status},
            )
            status_counts[status] = count
            total_active += count

        # Completed this month
        first_of_month = getdate(today()).replace(day=1)
        completed_this_month = frappe.db.count(
            "Repair Order",
            filters={
                "assigned_to": user,
                "status": "Delivered",
                "delivered_date": [">=", str(first_of_month)],
            },
        )

        # Revenue this month
        revenue_data = frappe.db.sql(
            """
            SELECT COALESCE(SUM(total_cost), 0) as revenue
            FROM `tabRepair Order`
            WHERE assigned_to = %(user)s
              AND status = 'Delivered'
              AND delivered_date >= %(first_of_month)s
            """,
            {"user": user, "first_of_month": str(first_of_month)},
            as_dict=True,
        )
        revenue = flt(revenue_data[0].revenue) if revenue_data else 0

        # Average turnaround (last 30 days)
        avg_turn = _get_technician_avg_days(user) or 0

        technicians.append(
            {
                "user": user,
                "user_name": user_name,
                "active_jobs": total_active,
                "status_breakdown": status_counts,
                "completed_this_month": completed_this_month,
                "revenue_this_month": revenue,
                "avg_turnaround_days": round(avg_turn, 1),
            }
        )

    # Sort by active jobs descending
    technicians.sort(key=lambda t: t["active_jobs"], reverse=True)

    return technicians


@frappe.whitelist(allow_guest=False)
def suggest_technician(
    repair_type: str | None = None,
    warehouse: str | None = None,
    priority: str = "Medium",
) -> dict[str, Any]:
    """Suggest the best technician for a new repair based on workload and skill.

    Scoring algorithm:
    - Lower active workload = higher score
    - Faster avg turnaround for this type = higher score
    - More experience with this type = higher score
    """
    frappe.has_permission("Repair Order", ptype="read", throw=True)

    # Get all potential technicians (users with repair permissions)
    active_statuses = ["Received", "Estimated", "Approved", "In Progress", "Waiting for Parts", "Quality Check"]

    # Get users who have been assigned repairs (known technicians)
    known_techs = frappe.db.sql(
        """
        SELECT DISTINCT assigned_to as user
        FROM `tabRepair Order`
        WHERE assigned_to IS NOT NULL AND assigned_to != ''
        """,
        as_dict=True,
    )

    if not known_techs:
        return {"suggestion": None, "message": "No technicians found"}

    scored: list[dict[str, Any]] = []

    for tech in known_techs:
        user = tech.user

        # 1. Current workload (lower is better)
        active_count = frappe.db.count(
            "Repair Order",
            filters={"assigned_to": user, "status": ["in", active_statuses]},
        )

        # 2. Experience with this repair type
        type_experience = 0
        if repair_type:
            type_experience = frappe.db.count(
                "Repair Order",
                filters={"assigned_to": user, "repair_type": repair_type, "status": "Delivered"},
            )

        # 3. Average turnaround
        avg_days = _get_technician_avg_days(user, repair_type) or 10

        # Calculate score (higher is better)
        workload_score = max(0, 20 - active_count * 3)  # 0-20 points
        experience_score = min(type_experience * 2, 20)  # 0-20 points
        speed_score = max(0, 20 - avg_days * 2)  # 0-20 points

        total_score = workload_score + experience_score + speed_score

        scored.append(
            {
                "user": user,
                "user_name": frappe.db.get_value("User", user, "full_name") or user,
                "score": round(total_score, 1),
                "active_jobs": active_count,
                "type_experience": type_experience,
                "avg_days": round(avg_days, 1),
            }
        )

    scored.sort(key=lambda x: x["score"], reverse=True)

    return {
        "suggestion": scored[0] if scored else None,
        "alternatives": scored[1:4],
        "total_technicians": len(scored),
    }
