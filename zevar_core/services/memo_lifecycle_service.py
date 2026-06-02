"""Memo Contract lifecycle service.

Handles vendor memos (goods on approval from supplier) and
customer memos (goods on approval to customer) with aging
and disposition tracking.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_to_date, flt, now_datetime


def create_memo(
	memo_class: str,
	items: list[dict],
	customer: str | None = None,
	vendor: str | None = None,
	valid_until: str | None = None,
	notes: str | None = None,
) -> dict:
	"""Create a new memo contract.

	Items is a list of dicts: [{item_code, serial_no, qty, valuation_rate}]
	"""
	_validate_memo_class(memo_class, customer, vendor)

	memo = frappe.new_doc("Memo Contract")
	memo.memo_class = memo_class
	memo.customer = customer or ""
	memo.vendor = vendor or ""
	memo.valid_until = valid_until or add_to_date(now_datetime(), days=30)
	memo.notes = notes or ""

	for item in items:
		memo.append("items", {
			"item_code": item["item_code"],
			"serial_no": item.get("serial_no", ""),
			"qty": item.get("qty", 1),
			"valuation_rate": item.get("valuation_rate", 0),
			"line_status": "Open",
		})

	memo.insert(ignore_permissions=True)
	memo.submit()

	return {"success": True, "memo_contract": memo.name, "memo_class": memo_class}


def mark_item_sold(memo_contract: str, item_code: str, serial_no: str | None = None) -> dict:
	"""Mark a specific item on a memo as sold."""
	memo = frappe.get_doc("Memo Contract", memo_contract)

	for row in memo.items:
		if row.item_code == item_code and (not serial_no or row.serial_no == serial_no):
			if row.line_status != "Open":
				frappe.throw(_("Item {0} is already {1}").format(item_code, row.line_status))
			row.line_status = "Sold"
			break
	else:
		frappe.throw(_("Item {0} not found on memo {1}").format(item_code, memo_contract))

	memo.save(ignore_permissions=True)
	_check_memo_completion(memo)

	return {"success": True, "memo_contract": memo_contract, "item_code": item_code, "status": "Sold"}


def mark_item_returned(
	memo_contract: str,
	item_code: str,
	returned_by: str | None = None,
	serial_no: str | None = None,
	return_slip_ref: str | None = None,
) -> dict:
	"""Mark a specific item on a memo as returned."""
	memo = frappe.get_doc("Memo Contract", memo_contract)

	for row in memo.items:
		if row.item_code == item_code and (not serial_no or row.serial_no == serial_no):
			if row.line_status != "Open":
				frappe.throw(_("Item {0} is already {1}").format(item_code, row.line_status))
			row.line_status = "Returned"
			row.returned_at = now_datetime()
			row.returned_by = returned_by or frappe.session.user
			if return_slip_ref:
				row.return_slip_ref = return_slip_ref
			break
	else:
		frappe.throw(_("Item {0} not found on memo {1}").format(item_code, memo_contract))

	memo.save(ignore_permissions=True)
	_check_memo_completion(memo)

	return {"success": True, "memo_contract": memo_contract, "item_code": item_code, "status": "Returned"}


def get_aging_summary(memo_class: str | None = None) -> dict:
	"""Get aging buckets for open memo contracts."""
	filters = {"docstatus": 1, "final_disposition": "Open"}
	if memo_class:
		filters["memo_class"] = memo_class

	memos = frappe.get_all(
		"Memo Contract",
		filters=filters,
		fields=["name", "memo_class", "customer", "vendor", "valid_until", "creation"],
		order_by="creation asc",
	)

	buckets = {"0-7": [], "8-14": [], "15-30": [], "30+": []}
	now = now_datetime()

	for memo in memos:
		created = memo.creation
		if isinstance(created, str):
			from frappe.utils import get_datetime
			created = get_datetime(created)

		days_out = (now - created).days

		item_count = frappe.db.count("Memo Contract Item", {
			"parent": memo.name,
			"line_status": "Open",
		})

		entry = {
			"memo_contract": memo.name,
			"memo_class": memo.memo_class,
			"customer": memo.customer,
			"vendor": memo.vendor,
			"days_out": days_out,
			"open_items": item_count,
			"valid_until": str(memo.valid_until),
		}

		if days_out <= 7:
			buckets["0-7"].append(entry)
		elif days_out <= 14:
			buckets["8-14"].append(entry)
		elif days_out <= 30:
			buckets["15-30"].append(entry)
		else:
			buckets["30+"].append(entry)

	total = sum(len(v) for v in buckets.values())
	return {"buckets": buckets, "total_open": total}


def send_aging_alerts(days_threshold: int = 21) -> list[str]:
	"""Send alerts for memos exceeding the aging threshold. Called by scheduler."""
	from frappe.utils import add_days

	cutoff = add_days(now_datetime(), -days_threshold)
	alerts_sent = []

	open_memos = frappe.get_all(
		"Memo Contract",
		filters={
			"docstatus": 1,
			"final_disposition": "Open",
			"creation": ["<=", cutoff],
			"auto_aging_alert_sent_at": ["is", "not set"],
		},
		fields=["name", "memo_class", "customer", "vendor"],
	)

	for memo in open_memos:
		try:
			frappe.db.set_value("Memo Contract", memo.name, "auto_aging_alert_sent_at", now_datetime())
			frappe.log_error(
				f"Memo aging alert: {memo.name} ({memo.memo_class})",
				f"Customer: {memo.customer}, Vendor: {memo.vendor} — exceeds {days_threshold} days",
			)
			alerts_sent.append(memo.name)
		except Exception:
			frappe.log_error(f"Failed to send aging alert for memo {memo.name}", frappe.get_traceback())

	return alerts_sent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _validate_memo_class(memo_class: str, customer: str | None, vendor: str | None):
	if memo_class not in ("Vendor", "Customer"):
		frappe.throw(_("memo_class must be 'Vendor' or 'Customer'"))
	if memo_class == "Customer" and not customer:
		frappe.throw(_("Customer memo requires a customer"))
	if memo_class == "Vendor" and not vendor:
		frappe.throw(_("Vendor memo requires a vendor"))


def _check_memo_completion(memo):
	open_items = [i for i in memo.items if i.line_status == "Open"]
	if not open_items:
		memo.final_disposition = "Sold"
		memo.save(ignore_permissions=True)
