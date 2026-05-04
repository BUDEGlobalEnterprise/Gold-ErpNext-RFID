import os
import sys

import frappe


def migrate():
	"""Migrate legacy DBF data to Frappe"""

	# Define the source directory for legacy DBF files
	legacy_dir = "/workspace/development/Zevar_URMS/Zevar_HIPmall_MD_1/"

	# Migrate items
	migrate_items(legacy_dir)

	# Migrate employees
	migrate_employees(legacy_dir)

	# Migrate gold prices
	migrate_gold_prices(legacy_dir)


def migrate_items(legacy_dir):
	"""Migrate inventory items from inventor.DBF"""
	dbf_path = os.path.join(legacy_dir, "inventor.DBF")

	if not os.path.exists(dbf_path):
		return

	# Read the DBF file using dbfread
	import pandas as pd
	from dbfread import DBF

	# Read the DBF file
	table = DBF(dbf_path, load=True)
	df = pd.DataFrame(iter(table))

	# Process items
	for _index, row in df.iterrows():
		try:
			doc = frappe.new_doc("Item")
			doc.item_code = row.get("SKU", "")
			doc.item_name = row.get("DESCRIPT", "")
			doc.description = row.get("DESC2", "")
			doc.item_group = row.get("CATEGORY", "")
			doc.brand = row.get("MFRID", "")
			doc.manufacturer = row.get("MFRID", "")
			doc.unit = row.get("COST_UNIT", "")
			doc.stock_uom = row.get("RET_UNIT", "")
			doc.weight = row.get("WEIGHT", 0)
			doc.weight_uom = row.get("WEIGHT", "")
			doc.price = row.get("COST", 0)
			doc.selling_price = row.get("SELLPRICE", 0)
			doc.cost = row.get("COSTSOLD", 0)
			doc.barcode = row.get("BARCODE", "")
			doc.tags = row.get("TAGTYPE", "")

			# Custom fields
			doc.custom_karat = row.get("GOLD", "")
			doc.custom_purity = row.get("GOLDCOST", "")
			doc.custom_stone_type = row.get("STONES", "")
			doc.custom_stone_weight = row.get("GOLDWGHT", 0)
			doc.custom_metal_type = row.get("METAL", "")
			doc.custom_style = row.get("STYLE", "")
			doc.custom_category = row.get("CATEGORY", "")
			doc.custom_vendor_code = row.get("VEN_CODE", "")
			doc.custom_last_cost = row.get("LAST_COST", 0)
			doc.custom_markup = row.get("MARKUP", 0)
			doc.custom_inventory_status = row.get("STATUS", "")

			doc.insert()

		except Exception:
			continue

	frappe.db.commit()  # nosemgrep


def migrate_employees(legacy_dir):
	"""Migrate employees from EMPLOYEE.DBF"""
	dbf_path = os.path.join(legacy_dir, "EMPLOYEE.DBF")

	if not os.path.exists(dbf_path):
		return

	# Read the DBF file using dbfread
	import pandas as pd
	from dbfread import DBF

	# Read the DBF file
	table = DBF(dbf_path, load=True)
	df = pd.DataFrame(iter(table))

	# Process employees
	for _index, row in df.iterrows():
		try:
			doc = frappe.new_doc("Employee")
			doc.employee = row.get("EMPID", "")
			doc.first_name = row.get("CLERKNAME", "")
			doc.last_name = row.get("CLERKNAME", "")
			doc.email = row.get("EMAIL", "")
			doc.phone = row.get("PHONE", "")
			doc.department = row.get("POSITION", "")
			doc.designation = row.get("POSITION", "")
			doc.date_of_joining = row.get("DATEHIRE", "")
			doc.reports_to = row.get("SUPERVISOR", "")
			doc.status = row.get("STATUS", "")
			doc.employee_type = row.get("POSITION", "")
			doc.commission_rate = row.get("COMMISSION", 0)

			doc.insert()

		except Exception:
			continue

	frappe.db.commit()  # nosemgrep


def migrate_gold_prices(legacy_dir):
	"""Migrate gold prices from GOLD$.dbf"""
	dbf_path = os.path.join(legacy_dir, "GOLD$.dbf")

	if not os.path.exists(dbf_path):
		return

	# Read the DBF file using dbfread
	import pandas as pd
	from dbfread import DBF

	# Read the DBF file
	table = DBF(dbf_path, load=True)
	df = pd.DataFrame(iter(table))

	# Process gold prices
	for _index, row in df.iterrows():
		try:
			doc = frappe.new_doc("Gold Price")
			doc.date = row.get("INVOICE", "")
			doc.gold_price = row.get("CASH", 0)
			doc.currency = row.get("CURRENCY", "USD")
			doc.source = row.get("SOURCE", "")
			doc.notes = row.get("MEMOS", "")

			doc.insert()

		except Exception:
			continue

	frappe.db.commit()  # nosemgrep


if __name__ == "__main__":
	migrate()
