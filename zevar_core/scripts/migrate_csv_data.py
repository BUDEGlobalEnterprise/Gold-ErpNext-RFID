import csv
import os
import re

import frappe

LEGACY_DATA_DIR = "/workspace/development/Zevar_URMS"


def parse_foxpro_header(header_row):
	columns = []
	for col in header_row:
		match = re.match(r"^([A-Z0-9_]+)", col)
		if match:
			columns.append(match.group(1))
		else:
			columns.append(col)
	return columns


def clean_value(value, field_type="string"):
	if value is None or value == "":
		return None
	value = str(value).strip()
	if not value:
		return None

	if field_type == "string":
		return value
	elif field_type == "int":
		try:
			return int(float(value))
		except ValueError:
			return 0
	elif field_type == "float":
		try:
			return float(value.replace(",", ""))
		except ValueError:
			return 0.0
	return value


def execute():
	print("Starting CSV Data Migration")
	print("=" * 80)

	frappe.flags.in_import = True

	# === MIGRATE SUPPLIERS ===
	supplier_file = os.path.join(LEGACY_DATA_DIR, "supplier.csv")
	if os.path.exists(supplier_file):
		print("\nMIGRATING SUPPLIERS")
		print("=" * 80)
		with open(supplier_file, encoding="utf-8", errors="ignore") as f:
			reader = csv.reader(f)
			header = parse_foxpro_header(next(reader))
			success = 0
			for row in reader:
				if len(row) < len(header):
					continue
				data = dict(zip(header, row, strict=False))
				supplier_name = clean_value(data.get("FULLNAME"))
				if not supplier_name:
					continue
				if frappe.db.exists("Supplier", {"supplier_name": supplier_name}):
					continue

				try:
					doc = frappe.new_doc("Supplier")
					doc.supplier_name = supplier_name
					doc.supplier_type = "Company"
					doc.insert(ignore_permissions=True, ignore_mandatory=True)
					success += 1
				except Exception as e:
					print(f"Error inserting Supplier {supplier_name}: {e}")
		print(f"✅ Imported {success} Suppliers")

	# === MIGRATE ITEMS ===
	item_file = os.path.join(LEGACY_DATA_DIR, "inventory.csv")
	if os.path.exists(item_file):
		print("\nMIGRATING ITEMS")
		print("=" * 80)
		with open(item_file, encoding="utf-8", errors="ignore") as f:
			reader = csv.reader(f)
			header = parse_foxpro_header(next(reader))
			success = 0
			for row in reader:
				if len(row) < len(header):
					continue
				data = dict(zip(header, row, strict=False))
				sku = clean_value(data.get("ABR"))
				if not sku:
					continue
				if frappe.db.exists("Item", {"item_code": sku}):
					continue

				item_name = clean_value(data.get("DESCRIPT")) or sku
				category = clean_value(data.get("CATEGORY")) or "All Item Groups"
				description = clean_value(data.get("DESC2")) or item_name
				cost = clean_value(data.get("COST"), "float") or 0.0

				try:
					if not frappe.db.exists("Item Group", category):
						ig = frappe.new_doc("Item Group")
						ig.item_group_name = category
						ig.parent_item_group = "All Item Groups"
						ig.insert(ignore_permissions=True, ignore_mandatory=True)
				except Exception:
					pass

				try:
					doc = frappe.new_doc("Item")
					doc.item_code = sku
					doc.item_name = item_name
					doc.description = description
					doc.item_group = category
					doc.stock_uom = "Nos"
					doc.is_stock_item = 1
					doc.is_purchase_item = 1
					doc.is_sales_item = 1
					doc.valuation_rate = cost
					doc.insert(ignore_permissions=True, ignore_mandatory=True)
					success += 1
				except Exception as e:
					print(f"Error inserting Item {sku}: {e}")
		print(f"✅ Imported {success} Items")

	# === MIGRATE CUSTOMERS ===
	customer_file = os.path.join(LEGACY_DATA_DIR, "customer.csv")
	if os.path.exists(customer_file):
		print("\nMIGRATING CUSTOMERS")
		print("=" * 80)
		with open(customer_file, encoding="utf-8", errors="ignore") as f:
			reader = csv.reader(f)
			header = parse_foxpro_header(next(reader))
			success = 0
			for row in reader:
				if len(row) < len(header):
					continue
				data = dict(zip(header, row, strict=False))

				first = clean_value(data.get("FIRST")) or ""
				last = clean_value(data.get("LAST")) or ""
				customer_name = f"{first} {last}".strip()
				if not customer_name:
					continue

				if frappe.db.exists("Customer", {"customer_name": customer_name}):
					continue

				try:
					doc = frappe.new_doc("Customer")
					doc.customer_name = customer_name
					doc.customer_type = "Individual"
					doc.customer_group = "All Customer Groups"
					doc.territory = "All Territories"

					doc.insert(ignore_permissions=True, ignore_mandatory=True)

					# Create contact and address
					phone = clean_value(data.get("PHONE"))
					email = clean_value(data.get("EMAIL"))

					if phone or email:
						contact = frappe.new_doc("Contact")
						contact.first_name = first or "Unknown"
						contact.last_name = last or ""
						contact.is_primary_contact = 1
						if email:
							contact.append("email_ids", {"email_id": email, "is_primary": 1})
						if phone:
							contact.append("phone_nos", {"phone": phone, "is_primary_phone": 1})
						contact.append("links", {"link_doctype": "Customer", "link_name": doc.name})
						contact.insert(ignore_permissions=True, ignore_mandatory=True)

					address1 = clean_value(data.get("ADDRESS"))
					city = clean_value(data.get("CITY"))
					state = clean_value(data.get("STATE"))
					zipcode = clean_value(data.get("ZIP"))

					if address1 or city or state or zipcode:
						addr = frappe.new_doc("Address")
						addr.address_title = customer_name
						addr.address_type = "Billing"
						addr.address_line1 = address1 or "Not provided"
						addr.city = city or "Unknown"
						addr.state = state or "Unknown"
						addr.pincode = zipcode
						addr.country = "United States"
						addr.append("links", {"link_doctype": "Customer", "link_name": doc.name})
						addr.insert(ignore_permissions=True, ignore_mandatory=True)

					success += 1
				except Exception as e:
					print(f"Error inserting Customer {customer_name}: {e}")

		print(f"✅ Imported {success} Customers")

	frappe.db.commit()
	print("Migration finished and committed.")
