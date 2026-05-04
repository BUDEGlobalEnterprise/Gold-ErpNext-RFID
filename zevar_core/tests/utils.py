import frappe
from frappe import _


def get_test_company() -> str:
	company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
		"Global Defaults", "default_company"
	)
	if not company:
		frappe.throw(_("Default company is required for tests."))
	return company


def ensure_customer(customer_name: str) -> str:
	"""Create a minimal customer if it does not already exist."""
	existing = frappe.db.exists("Customer", {"customer_name": customer_name})
	if existing:
		return existing

	customer = frappe.new_doc("Customer")
	customer.customer_name = customer_name
	customer.customer_type = "Individual"
	customer.customer_group = "Individual"
	customer.territory = "All Territories"
	customer.insert(ignore_permissions=True)
	return customer.name


def ensure_item_group(
	item_group_name: str = "Zevar Test Items",
	parent_item_group: str = "Products",
) -> str:
	"""Create a dedicated item group hierarchy for tests."""
	if (
		parent_item_group
		and parent_item_group != "All Item Groups"
		and not frappe.db.exists("Item Group", parent_item_group)
	):
		parent_group = frappe.new_doc("Item Group")
		parent_group.item_group_name = parent_item_group
		parent_group.parent_item_group = "All Item Groups"
		parent_group.insert(ignore_permissions=True)

	existing = frappe.db.exists("Item Group", item_group_name)
	if existing:
		return existing

	item_group = frappe.new_doc("Item Group")
	item_group.item_group_name = item_group_name
	item_group.parent_item_group = parent_item_group or "All Item Groups"
	item_group.insert(ignore_permissions=True)
	return item_group.name


def ensure_warehouse(warehouse_name: str = "Zevar Test Warehouse", company: str | None = None) -> str:
	"""Create a warehouse and return its actual document name."""
	company = company or get_test_company()
	existing = frappe.db.get_value(
		"Warehouse",
		{"warehouse_name": warehouse_name, "company": company},
		"name",
	)
	if existing:
		return existing

	warehouse = frappe.new_doc("Warehouse")
	warehouse.warehouse_name = warehouse_name
	warehouse.company = company
	warehouse.insert(ignore_permissions=True)
	return warehouse.name


def ensure_item(
	item_code: str,
	item_name: str,
	rate: float = 100.0,
	item_group_name: str = "Zevar Test Items",
) -> str:
	"""Create a stock sales item and return its name."""
	item_group = ensure_item_group(item_group_name)
	existing = frappe.db.exists("Item", item_code)
	if existing:
		current_group = frappe.db.get_value("Item", item_code, "item_group")
		if not current_group or not frappe.db.exists("Item Group", current_group):
			frappe.db.set_value("Item", item_code, "item_group", item_group)
		return existing

	item = frappe.new_doc("Item")
	item.item_code = item_code
	item.item_name = item_name
	item.item_group = item_group
	item.stock_uom = "Nos"
	item.is_stock_item = 1
	item.is_sales_item = 1
	item.standard_rate = rate
	item.insert(ignore_permissions=True)
	return item.name


def ensure_mode_of_payment(mode_of_payment: str, payment_type: str = "Cash") -> str:
	"""Create a payment mode used by POS tests if needed."""
	if frappe.db.exists("Mode of Payment", mode_of_payment):
		return mode_of_payment

	doc = frappe.new_doc("Mode of Payment")
	doc.mode_of_payment = mode_of_payment
	doc.type = payment_type
	doc.enabled = 1
	doc.insert(ignore_permissions=True)
	return doc.name


def ensure_pos_profile(
	profile_name: str = "Test POS Profile",
	warehouse_name: str = "Zevar Test Warehouse",
) -> str:
	"""Create a minimal POS profile suitable for tests."""
	existing = frappe.db.exists("POS Profile", profile_name)
	if existing:
		return existing

	company = get_test_company()
	warehouse = ensure_warehouse(warehouse_name=warehouse_name, company=company)
	customer = ensure_customer("Walk-In Customer")
	ensure_mode_of_payment("Cash", payment_type="Cash")

	profile = frappe.new_doc("POS Profile")
	profile.name = profile_name
	profile.company = company
	profile.warehouse = warehouse
	profile.currency = "USD"
	profile.customer = customer
	profile.selling_price_list = "Standard Selling"
	profile.append("payments", {"mode_of_payment": "Cash", "default": 1})
	profile.insert(ignore_permissions=True, ignore_mandatory=True)
	return profile.name
