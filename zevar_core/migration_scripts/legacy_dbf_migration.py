import os
import sys

import frappe
import pandas as pd
from dbfread import DBF
from frappe.utils import now_datetime

# Add the current directory to the path to import zevar_core modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def migrate_legacy_data():
	"""Migrate legacy DBF data to Frappe"""

	# Define the source directory for legacy DBF files
	legacy_dir = "/workspace/development/Zevar_URMS/Zevar_HIPmall_MD_1/"

	# Define mapping of DBF files to Frappe DocTypes with actual field names
	migration_map = {
		"inventor.DBF": {
			"doctype": "Item",
			"fields": {
				"item_code": "SKU",
				"item_name": "DESCRIPT",
				"description": "DESC2",
				"item_group": "CATEGORY",
				"brand": "MFRID",
				"manufacturer": "MFRID",
				"unit": "COST_UNIT",
				"stock_uom": "RET_UNIT",
				"weight": "WEIGHT",
				"weight_uom": "WEIGHT",
				"price": "COST",
				"selling_price": "SELLPRICE",
				"cost": "COSTSOLD",
				"barcode": "BARCODE",
				"tags": "TAGTYPE",
				"custom_fields": {
					"karat": "GOLD",
					"purity": "GOLDCOST",
					"stone_type": "STONES",
					"stone_weight": "GOLDWGHT",
					"metal_type": "METAL",
					"style": "STYLE",
					"category": "CATEGORY",
					"vendor_code": "VEN_CODE",
					"last_cost": "LAST_COST",
					"markup": "MARKUP",
					"inventory_status": "STATUS",
				},
			},
		},
		"EMPLOYEE.DBF": {
			"doctype": "Employee",
			"fields": {
				"employee": "EMPID",
				"first_name": "CLERKNAME",
				"last_name": "CLERKNAME",
				"email": "EMAIL",
				"phone": "PHONE",
				"department": "POSITION",
				"designation": "POSITION",
				"date_of_joining": "DATEHIRE",
				"reports_to": "SUPERVISOR",
				"status": "STATUS",
				"employee_type": "POSITION",
				"commission_rate": "COMMISSION",
			},
		},
		"GOLD$.dbf": {
			"doctype": "Gold Price",
			"fields": {
				"date": "INVOICE",
				"gold_price": "CASH",
				"currency": "CURRENCY",
				"source": "SOURCE",
				"notes": "MEMOS",
			},
		},
	}

	# Create a log file
	log_file = f"legacy_migration_{now_datetime().strftime('%Y%m%d_%H%M%S')}.log"
	with open(log_file, "w") as log:  # nosemgrep
		log.write(f"Legacy DBF Migration Log - {now_datetime()}\n")
		log.write("=" * 50 + "\n\n")

		for dbf_file, config in migration_map.items():
			dbf_path = os.path.join(legacy_dir, dbf_file)

			if not os.path.exists(dbf_path):
				log.write(f"WARNING: File not found - {dbf_file}\n")
				continue

			try:
				log.write(f"\nProcessing {dbf_file} -> {config['doctype']}\n")

				# Read the DBF file
				table = DBF(dbf_path, load=True)
				df = pd.DataFrame(iter(table))

				log.write(f"Found {len(df)} records in {dbf_file}\n")

				# Process each record
				for index, row in df.iterrows():
					try:
						# Create Frappe document
						doc = frappe.new_doc(config["doctype"])

						# Map fields
						for dbf_field, frappe_field in config["fields"].items():
							if isinstance(frappe_field, str):
								if dbf_field in row and pd.notna(row[dbf_field]):
									doc.set(frappe_field, row[dbf_field])
							elif isinstance(frappe_field, dict):
								# Handle custom fields
								for custom_field, custom_dbf_field in frappe_field.items():
									if custom_dbf_field in row and pd.notna(row[custom_dbf_field]):
										doc.set(custom_field, row[custom_dbf_field])

						# Save the document
						doc.insert()
						log.write(f"Created {config['doctype']} - {doc.name}\n")

					except Exception as e:
						log.write(f"ERROR processing row {index}: {e!s}\n")
						continue

				log.write(f"Successfully processed {len(df)} records from {dbf_file}\n")

			except Exception as e:
				log.write(f"ERROR processing {dbf_file}: {e!s}\n")
				continue

	log.write(f"\nMigration completed at {now_datetime()}\n")


if __name__ == "__main__":
	migrate_legacy_data()
