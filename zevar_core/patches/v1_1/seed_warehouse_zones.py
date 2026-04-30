import frappe
from frappe.utils import now_datetime

from zevar_core.constants import INVENTORY_ZONES, STORE_LOCATIONS


def execute():
	company = frappe.defaults.get_global_default("company") or "Zevar Jewelers"
	abbr = frappe.get_cached_value("Company", company, "abbr") or "Z"

	root_name = f"Stores - {abbr}"

	if not frappe.db.exists("Warehouse", root_name):
		root = frappe.get_doc(
			{
				"doctype": "Warehouse",
				"warehouse_name": "Stores",
				"company": company,
				"is_group": 1,
			}
		)
		root.insert(ignore_permissions=True)
		root_name = root.name

	for store_code, store_city in STORE_LOCATIONS.items():
		store_wh_name = f"{store_code} - {abbr}"
		if not frappe.db.exists("Warehouse", store_wh_name):
			store_wh = frappe.get_doc(
				{
					"doctype": "Warehouse",
					"warehouse_name": store_code,
					"parent_warehouse": root_name,
					"company": company,
					"is_group": 1,
				}
			)
			store_wh.insert(ignore_permissions=True)
			store_wh_name = store_wh.name

		for zone in INVENTORY_ZONES:
			zone_name = f"{zone} {store_code} - {abbr}"
			if not frappe.db.exists("Warehouse", zone_name):
				frappe.get_doc(
					{
						"doctype": "Warehouse",
						"warehouse_name": f"{zone} {store_code}",
						"parent_warehouse": store_wh_name,
						"company": company,
						"is_group": 0,
					}
				).insert(ignore_permissions=True)

		if frappe.db.exists("Store Location", {"store_code": store_code}):
			frappe.db.set_value(
				"Store Location",
				{"store_code": store_code},
				"default_warehouse",
				store_wh_name,
			)
		else:
			frappe.get_doc(
				{
					"doctype": "Store Location",
					"store_code": store_code,
					"store_name": store_city,
					"default_warehouse": store_wh_name,
					"city": store_city,
				}
			).insert(ignore_permissions=True)

	frappe.db.commit()
