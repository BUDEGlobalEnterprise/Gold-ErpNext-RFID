import frappe


def execute():
	"""Backfill custom_transaction_stream on historical Sales Invoices."""
	if not frappe.db.has_column("Sales Invoice", "custom_transaction_stream"):
		return

	# Update Repairs (where custom_repair_reference is set or similar linking exists)
	if frappe.db.has_column("Sales Invoice", "custom_repair_reference"):
		frappe.db.sql("""
			UPDATE `tabSales Invoice`
			SET custom_transaction_stream = 'Repair'
			WHERE (custom_transaction_stream IS NULL OR custom_transaction_stream = '')
			AND custom_repair_reference IS NOT NULL AND custom_repair_reference != ''
		""")

	# Update Layaways (where custom_layaway_reference is set)
	if frappe.db.has_column("Sales Invoice", "custom_layaway_reference"):
		frappe.db.sql("""
			UPDATE `tabSales Invoice`
			SET custom_transaction_stream = 'Layaway Final'
			WHERE (custom_transaction_stream IS NULL OR custom_transaction_stream = '')
			AND custom_layaway_reference IS NOT NULL AND custom_layaway_reference != ''
		""")

	# Fallback to Jewelry Sale for everything else
	frappe.db.sql("""
		UPDATE `tabSales Invoice`
		SET custom_transaction_stream = 'Jewelry Sale'
		WHERE (custom_transaction_stream IS NULL OR custom_transaction_stream = '')
	""")

	frappe.db.commit()
