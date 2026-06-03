import frappe
from frappe.utils import cint, cstr, flt, now, today

# ─── ACCOUNTING TRANSACTIONS (Payment Entry + Journal Entry) ──────────────────


@frappe.whitelist(allow_guest=False)
def get_transactions(
	doctype=None, from_date=None, to_date=None, party=None, account=None, page=1, page_size=20
):
	frappe.has_permission("Payment Entry", ptype="read", throw=True)

	page = max(1, cint(page))
	page_size = min(100, max(1, cint(page_size)))
	limit_start = (page - 1) * page_size

	results = []
	total = 0

	if not doctype or doctype == "Payment Entry":
		pe_filters = {"docstatus": ["!=", 2]}
		if from_date:
			pe_filters["posting_date"] = [">=", from_date]
		if to_date:
			pe_filters.setdefault("posting_date", ["<=", to_date])
		if party:
			pe_filters["party"] = party
		if account:
			pe_filters["paid_from"] = ["like", f"%{account}%"]

		pe_list = frappe.get_all(
			"Payment Entry",
			filters=pe_filters,
			fields=[
				"name",
				"posting_date",
				"payment_type",
				"party",
				"party_name",
				"paid_amount",
				"received_amount",
				"mode_of_payment",
				"reference_no",
				"reference_date",
				"status",
				"docstatus",
			],
			order_by="posting_date desc, creation desc",
			limit_start=limit_start if not doctype else 0,
			limit=page_size if not doctype else 999,
		)
		for pe in pe_list:
			pe["doctype"] = "Payment Entry"
			results.append(pe)

	if not doctype or doctype == "Journal Entry":
		je_filters = {"docstatus": ["!=", 2]}
		if from_date:
			je_filters["posting_date"] = [">=", from_date]
		if to_date:
			je_filters.setdefault("posting_date", ["<=", to_date])

		je_fields = [
			"name",
			"posting_date",
			"voucher_type",
			"total_debit",
			"total_credit",
			"user_remark",
			"docstatus",
			"cheque_no",
		]
		if frappe.get_meta("Journal Entry").has_field("cheque_date"):
			je_fields.append("cheque_date")
		elif frappe.get_meta("Journal Entry").has_field("reference_date"):
			je_fields.append("reference_date")

		je_list = frappe.get_all(
			"Journal Entry",
			filters=je_filters,
			fields=je_fields,
			order_by="posting_date desc, creation desc",
			limit_start=limit_start if not doctype else 0,
			limit=page_size if not doctype else 999,
		)
		for je in je_list:
			je["doctype"] = "Journal Entry"
			je["party"] = ""
			je["party_name"] = ""
			je["paid_amount"] = je.get("total_debit", 0)
			je["mode_of_payment"] = je.get("voucher_type", "")
			je["reference_date"] = je.get("cheque_date") or je.get("reference_date")
			results.append(je)

	results.sort(key=lambda x: x.get("posting_date", ""), reverse=True)
	total = len(results)
	results = results[limit_start : limit_start + page_size]

	return {"success": True, "transactions": results, "total": total, "page": page, "page_size": page_size}


@frappe.whitelist(allow_guest=False)
def get_transaction_detail(doctype, name):
	doctype = cstr(doctype).strip()
	name = cstr(name).strip()
	frappe.has_permission(doctype, ptype="read", throw=True)

	if not frappe.db.exists(doctype, name):
		frappe.throw(f"{doctype} not found")

	doc = frappe.get_doc(doctype, name)
	return {"success": True, "transaction": doc.as_dict()}


@frappe.whitelist(allow_guest=False)
def create_payment_entry(
	payment_type,
	party,
	paid_amount,
	mode_of_payment,
	paid_from=None,
	paid_to=None,
	reference_no=None,
	reference_date=None,
):
	frappe.has_permission("Payment Entry", ptype="create", throw=True)

	payment_type = cstr(payment_type).strip()
	if payment_type not in ("Receive", "Pay", "Internal Transfer"):
		frappe.throw("Invalid payment type")

	paid_amount = flt(paid_amount)
	if paid_amount <= 0:
		frappe.throw("Amount must be greater than zero")

	pe = frappe.new_doc("Payment Entry")
	pe.payment_type = payment_type
	pe.posting_date = today()
	pe.mode_of_payment = cstr(mode_of_payment).strip()
	pe.party_type = "Customer" if payment_type == "Receive" else "Supplier"
	pe.party = cstr(party).strip()
	pe.paid_amount = paid_amount
	pe.received_amount = paid_amount
	if paid_from:
		pe.paid_from = paid_from
	if paid_to:
		pe.paid_to = paid_to
	if reference_no:
		pe.reference_no = cstr(reference_no).strip()
	if reference_date:
		pe.reference_date = reference_date

	pe.insert()
	return {"success": True, "name": pe.name}


@frappe.whitelist(allow_guest=False)
def create_journal_entry(accounts_json, voucher_type="Journal Entry", user_remark=None):
	frappe.has_permission("Journal Entry", ptype="create", throw=True)

	import json

	accounts = json.loads(accounts_json) if isinstance(accounts_json, str) else accounts_json
	if not accounts or not isinstance(accounts, list):
		frappe.throw("At least one account row is required")

	je = frappe.new_doc("Journal Entry")
	je.voucher_type = cstr(voucher_type).strip() or "Journal Entry"
	je.posting_date = today()
	if user_remark:
		je.user_remark = cstr(user_remark).strip()

	for row in accounts:
		account = cstr(row.get("account", "")).strip()
		if not account:
			continue
		je.append(
			"accounts",
			{
				"account": account,
				"debit_in_account_currency": flt(row.get("debit", 0)),
				"credit_in_account_currency": flt(row.get("credit", 0)),
				"party_type": row.get("party_type"),
				"party": row.get("party"),
				"cost_center": row.get("cost_center"),
			},
		)

	if not je.accounts:
		frappe.throw("No valid account entries provided")

	je.insert()
	return {"success": True, "name": je.name}


@frappe.whitelist(allow_guest=False)
def submit_transaction(doctype, name):
	doctype = cstr(doctype).strip()
	name = cstr(name).strip()
	frappe.has_permission(doctype, ptype="submit", throw=True)

	doc = frappe.get_doc(doctype, name)
	doc.submit()
	return {"success": True, "name": doc.name, "status": "Submitted"}


@frappe.whitelist(allow_guest=False)
def cancel_transaction(doctype, name):
	doctype = cstr(doctype).strip()
	name = cstr(name).strip()
	frappe.has_permission(doctype, ptype="cancel", throw=True)

	doc = frappe.get_doc(doctype, name)
	doc.cancel()
	return {"success": True, "name": doc.name, "status": "Cancelled"}


# ─── TERMINALS (POS Profile + POS Closing Entry) ──────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_terminals(page=1, page_size=50):
	frappe.has_permission("POS Profile", ptype="read", throw=True)

	page = max(1, cint(page))
	page_size = min(100, max(1, cint(page_size)))
	limit_start = (page - 1) * page_size

	fields = ["name", "company", "warehouse"]
	if frappe.get_meta("POS Profile").has_field("posa_pos_profile_name"):
		fields.append("posa_pos_profile_name")

	profiles = frappe.get_all(
		"POS Profile",
		filters={"disabled": 0},
		fields=fields,
		order_by="name asc",
		limit_start=limit_start,
		limit=page_size,
	)
	total = frappe.db.count("POS Profile", {"disabled": 0})

	for p in profiles:
		oe_fields = ["name", "user", "company"]
		if frappe.get_meta("POS Opening Entry").has_field("pos_opening_time"):
			oe_fields.append("pos_opening_time")
		elif frappe.get_meta("POS Opening Entry").has_field("period_start_date"):
			oe_fields.append("period_start_date")

		open_sessions = frappe.get_all(
			"POS Opening Entry",
			filters={"pos_profile": p["name"], "status": "Open"},
			fields=oe_fields,
			limit=1,
		)
		if open_sessions:
			s = open_sessions[0]
			p["status"] = "Open"
			p["current_user"] = s.user
			p["opened_at"] = str(s.get("pos_opening_time") or s.get("period_start_date") or "")

			today_txns = frappe.db.sql(
				"""SELECT COUNT(*) as cnt, SUM(grand_total) as total
                   FROM `tabSales Invoice`
                   WHERE pos_profile=%s AND posting_date=%s AND docstatus=1""",
				(p["name"], today()),
				as_dict=True,
			)
			p["today_invoices"] = cint((today_txns[0] or {}).get("cnt", 0))
			p["today_total"] = flt((today_txns[0] or {}).get("total", 0))
		else:
			p["status"] = "Closed"
			p["current_user"] = ""
			p["opened_at"] = ""
			p["today_invoices"] = 0
			p["today_total"] = 0

	return {"success": True, "terminals": profiles, "total": total, "page": page, "page_size": page_size}


@frappe.whitelist(allow_guest=False)
def get_terminal_status(name):
	frappe.has_permission("POS Profile", ptype="read", throw=True)
	name = cstr(name).strip()
	if not frappe.db.exists("POS Profile", name):
		frappe.throw("POS Profile not found")

	oe_fields = ["name", "user"]
	if frappe.get_meta("POS Opening Entry").has_field("pos_opening_time"):
		oe_fields.append("pos_opening_time")
	elif frappe.get_meta("POS Opening Entry").has_field("period_start_date"):
		oe_fields.append("period_start_date")

	if frappe.get_meta("POS Opening Entry").has_field("balance_amount"):
		oe_fields.append("balance_amount")

	open_entry = frappe.get_all(
		"POS Opening Entry",
		filters={"pos_profile": name, "status": "Open"},
		fields=oe_fields,
		limit=1,
	)

	# Map fields for backward compatibility
	if open_entry:
		oe = open_entry[0]
		if "pos_opening_time" not in oe:
			oe["pos_opening_time"] = oe.get("period_start_date")
		if "balance_amount" not in oe:
			doc = frappe.get_doc("POS Opening Entry", oe["name"])
			oe["balance_amount"] = sum(flt(row.opening_amount) for row in doc.balance_details)

	today_payments = frappe.db.sql(
		"""SELECT mode_of_payment, SUM(amount) as total
           FROM `tabSales Invoice Payment` sip
           JOIN `tabSales Invoice` si ON sip.parent = si.name
           WHERE si.pos_profile=%s AND si.posting_date=%s AND si.docstatus=1
           GROUP BY mode_of_payment""",
		(name, today()),
		as_dict=True,
	)

	return {
		"success": True,
		"profile": name,
		"open_entry": open_entry[0] if open_entry else None,
		"today_payments": today_payments,
	}


# ─── INVOICES (Sales Invoice + Purchase Invoice) ──────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_invoices(
	invoice_type="all", status=None, party=None, from_date=None, to_date=None, page=1, page_size=20
):
	frappe.has_permission("Sales Invoice", ptype="read", throw=True)

	page = max(1, cint(page))
	page_size = min(100, max(1, cint(page_size)))
	limit_start = (page - 1) * page_size

	results = []

	if invoice_type in ("all", "sales", "pending"):
		si_filters = {"docstatus": ["!=", 2], "is_return": 0}
		if status == "Draft":
			si_filters["docstatus"] = 0
		elif status == "Submitted":
			si_filters["docstatus"] = 1
		if party:
			si_filters["customer"] = party
		if from_date:
			si_filters["posting_date"] = [">=", from_date]
		if to_date:
			si_filters.setdefault("posting_date", ["<=", to_date])

		if invoice_type == "pending":
			si_filters["docstatus"] = 0

		si_list = frappe.get_all(
			"Sales Invoice",
			filters=si_filters,
			fields=[
				"name",
				"customer",
				"customer_name",
				"posting_date",
				"due_date",
				"grand_total",
				"outstanding_amount",
				"status",
				"docstatus",
				"currency",
			],
			order_by="posting_date desc",
			limit_start=limit_start if invoice_type != "all" else 0,
			limit=page_size if invoice_type != "all" else 999,
		)
		for si in si_list:
			si["invoice_type"] = "Sales"
			results.append(si)

	if invoice_type in ("all", "purchase"):
		pi_filters = {"docstatus": ["!=", 2], "is_return": 0}
		if status == "Draft":
			pi_filters["docstatus"] = 0
		elif status == "Submitted":
			pi_filters["docstatus"] = 1
		if party:
			pi_filters["supplier"] = party
		if from_date:
			pi_filters["posting_date"] = [">=", from_date]
		if to_date:
			pi_filters.setdefault("posting_date", ["<=", to_date])

		pi_list = frappe.get_all(
			"Purchase Invoice",
			filters=pi_filters,
			fields=[
				"name",
				"supplier",
				"supplier_name",
				"posting_date",
				"due_date",
				"grand_total",
				"outstanding_amount",
				"status",
				"docstatus",
				"currency",
			],
			order_by="posting_date desc",
			limit_start=limit_start if invoice_type != "all" else 0,
			limit=page_size if invoice_type != "all" else 999,
		)
		for pi in pi_list:
			pi["invoice_type"] = "Purchase"
			pi["customer"] = pi.get("supplier", "")
			pi["customer_name"] = pi.get("supplier_name", "")
			results.append(pi)

	results.sort(key=lambda x: x.get("posting_date", ""), reverse=True)
	total = len(results)
	results = results[limit_start : limit_start + page_size]

	return {"success": True, "invoices": results, "total": total, "page": page, "page_size": page_size}


@frappe.whitelist(allow_guest=False)
def get_invoice_detail(invoice_type, name):
	invoice_type = cstr(invoice_type).strip()
	name = cstr(name).strip()
	doctype = "Sales Invoice" if invoice_type == "Sales" else "Purchase Invoice"
	frappe.has_permission(doctype, ptype="read", throw=True)

	if not frappe.db.exists(doctype, name):
		frappe.throw(f"{doctype} not found")

	doc = frappe.get_doc(doctype, name)
	items = []
	for row in doc.items:
		items.append(
			{
				"item_code": row.item_code,
				"item_name": row.item_name,
				"qty": row.qty,
				"rate": row.rate,
				"amount": row.amount,
				"warehouse": row.warehouse,
			}
		)

	payments = []
	for row in getattr(doc, "payments", []):
		payments.append(
			{
				"mode_of_payment": row.mode_of_payment,
				"amount": row.amount,
			}
		)

	return {
		"success": True,
		"invoice": {
			"name": doc.name,
			"doctype": doctype,
			"invoice_type": invoice_type,
			"posting_date": str(doc.posting_date),
			"due_date": str(doc.due_date) if doc.due_date else "",
			"grand_total": flt(doc.grand_total),
			"outstanding_amount": flt(doc.outstanding_amount),
			"status": doc.status,
			"docstatus": doc.docstatus,
			"currency": doc.currency,
			"customer" if invoice_type == "Sales" else "supplier": doc.customer
			if invoice_type == "Sales"
			else doc.supplier,
			"customer_name" if invoice_type == "Sales" else "supplier_name": doc.customer_name
			if invoice_type == "Sales"
			else doc.supplier_name,
			"items": items,
			"payments": payments,
		},
	}


@frappe.whitelist(allow_guest=False)
def submit_invoice(invoice_type, name):
	doctype = "Sales Invoice" if cstr(invoice_type).strip() == "Sales" else "Purchase Invoice"
	frappe.has_permission(doctype, ptype="submit", throw=True)
	name = cstr(name).strip()

	doc = frappe.get_doc(doctype, name)
	doc.submit()
	return {"success": True, "name": doc.name, "status": doc.status}


@frappe.whitelist(allow_guest=False)
def cancel_invoice(invoice_type, name):
	doctype = "Sales Invoice" if cstr(invoice_type).strip() == "Sales" else "Purchase Invoice"
	frappe.has_permission(doctype, ptype="cancel", throw=True)
	name = cstr(name).strip()

	doc = frappe.get_doc(doctype, name)
	doc.cancel()
	return {"success": True, "name": doc.name, "status": "Cancelled"}


# ─── CREDIT NOTES (Sales/Purchase Invoice with is_return=1) ───────────────────


@frappe.whitelist(allow_guest=False)
def get_credit_notes(note_type="all", party=None, from_date=None, to_date=None, page=1, page_size=20):
	frappe.has_permission("Sales Invoice", ptype="read", throw=True)

	page = max(1, cint(page))
	page_size = min(100, max(1, cint(page_size)))
	limit_start = (page - 1) * page_size

	results = []

	if note_type in ("all", "outgoing"):
		si_filters = {"docstatus": ["!=", 2], "is_return": 1}
		if party:
			si_filters["customer"] = party
		if from_date:
			si_filters["posting_date"] = [">=", from_date]
		if to_date:
			si_filters.setdefault("posting_date", ["<=", to_date])

		si_list = frappe.get_all(
			"Sales Invoice",
			filters=si_filters,
			fields=[
				"name",
				"customer",
				"customer_name",
				"posting_date",
				"grand_total",
				"return_against",
				"status",
				"docstatus",
			],
			order_by="posting_date desc",
			limit_start=0,
			limit=999,
		)
		for si in si_list:
			si["note_type"] = "Outgoing"
			si["party"] = si.get("customer", "")
			si["party_name"] = si.get("customer_name", "")
			results.append(si)

	if note_type in ("all", "incoming"):
		pi_filters = {"docstatus": ["!=", 2], "is_return": 1}
		if party:
			pi_filters["supplier"] = party
		if from_date:
			pi_filters["posting_date"] = [">=", from_date]
		if to_date:
			pi_filters.setdefault("posting_date", ["<=", to_date])

		pi_list = frappe.get_all(
			"Purchase Invoice",
			filters=pi_filters,
			fields=[
				"name",
				"supplier",
				"supplier_name",
				"posting_date",
				"grand_total",
				"return_against",
				"status",
				"docstatus",
			],
			order_by="posting_date desc",
			limit_start=0,
			limit=999,
		)
		for pi in pi_list:
			pi["note_type"] = "Incoming"
			pi["party"] = pi.get("supplier", "")
			pi["party_name"] = pi.get("supplier_name", "")
			results.append(pi)

	results.sort(key=lambda x: x.get("posting_date", ""), reverse=True)
	total = len(results)
	results = results[limit_start : limit_start + page_size]

	return {"success": True, "credit_notes": results, "total": total, "page": page, "page_size": page_size}


@frappe.whitelist(allow_guest=False)
def create_credit_note(invoice_type, return_against, reason=None):
	invoice_type = cstr(invoice_type).strip()
	return_against = cstr(return_against).strip()

	if invoice_type == "Sales":
		frappe.has_permission("Sales Invoice", ptype="create", throw=True)
		if not frappe.db.exists("Sales Invoice", return_against):
			frappe.throw("Original Sales Invoice not found")

		original = frappe.get_doc("Sales Invoice", return_against)
		if original.docstatus != 1:
			frappe.throw("Original invoice must be submitted")

		cn = frappe.copy_doc(original)
		cn.is_return = 1
		cn.return_against = return_against
		cn.posting_date = today()
		for item in cn.items:
			item.qty = -abs(item.qty)
			item.amount = -abs(item.amount)
		cn.set_missing_values()
		cn.insert()
	else:
		frappe.has_permission("Purchase Invoice", ptype="create", throw=True)
		if not frappe.db.exists("Purchase Invoice", return_against):
			frappe.throw("Original Purchase Invoice not found")

		original = frappe.get_doc("Purchase Invoice", return_against)
		if original.docstatus != 1:
			frappe.throw("Original invoice must be submitted")

		cn = frappe.copy_doc(original)
		cn.is_return = 1
		cn.return_against = return_against
		cn.posting_date = today()
		for item in cn.items:
			item.qty = -abs(item.qty)
			item.amount = -abs(item.amount)
		cn.set_missing_values()
		cn.insert()

	return {"success": True, "name": cn.name, "invoice_type": invoice_type}


# ─── EXPORT UBL ───────────────────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_exportable_invoices(invoice_type="sales", from_date=None, to_date=None, page=1, page_size=50):
	frappe.has_permission("Sales Invoice", ptype="read", throw=True)

	page = max(1, cint(page))
	page_size = min(100, max(1, cint(page_size)))
	limit_start = (page - 1) * page_size

	doctype = "Sales Invoice" if invoice_type == "sales" else "Purchase Invoice"
	filters = {"docstatus": 1, "is_return": 0}
	if from_date:
		filters["posting_date"] = [">=", from_date]
	if to_date:
		filters.setdefault("posting_date", ["<=", to_date])

	invoices = frappe.get_all(
		doctype,
		filters=filters,
		fields=[
			"name",
			"posting_date",
			"grand_total",
			"currency",
			"customer" if invoice_type == "sales" else "supplieras party",
		],
		order_by="posting_date desc",
		limit_start=limit_start,
		limit=page_size,
	)
	total = frappe.db.count(doctype, filters)

	return {"success": True, "invoices": invoices, "total": total, "page": page, "page_size": page_size}


@frappe.whitelist(allow_guest=False)
def export_ubl(invoices_json):
	frappe.has_permission("Sales Invoice", ptype="read", throw=True)
	frappe.only_for("Accounts Manager", "System Manager", "Administrator")

	import json

	invoice_names = json.loads(invoices_json) if isinstance(invoices_json, str) else invoices_json
	if not invoice_names:
		frappe.throw("No invoices selected for export")

	export_data = []
	for name in invoice_names:
		name = cstr(name).strip()
		if not frappe.db.exists("Sales Invoice", name):
			continue
		doc = frappe.get_doc("Sales Invoice", name)
		export_data.append(
			{
				"name": doc.name,
				"posting_date": str(doc.posting_date),
				"customer": doc.customer,
				"customer_name": doc.customer_name,
				"grand_total": flt(doc.grand_total),
				"currency": doc.currency,
				"taxes": [
					{"account": t.account_head, "rate": flt(t.rate), "amount": flt(t.tax_amount)}
					for t in doc.taxes
				],
				"items": [
					{"item_code": i.item_code, "qty": i.qty, "rate": flt(i.rate), "amount": flt(i.amount)}
					for i in doc.items
				],
			}
		)

	return {"success": True, "export_data": export_data, "count": len(export_data)}


# ─── ACCOUNTS LIST (for selectors) ────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_accounts(company=None, root_only=0):
	frappe.has_permission("Account", ptype="read", throw=True)

	filters = {"disabled": 0}
	if company:
		filters["company"] = company
	if cint(root_only):
		filters["is_group"] = 1

	accounts = frappe.get_all(
		"Account",
		filters=filters,
		fields=["name", "account_name", "parent_account", "is_group", "account_type", "root_type"],
		order_by="lft asc",
		limit=500,
	)

	return {"success": True, "accounts": accounts}


# ─── MODES OF PAYMENT (for selectors) ─────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_modes_of_payment():
	frappe.has_permission("Mode of Payment", ptype="read", throw=True)

	modes = frappe.get_all(
		"Mode of Payment",
		filters={},
		fields=["name", "type"],
		order_by="name asc",
	)

	return {"success": True, "modes": modes}
