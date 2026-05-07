import frappe
from frappe.utils import cint, cstr, flt


@frappe.whitelist(allow_guest=False)
def get_settings():
	frappe.only_for("System Manager", "Store Manager", "Administrator")

	company = frappe.db.get_single_value("Global Defaults", "default_company") or frappe.db.get_value("Company", {}, "name")

	pos_profiles = frappe.get_all(
		"POS Profile",
		filters={"disabled": 0},
		fields=["name", "company", "warehouse", "posa_pos_profile_name",
				"customer", "selling_price_list", "cost_center", "income_account", "expense_account"],
		order_by="name asc",
	)

	warehouses = frappe.get_all(
		"Warehouse",
		filters={"disabled": 0, "is_group": 0},
		fields=["name", "warehouse_name", "parent_warehouse"],
		order_by="name asc",
	)

	customers = frappe.get_all(
		"Customer",
		filters={"disabled": 0},
		fields=["name", "customer_name", "customer_group"],
		order_by="customer_name asc",
		limit=200,
	)

	suppliers = frappe.get_all(
		"Supplier",
		filters={"disabled": 0},
		fields=["name", "supplier_name", "supplier_group"],
		order_by="supplier_name asc",
		limit=200,
	)

	price_lists = frappe.get_all(
		"Price List",
		filters={"enabled": 1},
		fields=["name", "price_list_name", "buying", "selling", "currency"],
		order_by="name asc",
	)

	modes = frappe.get_all(
		"Mode of Payment",
		filters={},
		fields=["name", "type"],
		order_by="name asc",
	)

	tax_templates = frappe.get_all(
		"Sales Taxes and Charges Template",
		filters={"disabled": 0},
		fields=["name", "company", "tax_category"],
		order_by="name asc",
	)

	cost_centers = frappe.get_all(
		"Cost Center",
		filters={"disabled": 0, "is_group": 0},
		fields=["name", "cost_center_name", "parent_cost_center"],
		order_by="lft asc",
	)

	accounts = frappe.get_all(
		"Account",
		filters={"disabled": 0, "is_group": 0},
		fields=["name", "account_name", "account_type", "root_type"],
		order_by="lft asc",
		limit=300,
	)

	users = frappe.get_all(
		"User",
		filters={"enabled": 1, "user_type": "System User"},
		fields=["name", "full_name", "email", "user_image"],
		order_by="full_name asc",
	)

	roles = frappe.get_all(
		"Role",
		filters={"disabled": 0},
		fields=["name"],
		order_by="name asc",
	)

	print_formats = frappe.get_all(
		"Print Format",
		filters={},
		fields=["name", "doc_type", "standard"],
		order_by="name asc",
	)

	item_groups = frappe.get_all(
		"Item Group",
		filters={"is_group": 0},
		fields=["name", "parent_item_group"],
		order_by="lft asc",
	)

	brands = frappe.get_all(
		"Brand",
		filters={},
		fields=["name"],
		order_by="name asc",
	)

	zevar_settings = {}
	if frappe.db.exists("Property Setter", {"doc_type": "POS Profile", "property": "default"}):
		zevar_settings["default_pos_profile"] = frappe.db.get_value("Property Setter", {"doc_type": "POS Profile", "property": "default"}, "value")

	return {
		"success": True,
		"company": company,
		"pos_profiles": pos_profiles,
		"warehouses": warehouses,
		"customers": customers,
		"suppliers": suppliers,
		"price_lists": price_lists,
		"modes_of_payment": modes,
		"tax_templates": tax_templates,
		"cost_centers": cost_centers,
		"accounts": accounts,
		"users": users,
		"roles": roles,
		"print_formats": print_formats,
		"item_groups": item_groups,
		"brands": brands,
		"zevar_settings": zevar_settings,
	}


@frappe.whitelist(allow_guest=False)
def get_pos_profile(name):
	frappe.only_for("System Manager", "Store Manager", "Administrator")
	name = cstr(name).strip()

	if not frappe.db.exists("POS Profile", name):
		frappe.throw("POS Profile not found")

	doc = frappe.get_doc("POS Profile", name)

	payment_methods = []
	for row in doc.get("payments", []):
		payment_methods.append({
			"mode_of_payment": row.mode_of_payment,
			"default": row.default,
		})

	item_groups_list = []
	for row in doc.get("posa_idx_items_groups", []):
		item_groups_list.append({
			"item_group": row.get("item_group", ""),
		})

	return {
		"success": True,
		"profile": {
			"name": doc.name,
			"company": doc.company,
			"warehouse": doc.warehouse,
			"customer": doc.customer,
			"selling_price_list": doc.selling_price_list,
			"cost_center": doc.cost_center,
			"income_account": doc.income_account,
			"expense_account": doc.expense_account,
			"posa_pos_profile_name": getattr(doc, "posa_pos_profile_name", ""),
			"disabled": doc.disabled,
			"currency": getattr(doc, "currency", ""),
			"payment_methods": payment_methods,
			"item_groups": item_groups_list,
		},
	}


@frappe.whitelist(allow_guest=False)
def create_pos_profile(company, warehouse, customer=None, selling_price_list=None,
						cost_center=None, income_account=None, expense_account=None,
						payments_json=None, name_override=None):
	frappe.only_for("System Manager", "Administrator")

	import json

	company = cstr(company).strip()
	if not company:
		frappe.throw("Company is required")

	profile = frappe.new_doc("POS Profile")
	if name_override:
		profile.posa_pos_profile_name = cstr(name_override).strip()
	profile.company = company
	profile.warehouse = cstr(warehouse).strip()
	if customer:
		profile.customer = cstr(customer).strip()
	if selling_price_list:
		profile.selling_price_list = cstr(selling_price_list).strip()
	if cost_center:
		profile.cost_center = cstr(cost_center).strip()
	if income_account:
		profile.income_account = cstr(income_account).strip()
	if expense_account:
		profile.expense_account = cstr(expense_account).strip()

	if payments_json:
		payments = json.loads(payments_json) if isinstance(payments_json, str) else payments_json
		for p in payments:
			mode = cstr(p.get("mode_of_payment", "")).strip()
			if not mode:
				continue
			profile.append("payments", {
				"mode_of_payment": mode,
				"default": cint(p.get("default", 0)),
			})

	profile.insert()
	return {"success": True, "name": profile.name}


@frappe.whitelist(allow_guest=False)
def update_pos_profile(name, **kwargs):
	frappe.only_for("System Manager", "Administrator")
	name = cstr(name).strip()

	if not frappe.db.exists("POS Profile", name):
		frappe.throw("POS Profile not found")

	doc = frappe.get_doc("POS Profile", name)

	updatable = ["warehouse", "customer", "selling_price_list", "cost_center",
				 "income_account", "expense_account", "posa_pos_profile_name", "disabled"]

	for field in updatable:
		if field in kwargs:
			setattr(doc, field, kwargs[field])

	if "payments_json" in kwargs:
		import json
		doc.payments = []
		payments = json.loads(kwargs["payments_json"]) if isinstance(kwargs["payments_json"], str) else kwargs["payments_json"]
		for p in payments:
			mode = cstr(p.get("mode_of_payment", "")).strip()
			if not mode:
				continue
			doc.append("payments", {
				"mode_of_payment": mode,
				"default": cint(p.get("default", 0)),
			})

	doc.save()
	return {"success": True, "name": doc.name}


@frappe.whitelist(allow_guest=False)
def delete_pos_profile(name):
	frappe.only_for("System Manager", "Administrator")
	name = cstr(name).strip()

	if not frappe.db.exists("POS Profile", name):
		frappe.throw("POS Profile not found")

	frappe.delete_doc("POS Profile", name)
	return {"success": True}


@frappe.whitelist(allow_guest=False)
def get_users_with_roles(page=1, page_size=50):
	frappe.only_for("System Manager", "Administrator")

	page = max(1, cint(page))
	page_size = min(100, max(1, cint(page_size)))
	limit_start = (page - 1) * page_size

	users = frappe.get_all(
		"User",
		filters={"enabled": 1, "user_type": "System User"},
		fields=["name", "full_name", "email", "user_image", "creation"],
		order_by="full_name asc",
		limit_start=limit_start,
		limit=page_size,
	)
	total = frappe.db.count("User", {"enabled": 1, "user_type": "System User"})

	for u in users:
		roles = frappe.get_all(
			"Has Role",
			filters={"parent": u["name"], "parenttype": "User"},
			fields=["role"],
		)
		u["roles"] = [r["role"] for r in roles]

	return {"success": True, "users": users, "total": total, "page": page, "page_size": page_size}


@frappe.whitelist(allow_guest=False)
def update_user_roles(user_email, roles_json):
	frappe.only_for("System Manager", "Administrator")

	import json

	user_email = cstr(user_email).strip()
	if not frappe.db.exists("User", user_email):
		frappe.throw("User not found")

	roles = json.loads(roles_json) if isinstance(roles_json, str) else roles_json

	doc = frappe.get_doc("User", user_email)
	existing_roles = {r.role for r in doc.roles}
	new_roles = set(roles)

	for role in new_roles - existing_roles:
		if frappe.db.exists("Role", role):
			doc.append("roles", {"role": role})

	for role in existing_roles - new_roles:
		if role in ("Administrator", "Guest"):
			continue
		doc.roles = [r for r in doc.roles if r.role != role]

	doc.save(ignore_permissions=True)
	return {"success": True}


@frappe.whitelist(allow_guest=False)
def create_user(email, first_name, last_name=None, roles_json=None, send_welcome_email=1):
	frappe.only_for("System Manager", "Administrator")

	import json

	email = cstr(email).strip().lower()
	first_name = cstr(first_name).strip()
	if not email or not first_name:
		frappe.throw("Email and first name are required")

	if frappe.db.exists("User", email):
		frappe.throw("User already exists")

	user = frappe.new_doc("User")
	user.email = email
	user.first_name = first_name
	user.last_name = cstr(last_name).strip() if last_name else ""
	user.send_welcome_email = cint(send_welcome_email)
	user.user_type = "System User"

	if roles_json:
		roles = json.loads(roles_json) if isinstance(roles_json, str) else roles_json
		for role in roles:
			if frappe.db.exists("Role", role):
				user.append("roles", {"role": role})

	user.insert(ignore_permissions=True)
	return {"success": True, "name": user.name}


@frappe.whitelist(allow_guest=False)
def get_print_formats(doctype=None):
	frappe.only_for("System Manager", "Store Manager", "Administrator")

	filters = {}
	if doctype:
		filters["doc_type"] = cstr(doctype).strip()

	formats = frappe.get_all(
		"Print Format",
		filters=filters,
		fields=["name", "doc_type", "standard", "custom_format", "print_style"],
		order_by="doc_type, name asc",
	)

	return {"success": True, "print_formats": formats}


@frappe.whitelist(allow_guest=False)
def get_company_settings():
	frappe.only_for("System Manager", "Administrator")

	company = frappe.db.get_single_value("Global Defaults", "default_company") or frappe.db.get_value("Company", {}, "name")
	if not company:
		return {"success": True, "company": None, "settings": {}}

	doc = frappe.get_doc("Company", company)

	return {
		"success": True,
		"company": company,
		"settings": {
			"company_name": doc.company_name,
			"abbr": doc.abbr,
			"default_currency": doc.default_currency,
			"country": doc.country,
			"tax_id": getattr(doc, "tax_id", ""),
			"registration_number": getattr(doc, "registration_number", ""),
		},
	}


@frappe.whitelist(allow_guest=False)
def get_system_info():
	frappe.only_for("System Manager", "Administrator")

	from frappe.utils.user import get_system_managers

	return {
		"success": True,
		"system_info": {
			"frappe_version": frappe.__version__,
			"installed_apps": frappe.get_installed_apps(),
			"site_name": frappe.local.site,
			"default_company": frappe.db.get_single_value("Global Defaults", "default_company"),
			"system_managers": get_system_managers(),
			"maintenance_mode": frappe.conf.get("maintenance_mode", False),
		},
	}
