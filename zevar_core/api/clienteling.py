"""
Clienteling API - Full customer intelligence for POS CRM Modal and Drawer.
Includes: profile, purchases, loyalty, repairs, layaways, trade-ins, A/R, CRM pipeline, notes.
"""

import calendar

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import flt, getdate, nowdate

from zevar_core.api.customer import _check_pos_customer_role


@frappe.whitelist()
@rate_limit(limit=60, seconds=60)
def get_customer_intelligence(customer: str) -> dict:
	"""
	Full customer intelligence for the CRM modal.
	Returns: profile, purchases, loyalty, repairs, layaways, trade-ins, A/R, occasions, CRM, notes.
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

	# ==================== PROFILE ====================
	profile = {
		"name": customer_doc.name,
		"customer_name": customer_doc.customer_name,
		"mobile_no": customer_doc.mobile_no or "",
		"email_id": customer_doc.email_id or "",
		"customer_group": customer_doc.customer_group or "",
		"customer_type": customer_doc.customer_type or "",
		"customer_status": safe_get("custom_customer_status") or "Regular",
		"birth_date": safe_get("custom_birthday"),
		"marriage_date": safe_get("custom_anniversary"),
		"spouse_name": safe_get("custom_spouse_name"),
		"gender": safe_get("gender"),
		"ring_size": safe_get("custom_ring_size"),
		"ring_left_size": safe_get("custom_ring_left_size") or safe_get("custom_ring_size"),
		"ring_right_size": safe_get("custom_ring_right_size") or safe_get("custom_ring_size"),
		"wrist_size": safe_get("custom_wrist_size"),
		"neck_size": safe_get("custom_neck_size"),
		"preferred_metal": safe_get("custom_preferred_metal"),
		"preferred_purity": safe_get("custom_preferred_purity"),
		"jewelry_preferences": safe_get("custom_jewelry_preferences"),
		"lifetime_value": flt(safe_get("custom_lifetime_spend")),
		"ytd_spend": flt(safe_get("custom_ytd_spend")),
		"discount_rate": flt(safe_get("custom_discount_rate")),
		"customer_code": safe_get("custom_custcode"),
		"salesman1": safe_get("custom_salesman1"),
		"salesman2": safe_get("custom_salesman2"),
		"title": safe_get("custom_title"),
		"phone2": safe_get("custom_phone2"),
		"comments": safe_get("custom_comments"),
		"tags": safe_get("_user_tags"),
		"customer_since": str(customer_doc.creation.date()) if customer_doc.creation else "",
	}

	# ==================== PURCHASE HISTORY ====================
	invoices = frappe.get_all(
		"Sales Invoice",
		filters={"customer": customer, "docstatus": ["<", 2], "is_return": 0},
		fields=["name", "posting_date", "grand_total", "status", "outstanding_amount", "is_pos"],
		order_by="posting_date desc",
	)

	total_spent = sum(inv.grand_total for inv in invoices)
	visit_count = len(invoices)
	avg_order = total_spent / visit_count if visit_count else 0

	profile["total_spent"] = total_spent
	profile["visit_count"] = visit_count
	profile["avg_order_value"] = round(avg_order, 2)
	profile["first_purchase_date"] = str(invoices[-1].posting_date) if invoices else None
	profile["last_purchase_date"] = str(invoices[0].posting_date) if invoices else None
	profile["days_since_last_visit"] = (
		(getdate(nowdate()) - getdate(invoices[0].posting_date)).days if invoices else None
	)
	if not profile["lifetime_value"]:
		profile["lifetime_value"] = total_spent

	recent = invoices[:20]
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
		status = inv.status or ("Paid" if (inv.outstanding_amount or 0) == 0 else "Unpaid")
		recent_purchases.append({
			"invoice": inv.name,
			"date": str(inv.posting_date),
			"items": item_map.get(inv.name, []),
			"grand_total": inv.grand_total,
			"status": status,
			"is_pos": inv.is_pos,
		})

	# ==================== LOYALTY POINTS ====================
	loyalty = {"program": "", "points": 0, "history": []}
	try:
		loyalty_entries = frappe.get_all(
			"Loyalty Point Entry",
			filters={"customer": customer},
			fields=["name", "loyalty_program", "loyalty_points", "posting_date", "invoice", "expiry_date"],
			order_by="posting_date desc",
			limit=20,
		)
		if loyalty_entries:
			total_points = 0
			for le in frappe.get_all("Loyalty Point Entry", filters={"customer": customer}, fields=["loyalty_points"]):
				total_points += le.loyalty_points
			# Subtract redemptions
			redemptions = frappe.get_all(
				"Loyalty Point Entry Redemption",
				filters={"customer": customer},
				fields=["loyalty_points"],
			)
			for r in redemptions:
				total_points -= r.loyalty_points

			loyalty["points"] = total_points
			loyalty["program"] = loyalty_entries[0].loyalty_program or ""
			loyalty["history"] = [
				{
					"date": str(le.posting_date),
					"points": le.loyalty_points,
					"invoice": le.invoice or "",
					"program": le.loyalty_program or "",
				}
				for le in loyalty_entries[:10]
			]
	except Exception:
		pass

	# ==================== REPAIRS ====================
	repairs = []
	try:
		repair_docs = frappe.get_all(
			"Repair Order",
			filters={"customer": customer},
			fields=["name", "status", "creation", "total_cost", "item_description", "serial_number", "item_type", "item_brand"],
			order_by="creation desc",
			limit=20,
		)
		repairs = [
			{
				"name": r.name,
				"status": r.status,
				"date": str(r.creation.date()) if r.creation else "",
				"cost": flt(r.total_cost),
				"description": r.item_description or "",
				"item": r.item_type or r.item_brand or r.serial_number or "",
			}
			for r in repair_docs
		]
	except Exception:
		pass

	# ==================== LAYAWAYS ====================
	layaways = []
	try:
		layaway_docs = frappe.get_all(
			"Layaway Contract",
			filters={"customer": customer},
			fields=["name", "status", "creation", "total_amount", "total_paid", "balance_amount"],
			order_by="creation desc",
			limit=20,
		)
		layaways = [
			{
				"name": l.name,
				"status": l.status,
				"date": str(l.creation.date()) if l.creation else "",
				"total": flt(l.total_amount),
				"paid": flt(l.total_paid),
				"balance": flt(l.balance_amount),
			}
			for l in layaway_docs
		]
	except Exception:
		pass

	# ==================== TRADE-INS ====================
	trade_ins = []
	try:
		# Trade In Record is a child table linked to Sales Invoice
		# Find trade-ins via Sales Invoice items with trade-in reference
		trade_invoices = frappe.get_all(
			"Sales Invoice",
			filters={"customer": customer, "docstatus": 1},
			fields=["name"],
			limit=50,
		)
		if trade_invoices:
			inv_names = [i.name for i in trade_invoices]
			trade_docs = frappe.get_all(
				"Trade In Record",
				filters={"parent": ["in", inv_names], "parenttype": "Sales Invoice"},
				fields=["name", "creation", "trade_in_value", "original_item_code", "new_item_code", "upgrade_validation"],
				order_by="creation desc",
				limit=10,
			)
			trade_ins = [
				{
					"name": t.name,
					"status": t.upgrade_validation or "Pending",
					"date": str(t.creation.date()) if t.creation else "",
					"value": flt(t.trade_in_value),
					"description": t.original_item_code or "",
				}
				for t in trade_docs
			]
	except Exception:
		pass

	# ==================== A/R BALANCE ====================
	ar_balance = {"total_outstanding": 0, "entries": []}
	try:
		outstanding_invoices = frappe.get_all(
			"Sales Invoice",
			filters={"customer": customer, "docstatus": 1, "outstanding_amount": [">", 0]},
			fields=["name", "posting_date", "grand_total", "outstanding_amount"],
			order_by="posting_date desc",
			limit=10,
		)
		ar_balance["total_outstanding"] = sum(inv.outstanding_amount for inv in outstanding_invoices)
		ar_balance["entries"] = [
			{
				"invoice": inv.name,
				"date": str(inv.posting_date),
				"total": inv.grand_total,
				"outstanding": inv.outstanding_amount,
			}
			for inv in outstanding_invoices
		]
	except Exception:
		pass

	# ==================== OCCASIONS ====================
	today = getdate(nowdate())
	occasions = []
	for field, label_type in [("custom_birthday", "birthday"), ("custom_anniversary", "anniversary")]:
		date_val = safe_get(field)
		if not date_val:
			continue
		try:
			event_date = getdate(date_val) if isinstance(date_val, str) else getdate(date_val)
		except Exception:
			continue
		month, day = event_date.month, event_date.day
		max_day = calendar.monthrange(today.year, month)[1]
		day = min(day, max_day)
		try:
			upcoming = getdate(f"{today.year}-{month:02d}-{day:02d}")
		except Exception:
			continue
		if upcoming < today:
			try:
				next_yr = today.year + 1
				next_day = min(day, calendar.monthrange(next_yr, month)[1])
				upcoming = getdate(f"{next_yr}-{month:02d}-{next_day:02d}")
			except Exception:
				continue
		days_until = (upcoming - today).days
		if days_until <= 60:
			occasions.append({
				"type": label_type,
				"date": str(upcoming),
				"days_until": days_until,
				"original_date": str(event_date),
			})

	# ==================== CRM PIPELINE ====================
	pipeline = _get_crm_pipeline(customer, customer_doc, safe_get)

	# ==================== NOTES ====================
	notes = safe_get("custom_internal_notes")

	return {
		"profile": profile,
		"recent_purchases": recent_purchases,
		"loyalty": loyalty,
		"repairs": repairs,
		"layaways": layaways,
		"trade_ins": trade_ins,
		"ar_balance": ar_balance,
		"upcoming_occasions": occasions,
		"notes": notes,
		"pipeline": pipeline,
	}


def _get_crm_pipeline(customer_name, customer_doc, safe_get):
	"""Build CRM pipeline data for a customer."""
	pipeline = {"lead": None, "deal": None, "tasks": []}
	if "crm" not in frappe.get_installed_apps():
		return pipeline

	crm_lead = None
	try:
		crm_lead = customer_doc.get("custom_crm_lead")
	except Exception:
		pass
	if crm_lead:
		try:
			lead = frappe.get_doc("CRM Lead", crm_lead)
			pipeline["lead"] = {
				"name": lead.name, "status": lead.status,
				"source": lead.source or "", "lead_owner": lead.lead_owner or "",
				"created_on": str(lead.creation),
			}
		except Exception:
			pass

	crm_deal = None
	try:
		crm_deal = customer_doc.get("custom_crm_deal")
	except Exception:
		pass
	if crm_deal:
		try:
			deal = frappe.get_doc("CRM Deal", crm_deal)
			pipeline["deal"] = {
				"name": deal.name, "status": deal.status,
				"deal_value": deal.deal_value or 0, "probability": deal.probability or 0,
				"next_step": deal.next_step or "",
				"expected_closure_date": str(deal.expected_closure_date) if deal.expected_closure_date else "",
				"deal_owner": deal.deal_owner or "",
			}
		except Exception:
			pass

	try:
		tasks = frappe.get_all(
			"CRM Task",
			filters={"reference_doctype": "Customer", "reference_docname": customer_name,
					 "status": ["not in", ["Done", "Canceled"]]},
			fields=["name", "title", "due_date", "status", "priority"],
			order_by="due_date asc", limit=5,
		)
		pipeline["tasks"] = [
			{"name": t.name, "title": t.title, "due_date": str(t.due_date) if t.due_date else "",
			 "status": t.status, "priority": t.priority}
			for t in tasks
		]
	except Exception:
		pass
	return pipeline


@frappe.whitelist()
def create_crm_task_from_pos(customer: str, title: str, due_date: str = None, description: str = None) -> dict:
	if "crm" not in frappe.get_installed_apps():
		frappe.throw(_("CRM app is not installed."))
	if not customer or not frappe.db.exists("Customer", customer):
		frappe.throw(_("Customer '{0}' not found.").format(customer))
	if not title or not title.strip():
		frappe.throw(_("Task title is required."))
	task = frappe.get_doc({
		"doctype": "CRM Task", "title": title.strip(), "status": "Todo", "priority": "Medium",
		"due_date": due_date, "description": description or "",
		"assigned_to": frappe.session.user,
		"reference_doctype": "Customer", "reference_docname": customer,
	})
	task.insert(ignore_permissions=True)
	return {"success": True, "task": task.name}


@frappe.whitelist(methods=["POST"])
@rate_limit(limit=30, seconds=60)
def add_customer_note(customer: str, note: str) -> dict:
	_check_pos_customer_role()
	if not customer or not frappe.db.exists("Customer", customer):
		frappe.throw(_("Customer '{0}' not found.").format(customer))
	if not note or not note.strip():
		frappe.throw(_("Note text is required."))
	customer_doc = frappe.get_doc("Customer", customer)
	customer_meta = frappe.get_meta("Customer")
	if not customer_meta.has_field("custom_internal_notes"):
		frappe.throw(_("Internal notes field is not configured."))
	user_fullname = frappe.get_value("User", frappe.session.user, "full_name") or frappe.session.user
	timestamp = getdate(nowdate()).strftime("%Y-%m-%d")
	new_entry = f"[{timestamp} by {user_fullname}] {note.strip()}\n"
	existing = customer_doc.custom_internal_notes or ""
	customer_doc.custom_internal_notes = new_entry + existing
	customer_doc.save()
	return {"success": True, "notes": customer_doc.custom_internal_notes}
