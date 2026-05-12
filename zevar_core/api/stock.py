import frappe
from frappe.utils import cint, cstr, flt, today

# ─── SUPPLIER ORDERS (Purchase Order) ────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_supplier_orders(status=None, supplier=None, from_date=None, to_date=None, page=1, page_size=20):
	frappe.has_permission("Purchase Order", ptype="read", throw=True)

	filters = {"docstatus": ["!=", 2]}
	if status:
		filters["status"] = status
	if supplier:
		filters["supplier"] = supplier
	if from_date:
		filters["transaction_date"] = [">=", from_date]
	if to_date:
		filters.setdefault("transaction_date", [])
		if isinstance(filters["transaction_date"], list):
			filters["transaction_date"] = ["between", [from_date or "2000-01-01", to_date]]

	page = max(1, cint(page))
	page_size = min(100, max(1, cint(page_size)))
	limit_start = (page - 1) * page_size

	orders = frappe.get_all(
		"Purchase Order",
		filters=filters,
		fields=[
			"name",
			"supplier",
			"supplier_name",
			"transaction_date",
			"schedule_date",
			"status",
			"grand_total",
			"currency",
			"per_received",
			"per_billed",
			"docstatus",
		],
		order_by="transaction_date desc",
		limit_start=limit_start,
		limit=page_size,
	)
	total = frappe.db.count("Purchase Order", filters)

	return {"success": True, "orders": orders, "total": total, "page": page, "page_size": page_size}


@frappe.whitelist(allow_guest=False)
def get_supplier_order_detail(name):
	frappe.has_permission("Purchase Order", ptype="read", throw=True)
	name = cstr(name).strip()
	if not frappe.db.exists("Purchase Order", name):
		frappe.throw("Purchase Order not found")

	doc = frappe.get_doc("Purchase Order", name)
	items = []
	for row in doc.items:
		items.append(
			{
				"item_code": row.item_code,
				"item_name": row.item_name,
				"qty": row.qty,
				"received_qty": row.received_qty,
				"rate": row.rate,
				"amount": row.amount,
				"warehouse": row.warehouse,
				"schedule_date": str(row.schedule_date) if row.schedule_date else "",
			}
		)

	return {
		"success": True,
		"order": {
			"name": doc.name,
			"supplier": doc.supplier,
			"supplier_name": doc.supplier_name,
			"transaction_date": str(doc.transaction_date),
			"schedule_date": str(doc.schedule_date) if doc.schedule_date else "",
			"status": doc.status,
			"grand_total": flt(doc.grand_total),
			"currency": doc.currency,
			"docstatus": doc.docstatus,
			"per_received": flt(doc.per_received),
			"per_billed": flt(doc.per_billed),
			"items": items,
		},
	}


@frappe.whitelist(allow_guest=False)
def create_purchase_order(supplier, items_json, warehouse=None, schedule_date=None):
	frappe.has_permission("Purchase Order", ptype="create", throw=True)

	import json

	supplier = cstr(supplier).strip()
	if not supplier:
		frappe.throw("Supplier is required")
	if not frappe.db.exists("Supplier", supplier):
		frappe.throw(f"Supplier '{supplier}' not found")

	items = json.loads(items_json) if isinstance(items_json, str) else items_json
	if not items or not isinstance(items, list):
		frappe.throw("At least one item is required")

	po = frappe.new_doc("Purchase Order")
	po.supplier = supplier
	po.transaction_date = today()
	po.schedule_date = schedule_date or today()

	for item in items:
		item_code = cstr(item.get("item_code", "")).strip()
		if not item_code:
			continue
		po.append(
			"items",
			{
				"item_code": item_code,
				"qty": max(1, flt(item.get("qty", 1))),
				"rate": flt(item.get("rate", 0)),
				"warehouse": item.get("warehouse")
				or warehouse
				or frappe.defaults.get_user_default("Warehouse"),
				"schedule_date": item.get("schedule_date") or schedule_date or today(),
			},
		)

	if not po.items:
		frappe.throw("No valid items provided")

	po.insert()
	return {"success": True, "name": po.name, "status": po.status}


@frappe.whitelist(allow_guest=False)
def submit_purchase_order(name):
	frappe.has_permission("Purchase Order", ptype="submit", throw=True)
	name = cstr(name).strip()
	doc = frappe.get_doc("Purchase Order", name)
	doc.submit()
	return {"success": True, "name": doc.name, "status": doc.status}


@frappe.whitelist(allow_guest=False)
def cancel_purchase_order(name):
	frappe.has_permission("Purchase Order", ptype="cancel", throw=True)
	name = cstr(name).strip()
	doc = frappe.get_doc("Purchase Order", name)
	doc.cancel()
	return {"success": True, "name": doc.name, "status": "Cancelled"}


# ─── INCOMING MEMOS (Purchase Receipt filtered for memo/consignment) ─────────


@frappe.whitelist(allow_guest=False)
def get_incoming_memos(status=None, supplier=None, page=1, page_size=20):
	frappe.has_permission("Purchase Receipt", ptype="read", throw=True)

	filters = {"docstatus": ["!=", 2]}
	if status:
		filters["status"] = status
	if supplier:
		filters["supplier"] = supplier

	page = max(1, cint(page))
	page_size = min(100, max(1, cint(page_size)))
	limit_start = (page - 1) * page_size

	memos = frappe.get_all(
		"Purchase Receipt",
		filters=filters,
		fields=[
			"name",
			"supplier",
			"supplier_name",
			"posting_date",
			"status",
			"grand_total",
			"currency",
			"docstatus",
			"is_return",
			"total_qty",
		],
		order_by="posting_date desc",
		limit_start=limit_start,
		limit=page_size,
	)
	total = frappe.db.count("Purchase Receipt", filters)

	return {"success": True, "memos": memos, "total": total, "page": page, "page_size": page_size}


@frappe.whitelist(allow_guest=False)
def create_memo(supplier, items_json, warehouse=None):
	frappe.has_permission("Purchase Receipt", ptype="create", throw=True)

	import json

	supplier = cstr(supplier).strip()
	if not supplier:
		frappe.throw("Supplier is required")

	items = json.loads(items_json) if isinstance(items_json, str) else items_json
	if not items:
		frappe.throw("At least one item is required")

	pr = frappe.new_doc("Purchase Receipt")
	pr.supplier = supplier
	pr.posting_date = today()

	for item in items:
		item_code = cstr(item.get("item_code", "")).strip()
		if not item_code:
			continue
		pr.append(
			"items",
			{
				"item_code": item_code,
				"qty": max(1, flt(item.get("qty", 1))),
				"rate": flt(item.get("rate", 0)),
				"warehouse": item.get("warehouse")
				or warehouse
				or frappe.defaults.get_user_default("Warehouse"),
			},
		)

	if not pr.items:
		frappe.throw("No valid items provided")

	pr.insert()
	return {"success": True, "name": pr.name}


@frappe.whitelist(allow_guest=False)
def receive_memo(name):
	frappe.has_permission("Purchase Receipt", ptype="submit", throw=True)
	name = cstr(name).strip()
	doc = frappe.get_doc("Purchase Receipt", name)
	doc.submit()
	return {"success": True, "name": doc.name, "status": doc.status}


# ─── ASSEMBLIES (Stock Entry: Manufacture / Repack) ──────────────────────────


@frappe.whitelist(allow_guest=False)
def get_assemblies(status=None, purpose=None, page=1, page_size=20):
	frappe.has_permission("Stock Entry", ptype="read", throw=True)

	filters = {
		"purpose": ["in", ["Manufacture", "Repack"]],
		"docstatus": ["!=", 2],
	}
	if purpose and purpose in ("Manufacture", "Repack"):
		filters["purpose"] = purpose
	if status == "Draft":
		filters["docstatus"] = 0
	elif status == "Submitted":
		filters["docstatus"] = 1

	page = max(1, cint(page))
	page_size = min(100, max(1, cint(page_size)))
	limit_start = (page - 1) * page_size

	entries = frappe.get_all(
		"Stock Entry",
		filters=filters,
		fields=[
			"name",
			"purpose",
			"posting_date",
			"from_warehouse",
			"to_warehouse",
			"total_amount",
			"docstatus",
		],
		order_by="posting_date desc",
		limit_start=limit_start,
		limit=page_size,
	)
	total = frappe.db.count("Stock Entry", filters)

	return {"success": True, "assemblies": entries, "total": total, "page": page, "page_size": page_size}


@frappe.whitelist(allow_guest=False)
def create_assembly(items_json, source_warehouse=None, target_warehouse=None, purpose="Manufacture"):
	frappe.has_permission("Stock Entry", ptype="create", throw=True)

	import json

	if purpose not in ("Manufacture", "Repack"):
		frappe.throw("Purpose must be Manufacture or Repack")

	items = json.loads(items_json) if isinstance(items_json, str) else items_json
	if not items:
		frappe.throw("At least one item is required")

	se = frappe.new_doc("Stock Entry")
	se.purpose = purpose
	se.posting_date = today()
	se.from_warehouse = source_warehouse
	se.to_warehouse = target_warehouse

	for item in items:
		item_code = cstr(item.get("item_code", "")).strip()
		if not item_code:
			continue
		se.append(
			"items",
			{
				"item_code": item_code,
				"qty": max(0.001, flt(item.get("qty", 1))),
				"s_warehouse": item.get("s_warehouse") or source_warehouse,
				"t_warehouse": item.get("t_warehouse") or target_warehouse,
			},
		)

	if not se.items:
		frappe.throw("No valid items provided")

	se.insert()
	return {"success": True, "name": se.name}


@frappe.whitelist(allow_guest=False)
def disassemble(name):
	frappe.has_permission("Stock Entry", ptype="cancel", throw=True)
	name = cstr(name).strip()
	doc = frappe.get_doc("Stock Entry", name)
	if doc.purpose not in ("Manufacture", "Repack"):
		frappe.throw("Can only disassemble Manufacture or Repack entries")
	doc.cancel()
	return {"success": True, "name": doc.name}


# ─── METALS ──────────────────────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_metals(page=1, page_size=50):
	frappe.has_permission("Item", ptype="read", throw=True)

	page = max(1, cint(page))
	page_size = min(100, max(1, cint(page_size)))
	limit_start = (page - 1) * page_size

	metal_groups = frappe.get_all(
		"Item Group",
		filters={"name": ["like", "%Metal%"]},
		pluck="name",
	)
	if not metal_groups:
		metal_groups = ["Metals"]

	items = frappe.get_all(
		"Item",
		filters={"item_group": ["in", metal_groups], "disabled": 0},
		fields=[
			"name as item_code",
			"item_name",
			"item_group",
			"stock_uom",
			"standard_rate",
			"valuation_rate",
			"custom_metal_type",
			"custom_purity",
			"custom_gross_weight",
		],
		limit_start=limit_start,
		limit=page_size,
	)
	total = frappe.db.count("Item", {"item_group": ["in", metal_groups], "disabled": 0})

	for item in items:
		item["stock_qty"] = flt(
			frappe.db.sql(
				"SELECT SUM(actual_qty) FROM `tabBin` WHERE item_code=%s",
				(item["item_code"],),
			)[0][0]
			or 0
		)
		item["current_value"] = flt(item.get("standard_rate") or item.get("valuation_rate") or 0)

	return {"success": True, "items": items, "total": total, "page": page, "page_size": page_size}


# ─── GEMS ────────────────────────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_gems(gem_type=None, certified_only=0, page=1, page_size=50):
	frappe.has_permission("Item", ptype="read", throw=True)

	page = max(1, cint(page))
	page_size = min(100, max(1, cint(page_size)))
	limit_start = (page - 1) * page_size

	gem_groups = frappe.get_all(
		"Item Group",
		filters={"name": ["like", "%Gem%"]},
		pluck="name",
	)
	stone_groups = frappe.get_all(
		"Item Group",
		filters={"name": ["like", "%Stone%"]},
		pluck="name",
	)
	all_groups = list(set(gem_groups + stone_groups)) or ["Gems", "Stones"]

	filters = {"item_group": ["in", all_groups], "disabled": 0}
	if gem_type:
		filters["custom_gem_type"] = gem_type

	items = frappe.get_all(
		"Item",
		filters=filters,
		fields=[
			"name as item_code",
			"item_name",
			"item_group",
			"standard_rate",
			"valuation_rate",
			"image",
			"custom_gem_type",
			"custom_carat_weight",
			"custom_gem_shape",
			"custom_gem_color",
			"custom_gem_clarity",
			"custom_gem_cut",
			"custom_certification_number",
		],
		limit_start=limit_start,
		limit=page_size,
	)
	total = frappe.db.count("Item", filters)

	for item in items:
		item["stock_qty"] = flt(
			frappe.db.sql(
				"SELECT SUM(actual_qty) FROM `tabBin` WHERE item_code=%s",
				(item["item_code"],),
			)[0][0]
			or 0
		)

	return {"success": True, "items": items, "total": total, "page": page, "page_size": page_size}


# ─── WAREHOUSES (Storages) ───────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_warehouses(parent=None, page=1, page_size=50):
	frappe.has_permission("Warehouse", ptype="read", throw=True)

	page = max(1, cint(page))
	page_size = min(100, max(1, cint(page_size)))
	limit_start = (page - 1) * page_size

	filters = {"disabled": 0}
	if parent:
		filters["parent_warehouse"] = parent

	warehouses = frappe.get_all(
		"Warehouse",
		filters=filters,
		fields=[
			"name",
			"warehouse_name",
			"parent_warehouse",
			"is_group",
			"warehouse_type",
			"company",
		],
		order_by="lft asc",
		limit_start=limit_start,
		limit=page_size,
	)
	total = frappe.db.count("Warehouse", filters)

	for wh in warehouses:
		result = frappe.db.sql(
			"""SELECT COUNT(DISTINCT item_code) as item_count,
                      SUM(actual_qty * valuation_rate) as total_value
               FROM `tabBin` WHERE warehouse=%s AND actual_qty > 0""",
			(wh["name"],),
			as_dict=True,
		)
		wh["item_count"] = cint((result[0] or {}).get("item_count", 0))
		wh["total_value"] = flt((result[0] or {}).get("total_value", 0))

	return {"success": True, "warehouses": warehouses, "total": total, "page": page, "page_size": page_size}


@frappe.whitelist(allow_guest=False)
def get_warehouse_details(name):
	frappe.has_permission("Warehouse", ptype="read", throw=True)
	name = cstr(name).strip()
	if not frappe.db.exists("Warehouse", name):
		frappe.throw("Warehouse not found")

	wh = frappe.get_doc("Warehouse", name)
	items = frappe.db.sql(
		"""SELECT b.item_code, i.item_name, b.actual_qty, b.valuation_rate,
                  (b.actual_qty * b.valuation_rate) as value
           FROM `tabBin` b
           JOIN `tabItem` i ON b.item_code = i.name
           WHERE b.warehouse=%s AND b.actual_qty > 0
           ORDER BY b.item_code""",
		(name,),
		as_dict=True,
	)

	children = frappe.get_all(
		"Warehouse",
		filters={"parent_warehouse": name, "disabled": 0},
		fields=["name", "warehouse_name", "is_group"],
	)

	return {
		"success": True,
		"warehouse": {
			"name": wh.name,
			"warehouse_name": wh.warehouse_name,
			"parent_warehouse": wh.parent_warehouse,
			"is_group": wh.is_group,
			"warehouse_type": wh.warehouse_type,
		},
		"items": items,
		"children": children,
	}


# ─── CATEGORIES (Item Group) ────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_categories(parent=None, page=1, page_size=100):
	frappe.has_permission("Item Group", ptype="read", throw=True)

	page = max(1, cint(page))
	page_size = min(200, max(1, cint(page_size)))
	limit_start = (page - 1) * page_size

	filters = {}
	if parent:
		filters["parent_item_group"] = parent

	groups = frappe.get_all(
		"Item Group",
		filters=filters,
		fields=["name", "item_group_name", "parent_item_group", "is_group", "image"],
		order_by="lft asc",
		limit_start=limit_start,
		limit=page_size,
	)
	total = frappe.db.count("Item Group", filters)

	for g in groups:
		g["item_count"] = frappe.db.count("Item", {"item_group": g["name"], "disabled": 0})

	return {"success": True, "categories": groups, "total": total, "page": page, "page_size": page_size}


# ─── BRANDS ──────────────────────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_brands(search=None, page=1, page_size=50):
	frappe.has_permission("Brand", ptype="read", throw=True)

	page = max(1, cint(page))
	page_size = min(100, max(1, cint(page_size)))
	limit_start = (page - 1) * page_size

	filters = {}
	if search:
		filters["name"] = ["like", f"%{cstr(search).strip()}%"]

	brands = frappe.get_all(
		"Brand",
		filters=filters,
		fields=["name", "brand as brand_name", "image"],
		order_by="name asc",
		limit_start=limit_start,
		limit=page_size,
	)
	total = frappe.db.count("Brand", filters)

	for b in brands:
		b["item_count"] = frappe.db.count("Item", {"brand": b["name"], "disabled": 0})

	return {"success": True, "brands": brands, "total": total, "page": page, "page_size": page_size}


# ─── COLLECTIONS ─────────────────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_collections(page=1, page_size=50):
	frappe.has_permission("Item Group", ptype="read", throw=True)

	page = max(1, cint(page))
	page_size = min(100, max(1, cint(page_size)))
	limit_start = (page - 1) * page_size

	groups = frappe.get_all(
		"Item Group",
		filters={"is_group": 0},
		fields=["name", "item_group_name", "parent_item_group", "image"],
		order_by="name asc",
		limit_start=limit_start,
		limit=page_size,
	)
	total = frappe.db.count("Item Group", {"is_group": 0})

	for g in groups:
		g["item_count"] = frappe.db.count("Item", {"item_group": g["name"], "disabled": 0})

	return {"success": True, "collections": groups, "total": total, "page": page, "page_size": page_size}


# ─── SUPPLIER LIST (for selectors) ──────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_suppliers(search=None, page=1, page_size=20):
	frappe.has_permission("Supplier", ptype="read", throw=True)

	page = max(1, cint(page))
	page_size = min(100, max(1, cint(page_size)))
	limit_start = (page - 1) * page_size

	filters = {"disabled": 0}
	if search:
		search = cstr(search).strip()
		filters["supplier_name"] = ["like", f"%{search}%"]

	suppliers = frappe.get_all(
		"Supplier",
		filters=filters,
		fields=["name", "supplier_name", "supplier_group", "supplier_type"],
		order_by="supplier_name asc",
		limit_start=limit_start,
		limit=page_size,
	)
	total = frappe.db.count("Supplier", filters)

	return {"success": True, "suppliers": suppliers, "total": total}

@frappe.whitelist(allow_guest=False)
def get_items_by_case(display_case: str) -> list:
	"""Return full item list for a specific display case."""
	if not frappe.db.exists("Display Case", display_case):
		frappe.throw(frappe._("Display Case {0} not found").format(display_case))

	warehouse = frappe.db.get_value("Display Case", display_case, "warehouse")
	if not warehouse:
		return []

	items = frappe.db.sql("""
		SELECT 
			b.item_code, 
			i.item_name, 
			b.actual_qty, 
			b.valuation_rate,
			(b.actual_qty * b.valuation_rate) as value,
			i.image,
			i.custom_metal_type as metal,
			i.custom_purity as purity,
			i.custom_jewelry_type as jewelry_type
		FROM `tabBin` b
		JOIN `tabItem` i ON b.item_code = i.name
		WHERE b.warehouse = %s AND b.actual_qty > 0
		ORDER BY i.custom_jewelry_type, b.item_code
	""", (warehouse,), as_dict=True)

	return items
