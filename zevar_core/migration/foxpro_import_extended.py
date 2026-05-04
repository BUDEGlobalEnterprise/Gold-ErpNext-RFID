from datetime import datetime

import frappe

from zevar_core.migration.foxpro_import import (
	_ensure_designation,
	_get_default_customer,
	_get_default_item,
	_get_or_create_item_group,
	_set_custom_field,
	clean_float,
	clean_int,
	clean_str,
	find_dbf,
	format_date,
	read_dbf,
)

REPAIR_STATUS_MAP = {
	"R": "Received",
	"I": "In Progress",
	"C": "Completed",
	"D": "Delivered",
	"X": "Cancelled",
}
TENDER_MODE_MAP = {
	"CA": "Cash",
	"CK": "Check",
	"VI": "Visa",
	"MC": "Mastercard",
	"AM": "Amex",
	"DI": "Discover",
}

# ──────────────────────────────────────────────────
# Stone Cuts (from CUTS.DBF)
# ──────────────────────────────────────────────────


def import_stone_cuts(backup_path: str, dry_run: bool = False) -> dict:
	"""Import stone cut types from CUTS.DBF as Item Attribute values."""
	stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}

	dbf_path = find_dbf(backup_path, "CUTS.DBF")
	if not dbf_path:
		stats["errors"].append("CUTS.DBF not found")
		return stats

	records = read_dbf(dbf_path)
	stats["total"] = len(records)

	attr_name = "Cut"
	if not dry_run and not frappe.db.exists("Item Attribute", attr_name):
		attr_doc = frappe.new_doc("Item Attribute")
		attr_doc.attribute_name = attr_name
		attr_doc.numeric_values = 0
		attr_doc.insert(ignore_permissions=True)

	existing_values = set()
	if not dry_run and frappe.db.exists("Item Attribute", attr_name):
		attr_doc = frappe.get_doc("Item Attribute", attr_name)
		for av in attr_doc.item_attribute_values:
			existing_values.add(av.attribute_value)

	abbr_counter = len(existing_values)
	for record in records:
		try:
			value = clean_str(record.get("cut"))
			if not value or value in existing_values:
				stats["skipped"] += 1
				continue

			if dry_run:
				stats["imported"] += 1
				continue

			abbr_counter += 1
			abbr = f"CU{abbr_counter:02d}"

			attr_doc = frappe.get_doc("Item Attribute", attr_name)
			attr_doc.append("item_attribute_values", {"attribute_value": value, "abbr": abbr})
			attr_doc.save(ignore_permissions=True)
			existing_values.add(value)
			stats["imported"] += 1

		except Exception as e:
			stats["errors"].append(f"Cut {record.get('cut', '?')}: {str(e)[:100]}")

	if not dry_run:
		frappe.db.commit()  # nosemgrep
	return stats


# ──────────────────────────────────────────────────
# Stone Types (from TYPES.DBF)
# ──────────────────────────────────────────────────


def import_stone_types(backup_path: str, dry_run: bool = False) -> dict:
	"""Import stone/gem types from TYPES.DBF as Item Attribute values."""
	stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}

	dbf_path = find_dbf(backup_path, "TYPES.DBF")
	if not dbf_path:
		stats["errors"].append("TYPES.DBF not found")
		return stats

	records = read_dbf(dbf_path)
	stats["total"] = len(records)

	attr_name = "Stone Type"
	if not dry_run and not frappe.db.exists("Item Attribute", attr_name):
		attr_doc = frappe.new_doc("Item Attribute")
		attr_doc.attribute_name = attr_name
		attr_doc.numeric_values = 0
		attr_doc.insert(ignore_permissions=True)

	existing_values = set()
	if not dry_run and frappe.db.exists("Item Attribute", attr_name):
		attr_doc = frappe.get_doc("Item Attribute", attr_name)
		for av in attr_doc.item_attribute_values:
			existing_values.add(av.attribute_value)

	abbr_counter = len(existing_values)
	for record in records:
		try:
			value = clean_str(record.get("type"))
			if not value or value in existing_values:
				stats["skipped"] += 1
				continue

			if dry_run:
				stats["imported"] += 1
				continue

			abbr_counter += 1
			abbr = f"ST{abbr_counter:02d}"

			attr_doc = frappe.get_doc("Item Attribute", attr_name)
			attr_doc.append("item_attribute_values", {"attribute_value": value, "abbr": abbr})
			attr_doc.save(ignore_permissions=True)
			existing_values.add(value)
			stats["imported"] += 1

		except Exception as e:
			stats["errors"].append(f"Stone Type {record.get('type', '?')}: {str(e)[:100]}")

	if not dry_run:
		frappe.db.commit()  # nosemgrep
	return stats


# ──────────────────────────────────────────────────
# Departments (from dept.dbf)
# ──────────────────────────────────────────────────


def import_departments(backup_path: str, dry_run: bool = False) -> dict:
	"""Import departments from dept.dbf as Item Groups."""
	stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}

	dbf_path = find_dbf(backup_path, "dept.dbf")
	if not dbf_path:
		stats["errors"].append("dept.dbf not found")
		return stats

	records = read_dbf(dbf_path)
	stats["total"] = len(records)

	for record in records:
		try:
			# COLUMN1=abbrev, COLUMN2=full name
			fullname = clean_str(record.get("column2"))
			abbrev = clean_str(record.get("column1"))
			if not fullname and not abbrev:
				stats["skipped"] += 1
				continue
			# Skip header row
			if fullname == "Fullname of Dept" or abbrev == "Dept Abbrev":
				stats["skipped"] += 1
				continue

			name = fullname or abbrev
			if frappe.db.exists("Item Group", name):
				stats["skipped"] += 1
				continue

			if dry_run:
				stats["imported"] += 1
				continue

			doc = frappe.new_doc("Item Group")
			doc.item_group_name = name
			doc.parent_item_group = "All Item Groups"
			doc.is_group = 0
			doc.insert(ignore_permissions=True, ignore_mandatory=True)
			stats["imported"] += 1

		except Exception as e:
			stats["errors"].append(f"Dept {record.get('column1', '?')}: {str(e)[:100]}")

	if not dry_run:
		frappe.db.commit()  # nosemgrep
	return stats


# ──────────────────────────────────────────────────
# Subcategories (from subcat.dbf)
# ──────────────────────────────────────────────────


def import_subcategories(backup_path: str, dry_run: bool = False) -> dict:
	"""Import subcategories from subcat.dbf as Item Groups."""
	stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}

	dbf_path = find_dbf(backup_path, "subcat.dbf")
	if not dbf_path:
		stats["errors"].append("subcat.dbf not found")
		return stats

	records = read_dbf(dbf_path)
	stats["total"] = len(records)

	for record in records:
		try:
			cdesc = clean_str(record.get("cdesc"))
			code = clean_str(record.get("code"))
			if not cdesc and not code:
				stats["skipped"] += 1
				continue

			name = cdesc or code
			if frappe.db.exists("Item Group", name):
				stats["skipped"] += 1
				continue

			if dry_run:
				stats["imported"] += 1
				continue

			doc = frappe.new_doc("Item Group")
			doc.item_group_name = name
			doc.parent_item_group = "All Item Groups"
			doc.is_group = 0
			doc.insert(ignore_permissions=True, ignore_mandatory=True)
			stats["imported"] += 1

		except Exception as e:
			stats["errors"].append(f"Subcat {record.get('code', '?')}: {str(e)[:100]}")

	if not dry_run:
		frappe.db.commit()  # nosemgrep
	return stats


# ──────────────────────────────────────────────────
# Tax Rates (from taxrate.dbf)
# ──────────────────────────────────────────────────


def import_tax_rates(backup_path: str, dry_run: bool = False) -> dict:
	"""Import tax rates from taxrate.dbf as Sales Taxes and Charges Templates."""
	stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}

	dbf_path = find_dbf(backup_path, "taxrate.dbf")
	if not dbf_path:
		stats["errors"].append("taxrate.dbf not found")
		return stats

	records = read_dbf(dbf_path)
	stats["total"] = len(records)

	company = frappe.defaults.get_global_default("company") if not dry_run else "Default"

	for record in records:
		try:
			taxcode = clean_str(record.get("taxcode"))
			descript = clean_str(record.get("descript"))
			rate = clean_float(record.get("rate"))

			if not taxcode:
				stats["skipped"] += 1
				continue

			title = descript or f"Tax {taxcode}"

			if frappe.db.exists("Sales Taxes and Charges Template", {"title": title}):
				stats["skipped"] += 1
				continue

			if dry_run:
				stats["imported"] += 1
				continue

			doc = frappe.new_doc("Sales Taxes and Charges Template")
			doc.title = title
			doc.company = company
			if rate > 0:
				doc.append(
					"taxes",
					{
						"charge_type": "On Net Total",
						"account_head": _get_or_create_tax_account(company),
						"rate": rate,
						"description": descript or title,
					},
				)
			doc.insert(ignore_permissions=True, ignore_mandatory=True)
			stats["imported"] += 1

		except Exception as e:
			stats["errors"].append(f"Tax {record.get('taxcode', '?')}: {str(e)[:100]}")

	if not dry_run:
		frappe.db.commit()  # nosemgrep
	return stats


def _get_or_create_tax_account(company: str) -> str:
	"""Get or create a default tax account."""
	existing = frappe.db.get_value("Account", {"account_type": "Tax", "company": company}, "name")
	if existing:
		return existing
	# Fallback: find any account with 'tax' in the name
	existing = frappe.db.get_value("Account", {"account_name": ["like", "%tax%"], "company": company}, "name")
	if existing:
		return existing
	# Last resort: return first income account
	return frappe.db.get_value("Account", {"root_type": "Liability", "company": company}, "name") or "Tax"


# ──────────────────────────────────────────────────
# Slush Items (from SLUSH.DBF - same schema as inventor.DBF)
# ──────────────────────────────────────────────────


def import_slush_items(backup_path: str, dry_run: bool = False) -> dict:
	"""Import slush/special items from SLUSH.DBF (same schema as inventor.DBF)."""
	stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}

	dbf_path = find_dbf(backup_path, "SLUSH.DBF")
	if not dbf_path:
		stats["errors"].append("SLUSH.DBF not found")
		return stats

	# Reuse inventory import logic by reading the DBF and processing each record
	records = read_dbf(dbf_path)
	stats["total"] = len(records)

	for idx, record in enumerate(records):
		try:
			barcode = clean_str(record.get("barcode"))
			stockno = clean_str(record.get("stockno"))
			descript = clean_str(record.get("descript"))
			abr = clean_str(record.get("abr"))

			if not barcode and not stockno:
				stats["skipped"] += 1
				continue

			item_code = (
				barcode if barcode else f"SLUSH-{abr}-{stockno}" if abr and stockno else f"SLUSH-{stockno}"
			)
			item_name = descript if descript else item_code

			if frappe.db.exists("Item", item_code):
				stats["skipped"] += 1
				continue

			if dry_run:
				stats["imported"] += 1
				continue

			category = clean_str(record.get("category"))
			clean_str(record.get("goldtype"))

			doc = frappe.new_doc("Item")
			doc.item_code = item_code
			doc.item_name = item_name[:140]
			doc.stock_uom = "Nos"
			doc.is_stock_item = 1

			if category:
				doc.item_group = _get_or_create_item_group(category)

			cost = clean_float(record.get("cost"))
			asklow = clean_float(record.get("asklow"))
			askhigh = clean_float(record.get("askhigh"))
			if asklow > 0:
				doc.standard_rate = asklow
			elif askhigh > 0:
				doc.standard_rate = askhigh
			if cost > 0:
				doc.valuation_rate = cost

			_set_custom_field(doc, "custom_source", "SLUSH")
			_set_custom_field(doc, "custom_legacy_abr", abr)
			_set_custom_field(doc, "custom_legacy_stockno", stockno)

			doc.insert(ignore_permissions=True, ignore_mandatory=True)
			stats["imported"] += 1

			if (idx + 1) % 50 == 0:
				frappe.db.commit()  # nosemgrep

		except Exception as e:
			stats["errors"].append(f"Slush {record.get('barcode', '?')}: {str(e)[:100]}")

	if not dry_run:
		frappe.db.commit()  # nosemgrep
	return stats


# ──────────────────────────────────────────────────
# System Constants (from CONSTANT.DBF)
# ──────────────────────────────────────────────────


def import_system_constants(backup_path: str, dry_run: bool = False) -> dict:
	"""Import system constants from CONSTANT.DBF into Gold Settings."""
	stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}

	dbf_path = find_dbf(backup_path, "CONSTANT.DBF")
	if not dbf_path:
		stats["errors"].append("CONSTANT.DBF not found")
		return stats

	records = read_dbf(dbf_path)
	stats["total"] = len(records)

	if not records:
		return stats

	# Use first non-empty record
	constant = records[0]

	if dry_run:
		stats["imported"] = 1
		return stats

	try:
		if frappe.db.exists("DocType", "Gold Settings"):
			frappe.get_single("Gold Settings")
			# Store spot gold/silver prices as gold rate logs
			spot_gold = clean_float(constant.get("spotgold"))
			if spot_gold > 0:
				if not frappe.db.exists("Gold Rate Log", {"gold_price": spot_gold}):
					gr = frappe.new_doc("Gold Rate Log")
					gr.gold_price = spot_gold
					gr.currency = "USD"
					gr.source = "Legacy Import (CONSTANT.DBF)"
					gr.fetch_time = frappe.utils.now_datetime()
					gr.insert(ignore_permissions=True, ignore_mandatory=True)

			spot_silver = clean_float(constant.get("spotsilver"))
			if spot_silver > 0:
				if not frappe.db.exists("Gold Rate Log", {"gold_price": spot_silver}):
					gr = frappe.new_doc("Gold Rate Log")
					gr.gold_price = spot_silver
					gr.currency = "USD"
					gr.source = "Legacy Silver Price"
					gr.fetch_time = frappe.utils.now_datetime()
					gr.insert(ignore_permissions=True, ignore_mandatory=True)

			frappe.db.commit()  # nosemgrep

		stats["imported"] = 1
	except Exception as e:
		stats["errors"].append(f"Constants: {str(e)[:100]}")

	return stats


# ──────────────────────────────────────────────────
# Appraisals (from NEWAPPR.DBF - REWRITES existing import)
# ──────────────────────────────────────────────────


ITEM_TYPE_KEYWORDS = {
	"ring": "Ring",
	"band": "Ring",
	"eng": "Ring",
	"necklace": "Necklace",
	"pendant": "Pendant",
	"bracelet": "Bracelet",
	"earring": "Earring",
	"watch": "Watch",
	"chain": "Necklace",
	"bangle": "Bracelet",
	"eternity": "Ring",
}


def _guess_item_type(descript: str) -> str:
	"""Guess item type from description keywords."""
	desc_lower = (descript or "").lower()
	for kw, val in ITEM_TYPE_KEYWORDS.items():
		if kw in desc_lower:
			return val
	return "Other"


def _get_or_create_metal(metal_name: str) -> str | None:
	"""Get or create a Zevar Metal record by name."""
	if not metal_name:
		return None
	if frappe.db.exists("DocType", "Zevar Metal") and frappe.db.exists("Zevar Metal", metal_name):
		return metal_name
	try:
		if frappe.db.exists("DocType", "Zevar Metal"):
			doc = frappe.new_doc("Zevar Metal")
			doc.name = metal_name
			doc.insert(ignore_permissions=True, ignore_mandatory=True)
			return metal_name
	except Exception:
		pass
	return None


def import_appraisals(backup_path: str, dry_run: bool = False) -> dict:
	"""Import jewelry appraisals from NEWAPPR.DBF (147 records)."""
	stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}

	# Try NEWAPPR.DBF first (has actual data), fall back to 1APTERM1.DBF
	dbf_path = find_dbf(backup_path, "NEWAPPR.DBF") or find_dbf(backup_path, "1APTERM1.DBF")
	if not dbf_path:
		stats["errors"].append("NEWAPPR.DBF not found")
		return stats

	records = read_dbf(dbf_path)
	stats["total"] = len(records)

	if not records:
		return stats

	# Pre-fetch customer mapping
	customer_cache = {}
	for c in frappe.get_all("Customer", fields=["name", "customer_name"]):
		customer_cache[c.customer_name.lower()] = c.name

	# Get default appraiser
	default_appraiser = frappe.db.get_value("Employee", {"status": "Active"}, "name") or "Administrator"

	for i, record in enumerate(records):
		try:
			lastname = clean_str(record.get("lastname") or record.get("last"))
			firstname = clean_str(record.get("firstname") or record.get("first"))
			descript = clean_str(record.get("descript") or record.get("desc1"))
			stockno = clean_str(record.get("stockno"))

			if not descript and not stockno:
				stats["skipped"] += 1
				continue

			appraisal_id = str(clean_int(record.get("appraisal"))) or f"{i + 1:04d}"

			# Check by certificate_number or naming
			existing = frappe.db.get_value("Jewelry Appraisal", {"certificate_number": appraisal_id}, "name")
			if existing:
				stats["skipped"] += 1
				continue

			if dry_run:
				stats["imported"] += 1
				continue

			doc = frappe.new_doc("Jewelry Appraisal")

			# Resolve customer
			if firstname or lastname:
				cust_name = f"{firstname} {lastname}".strip()
				doc.customer = customer_cache.get(cust_name.lower(), _get_default_customer())

			doc.appraisal_date = format_date(record.get("transdate")) or frappe.utils.today()
			doc.appraiser = default_appraiser
			doc.status = "Completed"

			# Description
			desc_parts = [p for p in [descript, clean_str(record.get("desc2"))] if p]
			doc.item_description = " ".join(desc_parts)[:140] if desc_parts else descript or stockno
			doc.item_type = _guess_item_type(descript)

			# Metal
			metal_type = clean_str(record.get("metal_type"))
			if metal_type:
				resolved = _get_or_create_metal(metal_type)
				if resolved:
					doc.metal_type = resolved

			karat_type = clean_str(record.get("karat_type"))
			if karat_type and frappe.db.exists("Zevar Purity", karat_type):
				doc.metal_purity = karat_type

			weight = clean_float(record.get("weight"))
			if weight > 0:
				doc.total_weight_grams = weight

			est_value = clean_float(record.get("estvalue"))
			if est_value > 0:
				doc.appraised_value = est_value

			purchase = clean_float(record.get("purchase"))
			if purchase > 0:
				doc.replacement_value = purchase

			# Notes from memo
			apprtext = clean_str(record.get("apprtext"))
			if apprtext:
				doc.notes = apprtext

			doc.certificate_number = appraisal_id

			# Custom fields for stone data
			_set_custom_field(doc, "custom_legacy_stock_no", stockno)
			_set_custom_field(doc, "custom_legacy_abr", clean_str(record.get("abr")))
			_set_custom_field(doc, "custom_center_stone_weight", clean_float(record.get("centerwgt")))
			_set_custom_field(doc, "custom_center_stone_cut", clean_str(record.get("centercut")))
			_set_custom_field(doc, "custom_center_stone_type", clean_str(record.get("centertype")))
			_set_custom_field(doc, "custom_center_stone_clarity", clean_str(record.get("centerclar")))
			_set_custom_field(doc, "custom_center_stone_color", clean_str(record.get("centercol")))
			_set_custom_field(doc, "custom_side_stones_weight", clean_float(record.get("side_wgt")))
			_set_custom_field(doc, "custom_side_stones_qty", clean_int(record.get("side_qty")))
			_set_custom_field(doc, "custom_stones_count", clean_int(record.get("stones")))

			doc.insert(ignore_permissions=True, ignore_mandatory=True)
			stats["imported"] += 1

			if (i + 1) % 50 == 0:
				frappe.db.commit()  # nosemgrep

		except Exception as e:
			stats["errors"].append(f"Appraisal {i}: {str(e)[:100]}")

	if not dry_run:
		frappe.db.commit()  # nosemgrep
	return stats


# ──────────────────────────────────────────────────
# Receipt Line Items (from receipt.DBF)
# ──────────────────────────────────────────────────


def import_receipt_lines(backup_path: str, dry_run: bool = False) -> dict:
	"""Import receipt line items from receipt.DBF as Sales Invoice items."""
	stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}

	dbf_path = find_dbf(backup_path, "receipt.DBF")
	if not dbf_path:
		stats["errors"].append("receipt.DBF not found")
		return stats

	records = read_dbf(dbf_path)
	stats["total"] = len(records)

	if not records:
		return stats

	# Build cache: receiptno -> Sales Invoice name
	si_cache = {}
	for si in frappe.get_all(
		"Sales Invoice",
		filters={"custom_legacy_trans_no": ["!=", ""]},
		fields=["name", "custom_legacy_trans_no"],
	):
		si_cache[si.custom_legacy_trans_no] = si.name

	# Also build a transno->receiptno mapping from trans.dbf
	trans_dbf = find_dbf(backup_path, "trans.dbf")
	trans_to_receipt = {}
	if trans_dbf:
		for rec in read_dbf(trans_dbf):
			tn = clean_str(rec.get("transno"))
			rn = clean_str(rec.get("receiptno"))
			if tn and rn:
				trans_to_receipt[rn] = tn

	# Group receipt records by RECEIPTNO
	receipt_groups = {}
	for record in records:
		if clean_str(record.get("deleted")) == "1":
			continue
		# Skip slush placeholder items
		if clean_str(record.get("slush")) == "Y" and clean_str(record.get("payment")) == "R":
			continue

		rn = clean_str(record.get("receiptno"))
		if rn:
			receipt_groups.setdefault(rn, []).append(record)

	for rn, items in receipt_groups.items():
		try:
			# Find matching Sales Invoice
			transno = trans_to_receipt.get(rn)
			si_name = si_cache.get(transno) if transno else None

			if not si_name:
				stats["skipped"] += len(items)
				continue

			if dry_run:
				stats["imported"] += len(items)
				continue

			si_doc = frappe.get_doc("Sales Invoice", si_name)

			for item_record in items:
				descs = clean_str(item_record.get("descs"))
				qty_str = clean_str(item_record.get("qtysold"))
				price = clean_float(item_record.get("price"))
				cost = clean_float(item_record.get("cost"))

				qty = 1
				try:
					qty = abs(int(float(qty_str.strip()))) if qty_str else 1
				except (ValueError, AttributeError):
					pass

				if qty == 0:
					qty = 1

				# Try to find matching item
				clean_str(item_record.get("category"))
				clean_str(item_record.get("stocknum"))
				item_code = _get_default_item()

				si_doc.append(
					"items",
					{
						"item_code": item_code,
						"item_name": (descs or "Legacy Item")[:140],
						"qty": qty,
						"rate": price if price > 0 else cost if cost > 0 else 0,
						"description": descript[:140] if (descript := descs) else None,
					},
				)

			si_doc.save(ignore_permissions=True)
			stats["imported"] += len(items)

		except Exception as e:
			stats["errors"].append(f"Receipt {rn}: {str(e)[:100]}")
			stats["skipped"] += len(items)

		if not dry_run and len(receipt_groups) % 50 == 0:
			frappe.db.commit()  # nosemgrep

	if not dry_run:
		frappe.db.commit()  # nosemgrep
	return stats


# ──────────────────────────────────────────────────
# Payment Tenders (from TENDER.DBF)
# ──────────────────────────────────────────────────


TENDER_MODE_MAP = {
	"01": "Cash",
	"1": "Cash",
	"02": "Check",
	"2": "Check",
	"03": "Credit Card",
	"3": "Credit Card",
	"04": "Debit Card",
	"4": "Debit Card",
}


def import_payment_tenders(backup_path: str, dry_run: bool = False) -> dict:
	"""Import payment tenders from TENDER.DBF as Payment Entries."""
	stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}

	dbf_path = find_dbf(backup_path, "TENDER.DBF")
	if not dbf_path:
		stats["errors"].append("TENDER.DBF not found")
		return stats

	records = read_dbf(dbf_path)
	stats["total"] = len(records)

	if not records:
		return stats

	company = frappe.defaults.get_global_default("company") if not dry_run else "Default"

	# Build SI cache for linking
	si_cache = {}
	for si in frappe.get_all(
		"Sales Invoice",
		filters={"custom_legacy_trans_no": ["!=", ""]},
		fields=["name", "custom_legacy_trans_no", "customer", "grand_total"],
	):
		si_cache[si.custom_legacy_trans_no] = si

	for idx, record in enumerate(records):
		try:
			# Skip voided tenders
			if clean_str(record.get("voided")) == "Y":
				stats["skipped"] += 1
				continue

			transno = clean_str(record.get("transno"))
			amount = clean_float(record.get("amount"))

			if amount <= 0:
				stats["skipped"] += 1
				continue

			if dry_run:
				stats["imported"] += 1
				continue

			# Resolve customer from linked Sales Invoice
			si_info = si_cache.get(transno)
			customer = si_info.customer if si_info else _get_default_customer()

			doc = frappe.new_doc("Payment Entry")
			doc.payment_type = "Receive"
			doc.posting_date = format_date(record.get("transdate")) or frappe.utils.today()
			doc.company = company
			doc.party_type = "Customer"
			doc.party = customer
			doc.paid_amount = amount
			doc.received_amount = amount

			# Mode of payment
			tender_code = clean_str(record.get("tendercode"))
			mode = TENDER_MODE_MAP.get(tender_code, clean_str(record.get("tenderdesc")) or "Cash")
			doc.mode_of_payment = mode

			# Reference
			cardnum = clean_str(record.get("cardnum"))
			doc.reference_no = cardnum or transno
			doc.reference_date = format_date(record.get("transdate")) or frappe.utils.today()

			# Link to Sales Invoice if available
			if si_info:
				doc.append(
					"references",
					{
						"reference_doctype": "Sales Invoice",
						"reference_name": si_info.name,
						"total_amount": si_info.grand_total or amount,
						"allocated_amount": amount,
					},
				)

			doc.insert(ignore_permissions=True, ignore_mandatory=True)
			stats["imported"] += 1

			if (idx + 1) % 50 == 0:
				frappe.db.commit()  # nosemgrep

		except Exception as e:
			stats["errors"].append(f"Tender {record.get('transno', '?')}: {str(e)[:100]}")

	if not dry_run:
		frappe.db.commit()  # nosemgrep
	return stats


# ──────────────────────────────────────────────────
# Repair Orders (from jrepair.DBF)
# ──────────────────────────────────────────────────


REPAIR_STATUS_MAP = {
	"1": "Received",
	"2": "In Progress",
	"3": "Ready for Pickup",
	"4": "Delivered",
	"5": "Delivered",
}


def import_repair_orders(backup_path: str, dry_run: bool = False) -> dict:
	"""Import repair orders from jrepair.DBF."""
	stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}

	dbf_path = find_dbf(backup_path, "jrepair.DBF")
	if not dbf_path:
		stats["errors"].append("jrepair.DBF not found")
		return stats

	records = read_dbf(dbf_path)
	stats["total"] = len(records)

	if not records:
		return stats

	# Pre-fetch customer and repair type caches
	customer_cache = {}
	for c in frappe.get_all("Customer", fields=["name", "customer_name"]):
		customer_cache[c.customer_name.lower()] = c.name

	repair_types = [rt.name for rt in frappe.get_all("Repair Type")]
	default_repair_type = repair_types[0] if repair_types else None

	for _idx, record in enumerate(records):
		try:
			rpairno = clean_str(record.get("rpairno"))
			customer_str = clean_str(record.get("customer"))

			if not rpairno:
				stats["skipped"] += 1
				continue

			# Check existing
			if frappe.db.exists("Repair Order", {"customer_notes": f"Legacy Repair #{rpairno}"}):
				stats["skipped"] += 1
				continue

			if dry_run:
				stats["imported"] += 1
				continue

			doc = frappe.new_doc("Repair Order")

			# Customer resolution
			if customer_str:
				# Parse "LASTNAME, FIRSTNAME" format
				if "," in customer_str:
					parts = customer_str.split(",", 1)
					cust_name = f"{parts[1].strip()} {parts[0].strip()}"
				else:
					cust_name = customer_str
				doc.customer = customer_cache.get(cust_name.lower(), _get_default_customer())

			doc.customer_phone = clean_str(record.get("phone"))

			# Description
			desc_parts = []
			for d in ["desc1", "desc2"]:
				v = clean_str(record.get(d))
				if v:
					desc_parts.append(v)
			doc.item_description = " ".join(desc_parts) if desc_parts else f"Legacy Repair #{rpairno}"

			# Repair type
			item_type = clean_str(record.get("itemtype"))
			if item_type and item_type in repair_types:
				doc.repair_type = item_type
			elif default_repair_type:
				doc.repair_type = default_repair_type

			# Metal
			goldtype = clean_str(record.get("goldtype"))
			if goldtype:
				resolved = _get_or_create_metal(goldtype)
				if resolved:
					doc.metal_type = resolved

			# Status
			status_code = clean_str(record.get("status"))
			doc.status = REPAIR_STATUS_MAP.get(status_code, "Received")

			# Dates
			datein = clean_str(record.get("datein"))
			if datein:
				doc.received_date = _parse_foxpro_date(datein)

			dateprom = clean_str(record.get("dateprom"))
			if dateprom:
				doc.promised_date = _parse_foxpro_date(dateprom)

			datecomp = clean_str(record.get("datecomp"))
			if datecomp:
				doc.completed_date = _parse_foxpro_date(datecomp)

			# Costs
			doc.estimated_cost = clean_float(record.get("price"))
			doc.material_cost = clean_float(record.get("matert"))
			doc.labor_cost = clean_float(record.get("labort"))
			doc.total_cost = clean_float(record.get("totalchar"))

			# Notes
			instructions = []
			for inst in ["instruc1", "instruc2", "instruc3", "instruc4"]:
				v = clean_str(record.get(inst))
				if v:
					instructions.append(v)
			doc.customer_notes = "\n".join(instructions) if instructions else f"Legacy Repair #{rpairno}"

			doc.insert(ignore_permissions=True, ignore_mandatory=True)
			stats["imported"] += 1

		except Exception as e:
			stats["errors"].append(f"Repair {record.get('rpairno', '?')}: {str(e)[:100]}")

	if not dry_run:
		frappe.db.commit()  # nosemgrep
	return stats


def _parse_foxpro_date(val) -> str | None:
	"""Parse FoxPro date strings like '05/27/18' or '05/20/18'."""
	if not val:
		return None
	val = str(val).strip()
	if not val or val == "-":
		return None
	for fmt in ("%m/%d/%y", "%m/%d/%Y", "%Y%m%d", "%m%d%y"):
		try:
			return datetime.strptime(val, fmt).strftime("%Y-%m-%d")
		except ValueError:
			continue
	return None


# ──────────────────────────────────────────────────
# Layaway Contracts (from lw-maste.DBF + lw-entry.DBF)
# ──────────────────────────────────────────────────


def import_layaway_contracts(backup_path: str, dry_run: bool = False) -> dict:
	"""Import layaway contracts from lw-maste.DBF and payment schedules from lw-entry.DBF."""
	stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}

	# Read master records
	master_path = find_dbf(backup_path, "lw-maste.DBF")
	if not master_path:
		stats["errors"].append("lw-maste.DBF not found")
		return stats

	master_records = read_dbf(master_path)
	stats["total"] = len(master_records)

	# Read entry (schedule) records
	entry_records = []
	entry_path = find_dbf(backup_path, "lw-entry.DBF")
	if entry_path:
		entry_records = read_dbf(entry_path)

	# Group entries by ARNUM
	entries_by_arnum = {}
	for entry in entry_records:
		arnum = clean_str(entry.get("arnum"))
		if arnum:
			entries_by_arnum.setdefault(arnum, []).append(entry)

	# Pre-fetch customers
	customer_cache = {}
	for c in frappe.get_all("Customer", fields=["name", "customer_name"]):
		customer_cache[c.customer_name.lower()] = c.name

	for idx, record in enumerate(master_records):
		try:
			arnum = clean_str(record.get("arnum"))
			first = clean_str(record.get("first"))
			last = clean_str(record.get("last"))

			if not arnum:
				stats["skipped"] += 1
				continue

			# Resolve customer
			customer = None
			if first or last:
				cust_name = f"{first} {last}".strip().lower()
				customer = customer_cache.get(cust_name)

			if not customer:
				# Try by ARNUM matching legacy account number
				customer = frappe.db.get_value("Customer", {"custom_legacy_account_no": arnum}, "name")

			if not customer:
				# Create customer on-the-fly
				cust_name = f"{first} {last}".strip() if (first or last) else f"Layaway Customer {arnum}"
				if len(cust_name) >= 2 and not frappe.db.exists("Customer", {"customer_name": cust_name}):
					try:
						c = frappe.new_doc("Customer")
						c.customer_name = cust_name
						c.customer_type = "Individual"
						c.customer_group = "Individual"
						c.territory = "All Territories"
						_set_custom_field(c, "custom_legacy_account_no", f"LW-{arnum}")
						c.insert(ignore_permissions=True, ignore_mandatory=True)
						customer = c.name
						customer_cache[cust_name.lower()] = c.name
					except Exception:
						customer = _get_default_customer()
				else:
					customer = _get_default_customer()

			if dry_run:
				stats["imported"] += 1
				continue

			doc = frappe.new_doc("Layaway Contract")
			doc.customer = customer

			# Status
			code = clean_str(record.get("code"))
			status_map = {"L": "Active", "C": "Completed", "X": "Cancelled"}
			doc.status = status_map.get(code, "Active")

			# Amounts
			balance = clean_float(record.get("balance"))
			ytdsales = clean_float(record.get("ytdsales"))
			total_amount = ytdsales if ytdsales > 0 else balance
			doc.balance_amount = balance
			doc.total_amount = total_amount
			doc.deposit_amount = total_amount - balance if total_amount > balance else 0

			# Dates
			entries = entries_by_arnum.get(arnum, [])
			if entries:
				first_entry = entries[0]
				doc.contract_date = format_date(first_entry.get("invdate")) or frappe.utils.today()
				doc.maximum_duration_months = "6"  # default

				# Add payment schedule from entries
				for entry in entries:
					amt_paid = clean_float(entry.get("amtpaid"))
					pay_date = format_date(entry.get("datepaid"))
					if pay_date:
						doc.append(
							"payment_schedule",
							{
								"payment_date": pay_date,
								"expected_amount": amt_paid
								if amt_paid > 0
								else clean_float(entry.get("invtot")),
							},
						)
			else:
				doc.contract_date = frappe.utils.today()
				doc.maximum_duration_months = "6"

			# Add a placeholder item
			doc.append(
				"items",
				{
					"item_code": _get_default_item(),
					"item_name": f"Layaway #{arnum}",
					"qty": 1,
					"rate": total_amount if total_amount > 0 else balance,
				},
			)

			doc.insert(ignore_permissions=True, ignore_mandatory=True)
			stats["imported"] += 1

			if (idx + 1) % 100 == 0:
				frappe.db.commit()  # nosemgrep

		except Exception as e:
			stats["errors"].append(f"Layaway {record.get('arnum', '?')}: {str(e)[:100]}")

	if not dry_run:
		frappe.db.commit()  # nosemgrep
	return stats


# ──────────────────────────────────────────────────
# Layaway Payment Links (from lw-link.DBF)
# ──────────────────────────────────────────────────


def import_layaway_links(backup_path: str, dry_run: bool = False) -> dict:
	"""Import layaway payment links from lw-link.DBF as Payment Entries."""
	stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}

	dbf_path = find_dbf(backup_path, "lw-link.DBF")
	if not dbf_path:
		stats["errors"].append("lw-link.DBF not found")
		return stats

	records = read_dbf(dbf_path)
	stats["total"] = len(records)

	if not records:
		return stats

	company = frappe.defaults.get_global_default("company") if not dry_run else "Default"

	# Build layaway contract cache by customer name patterns
	default_customer = _get_default_customer()

	for idx, record in enumerate(records):
		try:
			amount = clean_float(record.get("amount"))
			if amount <= 0:
				stats["skipped"] += 1
				continue

			if dry_run:
				stats["imported"] += 1
				continue

			arnum = clean_str(record.get("arnum"))

			doc = frappe.new_doc("Payment Entry")
			doc.payment_type = "Receive"
			doc.posting_date = format_date(record.get("datepaid")) or frappe.utils.today()
			doc.company = company
			doc.party_type = "Customer"
			doc.party = default_customer
			doc.paid_amount = amount
			doc.received_amount = amount

			trans_type = clean_str(record.get("transtype")) or "LAYAWAY"
			pay_type = clean_str(record.get("paytype"))
			mode = TENDER_MODE_MAP.get(pay_type, "Cash")
			doc.mode_of_payment = mode

			doc.reference_no = f"LW-{arnum}-{clean_str(record.get('invnum'))}"
			doc.reference_date = format_date(record.get("datepaid")) or frappe.utils.today()

			doc.remarks = f"Legacy layaway payment: {trans_type}, AR#{arnum}"

			doc.insert(ignore_permissions=True, ignore_mandatory=True)
			stats["imported"] += 1

			if (idx + 1) % 100 == 0:
				frappe.db.commit()  # nosemgrep

		except Exception as e:
			stats["errors"].append(f"LW-Link {record.get('arnum', '?')}: {str(e)[:100]}")

	if not dry_run:
		frappe.db.commit()  # nosemgrep
	return stats


# ──────────────────────────────────────────────────
# Salespersons (from saleman.dbf - updates Employee records)
# ──────────────────────────────────────────────────


def import_salespersons(backup_path: str, dry_run: bool = False) -> dict:
	"""Import salesperson commission data from saleman.dbf onto existing Employee records."""
	stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}

	dbf_path = find_dbf(backup_path, "saleman.dbf")
	if not dbf_path:
		stats["errors"].append("saleman.dbf not found")
		return stats

	records = read_dbf(dbf_path)
	stats["total"] = len(records)

	for record in records:
		try:
			empid = clean_str(record.get("empid"))
			if not empid:
				stats["skipped"] += 1
				continue

			# Skip system accounts
			clerkname = clean_str(record.get("clerkname"))
			if clerkname == "SYSTEM ACCOUNT" or empid == "00001":
				stats["skipped"] += 1
				continue

			# Find matching Employee
			emp_name = frappe.db.get_value("Employee", {"employee_number": empid}, "name")
			if not emp_name:
				stats["skipped"] += 1
				continue

			if dry_run:
				stats["imported"] += 1
				continue

			doc = frappe.get_doc("Employee", emp_name)

			_set_custom_field(doc, "custom_initials", clean_str(record.get("initials")))
			_set_custom_field(doc, "custom_commission_rate", clean_float(record.get("commission")))
			_set_custom_field(doc, "custom_sales_level", clean_str(record.get("level")))
			_set_custom_field(doc, "custom_discount_permission", clean_float(record.get("disc_per")))
			_set_custom_field(doc, "custom_ytd_sales", clean_float(record.get("ytdsales")))
			_set_custom_field(doc, "custom_sales_goal", clean_float(record.get("goal")))

			homestore = clean_str(record.get("homestore"))
			if homestore:
				sc = homestore.zfill(2)
				if frappe.db.exists("Store Location", sc):
					_set_custom_field(doc, "custom_home_store", sc)

			# Manager designation
			if clean_int(record.get("nmanager")) == 1:
				_set_custom_field(doc, "custom_is_manager", 1)
				_ensure_designation("Manager")
				doc.designation = "Manager"

			# Update hire date if available and not set
			hire_date = format_date(record.get("hiredate"))
			if hire_date and not doc.date_of_joining:
				doc.date_of_joining = hire_date

			# If exit date, mark as Left
			exit_date = format_date(record.get("exitdate"))
			if exit_date:
				doc.status = "Left"
				doc.relieving_date = exit_date

			doc.save(ignore_permissions=True)
			stats["imported"] += 1

		except Exception as e:
			stats["errors"].append(f"Salesperson {record.get('empid', '?')}: {str(e)[:100]}")

	if not dry_run:
		frappe.db.commit()  # nosemgrep
	return stats


# ──────────────────────────────────────────────────
# Commission Rules (from bonus.dbf)
# ──────────────────────────────────────────────────


def import_commission_rules(backup_path: str, dry_run: bool = False) -> dict:
	"""Import commission structures from bonus.dbf into Commission Rule + Commission Range."""
	stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}

	dbf_path = find_dbf(backup_path, "bonus.dbf")
	if not dbf_path:
		stats["errors"].append("bonus.dbf not found")
		return stats

	records = read_dbf(dbf_path)
	stats["total"] = len(records)

	if not records:
		return stats

	# Group by employee number
	emp_groups = {}
	for record in records:
		emplnum = clean_str(record.get("emplnum"))
		if emplnum:
			emp_groups.setdefault(emplnum, []).append(record)

	for emplnum, bonus_records in emp_groups.items():
		try:
			if emplnum == "1":
				stats["skipped"] += len(bonus_records)
				continue

			# Resolve employee
			emp_name = frappe.db.get_value(
				"Employee", {"employee_number": str(int(float(emplnum))).zfill(5)}, "name"
			)
			if not emp_name:
				stats["skipped"] += len(bonus_records)
				continue

			rule_name = f"Commission - Employee {emplnum}"
			if frappe.db.exists("Commission Rule", {"rule_name": rule_name}):
				stats["skipped"] += len(bonus_records)
				continue

			if dry_run:
				stats["imported"] += len(bonus_records)
				continue

			# Determine calculation type
			has_amount_tiers = any(
				clean_float(r.get("amt_from")) > 0 or clean_float(r.get("amt_upto")) > 0
				for r in bonus_records
			)
			calc_type = "By Sale Amount" if has_amount_tiers else "By Discount Range"

			doc = frappe.new_doc("Commission Rule")
			doc.rule_name = rule_name
			doc.employee = emp_name
			doc.calculation_type = calc_type

			for br in bonus_records:
				if calc_type == "By Discount Range":
					disc_from = clean_float(br.get("disc_from"))
					disc_to = clean_float(br.get("disc_to"))
					percent = clean_float(br.get("percent"))
					if percent > 0:
						doc.append(
							"commission_ranges",
							{
								"min_value": disc_from,
								"max_value": disc_to,
								"commission_percent": percent,
							},
						)
				else:
					amt_from = clean_float(br.get("amt_from"))
					amt_upto = clean_float(br.get("amt_upto"))
					commrate = clean_float(br.get("commrate"))
					if commrate > 0:
						doc.append(
							"commission_ranges",
							{
								"min_value": amt_from,
								"max_value": amt_upto,
								"commission_percent": commrate,
							},
						)

			doc.insert(ignore_permissions=True, ignore_mandatory=True)
			stats["imported"] += len(bonus_records)

		except Exception as e:
			stats["errors"].append(f"Commission empl#{emplnum}: {str(e)[:100]}")
			stats["skipped"] += len(bonus_records)

	if not dry_run:
		frappe.db.commit()  # nosemgrep
	return stats


# ──────────────────────────────────────────────────
# Payroll / Attendance (from payroll1.dbf)
# ──────────────────────────────────────────────────


def import_payroll(backup_path: str, dry_run: bool = False) -> dict:
	"""Import payroll/attendance data from payroll1.dbf as Attendance records."""
	stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}

	dbf_path = find_dbf(backup_path, "payroll1.dbf")
	if not dbf_path:
		stats["errors"].append("payroll1.dbf not found")
		return stats

	records = read_dbf(dbf_path)
	stats["total"] = len(records)

	if not records:
		return stats

	# Only process "IN" records (each punch pair has an IN and OUT row)
	for idx, record in enumerate(records):
		try:
			inout = clean_str(record.get("inout"))
			if inout != "IN":
				stats["skipped"] += 1
				continue

			empid = clean_str(record.get("empid"))
			weekof = format_date(record.get("weekof"))

			if not empid:
				stats["skipped"] += 1
				continue

			# Resolve employee
			emp_name = frappe.db.get_value("Employee", {"employee_number": empid}, "name")
			if not emp_name:
				stats["skipped"] += 1
				continue

			if not weekof:
				stats["skipped"] += 1
				continue

			if dry_run:
				stats["imported"] += 1
				continue

			# Create one attendance per week (Sunday start)
			attendance_date = weekof

			# Check for duplicate
			if frappe.db.exists("Attendance", {"employee": emp_name, "attendance_date": attendance_date}):
				stats["skipped"] += 1
				continue

			hours = clean_float(record.get("hours"))

			doc = frappe.new_doc("Attendance")
			doc.employee = emp_name
			doc.attendance_date = attendance_date
			doc.status = "Present"
			doc.working_hours = hours if hours > 0 else 8

			doc.insert(ignore_permissions=True, ignore_mandatory=True)
			stats["imported"] += 1

			if (idx + 1) % 100 == 0:
				frappe.db.commit()  # nosemgrep

		except Exception as e:
			stats["errors"].append(f"Payroll {record.get('empid', '?')}: {str(e)[:100]}")

	if not dry_run:
		frappe.db.commit()  # nosemgrep
	return stats


# ──────────────────────────────────────────────────
# Audit Trail (from audit.dbf)
# ──────────────────────────────────────────────────


def import_audit_trail(backup_path: str, dry_run: bool = False) -> dict:
	"""Import audit trail from audit.dbf into POS Audit Log."""
	stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}

	dbf_path = find_dbf(backup_path, "audit.dbf")
	if not dbf_path:
		stats["errors"].append("audit.dbf not found")
		return stats

	records = read_dbf(dbf_path)
	stats["total"] = len(records)

	for idx, record in enumerate(records):
		try:
			action = clean_str(record.get("caction"))
			if not action:
				stats["skipped"] += 1
				continue

			if dry_run:
				stats["imported"] += 1
				continue

			doc = frappe.new_doc("POS Audit Log")
			doc.user = "Administrator"
			doc.timestamp = format_date(record.get("dttime")) or frappe.utils.now_datetime()
			doc.details = action[:500]

			# Map event type
			action_lower = action.lower()
			if "login" in action_lower:
				doc.event_type = "Login Success"
			elif "delete" in action_lower:
				doc.event_type = "Security"
			elif "changed" in action_lower or "change" in action_lower:
				doc.event_type = "Price Override"
			else:
				doc.event_type = "System"

			# Category
			ctype = clean_str(record.get("ctype"))
			doc.category = ctype if ctype else "General"

			# Reference
			abr = clean_str(record.get("abr"))
			stockno = clean_str(record.get("stockno"))
			if abr or stockno:
				doc.reference_document = f"{abr}/{stockno}"

			doc.insert(ignore_permissions=True, ignore_mandatory=True)
			stats["imported"] += 1

			if (idx + 1) % 100 == 0:
				frappe.db.commit()  # nosemgrep

		except Exception as e:
			stats["errors"].append(f"Audit {idx}: {str(e)[:100]}")

	if not dry_run:
		frappe.db.commit()  # nosemgrep
	return stats


# ──────────────────────────────────────────────────
# Sold Item History (from SOLDPARM.dbf)
# ──────────────────────────────────────────────────


def import_sold_history(backup_path: str, dry_run: bool = False) -> dict:
	"""Import sold item history from SOLDPARM.dbf into Customer Ledger Entries."""
	stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}

	dbf_path = find_dbf(backup_path, "SOLDPARM.dbf")
	if not dbf_path:
		stats["errors"].append("SOLDPARM.dbf not found")
		return stats

	records = read_dbf(dbf_path)
	stats["total"] = len(records)

	for idx, record in enumerate(records):
		try:
			day = clean_str(record.get("day"))
			descs = clean_str(record.get("descs"))
			price = clean_float(record.get("price"))

			if not descs and price <= 0:
				stats["skipped"] += 1
				continue

			if dry_run:
				stats["imported"] += 1
				continue

			doc = frappe.new_doc("Customer Ledger Entry")
			doc.entry_date = format_date(day) or frappe.utils.today()
			doc.entry_type = "Sale"
			doc.description = descs or "Legacy Sale"
			doc.debit = price if price > 0 else 0

			vendor = clean_str(record.get("vendorid"))
			cat = clean_str(record.get("category"))
			if vendor or cat:
				doc.reference_type = f"Vendor: {vendor}, Cat: {cat}"

			doc.insert(ignore_permissions=True, ignore_mandatory=True)
			stats["imported"] += 1

			if (idx + 1) % 50 == 0:
				frappe.db.commit()  # nosemgrep

		except Exception as e:
			stats["errors"].append(f"SoldParm {idx}: {str(e)[:100]}")

	if not dry_run:
		frappe.db.commit()  # nosemgrep
	return stats


# ──────────────────────────────────────────────────
# Deleted Inventory (from invdel.dbf)
# ──────────────────────────────────────────────────


def import_deleted_inventory(backup_path: str, dry_run: bool = False) -> dict:
	"""Import deleted inventory records from invdel.dbf as POS Audit Log entries."""
	stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}

	dbf_path = find_dbf(backup_path, "invdel.dbf")
	if not dbf_path:
		stats["errors"].append("invdel.dbf not found")
		return stats

	records = read_dbf(dbf_path)
	stats["total"] = len(records)

	for idx, record in enumerate(records):
		try:
			barcode = clean_str(record.get("barcode"))
			descript = clean_str(record.get("descript"))
			reason = clean_str(record.get("reasons"))
			trans_date = format_date(record.get("transdate"))
			deleted_by = clean_str(record.get("deletedby"))

			if dry_run:
				stats["imported"] += 1
				continue

			doc = frappe.new_doc("POS Audit Log")
			doc.user = "Administrator"
			doc.timestamp = trans_date or frappe.utils.now_datetime()
			doc.event_type = "Security"
			doc.category = "Inventory Deletion"
			doc.reference_document = barcode or f"INV-{idx}"
			doc.details = f"Deleted: {descript or 'Unknown item'} | Reason: {reason or 'N/A'} | By: {deleted_by or 'Unknown'}"

			doc.insert(ignore_permissions=True, ignore_mandatory=True)
			stats["imported"] += 1

			if (idx + 1) % 100 == 0:
				frappe.db.commit()  # nosemgrep

		except Exception as e:
			stats["errors"].append(f"InvDel {idx}: {str(e)[:100]}")

	if not dry_run:
		frappe.db.commit()  # nosemgrep
	return stats


# ──────────────────────────────────────────────────
# Watch Details (from wdetails.dbf -> Item custom fields)
# ──────────────────────────────────────────────────


def import_watch_details(backup_path: str, dry_run: bool = False) -> dict:
	"""Import watch details from wdetails.dbf as Item custom field updates."""
	stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}

	dbf_path = find_dbf(backup_path, "wdetails.dbf")
	if not dbf_path:
		stats["errors"].append("wdetails.dbf not found")
		return stats

	records = read_dbf(dbf_path)
	stats["total"] = len(records)

	for _idx, record in enumerate(records):
		try:
			abr = clean_str(record.get("abr"))
			stockno = clean_str(record.get("stockno"))
			model = clean_str(record.get("model__"))
			serial = clean_str(record.get("serial__"))

			if not abr and not stockno:
				stats["skipped"] += 1
				continue

			# Try to find matching Item
			item_code = None
			# Try by barcode pattern
			if frappe.db.exists("Item", {"custom_legacy_abr": abr, "custom_legacy_stockno": stockno}):
				item_code = frappe.db.get_value(
					"Item", {"custom_legacy_abr": abr, "custom_legacy_stockno": stockno}, "name"
				)

			if not item_code:
				stats["skipped"] += 1
				continue

			if dry_run:
				stats["imported"] += 1
				continue

			doc = frappe.get_doc("Item", item_code)
			_set_custom_field(doc, "custom_watch_model", model)
			_set_custom_field(doc, "custom_watch_serial", serial)
			_set_custom_field(doc, "custom_watch_condition", clean_str(record.get("condition")))
			_set_custom_field(doc, "custom_watch_supplier", clean_str(record.get("supplierid")))
			doc.save(ignore_permissions=True)
			stats["imported"] += 1

		except Exception as e:
			stats["errors"].append(f"Watch {record.get('abr', '?')}: {str(e)[:100]}")

	if not dry_run:
		frappe.db.commit()  # nosemgrep
	return stats
