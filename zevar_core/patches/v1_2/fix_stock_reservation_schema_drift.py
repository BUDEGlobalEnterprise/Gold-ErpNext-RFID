"""Fix Stock Reservation schema drift — add 11 missing fields + 3 indexes.

reservation_manager.py references fields that don't exist in stock_reservation.json:
reservation_type, auto_expire_on, cart_reference, salesperson, pos_session,
converted_from, release_reason, released_by, released_at, priority, intended_use.

This patch is idempotent — safe to run multiple times.
"""

import frappe
from frappe.utils import now_datetime


def execute():
	if not frappe.db.exists("DocType", "Stock Reservation"):
		return

	_add_missing_fields()
	_add_indexes()
	_backfill_reservation_type()


def _add_missing_fields():
	"""Add fields that reservation_manager.py expects but are missing from the schema."""
	meta = frappe.get_meta("Stock Reservation")
	existing = {f.fieldname for f in meta.fields}

	new_fields = [
		{
			"fieldname": "reservation_type",
			"fieldtype": "Select",
			"options": "Soft Hold\nHard Reserve\nLayaway Reserve",
			"label": "Reservation Type",
			"reqd": 1,
			"default": "Hard Reserve",
			"insert_after": "naming_series",
		},
		{
			"fieldname": "auto_expire_on",
			"fieldtype": "Datetime",
			"label": "Auto Expire On",
			"insert_after": "hold_until",
		},
		{
			"fieldname": "priority",
			"fieldtype": "Select",
			"options": "Normal\nHigh\nVIP",
			"label": "Priority",
			"default": "Normal",
			"insert_after": "status",
		},
		{
			"fieldname": "intended_use",
			"fieldtype": "Select",
			"options": "Try-On\nLayaway\nRepair\nSpecial Order\nOther",
			"label": "Intended Use",
			"insert_after": "priority",
		},
		{
			"fieldname": "cart_reference",
			"fieldtype": "Data",
			"label": "Cart Reference",
			"insert_after": "notes",
		},
		{
			"fieldname": "salesperson",
			"fieldtype": "Link",
			"options": "Employee",
			"label": "Salesperson",
			"insert_after": "cart_reference",
		},
		{
			"fieldname": "pos_session",
			"fieldtype": "Link",
			"options": "POS Opening Entry",
			"label": "POS Session",
			"insert_after": "salesperson",
		},
		{
			"fieldname": "converted_from",
			"fieldtype": "Link",
			"options": "Stock Reservation",
			"label": "Converted From",
			"insert_after": "pos_session",
		},
		{
			"fieldname": "release_reason",
			"fieldtype": "Small Text",
			"label": "Release Reason",
			"insert_after": "converted_from",
		},
		{
			"fieldname": "released_by",
			"fieldtype": "Link",
			"options": "User",
			"label": "Released By",
			"read_only": 1,
			"insert_after": "release_reason",
		},
		{
			"fieldname": "released_at",
			"fieldtype": "Datetime",
			"label": "Released At",
			"read_only": 1,
			"insert_after": "released_by",
		},
	]

	for field_def in new_fields:
		if field_def["fieldname"] not in existing:
			frappe.get_doc(
				{
					"doctype": "Custom Field",
					"dt": "Stock Reservation",
					"fieldname": field_def["fieldname"],
					"fieldtype": field_def["fieldtype"],
					"label": field_def["label"],
					"options": field_def.get("options", ""),
					"insert_after": field_def["insert_after"],
					"reqd": field_def.get("reqd", 0),
					"read_only": field_def.get("read_only", 0),
					"default": field_def.get("default", ""),
				}
			).insert(ignore_permissions=True)


def _add_indexes():
	"""Add performance indexes for the reservation conflict checks."""
	indexes = [
		("serial_no", "status", "docstatus"),
		("hold_until", "status"),
		("customer", "status"),
	]
	table = "`tabStock Reservation`"
	for cols in indexes:
		cols_str = "_".join(cols)
		idx_name = f"idx_sr_{cols_str}"
		try:
			frappe.db.sql(f"CREATE INDEX IF NOT EXISTS `{idx_name}` ON {table} ({', '.join(cols)})")
		except Exception:
			pass


def _backfill_reservation_type():
	"""Set reservation_type for existing reservations.

	Heuristic: if warehouse_to != warehouse_from, it was a hard reserve
	(the physical stock was moved). Otherwise it was a soft hold.
	"""
	table = "`tabStock Reservation`"
	try:
		has_col = frappe.db.has_column("Stock Reservation", "reservation_type")
	except Exception:
		has_col = False

	if not has_col:
		return

	frappe.db.sql(
		f"""
		UPDATE {table}
		SET reservation_type = 'Hard Reserve'
		WHERE reservation_type IS NULL OR reservation_type = ''
	""",
		as_dict=False,
	)
	frappe.db.commit()

	frappe.db.sql(f"""
		UPDATE {table}
		SET reservation_type = 'Soft Hold'
		WHERE warehouse_from = warehouse_to
		AND reservation_type = 'Hard Reserve'
		AND docstatus = 0
	""")
	frappe.db.commit()
