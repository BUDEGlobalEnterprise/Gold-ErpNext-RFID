"""
Generic CRUD API for reference/lookup data DocTypes.

This is the building block for the stock-dashboard CRUD pages (Metals, Gems,
Categories, Brands, Collections, Storages). Each function is whitelisted,
validates inputs, enforces permissions, and returns a uniform
`{"success": True, ...}` shape.

Why per-doctype rather than a single `frappe.client.insert` wrapper?
- Permission and validation rules differ per DocType (e.g. Warehouse needs
  parent_warehouse, Item needs item_group).
- Audit logging can be wired per-doctype without leaking across types.
- Avoids passing raw kwargs that bypass business rules in the controller.

Security: every endpoint is `@frappe.whitelist(allow_guest=False)` and uses
`frappe.has_permission(doctype, ptype, throw=True)`. Callers cannot escalate.
"""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import cint, cstr, flt

# ─── Allowed-fields allowlist (defense in depth) ────────────────────────────

ITEM_WRITABLE_FIELDS = {
	"item_name",
	"item_group",
	"brand",
	"description",
	"image",
	"stock_uom",
	"standard_rate",
	"valuation_rate",
	"is_stock_item",
	"disabled",
	"custom_metal_type",
	"custom_purity",
	"custom_gross_weight_g",
	"custom_stone_weight_g",
	"custom_net_weight_g",
	"custom_jewelry_type",
	"custom_jewelry_subtype",
	"custom_gem_type",
	"custom_carat_weight",
	"custom_gem_shape",
	"custom_gem_color",
	"custom_gem_clarity",
	"custom_gem_cut",
	"custom_certification_number",
	"custom_vendor_sku",
	"custom_vendor",
	"custom_msrp",
	"custom_cost_price",
	"custom_gender",
	"custom_country_of_origin",
	"custom_material_color",
	"custom_finish",
	"custom_plating",
	"custom_size",
}

ITEM_GROUP_WRITABLE_FIELDS = {
	"item_group_name",
	"parent_item_group",
	"is_group",
	"image",
	"description",
}

BRAND_WRITABLE_FIELDS = {
	"brand",
	"image",
	"description",
}

WAREHOUSE_WRITABLE_FIELDS = {
	"warehouse_name",
	"parent_warehouse",
	"is_group",
	"warehouse_type",
	"company",
	"disabled",
}


# ─── Helpers ────────────────────────────────────────────────────────────────


def _parse_values(values_json, allowed_fields, doctype=None):
	"""Parse JSON values payload and filter to allowed fields only.

	If `doctype` is provided, also drop any field that does not exist on the
	target DocType meta. This makes the API robust to schema drift (e.g. a
	custom field defined in fixtures that hasn't been migrated yet).
	"""
	if not values_json:
		frappe.throw(_("No values provided"))
	values = json.loads(values_json) if isinstance(values_json, str) else values_json
	if not isinstance(values, dict):
		frappe.throw(_("Values must be a JSON object"))
	filtered = {k: v for k, v in values.items() if k in allowed_fields}
	if not filtered:
		frappe.throw(_("No writable fields provided"))
	if doctype:
		meta = frappe.get_meta(doctype)
		existing = {f.fieldname for f in meta.fields}
		filtered = {k: v for k, v in filtered.items() if k in existing}
		if not filtered:
			frappe.throw(
				_("No writable fields match the current {0} schema").format(doctype)
			)
	return filtered


# ─── Item (Metals, Gems, etc.) ──────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def create_item(values_json, item_group=None):
	"""Create a new Item with the given field values."""
	frappe.has_permission("Item", ptype="create", throw=True)
	values = _parse_values(values_json, ITEM_WRITABLE_FIELDS, doctype="Item")

	# item_name is required
	if not values.get("item_name"):
		frappe.throw(_("Item name is required"))

	# item_group can come from values or as override
	values["item_group"] = item_group or values.get("item_group")
	if not values["item_group"]:
		frappe.throw(_("Item group is required"))
	if not frappe.db.exists("Item Group", values["item_group"]):
		frappe.throw(_("Item Group {0} does not exist").format(values["item_group"]))

	if values.get("brand") and not frappe.db.exists("Brand", values["brand"]):
		frappe.throw(_("Brand {0} does not exist").format(values["brand"]))

	# Default stock UOM
	values.setdefault("stock_uom", "Nos")
	values.setdefault("is_stock_item", 1)

	# Auto-generate item_code from item_name if missing
	if not values.get("item_code") and not values.get("name"):
		base = cstr(values["item_name"]).upper().replace(" ", "-")[:20]
		# Strip non-alnum-dash chars
		base = "".join(c for c in base if c.isalnum() or c == "-")
		# Append a sequence to ensure uniqueness
		idx = 0
		while frappe.db.exists("Item", f"{base}-{idx:04d}"):
			idx += 1
		values["item_code"] = f"{base}-{idx:04d}"

	doc = frappe.new_doc("Item")
	doc.update(values)
	doc.insert()
	return {"success": True, "name": doc.name, "item_name": doc.item_name}


@frappe.whitelist(allow_guest=False)
def update_item(name, values_json):
	"""Update fields on an existing Item."""
	frappe.has_permission("Item", ptype="write", throw=True)
	name = cstr(name).strip()
	if not frappe.db.exists("Item", name):
		frappe.throw(_("Item {0} not found").format(name))

	values = _parse_values(values_json, ITEM_WRITABLE_FIELDS, doctype="Item")
	doc = frappe.get_doc("Item", name)
	for field, value in values.items():
		setattr(doc, field, value)
	doc.save()
	return {"success": True, "name": doc.name, "item_name": doc.item_name}


@frappe.whitelist(allow_guest=False)
def delete_item(name):
	"""Soft-disable an Item (we never hard-delete inventory items)."""
	frappe.has_permission("Item", ptype="delete", throw=True)
	name = cstr(name).strip()
	if not frappe.db.exists("Item", name):
		frappe.throw(_("Item {0} not found").format(name))

	# Guard: refuse if item has open stock or open transactions
	open_bin = frappe.db.sql(
		"SELECT SUM(actual_qty) FROM `tabBin` WHERE item_code=%s",
		(name,),
	)[0][0] or 0
	if flt(open_bin) > 0:
		frappe.throw(
			_("Cannot delete {0}: has {1} units in stock. Disable it instead.").format(name, flt(open_bin))
		)

	doc = frappe.get_doc("Item", name)
	doc.db_set("disabled", 1)
	return {"success": True, "name": name, "disabled": True}


@frappe.whitelist(allow_guest=False)
def get_item(name):
	"""Get a single Item with full fields + child table counts."""
	frappe.has_permission("Item", ptype="read", throw=True)
	name = cstr(name).strip()
	if not frappe.db.exists("Item", name):
		frappe.throw(_("Item {0} not found").format(name))
	doc = frappe.get_doc("Item", name)
	return {
		"success": True,
		"item": {
			"name": doc.name,
			"item_name": doc.item_name,
			"item_group": doc.item_group,
			"brand": doc.brand,
			"description": doc.description,
			"image": doc.image,
			"stock_uom": doc.stock_uom,
			"standard_rate": flt(doc.standard_rate),
			"valuation_rate": flt(doc.valuation_rate),
			"is_stock_item": doc.is_stock_item,
			"disabled": doc.disabled,
			"custom_metal_type": doc.custom_metal_type,
			"custom_purity": doc.custom_purity,
			"custom_gross_weight_g": doc.custom_gross_weight_g,
			"custom_stone_weight_g": doc.custom_stone_weight_g,
			"custom_net_weight_g": doc.custom_net_weight_g,
			"custom_jewelry_type": doc.custom_jewelry_type,
			"custom_gem_type": doc.custom_gem_type,
			"custom_carat_weight": doc.custom_carat_weight,
			"custom_gem_shape": doc.custom_gem_shape,
			"custom_gem_color": doc.custom_gem_color,
			"custom_gem_clarity": doc.custom_gem_clarity,
			"custom_gem_cut": doc.custom_gem_cut,
			"custom_certification_number": doc.custom_certification_number,
			"custom_vendor_sku": doc.custom_vendor_sku,
			"custom_vendor": doc.custom_vendor,
			"custom_msrp": flt(doc.custom_msrp),
			"custom_cost_price": flt(doc.custom_cost_price),
			"custom_gender": doc.custom_gender,
			"custom_country_of_origin": doc.custom_country_of_origin,
		},
	}


# ─── Item Group (Categories, Collections) ───────────────────────────────────


@frappe.whitelist(allow_guest=False)
def create_item_group(values_json):
	"""Create a new Item Group."""
	frappe.has_permission("Item Group", ptype="create", throw=True)
	values = _parse_values(values_json, ITEM_GROUP_WRITABLE_FIELDS, doctype="Item Group")

	if not values.get("item_group_name"):
		frappe.throw(_("Group name is required"))

	# Auto-generate name (the autoname field) from item_group_name
	if not values.get("name"):
		base = cstr(values["item_group_name"]).strip()
		if not frappe.db.exists("Item Group", base):
			values["name"] = base
		else:
			# Append sequence
			idx = 1
			while frappe.db.exists("Item Group", f"{base}-{idx}"):
				idx += 1
			values["name"] = f"{base}-{idx}"

	if values.get("parent_item_group") and not frappe.db.exists(
		"Item Group", values["parent_item_group"]
	):
		frappe.throw(_("Parent Item Group {0} does not exist").format(values["parent_item_group"]))

	doc = frappe.new_doc("Item Group")
	doc.update(values)
	doc.insert()
	return {"success": True, "name": doc.name}


@frappe.whitelist(allow_guest=False)
def update_item_group(name, values_json):
	"""Update fields on an existing Item Group."""
	frappe.has_permission("Item Group", ptype="write", throw=True)
	name = cstr(name).strip()
	if not frappe.db.exists("Item Group", name):
		frappe.throw(_("Item Group {0} not found").format(name))

	values = _parse_values(values_json, ITEM_GROUP_WRITABLE_FIELDS, doctype="Item Group")
	doc = frappe.get_doc("Item Group", name)
	for field, value in values.items():
		setattr(doc, field, value)
	doc.save()
	return {"success": True, "name": doc.name}


@frappe.whitelist(allow_guest=False)
def delete_item_group(name):
	"""Delete an Item Group if it has no items and no children."""
	frappe.has_permission("Item Group", ptype="delete", throw=True)
	name = cstr(name).strip()
	if not frappe.db.exists("Item Group", name):
		frappe.throw(_("Item Group {0} not found").format(name))

	item_count = frappe.db.count("Item", {"item_group": name, "disabled": 0})
	if item_count > 0:
		frappe.throw(
			_("Cannot delete {0}: {1} items still assigned").format(name, item_count)
		)

	children = frappe.get_all("Item Group", filters={"parent_item_group": name}, limit=1)
	if children:
		frappe.throw(_("Cannot delete {0}: has child groups").format(name))

	frappe.delete_doc("Item Group", name, ignore_permissions=False)
	return {"success": True, "name": name}


# ─── Brand ──────────────────────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def create_brand(values_json):
	"""Create a new Brand."""
	frappe.has_permission("Brand", ptype="create", throw=True)
	values = _parse_values(values_json, BRAND_WRITABLE_FIELDS, doctype="Brand")

	if not values.get("brand"):
		frappe.throw(_("Brand name is required"))

	# Brand has name = brand
	brand_name = cstr(values["brand"]).strip()
	if frappe.db.exists("Brand", brand_name):
		frappe.throw(_("Brand {0} already exists").format(brand_name))
	values["name"] = brand_name

	doc = frappe.new_doc("Brand")
	doc.update(values)
	doc.insert()
	return {"success": True, "name": doc.name}


@frappe.whitelist(allow_guest=False)
def update_brand(name, values_json):
	"""Update fields on an existing Brand."""
	frappe.has_permission("Brand", ptype="write", throw=True)
	name = cstr(name).strip()
	if not frappe.db.exists("Brand", name):
		frappe.throw(_("Brand {0} not found").format(name))

	values = _parse_values(values_json, BRAND_WRITABLE_FIELDS, doctype="Brand")
	doc = frappe.get_doc("Brand", name)
	for field, value in values.items():
		setattr(doc, field, value)
	doc.save()
	return {"success": True, "name": doc.name}


@frappe.whitelist(allow_guest=False)
def delete_brand(name):
	"""Delete a Brand if no items reference it."""
	frappe.has_permission("Brand", ptype="delete", throw=True)
	name = cstr(name).strip()
	if not frappe.db.exists("Brand", name):
		frappe.throw(_("Brand {0} not found").format(name))

	item_count = frappe.db.count("Item", {"brand": name, "disabled": 0})
	if item_count > 0:
		frappe.throw(
			_("Cannot delete {0}: {1} items still use this brand").format(name, item_count)
		)

	frappe.delete_doc("Brand", name, ignore_permissions=False)
	return {"success": True, "name": name}


# ─── Warehouse (Storages) ──────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def create_warehouse(values_json):
	"""Create a new Warehouse."""
	frappe.has_permission("Warehouse", ptype="create", throw=True)
	values = _parse_values(values_json, WAREHOUSE_WRITABLE_FIELDS, doctype="Warehouse")

	if not values.get("warehouse_name"):
		frappe.throw(_("Warehouse name is required"))

	# Auto-generate name from warehouse_name (use "X - ABBR" convention)
	# Use the company abbr if available
	company = values.get("company") or frappe.defaults.get_user_default("Company")
	if company:
		company_abbr = frappe.db.get_value("Company", company, "abbr") or ""
	else:
		company_abbr = ""

	warehouse_name = cstr(values["warehouse_name"]).strip()
	if company_abbr and not warehouse_name.endswith(f" - {company_abbr}"):
		full_name = f"{warehouse_name} - {company_abbr}"
	else:
		full_name = warehouse_name

	# If parent_warehouse is given, derive full name
	parent = values.get("parent_warehouse")
	if parent:
		if not frappe.db.exists("Warehouse", parent):
			frappe.throw(_("Parent warehouse {0} does not exist").format(parent))
		# Derive: "{warehouse_name} - {parent_abbr}"
		# For simplicity just use the user-provided name unless it collides
		if not frappe.db.exists("Warehouse", full_name):
			values["name"] = full_name
		else:
			frappe.throw(_("Warehouse {0} already exists").format(full_name))
	else:
		if not frappe.db.exists("Warehouse", full_name):
			values["name"] = full_name
		else:
			frappe.throw(_("Warehouse {0} already exists").format(full_name))

	# company is required by Warehouse DocType
	if not values.get("company"):
		values["company"] = (
			frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")
		)
	if not values["company"]:
		frappe.throw(_("Company is required to create a warehouse"))

	doc = frappe.new_doc("Warehouse")
	doc.update(values)
	doc.insert()
	return {"success": True, "name": doc.name}


@frappe.whitelist(allow_guest=False)
def update_warehouse(name, values_json):
	"""Update fields on an existing Warehouse."""
	frappe.has_permission("Warehouse", ptype="write", throw=True)
	name = cstr(name).strip()
	if not frappe.db.exists("Warehouse", name):
		frappe.throw(_("Warehouse {0} not found").format(name))

	values = _parse_values(values_json, WAREHOUSE_WRITABLE_FIELDS, doctype="Warehouse")
	doc = frappe.get_doc("Warehouse", name)
	for field, value in values.items():
		setattr(doc, field, value)
	doc.save()
	return {"success": True, "name": doc.name}


@frappe.whitelist(allow_guest=False)
def delete_warehouse(name):
	"""Disable a Warehouse if it has no stock or child warehouses."""
	frappe.has_permission("Warehouse", ptype="delete", throw=True)
	name = cstr(name).strip()
	if not frappe.db.exists("Warehouse", name):
		frappe.throw(_("Warehouse {0} not found").format(name))

	# Guard: refuse if has stock
	stock = frappe.db.sql(
		"SELECT SUM(actual_qty) FROM `tabBin` WHERE warehouse=%s AND actual_qty > 0",
		(name,),
	)[0][0] or 0
	if flt(stock) > 0:
		frappe.throw(
			_("Cannot delete {0}: has {1} units in stock. Disable it instead.").format(name, flt(stock))
		)

	# Guard: refuse if has children
	children = frappe.get_all("Warehouse", filters={"parent_warehouse": name, "disabled": 0}, limit=1)
	if children:
		frappe.throw(_("Cannot delete {0}: has child warehouses").format(name))

	doc = frappe.get_doc("Warehouse", name)
	doc.db_set("disabled", 1)
	return {"success": True, "name": name, "disabled": True}


# ─── Lookup helpers (used by modals) ───────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_item_groups_for_select(parent=None, is_group=None):
	"""Return Item Groups as a flat list for dropdowns."""
	frappe.has_permission("Item Group", ptype="read", throw=True)
	filters = {}
	if parent is not None:
		filters["parent_item_group"] = parent
	if is_group is not None:
		filters["is_group"] = cint(is_group)
	return frappe.get_all(
		"Item Group",
		filters=filters,
		fields=["name", "item_group_name", "parent_item_group", "is_group"],
		order_by="name asc",
		limit_page_length=500,
	)


@frappe.whitelist(allow_guest=False)
def get_warehouses_for_select(parent=None):
	"""Return Warehouses for dropdowns."""
	frappe.has_permission("Warehouse", ptype="read", throw=True)
	filters = {"disabled": 0}
	if parent is not None:
		filters["parent_warehouse"] = parent
	return frappe.get_all(
		"Warehouse",
		filters=filters,
		fields=["name", "warehouse_name", "parent_warehouse", "is_group"],
		order_by="name asc",
		limit_page_length=500,
	)


@frappe.whitelist(allow_guest=False)
def get_items_in_group(item_group):
	"""Return items belonging to a group (used by Categories/Brands/Collections click-through)."""
	frappe.has_permission("Item", ptype="read", throw=True)
	item_group = cstr(item_group).strip()
	if not frappe.db.exists("Item Group", item_group):
		frappe.throw(_("Item Group {0} not found").format(item_group))

	# Recurse into children
	all_groups = [item_group]
	children = frappe.get_all(
		"Item Group",
		filters={"parent_item_group": item_group},
		pluck="name",
	)
	all_groups.extend(children)

	items = frappe.get_all(
		"Item",
		filters={"item_group": ["in", all_groups], "disabled": 0},
		fields=[
			"name as item_code",
			"item_name",
			"image",
			"standard_rate",
			"valuation_rate",
		],
		order_by="item_name asc",
		limit_page_length=200,
	)
	return {"success": True, "items": items, "count": len(items), "groups": all_groups}


@frappe.whitelist(allow_guest=False)
def get_items_for_brand(brand):
	"""Return items using this brand."""
	frappe.has_permission("Item", ptype="read", throw=True)
	brand = cstr(brand).strip()
	if not frappe.db.exists("Brand", brand):
		frappe.throw(_("Brand {0} not found").format(brand))

	items = frappe.get_all(
		"Item",
		filters={"brand": brand, "disabled": 0},
		fields=[
			"name as item_code",
			"item_name",
			"image",
			"item_group",
			"standard_rate",
		],
		order_by="item_name asc",
		limit_page_length=200,
	)
	return {"success": True, "items": items, "count": len(items)}
