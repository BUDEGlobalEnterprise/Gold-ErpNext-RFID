"""Inventory v2 API endpoints.

Whitelisted Frappe RPC endpoints for the Inventory Management v2 features:
- Reference tables (Metal, Purity, Gemstone Type)
- BOM assembly / disassembly
- Gemstone tracking
- Repair parts consumption
- External bench dispatch
- Memo lifecycle
- Appraisal management
- Inventory locking
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint, flt


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_json_or_fail(value):
	if isinstance(value, dict):
		return value
	try:
		return frappe.parse_json(value)
	except Exception:
		frappe.throw(_("Invalid JSON: {0}").format(value))


def _require(data, key):
	val = data.get(key)
	if not val:
		frappe.throw(_("Parameter '{0}' is required").format(key))
	return val


# ---------------------------------------------------------------------------
# Reference Tables
# ---------------------------------------------------------------------------


@frappe.whitelist(allow_guest=False)
def list_metals():
	frappe.has_permission("Zevar Metal", ptype="read", throw=True)
	return frappe.get_all(
		"Zevar Metal",
		filters={"is_active": 1},
		fields=["name", "metal_code", "metal_name", "metal_type", "default_purity", "color_hex"],
		order_by="metal_name",
	)


@frappe.whitelist(allow_guest=False)
def list_purities(metal: str | None = None):
	frappe.has_permission("Zevar Purity", ptype="read", throw=True)
	filters = {"is_active": 1}
	if metal:
		filters["metal"] = metal
	return frappe.get_all(
		"Zevar Purity",
		filters=filters,
		fields=["name", "purity_code", "purity_name", "metal", "fine_metal_content", "is_millesimal", "aliases"],
		order_by="fine_metal_content desc",
	)


@frappe.whitelist(allow_guest=False)
def list_gemstone_types():
	frappe.has_permission("Zevar Gemstone Type", ptype="read", throw=True)
	return frappe.get_all(
		"Zevar Gemstone Type",
		filters={"is_active": 1},
		fields=["name", "gemstone_type_name", "category", "hardness_mohs", "color_hex"],
		order_by="category, gemstone_type_name",
	)


# ---------------------------------------------------------------------------
# BOM
# ---------------------------------------------------------------------------


@frappe.whitelist(allow_guest=False)
def get_bom_for_item(item_code: str):
	frappe.has_permission("Jewelry BOM", ptype="read", throw=True)
	bom = frappe.get_all(
		"Jewelry BOM",
		filters={"parent_item_code": item_code, "is_active": 1, "is_default": 1},
		fields=["name", "bom_name", "parent_item_code", "is_default", "labor_minutes", "labor_cost_per_minute", "overhead_pct", "yield_qty"],
		limit=1,
	)
	if not bom:
		return {"found": False}
	bom_doc = frappe.get_doc("Jewelry BOM", bom[0].name)
	components = []
	for c in bom_doc.components:
		components.append({
			"component_type": c.component_type,
			"component_item": c.component_item,
			"component_item_name": c.component_item_name,
			"qty_per_build": c.qty_per_build,
			"uom": c.uom,
			"serial_required": c.serial_required,
			"cost_share_pct": c.cost_share_pct,
		})
	return {"found": True, "bom": bom[0], "components": components}


@frappe.whitelist(allow_guest=False)
def list_boms(item_code: str | None = None):
	frappe.has_permission("Jewelry BOM", ptype="read", throw=True)
	filters = {"is_active": 1}
	if item_code:
		filters["parent_item_code"] = item_code
	return frappe.get_all(
		"Jewelry BOM",
		filters=filters,
		fields=["name", "bom_name", "parent_item_code", "is_default", "yield_qty"],
		order_by="parent_item_code, is_default desc",
	)


@frappe.whitelist(allow_guest=False)
def assemble_from_bom(bom_name: str, parent_serial_no: str | None = None):
	frappe.has_permission("Jewelry BOM", ptype="read", throw=True)
	frappe.only_for("Sales Manager", "Store Manager", "System Manager")

	from zevar_core.services.bom_service import assemble_from_bom as _assemble
	return _assemble(bom_name, parent_serial_no)


@frappe.whitelist(allow_guest=False)
def disassemble_to_components(parent_serial_no: str, bom_name: str, reason: str | None = None):
	frappe.has_permission("Jewelry BOM", ptype="read", throw=True)
	frappe.only_for("Sales Manager", "Store Manager", "System Manager")

	from zevar_core.services.bom_service import disassemble_to_components as _disassemble
	return _disassemble(parent_serial_no, bom_name, reason)


@frappe.whitelist(allow_guest=False)
def get_bom_cost_rollup(bom_name: str):
	frappe.has_permission("Jewelry BOM", ptype="read", throw=True)
	from zevar_core.services.bom_service import get_bom_cost_rollup as _rollup
	return _rollup(bom_name)


# ---------------------------------------------------------------------------
# Gemstones
# ---------------------------------------------------------------------------


@frappe.whitelist(allow_guest=False)
def list_gemstones(status: str | None = None, gemstone_type: str | None = None, limit: int = 50):
	frappe.has_permission("Zevar Gemstone", ptype="read", throw=True)
	filters = {}
	if status:
		filters["status"] = status
	if gemstone_type:
		filters["gemstone_type"] = gemstone_type
	return frappe.get_all(
		"Zevar Gemstone",
		filters=filters,
		fields=["name", "gemstone_type", "shape", "carat_weight", "color", "clarity", "cut", "status", "serial_no", "is_melee"],
		order_by="creation desc",
		limit_page_length=cint(limit),
	)


@frappe.whitelist(allow_guest=False)
def get_gemstone(name: str):
	frappe.has_permission("Zevar Gemstone", ptype="read", throw=True)
	if not frappe.db.exists("Zevar Gemstone", name):
		frappe.throw(_("Gemstone {0} not found").format(name))
	return frappe.get_value("Zevar Gemstone", name, ["*"], as_dict=True)


@frappe.whitelist(allow_guest=False)
def register_gemstone(data: str | dict):
	frappe.has_permission("Zevar Gemstone", ptype="create", throw=True)
	frappe.only_for("Sales Manager", "Store Manager", "System Manager")

	data = _parse_json_or_fail(data)
	gem = frappe.new_doc("Zevar Gemstone")
	for key in ("gemstone_type", "shape", "carat_weight", "color", "clarity", "cut",
				"cert_lab", "cert_number", "cert_date", "cost_basis", "vendor",
				"is_melee", "melee_parcel", "current_location"):
		if key in data:
			setattr(gem, key, data[key])
	gem.insert(ignore_permissions=True)
	return {"success": True, "name": gem.name}


@frappe.whitelist(allow_guest=False)
def attach_gemstone_to_serial(gemstone: str, serial_no: str):
	frappe.has_permission("Zevar Gemstone", ptype="write", throw=True)
	gem = frappe.get_doc("Zevar Gemstone", gemstone)
	if gem.status == "Mounted":
		frappe.throw(_("Gemstone {0} is already mounted").format(gemstone))
	gem.serial_no = serial_no
	gem.status = "Mounted"
	gem.save(ignore_permissions=True)
	return {"success": True, "gemstone": gemstone, "serial_no": serial_no, "status": "Mounted"}


@frappe.whitelist(allow_guest=False)
def detach_gemstone_from_serial(gemstone: str):
	frappe.has_permission("Zevar Gemstone", ptype="write", throw=True)
	frappe.only_for("Sales Manager", "Store Manager", "System Manager")
	gem = frappe.get_doc("Zevar Gemstone", gemstone)
	gem.serial_no = ""
	gem.parent_serial_no = ""
	gem.status = "In Stock"
	gem.save(ignore_permissions=True)
	return {"success": True, "gemstone": gemstone, "status": "In Stock"}


# ---------------------------------------------------------------------------
# Repair Parts
# ---------------------------------------------------------------------------


@frappe.whitelist(allow_guest=False)
def list_repair_parts(repair_order: str):
	frappe.has_permission("Repair Order", ptype="read", throw=True)
	from zevar_core.services.repair_parts_service import get_parts_summary
	return get_parts_summary(repair_order)


@frappe.whitelist(allow_guest=False)
def consume_repair_part(data: str | dict):
	frappe.has_permission("Repair Order", ptype="write", throw=True)
	frappe.only_for("Sales Manager", "Store Manager", "System Manager", "Sales User")

	data = _parse_json_or_fail(data)
	from zevar_core.services.repair_parts_service import consume_part
	return consume_part(
		repair_order=_require(data, "repair_order"),
		component_item=_require(data, "component_item"),
		qty=flt(data.get("qty", 1)),
		source_warehouse=_require(data, "source_warehouse"),
		unit_cost=flt(data.get("unit_cost", 0)) or None,
		serial_no=data.get("serial_no"),
		notes=data.get("notes"),
	)


@frappe.whitelist(allow_guest=False)
def return_repair_part(data: str | dict):
	frappe.has_permission("Repair Order", ptype="write", throw=True)
	frappe.only_for("Sales Manager", "Store Manager", "System Manager")

	data = _parse_json_or_fail(data)
	from zevar_core.services.repair_parts_service import return_unused_part
	return return_unused_part(
		repair_order=_require(data, "repair_order"),
		component_item=_require(data, "component_item"),
		qty=flt(data.get("qty", 1)),
		to_warehouse=_require(data, "to_warehouse"),
		serial_no=data.get("serial_no"),
	)


# ---------------------------------------------------------------------------
# External Bench
# ---------------------------------------------------------------------------


@frappe.whitelist(allow_guest=False)
def dispatch_to_external_bench(repair_order: str, vendor: str, estimated_days: int | None = None):
	frappe.has_permission("Repair Order", ptype="write", throw=True)
	frappe.only_for("Sales Manager", "Store Manager", "System Manager")

	from zevar_core.services.external_bench_service import dispatch_to_bench
	return dispatch_to_bench(repair_order, vendor, estimated_days)


@frappe.whitelist(allow_guest=False)
def receive_from_external_bench(repair_order: str, invoice_ref: str | None = None, bench_cost: float | None = None):
	frappe.has_permission("Repair Order", ptype="write", throw=True)
	frappe.only_for("Sales Manager", "Store Manager", "System Manager")

	from zevar_core.services.external_bench_service import receive_from_bench
	return receive_from_bench(repair_order, invoice_ref, bench_cost)


@frappe.whitelist(allow_guest=False)
def get_bench_status(vendor: str):
	frappe.has_permission("Repair Order", ptype="read", throw=True)
	from zevar_core.services.external_bench_service import get_bench_status as _status
	return _status(vendor)


# ---------------------------------------------------------------------------
# Memo Lifecycle
# ---------------------------------------------------------------------------


@frappe.whitelist(allow_guest=False)
def create_memo(data: str | dict):
	frappe.has_permission("Memo Contract", ptype="create", throw=True)
	frappe.only_for("Sales Manager", "Store Manager", "System Manager")

	data = _parse_json_or_fail(data)
	from zevar_core.services.memo_lifecycle_service import create_memo as _create
	return _create(
		memo_class=_require(data, "memo_class"),
		items=_require(data, "items"),
		customer=data.get("customer"),
		vendor=data.get("vendor"),
		valid_until=data.get("valid_until"),
		notes=data.get("notes"),
	)


@frappe.whitelist(allow_guest=False)
def mark_memo_item_sold(memo_contract: str, item_code: str, serial_no: str | None = None):
	frappe.has_permission("Memo Contract", ptype="write", throw=True)
	from zevar_core.services.memo_lifecycle_service import mark_item_sold
	return mark_item_sold(memo_contract, item_code, serial_no)


@frappe.whitelist(allow_guest=False)
def mark_memo_item_returned(memo_contract: str, item_code: str, serial_no: str | None = None, return_slip_ref: str | None = None):
	frappe.has_permission("Memo Contract", ptype="write", throw=True)
	from zevar_core.services.memo_lifecycle_service import mark_item_returned
	return mark_item_returned(memo_contract, item_code, serial_no=serial_no, return_slip_ref=return_slip_ref)


@frappe.whitelist(allow_guest=False)
def get_memo_aging_dashboard(memo_class: str | None = None):
	frappe.has_permission("Memo Contract", ptype="read", throw=True)
	from zevar_core.services.memo_lifecycle_service import get_aging_summary
	return get_aging_summary(memo_class)


# ---------------------------------------------------------------------------
# Appraisal
# ---------------------------------------------------------------------------


@frappe.whitelist(allow_guest=False)
def create_appraisal(data: str | dict):
	frappe.has_permission("Jewelry Appraisal", ptype="create", throw=True)

	data = _parse_json_or_fail(data)
	from zevar_core.services.appraisal_service import create_appraisal as _create
	return _create(
		item_code=_require(data, "item_code"),
		serial_no=data.get("serial_no"),
		template_name=data.get("template_name"),
		customer=data.get("customer"),
		appraised_value=flt(data.get("appraised_value", 0)),
		notes=data.get("notes"),
	)


@frappe.whitelist(allow_guest=False)
def list_expiring_appraisals(days_ahead: int = 90):
	frappe.has_permission("Jewelry Appraisal", ptype="read", throw=True)
	from zevar_core.services.appraisal_service import get_expiring_appraisals
	return get_expiring_appraisals(cint(days_ahead))


@frappe.whitelist(allow_guest=False)
def get_appraisal_history(item_code: str, serial_no: str | None = None):
	frappe.has_permission("Jewelry Appraisal", ptype="read", throw=True)
	from zevar_core.services.appraisal_service import get_appraisal_history as _history
	return _history(item_code, serial_no)


# ---------------------------------------------------------------------------
# Inventory Locking
# ---------------------------------------------------------------------------


@frappe.whitelist(allow_guest=False)
def acquire_inventory_lock(serial_no: str, lock_owner: str | None = None):
	frappe.has_permission("Serial No", ptype="read", throw=True)
	from zevar_core.services.inventory_locking import acquire_serial_lock
	return acquire_serial_lock(serial_no, lock_owner)


@frappe.whitelist(allow_guest=False)
def release_inventory_lock(serial_no: str, lock_token: str | None = None):
	frappe.has_permission("Serial No", ptype="read", throw=True)
	from zevar_core.services.inventory_locking import release_serial_lock
	return release_serial_lock(serial_no, lock_token)


@frappe.whitelist(allow_guest=False)
def check_inventory_lock(serial_no: str):
	frappe.has_permission("Serial No", ptype="read", throw=True)
	from zevar_core.services.inventory_locking import check_serial_locked
	return check_serial_locked(serial_no)
