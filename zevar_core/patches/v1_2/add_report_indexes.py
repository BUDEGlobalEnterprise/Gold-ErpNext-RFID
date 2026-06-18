import frappe

def execute():
	"""Add composite indexes for reporting performance."""

	if frappe.db.exists("DocType", "Sales Invoice"):
		try:
			existing = frappe.db.sql(  # nosemgrep
				"""
				SELECT INDEX_NAME
				FROM INFORMATION_SCHEMA.STATISTICS
				WHERE TABLE_SCHEMA = DATABASE()
				AND TABLE_NAME = 'tabSales Invoice'
				AND INDEX_NAME = 'idx_sales_invoice_report'
			"""
			)

			if not existing:
				frappe.db.sql(  # nosemgrep
					"CREATE INDEX `idx_sales_invoice_report` ON `tabSales Invoice` (`docstatus`, `posting_date`, `set_warehouse`)"
				)
		except Exception:
			pass

	if frappe.db.exists("DocType", "Sale Cost Breakdown"):
		try:
			existing = frappe.db.sql(  # nosemgrep
				"""
				SELECT INDEX_NAME
				FROM INFORMATION_SCHEMA.STATISTICS
				WHERE TABLE_SCHEMA = DATABASE()
				AND TABLE_NAME = 'tabSale Cost Breakdown'
				AND INDEX_NAME = 'idx_sale_cost_breakdown_posting_date'
			"""
			)

			if not existing:
				frappe.db.sql(  # nosemgrep
					"CREATE INDEX `idx_sale_cost_breakdown_posting_date` ON `tabSale Cost Breakdown` (`posting_date`)"
				)
		except Exception:
			pass

	frappe.db.commit()  # nosemgrep
