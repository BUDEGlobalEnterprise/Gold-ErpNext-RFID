import frappe


def execute():
	"""Rename gold purity labels from K suffix to Kt suffix.

	Canonical form is now 22Kt (not 22K). Updates:
	  - Gold Rate Log entries
	  - Zevar Purity master records
	  - Item custom_purity field values
	  - Creates new Kt purity records if they don't exist
	"""
	rename_map = {
		"24K": "24Kt",
		"22K": "22Kt",
		"18K": "18Kt",
		"14K": "14Kt",
		"10K": "10Kt",
	}

	for old_purity, new_purity in rename_map.items():
		if not frappe.db.exists("Zevar Purity", new_purity):
			old_doc = frappe.db.get_value("Zevar Purity", old_purity, ["fine_metal_content"], as_dict=True)
			if old_doc:
				frappe.get_doc(
					{
						"doctype": "Zevar Purity",
						"__newname": new_purity,
						"fine_metal_content": old_doc.fine_metal_content,
					}
				).insert(ignore_permissions=True)

		frappe.db.sql(
			"UPDATE `tabGold Rate Log` SET purity = %s WHERE purity = %s",
			(new_purity, old_purity),
		)

		frappe.db.sql(
			"UPDATE `tabItem` SET custom_purity = %s WHERE custom_purity = %s",
			(new_purity, old_purity),
		)

	frappe.db.commit()
