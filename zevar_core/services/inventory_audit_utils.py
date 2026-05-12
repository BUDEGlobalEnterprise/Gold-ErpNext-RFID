import json

import frappe
from frappe.utils import flt, now_datetime


def _reconcile_audit(session_doc):
	scanned_counts = {}
	has_unexpected = False
	total_value_scanned = 0.0
	item_codes = set()
	unexpected_items = []

	for scan in session_doc.scans:
		if scan.item_code:
			item_codes.add(scan.item_code)
			if scan.match_status == "Matched":
				scanned_counts[scan.item_code] = scanned_counts.get(scan.item_code, 0) + 1
			elif scan.match_status == "Unexpected":
				has_unexpected = True
				unexpected_items.append(scan.item_code)

	expected_items = frappe.db.sql(
		"""
		select item_code, actual_qty
		from `tabBin`
		where warehouse = %s and actual_qty > 0
	""",
		(session_doc.store_location,),
		as_dict=True,
	)

	for exp in expected_items:
		item_codes.add(exp.item_code)

	# Build a rate map
	item_rates = {}
	if item_codes:
		items = frappe.get_all(
			"Item",
			filters={"name": ["in", list(item_codes)]},
			fields=["name", "standard_rate", "valuation_rate"],
		)
		for itm in items:
			item_rates[itm.name] = flt(itm.standard_rate) or flt(itm.valuation_rate)

	for item_code, count in scanned_counts.items():
		rate = item_rates.get(item_code)
		if rate is None:
			frappe.log_error(f"Missing rate for {item_code}", "Audit Reconciliation Warning")
			rate = 0.0
		total_value_scanned += count * rate

	missing_items = []
	missing_count = 0
	total_value_discrepancy = 0.0

	for exp in expected_items:
		expected_qty = flt(exp.actual_qty)
		scanned_qty = scanned_counts.get(exp.item_code, 0)

		if scanned_qty < expected_qty:
			missing_qty = expected_qty - scanned_qty
			missing_items.append({"item_code": exp.item_code, "qty": missing_qty})
			missing_count += missing_qty
			rate = item_rates.get(exp.item_code)
			if rate is None:
				frappe.log_error(
					f"Missing valuation rate for expected item {exp.item_code}",
					"Audit Reconciliation Warning",
				)
				rate = 0.0
			total_value_discrepancy += missing_qty * rate

	# Add unexpected items to discrepancy value
	from collections import Counter

	unexpected_counts = Counter(unexpected_items)
	for item_code, count in unexpected_counts.items():
		rate = item_rates.get(item_code)
		if rate is not None:
			total_value_discrepancy -= count * rate

	return missing_items, missing_count, total_value_scanned, total_value_discrepancy, has_unexpected


def process_shrinkage_async(session, missing_items_json, store_location):
	try:
		raw_missing = json.loads(missing_items_json)
		missing_items = []

		# Bulk fetch Bin quantities
		item_codes = [m["item_code"] for m in raw_missing]
		bin_qtys = {}
		if item_codes:
			bins = frappe.get_all(
				"Bin",
				filters={"item_code": ["in", item_codes], "warehouse": store_location},
				fields=["item_code", "actual_qty"],
			)
			for b in bins:
				bin_qtys[b.item_code] = flt(b.actual_qty)

		for m in raw_missing:
			actual_qty_val = bin_qtys.get(m["item_code"])
			if actual_qty_val is None:
				valid_qty = flt(m["qty"])
			else:
				valid_qty = min(flt(m["qty"]), actual_qty_val)

			if valid_qty > 0:
				missing_items.append({"item_code": m["item_code"], "qty": valid_qty})

		if not missing_items:
			return

		# Create Stock Entry
		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Material Issue"
		se.company = frappe.defaults.get_user_default("company") or "Zevar Jewelers"
		cost_center = frappe.get_cached_value("Company", se.company, "cost_center")

		# Try to find a shrinkage warehouse, else default to material issue without target warehouse
		shrinkage_warehouse = frappe.db.get_value(
			"Warehouse", {"warehouse_name": ["like", "%Shrinkage%"]}, "name"
		)
		if shrinkage_warehouse:
			se.stock_entry_type = "Material Transfer"

		for missing in missing_items:
			item_row = {
				"item_code": missing["item_code"],
				"qty": missing["qty"],
				"s_warehouse": store_location,
				"cost_center": cost_center,
			}
			if shrinkage_warehouse:
				item_row["t_warehouse"] = shrinkage_warehouse
			se.append("items", item_row)

		se.insert()
		se.submit()

	except Exception:
		frappe.log_error(title=f"Error processing shrinkage for {session}", message=frappe.get_traceback())


def notify_shrinkage_async(session, missing_items_json, display_case):
	try:
		missing_items = json.loads(missing_items_json)
		owners = frappe.get_all(
			"Has Role", filters={"role": "Owner", "parenttype": "User"}, fields=["parent"]
		)
		recipients = [o.parent for o in owners]
		if recipients:
			items_html = "<br>".join(
				[
					f"{frappe.utils.escape_html(str(m['qty']))}x {frappe.utils.escape_html(str(m['item_code']))}"
					for m in missing_items
				]
			)
			frappe.sendmail(
				recipients=recipients,
				subject=f"Shrinkage Detected in Case {display_case}",
				message=f"Missing items during audit session {session}: <br>" + items_html,
			)
	except Exception:
		frappe.log_error(title=f"Error sending shrinkage alert for {session}", message=frappe.get_traceback())


def notify_variance_escalation(session, store_location, missing_items_json, freeze_reason):
	"""Notify owners and managers when a store is frozen due to audit variance."""
	try:
		missing_items = json.loads(missing_items_json)
		recipients = []

		# Get owners
		owners = frappe.get_all(
			"Has Role", filters={"role": "Owner", "parenttype": "User"}, fields=["parent"]
		)
		recipients.extend([o.parent for o in owners])

		# Get store managers
		managers = frappe.get_all(
			"Has Role", filters={"role": "Sales Manager", "parenttype": "User"}, fields=["parent"]
		)
		recipients.extend([m.parent for m in managers])

		recipients = list(set(recipients))
		if recipients:
			items_html = "<br>".join(
				[
					f"{frappe.utils.escape_html(str(m.get('qty', 1)))}x {frappe.utils.escape_html(str(m.get('item_code', 'Unknown')))}"
					for m in missing_items
				]
			)
			frappe.sendmail(
				recipients=recipients,
				subject=f"URGENT: Store {store_location} Frozen - Audit Variance Exceeded",
				message=f"""
				<h3>Audit Variance Escalation</h3>
				<p><strong>Store:</strong> {frappe.utils.escape_html(store_location)}</p>
				<p><strong>Session:</strong> {frappe.utils.escape_html(session)}</p>
				<p><strong>Reason:</strong> {frappe.utils.escape_html(freeze_reason)}</p>
				<p><strong>Missing Items:</strong></p>
				<p>{items_html}</p>
				<p><strong>Reservations and transfers are frozen until a manager approves the variance.</strong></p>
				""",
			)
	except Exception:
		frappe.log_error(
			title=f"Error sending variance escalation for {session}", message=frappe.get_traceback()
		)


def quarantine_unexpected_items(session, store_location):
	"""Move unexpected scan items to quarantine warehouse via Stock Entry."""
	try:
		session_doc = frappe.get_doc("Case Audit Session", session)
		unexpected = [s for s in session_doc.scans if s.match_status == "Unexpected" and s.item_code]

		if not unexpected:
			return

		# Find or create quarantine warehouse
		quarantine_wh = frappe.db.get_value(
			"Warehouse",
			{"warehouse_name": ["like", "%Quarantine%"], "name": ["like", f"%{store_location}%"]},
			"name",
		) or frappe.db.get_value("Warehouse", {"warehouse_name": ["like", "%Quarantine%"]}, "name")

		if not quarantine_wh:
			frappe.log_error(f"No Quarantine warehouse found for {store_location}", "Audit Quarantine")
			return

		# Group by item_code
		from collections import Counter

		item_counts = Counter(s.item_code for s in unexpected if s.item_code)

		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Material Transfer"
		se.company = frappe.defaults.get_user_default("company") or "Zevar Jewelers"
		cost_center = frappe.get_cached_value("Company", se.company, "cost_center")

		for item_code, qty in item_counts.items():
			se.append(
				"items",
				{
					"item_code": item_code,
					"qty": qty,
					"s_warehouse": store_location,
					"t_warehouse": quarantine_wh,
					"cost_center": cost_center,
				},
			)

		se.insert()
		se.submit()

		_log_audit_event(
			"unexpected_quarantined",
			"Inventory",
			session,
			f"Moved {len(item_counts)} unexpected items to quarantine from session {session}",
		)
	except Exception:
		frappe.log_error(
			title=f"Error quarantining unexpected items for {session}", message=frappe.get_traceback()
		)


def _log_audit_event(event_type, category, reference_document, details):
	audit_log = frappe.new_doc("POS Audit Log")
	audit_log.user = frappe.session.user or "Administrator"
	audit_log.event_type = event_type
	audit_log.category = category
	audit_log.reference_type = "Case Audit Session"
	audit_log.reference_document = reference_document
	audit_log.details = details
	audit_log.insert(ignore_permissions=True)


def execute_submit_scan(session_doc, barcode_or_epc):
	# Check for duplicates
	existing_scan = frappe.db.exists(
		"Case Audit Scan", {"parent": session_doc.name, "barcode_or_epc": barcode_or_epc}
	)
	if existing_scan:
		return {
			"success": True,
			"item_code": "",
			"match_status": "Duplicate",
			"scanned_count": session_doc.scanned_count,
		}

	# Find item by barcode or epc
	item_code = frappe.db.get_value("Item", {"custom_rfid_epc": barcode_or_epc}, "name")
	if not item_code:
		# Also check Item Barcode
		item_code = frappe.db.get_value(
			"Item Barcode", {"barcode": barcode_or_epc, "parenttype": "Item"}, "parent"
		)

	match_status = "Unexpected"
	item_name = ""
	valuation_rate = 0.0

	if item_code:
		item_data = frappe.db.get_value(
			"Item", item_code, ["item_name", "standard_rate", "valuation_rate"], as_dict=True
		)
		item_name = item_data.item_name
		valuation_rate = flt(item_data.standard_rate) or flt(item_data.valuation_rate)

		# Check if item is expected in this warehouse
		actual_qty = frappe.db.get_value(
			"Bin", {"item_code": item_code, "warehouse": session_doc.store_location}, "actual_qty"
		)

		if actual_qty and flt(actual_qty) > 0:
			match_status = "Matched"

	# Append to scans efficiently without saving the entire parent document
	scan_doc = frappe.new_doc("Case Audit Scan")
	scan_doc.parent = session_doc.name
	scan_doc.parenttype = "Case Audit Session"
	scan_doc.parentfield = "scans"
	scan_doc.item_code = item_code
	scan_doc.barcode_or_epc = barcode_or_epc
	scan_doc.scanned_at = now_datetime()
	scan_doc.match_status = match_status
	scan_doc.insert(ignore_permissions=True)

	session_doc.db_set("scanned_count", session_doc.scanned_count + 1)

	return {
		"success": True,
		"item_code": item_code,
		"item_name": item_name,
		"valuation_rate": valuation_rate,
		"match_status": match_status,
		"scanned_count": session_doc.scanned_count,
	}


def execute_batch_scan(session_doc, epcs):
	results = []
	duplicates_skipped = 0

	if session_doc.status != "In Progress":
		frappe.throw("Audit session is not in progress.")

	# Process EPCs efficiently
	existing_epcs = set(
		frappe.db.get_all("Case Audit Scan", {"parent": session_doc.name}, pluck="barcode_or_epc")
	)

	# Filter out duplicates first
	unique_new_epcs = []
	for epc in epcs:
		if epc in existing_epcs:
			duplicates_skipped += 1
		elif epc not in unique_new_epcs:
			unique_new_epcs.append(epc)

	if not unique_new_epcs:
		return {
			"success": True,
			"total_submitted": len(epcs),
			"duplicates_skipped": duplicates_skipped,
			"results": [],
		}

	# Bulk fetch Items
	items = frappe.get_all(
		"Item", filters={"custom_rfid_epc": ["in", unique_new_epcs]}, fields=["name", "custom_rfid_epc"]
	)
	epc_to_item = {itm.custom_rfid_epc: itm.name for itm in items}

	# Bulk fetch Bins
	item_codes = list(epc_to_item.values())
	bin_qtys = {}
	if item_codes:
		bins = frappe.get_all(
			"Bin",
			filters={"item_code": ["in", item_codes], "warehouse": session_doc.store_location},
			fields=["item_code", "actual_qty"],
		)
		for b in bins:
			bin_qtys[b.item_code] = flt(b.actual_qty)

	for epc in unique_new_epcs:
		item_code = epc_to_item.get(epc)
		match_status = "Matched" if item_code and bin_qtys.get(item_code, 0) > 0 else "Unexpected"

		session_doc.append(
			"scans",
			{
				"item_code": item_code,
				"barcode_or_epc": epc,
				"match_status": match_status,
				"scanned_at": now_datetime(),
			},
		)

		results.append({"epc": epc, "match_status": match_status, "item_code": item_code})

	if unique_new_epcs:
		session_doc.scanned_count += len(unique_new_epcs)
		session_doc.flags.ignore_validate_update_after_submit = True
		session_doc.save(ignore_permissions=True)

	return {
		"success": True,
		"total_submitted": len(epcs),
		"duplicates_skipped": duplicates_skipped,
		"results": results,
	}


def generate_discrepancy_records(session_doc):
	"""Generate Audit Discrepancy records based on scan results."""
	missing_items, missing_count, total_value_scanned, total_value_discrepancy, has_unexpected = (
		_reconcile_audit(session_doc)
	)

	# Create records for missing items
	for m in missing_items:
		item_code = m["item_code"]
		if not frappe.db.exists("Audit Discrepancy", {"audit_session": session_doc.name, "item_code": item_code}):
			doc = frappe.new_doc("Audit Discrepancy")
			doc.audit_session = session_doc.name
			doc.display_case = session_doc.display_case
			doc.item_code = item_code
			
			bin_qty = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": session_doc.store_location}, "actual_qty") or 0
			doc.expected_qty = bin_qty
			doc.found_qty = bin_qty - m["qty"]
			doc.status = "Pending"
			doc.discrepancy_type = "Missing"
			doc.insert(ignore_permissions=True)

	# Create records for unexpected items
	if has_unexpected:
		unexpected_scans = [s for s in session_doc.scans if s.match_status == "Unexpected"]
		from collections import Counter
		item_counts = Counter(s.item_code for s in unexpected_scans if s.item_code)

		for item_code, qty in item_counts.items():
			if not item_code: continue
			if not frappe.db.exists("Audit Discrepancy", {"audit_session": session_doc.name, "item_code": item_code}):
				doc = frappe.new_doc("Audit Discrepancy")
				doc.audit_session = session_doc.name
				doc.display_case = session_doc.display_case
				doc.item_code = item_code
				doc.expected_qty = 0
				doc.found_qty = qty
				doc.status = "Pending"
				doc.discrepancy_type = "Wrong Location"
				doc.insert(ignore_permissions=True)
