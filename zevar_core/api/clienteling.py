"""
Clienteling API - Customer intelligence, purchase history, and occasion tracking.
Provides data for the POS Clienteling Drawer.
"""

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import getdate, nowdate

from zevar_core.api.customer import _check_pos_customer_role


@frappe.whitelist()
@rate_limit(limit=60, seconds=60)
def get_customer_intelligence(customer: str) -> dict:
	"""
	Fetch aggregated customer intelligence for the clienteling drawer.
	Returns profile stats, recent purchases, upcoming occasions, and notes.
	"""
	_check_pos_customer_role()

	if not customer or not frappe.db.exists("Customer", customer):
		frappe.throw(_("Customer '{0}' not found.").format(customer))

	customer_doc = frappe.get_doc("Customer", customer)
	customer_meta = frappe.get_meta("Customer")

	def safe_get(field, default=""):
		if not customer_meta.has_field(field):
			return default
		return customer_doc.get(field) or default

	# --- Profile ---
	profile = {
		"name": customer_doc.name,
		"customer_name": customer_doc.customer_name,
		"mobile_no": customer_doc.mobile_no or "",
		"email_id": customer_doc.email_id or "",
		"customer_group": customer_doc.customer_group or "",
		"birth_date": safe_get("custom_birth_date"),
		"marriage_date": safe_get("custom_marriage_date"),
		"partner_name": safe_get("custom_partner_name"),
		"gender": safe_get("gender"),
		"ring_size": safe_get("custom_ring_size"),
		"ring_left_size": safe_get("custom_ring_left_size"),
		"ring_right_size": safe_get("custom_ring_right_size"),
		"wrist_size": safe_get("custom_wrist_size"),
		"neck_size": safe_get("custom_neck_size"),
		"preferred_metal": safe_get("custom_preferred_metal"),
		"preferred_purity": safe_get("custom_preferred_purity"),
		"tags": safe_get("_user_tags"),
	}

	# --- Purchase Stats ---
	invoices = frappe.get_all(
		"Sales Invoice",
		filters={"customer": customer, "docstatus": 1, "is_return": 0},
		fields=["name", "posting_date", "grand_total"],
		order_by="posting_date desc",
	)

	total_spent = sum(inv.grand_total for inv in invoices)
	visit_count = len(invoices)
	avg_order = total_spent / visit_count if visit_count else 0

	profile["total_spent"] = total_spent
	profile["visit_count"] = visit_count
	profile["avg_order_value"] = avg_order
	profile["first_purchase_date"] = str(invoices[-1].posting_date) if invoices else None
	profile["last_purchase_date"] = str(invoices[0].posting_date) if invoices else None
	profile["days_since_last_visit"] = (
		(getdate(nowdate()) - getdate(invoices[0].posting_date)).days if invoices else None
	)

	# --- Recent Purchases (limit 10) ---
	recent = invoices[:10]
	recent_invoice_names = [inv.name for inv in recent]

	item_map = {}
	if recent_invoice_names:
		items = frappe.get_all(
			"Sales Invoice Item",
			filters={"parent": ["in", recent_invoice_names]},
			fields=["parent", "item_name", "qty", "amount"],
		)
		for item in items:
			item_map.setdefault(item.parent, []).append({
				"item_name": item.item_name,
				"amount": item.amount,
				"qty": item.qty,
			})

	recent_purchases = []
	for inv in recent:
		recent_purchases.append({
			"invoice": inv.name,
			"date": str(inv.posting_date),
			"items": item_map.get(inv.name, []),
			"grand_total": inv.grand_total,
			"status": "Paid",
		})

	# --- Upcoming Occasions (within 60 days) ---
	today = getdate(nowdate())
	occasions = []
	for field, label_type in [("custom_birth_date", "birthday"), ("custom_marriage_date", "anniversary")]:
		date_val = safe_get(field)
		if date_val:
			d = getdate(date_val)
			next_occ = d.replace(year=today.year)
			if next_occ < today:
				next_occ = d.replace(year=today.year + 1)
			days_until = (next_occ - today).days
			if days_until <= 60:
				occasions.append({
					"type": label_type,
					"date": str(next_occ),
					"days_until": days_until,
					"label": f"{label_type.title()} in {days_until} days",
				})

	# --- Notes ---
	notes = safe_get("custom_internal_notes")

	return {
		"profile": profile,
		"recent_purchases": recent_purchases,
		"upcoming_occasions": occasions,
		"notes": notes,
	}


@frappe.whitelist(methods=["POST"])
@rate_limit(limit=30, seconds=60)
def add_customer_note(customer: str, note: str) -> dict:
	"""Append a timestamped note to the customer's internal notes."""
	_check_pos_customer_role()

	if not customer or not frappe.db.exists("Customer", customer):
		frappe.throw(_("Customer '{0}' not found.").format(customer))

	if not note or not note.strip():
		frappe.throw(_("Note text is required."))

	customer_doc = frappe.get_doc("Customer", customer)
	customer_meta = frappe.get_meta("Customer")

	if not customer_meta.has_field("custom_internal_notes"):
		frappe.throw(_("Internal notes field is not configured on Customer DocType."))

	user_fullname = frappe.get_value("User", frappe.session.user, "full_name") or frappe.session.user
	timestamp = getdate(nowdate()).strftime("%Y-%m-%d")
	new_entry = f"[{timestamp} by {user_fullname}] {note.strip()}\n"

	existing = customer_doc.custom_internal_notes or ""
	customer_doc.custom_internal_notes = new_entry + existing
	customer_doc.save()

	return {"success": True, "notes": customer_doc.custom_internal_notes}
