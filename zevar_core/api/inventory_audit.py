import json

import frappe
from frappe.utils import flt, now_datetime, add_days, today
from zevar_core.services.inventory_audit_utils import _log_audit_event, execute_submit_scan, execute_batch_scan


@frappe.whitelist(allow_guest=False)
def start_audit(display_case=None, store_location=None, scope="Spot", audit_plan=None):
	"""Start a new audit session. Supports scope-based audits beyond display cases.

	Args:
		display_case: Display Case name (for Spot/Showcase audits)
		store_location: Warehouse name (for Backstock/Full Store audits)
		scope: One of Spot, Showcase, Backstock, Full Store
		audit_plan: Optional Audit Plan to link
	"""
	frappe.has_permission("Case Audit Session", ptype="write", throw=True)

	scope = scope or "Spot"
	warehouse = None

	if scope in ("Spot", "Showcase"):
		if not display_case:
			frappe.throw("Display Case is required for Spot/Showcase audits")
		case_doc = (
			frappe.get_doc("Display Case", display_case)
			if frappe.db.exists("Display Case", display_case)
			else None
		)
		warehouse = case_doc.warehouse if case_doc else display_case
		if not store_location:
			store_location = warehouse
	elif scope in ("Backstock", "Full Store"):
		if not store_location:
			frappe.throw("Store Location is required for Backstock/Full Store audits")
		# For backstock, query back-stock and safe warehouses under the store
		# For full store, query all warehouses under the store
		warehouse = store_location

	if not warehouse:
		frappe.throw("Could not determine warehouse for audit")

	# Get expected items based on scope
	expected_items = _get_expected_items(warehouse, scope, display_case)

	expected_count = 0
	total_value_expected = 0.0
	for item in expected_items:
		expected_count += flt(item.actual_qty)
		rate = flt(item.standard_rate) or flt(item.valuation_rate)
		total_value_expected += flt(item.actual_qty) * rate

	# Create the audit session
	session = frappe.new_doc("Case Audit Session")
	session.store_location = store_location or warehouse
	session.display_case = display_case or ""
	session.scope = scope
	session.audit_plan = audit_plan or ""
	session.started_at = now_datetime()
	session.status = "In Progress"
	session.expected_count = expected_count
	session.scanned_count = 0
	session.total_value_expected = total_value_expected
	session.insert(ignore_permissions=True)

	# Update linked Audit Plan
	if audit_plan and frappe.db.exists("Audit Plan", audit_plan):
		frappe.db.set_value("Audit Plan", audit_plan, "status", "In Progress")

	_log_audit_event(
		"audit_started",
		"Inventory",
		session.name,
		f"Started {scope} audit for {display_case or store_location} with {expected_count} expected items.",
	)

	return {
		"success": True,
		"session_name": session.name,
		"session": session.name,
		"expected_items": expected_items,
		"expected_count": expected_count,
		"total_value_expected": total_value_expected,
		"scope": scope,
	}


def _get_expected_items(warehouse, scope, display_case=None):
	"""Get expected items based on audit scope."""
	filters = {"actual_qty": [">", 0]}

	if scope == "Spot":
		# Just the display case warehouse
		filters["warehouse"] = warehouse
	elif scope == "Showcase":
		# All showcase sub-warehouses
		filters["warehouse"] = ["like", f"%Showcase%"]
		if display_case:
			case_wh = frappe.db.get_value("Display Case", display_case, "warehouse")
			if case_wh:
				filters["warehouse"] = case_wh
		else:
			# All showcases under the store
			filters["warehouse"] = ["like", f"%{warehouse}%Showcase%"]
			del filters["warehouse"]
			showcase_whs = frappe.get_all("Warehouse", filters={"name": ["like", f"%Showcase%"]}, pluck="name")
			if not showcase_whs:
				filters["warehouse"] = warehouse
			else:
				return frappe.db.sql(
					"""
					select b.item_code, sum(b.actual_qty) as actual_qty,
						i.custom_rfid_epc, i.standard_rate, i.valuation_rate,
						(select barcode from `tabItem Barcode` ib where ib.parent = i.name limit 1) as barcode
					from `tabBin` b
					join `tabItem` i on b.item_code = i.name
					where b.warehouse in %s and b.actual_qty > 0
					group by b.item_code, i.custom_rfid_epc, i.standard_rate, i.valuation_rate
					""",
					(showcase_whs,),
					as_dict=True,
				)
	elif scope == "Backstock":
		# Back Stock + Safe zones under the store
		return frappe.db.sql(
			"""
			select b.item_code, b.actual_qty, i.custom_rfid_epc, i.standard_rate, i.valuation_rate,
				(select barcode from `tabItem Barcode` ib where ib.parent = i.name limit 1) as barcode,
				b.warehouse
			from `tabBin` b
			join `tabItem` i on b.item_code = i.name
			where (b.warehouse like %s or b.warehouse like %s) and b.actual_qty > 0
			""",
			(f"%{warehouse}%Back Stock%", f"%{warehouse}%Safe%"),
			as_dict=True,
		)
	elif scope == "Full Store":
		# All zones under the store root warehouse
		return frappe.db.sql(
			"""
			select b.item_code, b.actual_qty, i.custom_rfid_epc, i.standard_rate, i.valuation_rate,
				(select barcode from `tabItem Barcode` ib where ib.parent = i.name limit 1) as barcode,
				b.warehouse
			from `tabBin` b
			join `tabItem` i on b.item_code = i.name
			where b.warehouse like %s and b.actual_qty > 0
			""",
			(f"%{warehouse}%",),
			as_dict=True,
		)

	return frappe.db.sql(
		"""
		select b.item_code, b.actual_qty, i.custom_rfid_epc, i.standard_rate, i.valuation_rate,
			(select barcode from `tabItem Barcode` ib where ib.parent = i.name limit 1) as barcode
		from `tabBin` b
		join `tabItem` i on b.item_code = i.name
		where b.warehouse = %s and b.actual_qty > 0
		""",
		(filters.get("warehouse", warehouse),),
		as_dict=True,
	)


@frappe.whitelist(allow_guest=False)
def submit_scan(session, barcode_or_epc):
	session_doc = frappe.get_doc("Case Audit Session", session)
	frappe.has_permission("Case Audit Session", ptype="write", doc=session_doc, throw=True)

	if session_doc.status != "In Progress":
		frappe.throw("Audit session is not in progress.")

	return execute_submit_scan(session_doc, barcode_or_epc)


@frappe.whitelist(allow_guest=False)
def finalize_audit(session, two_person_signoff_by=None, freeze_override_reason=None):
	"""Finalize an audit session with optional two-person sign-off and freeze override.

	Args:
		session: Case Audit Session name
		two_person_signoff_by: User who provides the second sign-off (manager)
		freeze_override_reason: If session is Pending Manager Review, reason to unfreeze
	"""
	session_doc = frappe.get_doc("Case Audit Session", session)
	frappe.has_permission("Case Audit Session", ptype="write", doc=session_doc, throw=True)
	frappe.has_permission("Stock Entry", ptype="submit", throw=True)

	if session_doc.status != "In Progress":
		frappe.throw("Audit session is not in progress.")

	# Two-person sign-off
	from zevar_core.unified_retail_management_system.doctype.case_audit_session.case_audit_session import _get_audit_policy
	policy = _get_audit_policy()
	if policy.get("require_two_person_rule") and two_person_signoff_by:
		session_doc.two_person_signoff_by = two_person_signoff_by

	session_doc.submit()

	result = {
		"success": True,
		"status": session_doc.status,
		"missing_count": len(getattr(session_doc, "_missing_items", [])),
		"variance_dollar_total": flt(session_doc.variance_dollar_total),
		"shrinkage_processing_queued": session_doc.status in ("Discrepancy", "Reconciled with Shrinkage", "Pending Manager Review"),
	}

	return result


@frappe.whitelist(allow_guest=False)
def approve_variance(session, approve_reason):
	"""Manager approves a Pending Manager Review audit, unfreezing the store."""
	frappe.only_for("Sales Manager", "System Manager")

	session_doc = frappe.get_doc("Case Audit Session", session)
	if session_doc.docstatus != 1:
		frappe.throw("Session must be submitted first")

	if session_doc.status != "Pending Manager Review":
		frappe.throw("Session is not pending manager review")

	from zevar_core.unified_retail_management_system.doctype.case_audit_session.case_audit_session import unfreeze_store
	unfreeze_store(session_doc.store_location, frappe.session.user)

	# If shrinkage wasn't auto-posted, do it now
	if session_doc.variance_dollar_total and not session_doc.total_value_discrepancy:
		missing_items = _get_missing_items_for_session(session_doc)
		if missing_items:
			frappe.enqueue(
				"zevar_core.services.inventory_audit_utils.process_shrinkage_async",
				session=session_doc.name,
				missing_items_json=json.dumps(missing_items),
				store_location=session_doc.store_location,
				queue="long",
				now=frappe.flags.in_test,
			)

	# Update status
	frappe.db.set_value("Case Audit Session", session, "status", "Reconciled with Shrinkage")
	frappe.db.set_value("Case Audit Session", session, "freeze_reason", f"Approved: {approve_reason}")

	_log_audit_event(
		"variance_approved",
		"Inventory",
		session,
		f"Variance for {session} approved by {frappe.session.user}: {approve_reason}",
	)

	return {"success": True, "status": "Reconciled with Shrinkage"}


def _get_missing_items_for_session(session_doc):
	"""Re-derive missing items from a submitted session."""
	scanned_items = set()
	for scan in session_doc.scans:
		if scan.match_status == "Matched" and scan.item_code:
			scanned_items.add(scan.item_code)

	expected = frappe.db.sql(
		"select item_code, actual_qty from `tabBin` where warehouse = %s and actual_qty > 0",
		(session_doc.store_location,),
		as_dict=True,
	)
	missing = []
	for exp in expected:
		if exp.item_code not in scanned_items:
			missing.append({"item_code": exp.item_code, "qty": flt(exp.actual_qty)})
	return missing


@frappe.whitelist(allow_guest=False)
def batch_scan(session, epcs_json):
	session_doc = frappe.get_doc("Case Audit Session", session)
	frappe.has_permission("Case Audit Session", ptype="write", doc=session_doc, throw=True)

	if len(epcs_json) > 50000:
		frappe.throw("Payload too large. Please send smaller batches.")

	epcs = json.loads(epcs_json)
	if len(epcs) > 500:
		frappe.throw("Cannot process more than 500 EPCs in a single batch.")

	return execute_batch_scan(session_doc, epcs)


@frappe.whitelist(allow_guest=False)
def cancel_audit(session):
	session_doc = frappe.get_doc("Case Audit Session", session)
	frappe.has_permission("Case Audit Session", ptype="write", doc=session_doc, throw=True)
	session_doc.status = "Cancelled"
	session_doc.cancelled_at = now_datetime()
	session_doc.save(ignore_permissions=True)

	# Update linked Audit Plan
	if session_doc.audit_plan and frappe.db.exists("Audit Plan", session_doc.audit_plan):
		frappe.db.set_value("Audit Plan", session_doc.audit_plan, "status", "Scheduled")

	return {"success": True, "status": "Cancelled"}


@frappe.whitelist(allow_guest=False)
def get_audit_progress(session):
	session_doc = frappe.get_doc("Case Audit Session", session)
	frappe.has_permission("Case Audit Session", ptype="read", doc=session_doc, throw=True)

	matched = 0
	unexpected = 0
	duplicates = 0
	scanned_items = set()

	for scan in session_doc.scans:
		if scan.match_status == "Matched":
			matched += 1
			if scan.item_code:
				scanned_items.add(scan.item_code)
		elif scan.match_status == "Unexpected":
			unexpected += 1
		elif scan.match_status == "Duplicate":
			duplicates += 1

	expected_items = frappe.db.sql(
		"""
		select item_code, actual_qty
		from `tabBin`
		where warehouse = %s and actual_qty > 0
	""",
		(session_doc.store_location,),
		as_dict=True,
	)

	missing_items = []
	for exp in expected_items:
		if exp.item_code not in scanned_items:
			item_name = frappe.db.get_value("Item", exp.item_code, "item_name")
			rate = flt(frappe.db.get_value("Item", exp.item_code, "standard_rate") or 0)
			missing_items.append({
				"item_code": exp.item_code,
				"item_name": item_name,
				"expected_qty": flt(exp.actual_qty),
				"scanned_qty": 0,
				"valuation_rate": rate,
			})

	return {
		"success": True,
		"counts": {"matched": matched, "unexpected": unexpected, "duplicates": duplicates},
		"recent_scans": [s.as_dict() for s in session_doc.scans[-10:]] if session_doc.scans else [],
		"missing_items": missing_items,
		"unexpected_items": [
			{"item_code": s.item_code, "item_name": s.item_name, "barcode_or_epc": s.barcode_or_epc}
			for s in session_doc.scans if s.match_status == "Unexpected"
		][-20:],
		"session": {
			"name": session_doc.name,
			"status": session_doc.status,
			"scope": session_doc.scope,
			"expected_count": session_doc.expected_count,
			"scanned_count": session_doc.scanned_count,
			"total_value_expected": flt(session_doc.total_value_expected),
			"total_value_scanned": flt(session_doc.total_value_scanned),
			"total_value_discrepancy": flt(session_doc.total_value_discrepancy),
			"variance_dollar_total": flt(session_doc.variance_dollar_total),
			"store_location": session_doc.store_location,
			"display_case": session_doc.display_case,
		},
	}


@frappe.whitelist(allow_guest=False)
def get_audit_history(limit_start=0, page_size=10, status=None, scope=None):
	frappe.has_permission("Case Audit Session", ptype="read", throw=True)

	filters = {}
	if status:
		filters["status"] = status
	if scope:
		filters["scope"] = scope

	sessions = frappe.get_all(
		"Case Audit Session",
		filters=filters,
		fields=["name", "status", "started_at", "store_location", "scope", "expected_count", "scanned_count", "total_value_discrepancy", "variance_dollar_total"],
		limit_start=limit_start,
		limit=page_size,
		order_by="started_at desc",
	)
	total = frappe.db.count("Case Audit Session", filters)
	return {"success": True, "sessions": sessions, "total": total}


@frappe.whitelist(allow_guest=False)
def get_audit_dashboard(store=None):
	"""Get audit dashboard KPIs: next audit due, overdue, shrinkage, hit-rate."""
	frappe.has_permission("Case Audit Session", ptype="read", throw=True)

	from frappe.utils import add_months, getdate

	# Overdue audit plans
	overdue_plans = frappe.get_all("Audit Plan", filters={
		"status": "Scheduled",
		"scheduled_for": ["<", today()],
	}, fields=["name", "store_location", "scope", "scheduled_for"])

	# Next audit due
	next_plan = frappe.get_all("Audit Plan", filters={
		"status": "Scheduled",
		"scheduled_for": [">=", today()],
	}, fields=["name", "store_location", "scope", "scheduled_for"],
		order_by="scheduled_for asc", limit=1)

	# Shrinkage last 30 days
	thirty_days_ago = add_days(today(), -30)
	shrinkage_sessions = frappe.get_all("Case Audit Session", filters={
		"status": ["in", ["Discrepancy", "Reconciled with Shrinkage", "Pending Manager Review"]],
		"started_at": [">=", thirty_days_ago],
	}, fields=["sum(variance_dollar_total) as total_shrinkage", "count(*) as count"])

	total_shrinkage = flt((shrinkage_sessions[0] or {}).get("total_shrinkage", 0))
	shrinkage_count = (shrinkage_sessions[0] or {}).get("count", 0)

	# Audit hit rate (last 30 days)
	total_audits = frappe.db.count("Case Audit Session", filters={
		"started_at": [">=", thirty_days_ago],
		"docstatus": 1,
	})
	reconciled_audits = frappe.db.count("Case Audit Session", filters={
		"status": "Reconciled",
		"started_at": [">=", thirty_days_ago],
		"docstatus": 1,
	})
	hit_rate = (reconciled_audits / total_audits * 100) if total_audits > 0 else 100

	# Store frozen status
	frozen_stores = []
	if store:
		from zevar_core.unified_retail_management_system.doctype.case_audit_session.case_audit_session import is_store_frozen
		reason = is_store_frozen(store)
		if reason:
			frozen_stores.append({"store": store, "reason": reason})

	return {
		"success": True,
		"overdue_audits": len(overdue_plans),
		"overdue_plans": overdue_plans[:5],
		"next_audit": next_plan[0] if next_plan else None,
		"shrinkage_last_30_days": total_shrinkage,
		"shrinkage_session_count": shrinkage_count,
		"audit_hit_rate": round(hit_rate, 1),
		"total_audits_last_30_days": total_audits,
		"frozen_stores": frozen_stores,
	}


@frappe.whitelist(allow_guest=False)
def get_audit_plans(store=None, status="Scheduled"):
	"""Get audit plans for the plan picker in the UI."""
	frappe.has_permission("Audit Plan", ptype="read", throw=True)

	filters = {}
	if store:
		filters["store_location"] = store
	if status:
		filters["status"] = status

	plans = frappe.get_all("Audit Plan", filters=filters,
		fields=["name", "store_location", "scope", "scheduled_for", "assigned_to", "status"],
		order_by="scheduled_for asc", limit=50)

	return {"success": True, "plans": plans}


@frappe.whitelist(allow_guest=False)
def export_audit_results(session):
	import csv
	import uuid
	from io import StringIO

	session_doc = frappe.get_doc("Case Audit Session", session)
	frappe.has_permission("Case Audit Session", ptype="read", doc=session_doc, throw=True)
	f = StringIO()
	writer = csv.writer(f)
	writer.writerow(["Item Code", "Item Name", "Barcode/EPC", "Match Status", "Scanned At", "Valuation Rate"])

	for scan in session_doc.scans:
		writer.writerow([scan.item_code, scan.item_name, scan.barcode_or_epc, scan.match_status, scan.scanned_at, scan.valuation_rate])

	file_doc = frappe.new_doc("File")
	file_doc.file_name = f"audit_export_{session}_{uuid.uuid4().hex[:8]}.csv"
	file_doc.content = f.getvalue().encode("utf-8")
	file_doc.is_private = 1
	file_doc.insert()

	return {"success": True, "file_url": file_doc.file_url}
