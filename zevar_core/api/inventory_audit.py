import json

import frappe
from frappe import _
from frappe.utils import now_datetime, get_url, cint


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_item_code(barcode_or_epc):
	"""Try to resolve a barcode/EPC string to an item_code. Returns (item_code, item_data) or (None, None)."""
	item_code = frappe.db.get_value("Item", {"custom_rfid_epc": barcode_or_epc}, "name")
	if not item_code:
		item_code = frappe.db.get_value("Item Barcode", {"barcode": barcode_or_epc}, "parent")
	if not item_code:
		item_code = frappe.db.get_value("Item", barcode_or_epc, "name")
	if not item_code:
		return None, None
	item_data = frappe.db.get_value(
		"Item", item_code, ["item_name", "image", "valuation_rate"], as_dict=True
	)
	return item_code, item_data


def _check_permission(session_name):
	"""Check if user has permission to modify this audit session."""
	frappe.has_permission("Case Audit Session", "write", doc=session_name, throw=True)


def _get_expected_items(store_location: str) -> list[dict]:
	"""Get expected items and valuation from Bin and Item tables."""
	return frappe.db.sql(
		"""
		SELECT b.item_code, sum(b.actual_qty) as actual_qty,
		       COALESCE(i.valuation_rate, i.standard_rate, 0) as valuation_rate,
		       i.item_name, i.image
		FROM `tabBin` b
		JOIN `tabItem` i ON i.name = b.item_code
		WHERE b.warehouse = %s AND b.actual_qty > 0
		GROUP BY b.item_code, i.valuation_rate, i.standard_rate, i.item_name, i.image
	""",
		store_location,
		as_dict=1,
	)


def _log_audit_event(event_type, reference_name, details="", category="Inventory"):
	"""Safely log a POS Audit Log entry."""
	if not frappe.db.exists("DocType", "POS Audit Log"):
		return
	frappe.get_doc(
		{
			"doctype": "POS Audit Log",
			"user": frappe.session.user,
			"event_type": event_type,
			"category": category,
			"severity": "Info",
			"timestamp": now_datetime(),
			"reference_type": "Case Audit Session",
			"reference_document": reference_name,
			"details": details,
		}
	).insert(ignore_permissions=True)


# ---------------------------------------------------------------------------
# Start Audit
# ---------------------------------------------------------------------------

@frappe.whitelist()
def start_audit(store_location: str, auditor: str | None = None, notes: str | None = None) -> dict:
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	if not store_location:
		frappe.throw(_("Store Location is required."))

	session = frappe.new_doc("Case Audit Session")
	session.store_location = store_location
	session.auditor = auditor or frappe.session.user
	session.notes = notes
	session.started_at = now_datetime()
	session.status = "Draft"
	session.audit_type = "Barcode"

	# Get expected items with valuation
	expected_items_data = _get_expected_items(store_location)

	total_expected = sum(item.actual_qty for item in expected_items_data)
	total_value_expected = sum(
		item.actual_qty * (item.valuation_rate or 0) for item in expected_items_data
	)

	session.expected_count = total_expected
	session.scanned_count = 0
	session.total_value_expected = total_value_expected
	session.insert(ignore_permissions=True)

	_log_audit_event(
		"audit_started",
		session.name,
		details=f"Audit started for {store_location}, expected {total_expected} items (${total_value_expected:,.2f})",
	)

	return {
		"success": True,
		"session_name": session.name,
		"expected_count": total_expected,
		"total_value_expected": total_value_expected,
		"expected_items": expected_items_data,
	}


# ---------------------------------------------------------------------------
# Single Scan (with deduplication and enrichment)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def submit_scan(session_name: str, barcode_or_epc: str) -> dict:
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	session = frappe.get_doc("Case Audit Session", session_name)
	_check_permission(session_name)

	if session.status not in ("Draft", "In Progress"):
		frappe.throw(_("Can only scan into Draft or In Progress sessions."))

	if session.status == "Draft":
		session.status = "In Progress"

	# --- Deduplication check ---
	existing = frappe.get_all(
		"Case Audit Scan",
		filters={"parent": session_name, "barcode_or_epc": barcode_or_epc, "is_duplicate": 0},
		fields=["name", "item_code"],
		limit=1,
	)
	if existing:
		item_data = frappe.db.get_value(
			"Item", existing[0].item_code, ["item_name", "image", "valuation_rate"], as_dict=True
		) if existing[0].item_code else None
		return {
			"success": True,
			"match_status": "Duplicate",
			"item_code": existing[0].item_code,
			"item_name": item_data.item_name if item_data else None,
			"item_image": item_data.image if item_data else None,
			"valuation_rate": item_data.valuation_rate if item_data else 0,
			"message": "This barcode/EPC was already scanned in this session.",
		}

	# --- Resolve item ---
	item_code, item_data = _resolve_item_code(barcode_or_epc)

	if not item_code:
		session.append(
			"scans",
			{
				"barcode_or_epc": barcode_or_epc,
				"scanned_at": now_datetime(),
				"match_status": "Unexpected",
			},
		)
		session.scanned_count += 1
		session.save(ignore_permissions=True)
		return {
			"success": True,
			"match_status": "Unexpected",
			"barcode_or_epc": barcode_or_epc,
		}

	# --- Determine match status ---
	expected_qty = (
		frappe.db.get_value(
			"Bin", {"item_code": item_code, "warehouse": session.store_location}, "actual_qty"
		)
		or 0
	)
	already_scanned = frappe.db.count(
		"Case Audit Scan",
		{"parent": session_name, "item_code": item_code, "match_status": "Matched"}
	)
	match_status = "Matched" if (expected_qty > 0 and already_scanned < expected_qty) else "Unexpected"

	session.append(
		"scans",
		{
			"item_code": item_code,
			"barcode_or_epc": barcode_or_epc,
			"scanned_at": now_datetime(),
			"match_status": match_status,
			"item_name": item_data.item_name,
			"item_image": item_data.image,
			"valuation_rate": item_data.valuation_rate,
		},
	)
	session.scanned_count += 1
	session.save(ignore_permissions=True)

	return {
		"success": True,
		"match_status": match_status,
		"item_code": item_code,
		"item_name": item_data.item_name,
		"item_image": item_data.image,
		"valuation_rate": item_data.valuation_rate,
	}


# ---------------------------------------------------------------------------
# Batch Scan (RFID burst support)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def batch_scan(session_name: str, barcodes_or_epcs: str) -> dict:
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	codes = json.loads(barcodes_or_epcs)
	if not isinstance(codes, list):
		frappe.throw(_("barcodes_or_epcs must be a JSON array of strings."))
	if len(codes) > 500:
		frappe.throw(_("Maximum 500 codes per batch."))

	session = frappe.get_doc("Case Audit Session", session_name)
	_check_permission(session_name)
	if session.status not in ("Draft", "In Progress"):
		frappe.throw(_("Can only scan into Draft or In Progress sessions."))

	if session.status == "Draft":
		session.status = "In Progress"

	# Update audit type
	if session.audit_type == "Barcode":
		session.audit_type = "RFID"

	# Get already-scanned codes in this session (single query)
	existing_scans = frappe.get_all(
		"Case Audit Scan",
		filters={"parent": session_name, "is_duplicate": 0},
		fields=["barcode_or_epc"],
	)
	existing_codes = {s.barcode_or_epc for s in existing_scans}

	# Filter to only new codes
	new_codes = [c for c in codes if c and c not in existing_codes]
	duplicates_skipped = len(codes) - len(new_codes)

	# Bulk resolve RFID EPCs
	epc_to_item = {}
	if new_codes:
		records = frappe.db.sql(
			"SELECT name, custom_rfid_epc FROM `tabItem` WHERE custom_rfid_epc IN %s",
			[tuple(new_codes)],
			as_dict=True,
		)
		for r in records:
			epc_to_item[r.custom_rfid_epc] = r.name

		# Bulk resolve barcodes
		barcode_records = frappe.db.sql(
			"SELECT barcode, parent FROM `tabItem Barcode` WHERE barcode IN %s",
			[tuple(new_codes)],
			as_dict=True,
		)
		for r in barcode_records:
			if r.barcode not in epc_to_item:
				epc_to_item[r.barcode] = r.parent

	# Bulk fetch item data for resolved item_codes
	resolved_item_codes = set(epc_to_item.values())
	item_data_map = {}
	if resolved_item_codes:
		items = frappe.db.sql(
			"SELECT name, item_name, image, valuation_rate FROM `tabItem` WHERE name IN %s",
			[tuple(resolved_item_codes)],
			as_dict=True,
		)
		for i in items:
			item_data_map[i.name] = i

	# Get expected qty map
	expected_qty_map = {}
	if resolved_item_codes:
		bins = frappe.db.sql(
			"SELECT item_code, actual_qty FROM `tabBin` WHERE warehouse = %s AND actual_qty > 0",
			session.store_location,
			as_dict=True,
		)
		for b in bins:
			expected_qty_map[b.item_code] = (expected_qty_map.get(b.item_code, 0) or 0) + b.actual_qty

	# Count already-scanned per item in this session
	scanned_per_item = {}
	for s in session.scans:
		if s.match_status == "Matched" and s.item_code:
			scanned_per_item[s.item_code] = scanned_per_item.get(s.item_code, 0) + 1

	results = []
	for code in new_codes:
		item_code = epc_to_item.get(code)
		if not item_code:
			# Check if it's a direct item_code
			if code in item_data_map:
				item_code = code
			else:
				session.append("scans", {
					"barcode_or_epc": code,
					"scanned_at": now_datetime(),
					"match_status": "Unexpected",
				})
				session.scanned_count += 1
				results.append({"barcode_or_epc": code, "match_status": "Unexpected"})
				continue

		info = item_data_map.get(item_code, {})
		exp_qty = expected_qty_map.get(item_code, 0)
		already = scanned_per_item.get(item_code, 0)
		match_status = "Matched" if (exp_qty > 0 and already < exp_qty) else "Unexpected"

		session.append("scans", {
			"item_code": item_code,
			"barcode_or_epc": code,
			"scanned_at": now_datetime(),
			"match_status": match_status,
			"item_name": info.get("item_name"),
			"item_image": info.get("image"),
			"valuation_rate": info.get("valuation_rate"),
		})
		session.scanned_count += 1

		if match_status == "Matched":
			scanned_per_item[item_code] = already + 1

		results.append({
			"item_code": item_code,
			"item_name": info.get("item_name"),
			"barcode_or_epc": code,
			"match_status": match_status,
		})

	session.save(ignore_permissions=True)

	_log_audit_event(
		"audit_scan_batch",
		session_name,
		details=f"Batch scan: {len(new_codes)} new, {duplicates_skipped} duplicates skipped",
	)

	return {
		"success": True,
		"total_submitted": len(new_codes),
		"duplicates_skipped": duplicates_skipped,
		"results": results,
	}


# ---------------------------------------------------------------------------
# Get Audit Progress (real-time polling endpoint)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_audit_progress(session_name: str) -> dict:
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	session = frappe.get_doc("Case Audit Session", session_name)
	_check_permission(session_name)

	# Count by status
	counts = {"matched": 0, "unexpected": 0, "missing": 0, "duplicates": 0}
	for s in session.scans:
		if s.match_status == "Matched":
			counts["matched"] += 1
		elif s.match_status == "Unexpected":
			counts["unexpected"] += 1
		elif s.match_status == "Missing":
			counts["missing"] += 1
		if s.is_duplicate:
			counts["duplicates"] += 1

	# Recent scans (last 20)
	recent_scans = frappe.get_all(
		"Case Audit Scan",
		filters={"parent": session_name},
		fields=["item_code", "item_name", "barcode_or_epc", "match_status", "scanned_at",
		        "item_image", "valuation_rate", "is_duplicate"],
		order_by="scanned_at desc",
		limit=20,
	)

	# Missing items (expected but not fully scanned)
	expected_items_data = _get_expected_items(session.store_location)

	scanned_per_item = {}
	for s in session.scans:
		if s.match_status == "Matched" and s.item_code:
			scanned_per_item[s.item_code] = scanned_per_item.get(s.item_code, 0) + 1

	missing_items = []
	for expected in expected_items_data:
		scanned = scanned_per_item.get(expected.item_code, 0)
		if scanned < expected.actual_qty:
			missing_items.append({
				"item_code": expected.item_code,
				"item_name": expected.item_name,
				"image": expected.image,
				"expected_qty": expected.actual_qty,
				"scanned_qty": scanned,
				"short_qty": expected.actual_qty - scanned,
				"valuation_rate": expected.valuation_rate,
			})

	# Unexpected items (scanned but not expected in warehouse)
	unexpected_items = []
	for s in session.scans:
		if s.match_status == "Unexpected" and s.item_code:
			unexpected_items.append({
				"item_code": s.item_code,
				"item_name": s.item_name,
				"barcode_or_epc": s.barcode_or_epc,
				"valuation_rate": s.valuation_rate,
			})

	# Value tracking
	total_value_scanned = sum(
		(s.valuation_rate or 0) for s in session.scans if s.match_status == "Matched"
	)

	return {
		"session": {
			"name": session.name,
			"status": session.status,
			"store_location": session.store_location,
			"auditor": session.auditor,
			"audit_type": session.audit_type,
			"expected_count": session.expected_count,
			"scanned_count": session.scanned_count,
			"total_value_expected": session.total_value_expected,
			"total_value_scanned": total_value_scanned,
			"total_value_discrepancy": (session.total_value_expected or 0) - total_value_scanned,
			"started_at": str(session.started_at) if session.started_at else None,
			"completed_at": str(session.completed_at) if session.completed_at else None,
		},
		"counts": counts,
		"recent_scans": recent_scans,
		"missing_items": missing_items,
		"unexpected_items": unexpected_items,
	}


# ---------------------------------------------------------------------------
# Get Audit History
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_audit_history(
	warehouse: str | None = None,
	status: str | None = None,
	from_date: str | None = None,
	to_date: str | None = None,
	page: int = 1,
	page_size: int = 20,
) -> dict:
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	filters = {}
	if warehouse:
		filters["store_location"] = warehouse
	if status:
		filters["status"] = status
	if from_date:
		filters["started_at"] = [">=", from_date]
	if to_date:
		if "started_at" in filters:
			filters["started_at"] = ["between", [from_date, to_date]]
		else:
			filters["started_at"] = ["<=", to_date]

	total = frappe.db.count("Case Audit Session", filters=filters)
	sessions = frappe.get_all(
		"Case Audit Session",
		filters=filters,
		fields=[
			"name", "store_location", "auditor", "audit_type", "status",
			"expected_count", "scanned_count", "started_at", "completed_at",
			"total_value_expected", "total_value_scanned", "total_value_discrepancy",
		],
		order_by="started_at desc",
		start=(cint(page) - 1) * cint(page_size),
		limit=cint(page_size),
	)

	return {
		"success": True,
		"total": total,
		"page": cint(page),
		"page_size": cint(page_size),
		"sessions": sessions,
	}


# ---------------------------------------------------------------------------
# Export Audit Results as CSV
# ---------------------------------------------------------------------------

@frappe.whitelist()
def export_audit_results(session_name: str) -> dict:
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	session = frappe.get_doc("Case Audit Session", session_name)
	_check_permission(session_name)

	import csv
	import os

	filename = f"audit_results_{session.name.replace(' ', '_')}.csv"
	filepath = frappe.get_site_path("private", "files", filename)

	with open(filepath, "w", newline="") as f:
		writer = csv.writer(f)
		writer.writerow(["Item Code", "Item Name", "Barcode/EPC", "Match Status",
		                  "Scanned At", "Valuation Rate", "Is Duplicate"])

		for s in session.scans:
			writer.writerow([
				s.item_code or "",
				s.item_name or "",
				s.barcode_or_epc or "",
				s.match_status,
				str(s.scanned_at) if s.scanned_at else "",
				s.valuation_rate or 0,
				"Yes" if s.is_duplicate else "No",
			])

		# Summary rows
		writer.writerow([])
		writer.writerow(["Summary"])
		writer.writerow(["Expected Count", session.expected_count])
		writer.writerow(["Scanned Count", session.scanned_count])
		writer.writerow(["Total Value Expected", session.total_value_expected or 0])
		writer.writerow(["Total Value Scanned", session.total_value_scanned or 0])
		writer.writerow(["Total Value Discrepancy", session.total_value_discrepancy or 0])
		writer.writerow(["Status", session.status])

	file_doc = frappe.new_doc("File")
	file_doc.file_name = filename
	file_doc.file_url = f"/private/files/{filename}"
	file_doc.is_private = 1
	file_doc.attached_to_doctype = "Case Audit Session"
	file_doc.attached_to_name = session.name
	file_doc.insert(ignore_permissions=True)

	return {"success": True, "file_url": file_doc.file_url, "filename": filename}


# ---------------------------------------------------------------------------
# Cancel Audit
# ---------------------------------------------------------------------------

@frappe.whitelist()
def cancel_audit(session_name: str) -> dict:
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	session = frappe.get_doc("Case Audit Session", session_name)
	_check_permission(session_name)

	if session.status not in ("Draft", "In Progress"):
		frappe.throw(_("Can only cancel Draft or In Progress sessions."))

	session.status = "Cancelled"
	session.cancelled_at = now_datetime()
	session.save(ignore_permissions=True)

	_log_audit_event(
		"audit_cancelled",
		session_name,
		details=f"Audit {session_name} cancelled by {frappe.session.user}",
	)

	return {"success": True, "status": "Cancelled"}


# ---------------------------------------------------------------------------
# Finalize Audit
# ---------------------------------------------------------------------------

@frappe.whitelist()
def finalize_audit(session_name: str) -> dict:
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	session = frappe.get_doc("Case Audit Session", session_name)
	_check_permission(session_name)

	if session.status not in ("Draft", "In Progress"):
		frappe.throw(_("Can only finalize Draft or In Progress sessions."))

	expected_items_data = _get_expected_items(session.store_location)

	missing_items = []
	for expected in expected_items_data:
		item_code = expected.item_code
		expected_qty = expected.actual_qty

		scanned_qty = len(
			[s for s in session.scans if s.item_code == item_code and s.match_status == "Matched"]
		)
		if scanned_qty < expected_qty:
			missing_qty = expected_qty - scanned_qty
			item_name = expected.item_name
			missing_items.append({"item_code": item_code, "qty": missing_qty})
			for _ in range(int(missing_qty)):
				session.append(
					"scans",
					{
						"item_code": item_code,
						"item_name": item_name,
						"match_status": "Missing",
						"scanned_at": now_datetime(),
					},
				)

	# Compute value tracking
	total_value_scanned = sum(
		(s.valuation_rate or 0) for s in session.scans if s.match_status == "Matched"
	)
	session.total_value_scanned = total_value_scanned
	session.total_value_discrepancy = (session.total_value_expected or 0) - total_value_scanned

	session.completed_at = now_datetime()

	if missing_items or any(s.match_status == "Unexpected" for s in session.scans):
		session.status = "Discrepancy"
	else:
		session.status = "Reconciled"

	session.submit()

	# Process shrinkage
	shrinkage_entry = None
	if missing_items:
		company = (
			frappe.defaults.get_user_default("Company")
			or frappe.db.get_single_value("Global Defaults", "default_company")
			or "Zevar Jewelers"
		)

		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Material Issue"
		se.company = company
		se.purpose = "Material Issue"
		se.remarks = f"Shrinkage detected in Case Audit {session.name}"

		for item in missing_items:
			se.append(
				"items",
				{"item_code": item["item_code"], "qty": item["qty"], "s_warehouse": session.store_location},
			)

		se.flags.ignore_permissions = True
		se.insert()
		se.submit()
		shrinkage_entry = se.name

	event_type = "shrinkage_detected" if missing_items else "audit_reconciled"
	_log_audit_event(
		event_type,
		session.name,
		details=(
			f"Audit {session.name} finalized: {session.status}, "
			f"expected={session.expected_count}, scanned={session.scanned_count}, "
			f"discrepancy=${session.total_value_discrepancy:,.2f}, "
			f"shrinkage_entry={shrinkage_entry}"
		),
	)

	return {
		"success": True,
		"status": session.status,
		"missing_count": len(missing_items),
		"shrinkage_entry": shrinkage_entry,
		"total_value_expected": session.total_value_expected,
		"total_value_scanned": session.total_value_scanned,
		"total_value_discrepancy": session.total_value_discrepancy,
	}
