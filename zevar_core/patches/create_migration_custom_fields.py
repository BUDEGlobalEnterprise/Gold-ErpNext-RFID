"""
Create custom fields required for legacy FoxPro data migration.

Run: bench --site <site> execute zevar_core.patches.create_migration_custom_fields.execute
"""

import frappe
from frappe import _


def execute():
	"""Create all custom fields needed for legacy data import."""
	custom_fields = {
		"Customer": [
			{
				"fieldname": "custom_legacy_account_no",
				"label": "Legacy Account No",
				"fieldtype": "Data",
				"insert_after": "customer_group",
			},
			{
				"fieldname": "custom_company",
				"label": "Company",
				"fieldtype": "Data",
				"insert_after": "custom_legacy_account_no",
			},
			{
				"fieldname": "custom_title",
				"label": "Title",
				"fieldtype": "Data",
				"insert_after": "custom_company",
			},
			{
				"fieldname": "custom_birthday",
				"label": "Birthday",
				"fieldtype": "Data",
				"insert_after": "custom_title",
				"description": "Partial date from legacy system (e.g. 04-01-)",
			},
			{
				"fieldname": "custom_anniversary",
				"label": "Anniversary",
				"fieldtype": "Data",
				"insert_after": "custom_birthday",
			},
			{
				"fieldname": "custom_spouse_name",
				"label": "Spouse Name",
				"fieldtype": "Data",
				"insert_after": "custom_anniversary",
			},
			{
				"fieldname": "custom_discount_rate",
				"label": "Discount Rate (%)",
				"fieldtype": "Float",
				"insert_after": "custom_spouse_name",
			},
			{
				"fieldname": "custom_ytd_spend",
				"label": "YTD Spend",
				"fieldtype": "Currency",
				"insert_after": "custom_discount_rate",
			},
			{
				"fieldname": "custom_lifetime_spend",
				"label": "Lifetime Spend",
				"fieldtype": "Currency",
				"insert_after": "custom_ytd_spend",
			},
			{
				"fieldname": "custom_comments",
				"label": "Legacy Comments",
				"fieldtype": "Small Text",
				"insert_after": "custom_lifetime_spend",
			},
			{
				"fieldname": "custom_salesman1",
				"label": "Primary Salesman",
				"fieldtype": "Data",
				"insert_after": "custom_comments",
			},
			{
				"fieldname": "custom_salesman2",
				"label": "Secondary Salesman",
				"fieldtype": "Data",
				"insert_after": "custom_salesman1",
			},
			{
				"fieldname": "custom_refer_source",
				"label": "Referral Source",
				"fieldtype": "Data",
				"insert_after": "custom_salesman2",
			},
			{
				"fieldname": "custom_acct_type",
				"label": "Account Type",
				"fieldtype": "Data",
				"insert_after": "custom_refer_source",
			},
			{
				"fieldname": "custom_mailing",
				"label": "Mailing Opt-In",
				"fieldtype": "Check",
				"insert_after": "custom_acct_type",
			},
			{
				"fieldname": "custom_store_code",
				"label": "Store Code",
				"fieldtype": "Data",
				"insert_after": "custom_mailing",
			},
			{
				"fieldname": "custom_custcode",
				"label": "Customer Code",
				"fieldtype": "Data",
				"insert_after": "custom_store_code",
			},
			{
				"fieldname": "custom_link",
				"label": "Legacy Link",
				"fieldtype": "Data",
				"insert_after": "custom_custcode",
			},
			{
				"fieldname": "custom_phone2",
				"label": "Phone 2",
				"fieldtype": "Data",
				"insert_after": "custom_link",
			},
		],
		"Employee": [
			{
				"fieldname": "custom_commission_rate",
				"label": "Commission Rate (%)",
				"fieldtype": "Float",
				"insert_after": "employment_type",
			},
			{
				"fieldname": "custom_sales_level",
				"label": "Sales Level",
				"fieldtype": "Data",
				"insert_after": "custom_commission_rate",
			},
			{
				"fieldname": "custom_discount_permission",
				"label": "Max Discount (%)",
				"fieldtype": "Float",
				"insert_after": "custom_sales_level",
			},
			{
				"fieldname": "custom_ytd_sales",
				"label": "YTD Sales",
				"fieldtype": "Currency",
				"insert_after": "custom_discount_permission",
			},
			{
				"fieldname": "custom_sales_goal",
				"label": "Sales Goal",
				"fieldtype": "Currency",
				"insert_after": "custom_ytd_sales",
			},
			{
				"fieldname": "custom_home_store",
				"label": "Home Store",
				"fieldtype": "Link",
				"options": "Store Location",
				"insert_after": "custom_sales_goal",
			},
			{
				"fieldname": "custom_initials",
				"label": "Initials",
				"fieldtype": "Data",
				"insert_after": "custom_home_store",
			},
			{
				"fieldname": "custom_is_manager",
				"label": "Is Manager",
				"fieldtype": "Check",
				"insert_after": "custom_initials",
			},
		],
		"Item": [
			{
				"fieldname": "custom_source",
				"label": "Data Source",
				"fieldtype": "Data",
				"insert_after": "description",
			},
			{
				"fieldname": "custom_vendor_sku",
				"label": "Vendor SKU",
				"fieldtype": "Data",
				"insert_after": "custom_source",
			},
			{
				"fieldname": "custom_vendor",
				"label": "Vendor",
				"fieldtype": "Link",
				"options": "Supplier",
				"insert_after": "custom_vendor_sku",
			},
			{
				"fieldname": "custom_barcode",
				"label": "Barcode",
				"fieldtype": "Data",
				"insert_after": "custom_vendor",
			},
			{
				"fieldname": "custom_metal_type",
				"label": "Metal Type",
				"fieldtype": "Data",
				"insert_after": "custom_barcode",
			},
			{
				"fieldname": "custom_purity",
				"label": "Purity",
				"fieldtype": "Data",
				"insert_after": "custom_metal_type",
			},
			{
				"fieldname": "custom_jewelry_type",
				"label": "Jewelry Type",
				"fieldtype": "Data",
				"insert_after": "custom_purity",
			},
			{
				"fieldname": "custom_product_type",
				"label": "Product Type",
				"fieldtype": "Data",
				"insert_after": "custom_jewelry_type",
			},
			{
				"fieldname": "custom_gender",
				"label": "Gender",
				"fieldtype": "Data",
				"insert_after": "custom_product_type",
			},
			{
				"fieldname": "custom_gross_weight_g",
				"label": "Gross Weight (g)",
				"fieldtype": "Float",
				"insert_after": "custom_gender",
			},
			{
				"fieldname": "custom_msrp",
				"label": "MSRP",
				"fieldtype": "Currency",
				"insert_after": "custom_gross_weight_g",
			},
			{
				"fieldname": "custom_cost_price",
				"label": "Cost Price",
				"fieldtype": "Currency",
				"insert_after": "custom_msrp",
			},
			{
				"fieldname": "custom_size",
				"label": "Size",
				"fieldtype": "Data",
				"insert_after": "custom_cost_price",
			},
			{
				"fieldname": "custom_material_color",
				"label": "Material Color",
				"fieldtype": "Data",
				"insert_after": "custom_size",
			},
			{
				"fieldname": "custom_department",
				"label": "Department",
				"fieldtype": "Data",
				"insert_after": "custom_material_color",
			},
			{
				"fieldname": "custom_subcategory",
				"label": "Subcategory",
				"fieldtype": "Data",
				"insert_after": "custom_department",
			},
			{
				"fieldname": "custom_legacy_abr",
				"label": "Legacy Abbreviation",
				"fieldtype": "Data",
				"insert_after": "custom_subcategory",
			},
			{
				"fieldname": "custom_legacy_stockno",
				"label": "Legacy Stock Number",
				"fieldtype": "Data",
				"insert_after": "custom_legacy_abr",
			},
			{
				"fieldname": "custom_showcase",
				"label": "Showcase",
				"fieldtype": "Data",
				"insert_after": "custom_legacy_stockno",
			},
			{
				"fieldname": "custom_date_in",
				"label": "Date In",
				"fieldtype": "Date",
				"insert_after": "custom_showcase",
			},
			{
				"fieldname": "custom_date_sold",
				"label": "Date Sold",
				"fieldtype": "Date",
				"insert_after": "custom_date_in",
			},
			{
				"fieldname": "custom_invoice_ref",
				"label": "Invoice Reference",
				"fieldtype": "Data",
				"insert_after": "custom_date_sold",
			},
			{
				"fieldname": "custom_watch_model",
				"label": "Watch Model",
				"fieldtype": "Data",
				"insert_after": "custom_invoice_ref",
			},
			{
				"fieldname": "custom_watch_serial",
				"label": "Watch Serial",
				"fieldtype": "Data",
				"insert_after": "custom_watch_model",
			},
			{
				"fieldname": "custom_watch_condition",
				"label": "Watch Condition",
				"fieldtype": "Data",
				"insert_after": "custom_watch_serial",
			},
			{
				"fieldname": "custom_watch_supplier",
				"label": "Watch Supplier",
				"fieldtype": "Data",
				"insert_after": "custom_watch_condition",
			},
		],
		"Sales Invoice": [
			{
				"fieldname": "custom_legacy_trans_no",
				"label": "Legacy Trans No",
				"fieldtype": "Data",
				"insert_after": "title",
			},
			{
				"fieldname": "custom_store",
				"label": "Store",
				"fieldtype": "Link",
				"options": "Store Location",
				"insert_after": "custom_legacy_trans_no",
			},
			{
				"fieldname": "custom_receipt_no",
				"label": "Legacy Receipt No",
				"fieldtype": "Data",
				"insert_after": "custom_store",
			},
			{
				"fieldname": "custom_legacy_desc",
				"label": "Legacy Description",
				"fieldtype": "Data",
				"insert_after": "custom_receipt_no",
			},
			{
				"fieldname": "custom_trans_time",
				"label": "Transaction Time",
				"fieldtype": "Data",
				"insert_after": "custom_legacy_desc",
			},
		],
		"Supplier": [
			{
				"fieldname": "custom_legacy_abbrev",
				"label": "Legacy Abbreviation",
				"fieldtype": "Data",
				"insert_after": "supplier_name",
			},
			{
				"fieldname": "custom_legacy_account",
				"label": "Legacy Account No",
				"fieldtype": "Data",
				"insert_after": "custom_legacy_abbrev",
			},
			{
				"fieldname": "custom_budget",
				"label": "Budget",
				"fieldtype": "Currency",
				"insert_after": "custom_legacy_account",
			},
			{
				"fieldname": "custom_markup",
				"label": "Markup (%)",
				"fieldtype": "Percent",
				"insert_after": "custom_budget",
			},
			{
				"fieldname": "custom_discount",
				"label": "Discount (%)",
				"fieldtype": "Percent",
				"insert_after": "custom_markup",
			},
			{
				"fieldname": "custom_fax",
				"label": "Fax",
				"fieldtype": "Data",
				"insert_after": "custom_discount",
			},
			{
				"fieldname": "custom_phone2",
				"label": "Phone 2",
				"fieldtype": "Data",
				"insert_after": "custom_fax",
			},
			{
				"fieldname": "custom_total_purchases",
				"label": "Total Purchases",
				"fieldtype": "Currency",
				"insert_after": "custom_phone2",
			},
			{
				"fieldname": "custom_mtd_purchases",
				"label": "MTD Purchases",
				"fieldtype": "Currency",
				"insert_after": "custom_total_purchases",
			},
			{
				"fieldname": "custom_ptd_purchases",
				"label": "PTD Purchases",
				"fieldtype": "Currency",
				"insert_after": "custom_mtd_purchases",
			},
			{
				"fieldname": "custom_consigned",
				"label": "Consigned",
				"fieldtype": "Check",
				"insert_after": "custom_ptd_purchases",
			},
			{
				"fieldname": "custom_use_commission",
				"fieldtype": "Int",
				"label": "Use Commission",
				"insert_after": "custom_consigned",
			},
			{
				"fieldname": "custom_stock_turnover",
				"label": "Stock Turnover",
				"fieldtype": "Float",
				"insert_after": "custom_use_commission",
			},
			{
				"fieldname": "custom_product_line",
				"label": "Product Line",
				"fieldtype": "Small Text",
				"insert_after": "custom_stock_turnover",
			},
			{
				"fieldname": "custom_inactive",
				"label": "Inactive (Legacy)",
				"fieldtype": "Check",
				"insert_after": "custom_product_line",
			},
			{
				"fieldname": "custom_legacy_export",
				"label": "Legacy Export Ref",
				"fieldtype": "Data",
				"insert_after": "custom_inactive",
			},
		],
		"Jewelry Appraisal": [
			{
				"fieldname": "custom_legacy_stock_no",
				"label": "Legacy Stock No",
				"fieldtype": "Data",
				"insert_after": "certificate_number",
			},
			{
				"fieldname": "custom_legacy_abr",
				"label": "Legacy Vendor ABR",
				"fieldtype": "Data",
				"insert_after": "custom_legacy_stock_no",
			},
			{
				"fieldname": "custom_center_stone_weight",
				"label": "Center Stone Weight",
				"fieldtype": "Float",
				"insert_after": "custom_legacy_abr",
			},
			{
				"fieldname": "custom_center_stone_cut",
				"label": "Center Stone Cut",
				"fieldtype": "Data",
				"insert_after": "custom_center_stone_weight",
			},
			{
				"fieldname": "custom_center_stone_type",
				"label": "Center Stone Type",
				"fieldtype": "Data",
				"insert_after": "custom_center_stone_cut",
			},
			{
				"fieldname": "custom_center_stone_clarity",
				"label": "Center Stone Clarity",
				"fieldtype": "Data",
				"insert_after": "custom_center_stone_type",
			},
			{
				"fieldname": "custom_center_stone_color",
				"label": "Center Stone Color",
				"fieldtype": "Data",
				"insert_after": "custom_center_stone_clarity",
			},
			{
				"fieldname": "custom_side_stones_weight",
				"label": "Side Stones Weight",
				"fieldtype": "Float",
				"insert_after": "custom_center_stone_color",
			},
			{
				"fieldname": "custom_side_stones_qty",
				"label": "Side Stones Quantity",
				"fieldtype": "Int",
				"insert_after": "custom_side_stones_weight",
			},
			{
				"fieldname": "custom_stones_count",
				"label": "Total Stones",
				"fieldtype": "Int",
				"insert_after": "custom_side_stones_qty",
			},
		],
	}

	for doctype, fields in custom_fields.items():
		for cf in fields:
			fieldname = cf["fieldname"]
			if not frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": fieldname}):
				try:
					doc = frappe.get_doc(
						{
							"doctype": "Custom Field",
							"dt": doctype,
							"module": "Unified Retail Management System",
							**cf,
						}
					)
					doc.insert(ignore_permissions=True)
				except Exception as e:
					frappe.log_error(
						f"Failed to create {doctype}.{fieldname}: {e}",
						"Migration Custom Fields",
					)
		frappe.db.commit()  # nosemgrep

	# Create modes of payment for legacy tenders
	for mode in ["Cash", "Check", "Credit Card", "Debit Card"]:
		if not frappe.db.exists("Mode of Payment", mode):
			try:
				doc = frappe.new_doc("Mode of Payment")
				doc.mode_of_payment = mode
				doc.enabled = 1
				doc.insert(ignore_permissions=True)
			except frappe.DuplicateEntryError:
				pass
	frappe.db.commit()  # nosemgrep
