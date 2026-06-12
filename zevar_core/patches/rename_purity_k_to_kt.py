import frappe


def execute():
	"""Rename gold purity labels from K suffix to Kt suffix.

	Canonical form is now 22Kt (not 22K). Updates:
	  - Gold Rate Log entries
	  - Zevar Purity master records
	  - Item custom_purity field values
	  - Creates new Kt purity records if they don't exist
	"""
	# Fix any existing incorrect fine_metal_content values in the database (e.g. 18.0 -> 0.750, 14.0 -> 0.5833, 9.0 -> 0.375)
	frappe.db.sql(
		"UPDATE `tabZevar Purity` SET fine_metal_content = fine_metal_content / 24.0 WHERE fine_metal_content > 1 AND fine_metal_content <= 24"
	)
	frappe.db.sql(
		"UPDATE `tabZevar Purity` SET fine_metal_content = fine_metal_content / 1000.0 WHERE fine_metal_content > 24"
	)

	rename_map = {
		"24K": "24Kt",
		"22K": "22Kt",
		"18K": "18Kt",
		"14K": "14Kt",
		"10K": "10Kt",
	}

	for old_purity, new_purity in rename_map.items():
		if not frappe.db.exists("Zevar Purity", new_purity):
			old_doc = frappe.db.get_value(
				"Zevar Purity",
				old_purity,
				[
					"fine_metal_content",
					"purity_code",
					"purity_name",
					"metal",
					"is_millesimal",
					"aliases",
					"is_active",
				],
				as_dict=True,
			)
			if old_doc:
				frappe.get_doc(
					{
						"doctype": "Zevar Purity",
						"purity_name": new_purity,
						"purity_code": old_doc.purity_code or new_purity,
						"metal": old_doc.metal or "Yellow Gold",
						"fine_metal_content": old_doc.fine_metal_content,
						"is_millesimal": old_doc.is_millesimal or 0,
						"aliases": old_doc.aliases,
						"is_active": old_doc.is_active or 1,
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
