"""
Quick Item Entry API - Simplified item creation with auto vendor SKU.

Replaces the multi-step legacy item addition workflow with a single-call API.
"""

import frappe
from frappe import _
from frappe.utils import cint, flt, nowdate

_JEWELRY_TYPE_CODES = {
	"Rings": "RNG",
	"Chains": "CHN",
	"Necklaces": "NKL",
	"Earrings": "EAR",
	"Bracelets": "BRA",
	"Pendants": "PND",
	"Watches": "WTC",
	"Other": "OTH",
}


@frappe.whitelist()
def quick_add_item(
	item_name: str,
	vendor: str | None = None,
	vendor_sku: str | None = None,
	metal_type: str | None = None,
	purity: str | None = None,
	jewelry_type: str = "Other",
	gross_weight: float = 0,
	stone_weight: float = 0,
	msrp: float = 0,
	cost_price: float = 0,
	gender: str = "Unisex",
	country_of_origin: str = "USA",
	warehouse: str | None = None,
	qty: int = 1,
	image: str | None = None,
	description: str | None = None,
	**_kwargs,
) -> dict:
	"""
	Create a new Item in one step with auto-generated vendor SKU.

	This replaces the legacy multi-step workflow where users had to:
	1. Create Item → 2. Set vendor → 3. Add jewelry details → 4. Stock entry

	Now it's one call that handles everything.

	Args:
	    item_name: Display name for the item
	    vendor: Supplier name (Link to Supplier)
	    vendor_sku: Vendor's SKU. If empty, auto-generated from vendor prefix + sequence
	    metal_type: Metal type (Yellow Gold, White Gold, etc.)
	    purity: Purity (10K, 14K, 18K, etc.)
	    jewelry_type: Rings, Chains, Earrings, etc.
	    gross_weight: Gross weight in grams
	    stone_weight: Stone weight in grams
	    msrp: Retail price (USD)
	    cost_price: Cost price (USD)
	    gender: Unisex, Men's, Women's
	    country_of_origin: Default USA
	    warehouse: Target warehouse for stock
	    qty: Initial stock quantity
	    image: Image URL or file path
	    description: Item description

	Returns:
	    dict with item_code, vendor_sku, and status
	"""
	# Permission check — only Stock Manager or System Manager can add items
	if not frappe.has_permission("Item", "create"):
		frappe.throw(_("You don't have permission to create Items"), frappe.PermissionError)

	# Input validation
	try:
		gross_weight = max(0, float(gross_weight or 0))
		stone_weight = max(0, float(stone_weight or 0))
		msrp = max(0, float(msrp or 0))
		cost_price = max(0, float(cost_price or 0))
		qty = max(0, int(qty or 0))
	except (TypeError, ValueError):
		frappe.throw(_("Numeric fields must be valid numbers"))

	if not item_name or not item_name.strip():
		frappe.throw(_("Item name is required"))

	# Auto-generate vendor SKU if not provided
	if not vendor_sku:
		vendor_sku = _generate_vendor_sku(vendor, jewelry_type)

	# Calculate net weight
	net_weight = max(0, gross_weight - stone_weight)

	# Map jewelry type to item group
	item_group = _get_item_group(jewelry_type)

	# Create item with retry on duplicate item code
	max_retries = 3
	for attempt in range(max_retries):
		item_code = _generate_item_code(jewelry_type)
		item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": item_code,
				"item_name": item_name.strip(),
				"item_group": item_group,
				"description": description or item_name.strip(),
				"image": image,
				"stock_uom": "Nos",
				"is_stock_item": 1,
				# Jewelry Details
				"custom_metal_type": metal_type,
				"custom_purity": purity,
				"custom_gross_weight_g": gross_weight,
				"custom_stone_weight_g": stone_weight,
				"custom_net_weight_g": net_weight,
				# Classification
				"custom_product_type": "Jewelry",
				"custom_jewelry_type": jewelry_type,
				"custom_gender": gender,
				# Vendor & Pricing
				"custom_vendor": vendor,
				"custom_vendor_sku": vendor_sku,
				"custom_country_of_origin": country_of_origin,
				"custom_msrp": msrp,
				"custom_cost_price": cost_price,
				"custom_source": "Manual",
			}
		)
		try:
			item.insert()  # Uses session user's permissions
			break  # success
		except frappe.exceptions.DuplicateEntryError:
			if attempt == max_retries - 1:
				frappe.throw(
					_("Failed to generate a unique item code after {0} attempts").format(max_retries)
				)
			# else retry with a freshly generated code

	# Create stock entry if warehouse and qty provided
	stock_entry_created = False
	if warehouse and qty > 0:
		stock_entry_created = _create_stock_entry(item_code, warehouse, qty)

	return {
		"success": True,
		"item_code": item_code,
		"item_name": item_name,
		"vendor_sku": vendor_sku,
		"message": f"Item {item_code} created successfully"
		+ ("" if stock_entry_created else " (stock entry pending)"),
		"stock_entry_created": stock_entry_created,
	}


@frappe.whitelist()
def get_next_vendor_sku(vendor: str | None = None, jewelry_type: str = "Other") -> str:
	"""Preview the next auto-generated vendor SKU without creating an item."""
	return _generate_vendor_sku(vendor, jewelry_type)


def _generate_vendor_sku(vendor: str | None = None, jewelry_type: str = "Other") -> str:
	"""
	Auto-generate a unique vendor SKU.

	Format: {VENDOR_PREFIX}-{TYPE_CODE}-{SEQUENCE}
	Example: QGD-RNG-00142, STL-EAR-00023, ZEV-BRA-00001
	"""
	# Vendor prefix (first 3 chars uppercase, or ZEV for no vendor)
	if vendor:
		prefix = vendor[:3].upper().replace(" ", "")
	else:
		prefix = "ZEV"

	# Type code
	type_code = _JEWELRY_TYPE_CODES.get(jewelry_type, "OTH")

	# Get next sequence number for this prefix+type combo
	pattern = f"{prefix}-{type_code}-%"
	last_sku = frappe.db.sql(  # nosemgrep
		"""
        SELECT custom_vendor_sku FROM `tabItem`
        WHERE custom_vendor_sku LIKE %s
        ORDER BY custom_vendor_sku DESC LIMIT 1
        FOR UPDATE
    """,
		(pattern,),
		as_dict=True,
	)

	if last_sku and last_sku[0].custom_vendor_sku:
		try:
			last_num = int(last_sku[0].custom_vendor_sku.split("-")[-1])
			next_num = last_num + 1
		except (ValueError, IndexError):
			next_num = 1
	else:
		next_num = 1

	return f"{prefix}-{type_code}-{next_num:05d}"


def _generate_item_code(jewelry_type: str) -> str:
	"""Generate a unique item code in format ZEV-{TYPE}-{SEQUENCE}."""
	type_code = _JEWELRY_TYPE_CODES.get(jewelry_type, "OTH")
	prefix = f"ZEV-{type_code}"

	last = frappe.db.sql(  # nosemgrep
		"""
        SELECT name FROM `tabItem`
        WHERE name LIKE %s
        ORDER BY name DESC LIMIT 1
        FOR UPDATE
    """,
		(f"{prefix}-%",),
		as_dict=True,
	)

	if last:
		try:
			last_num = int(last[0].name.split("-")[-1])
			next_num = last_num + 1
		except (ValueError, IndexError):
			next_num = 1
	else:
		next_num = 1

	return f"{prefix}-{next_num:04d}"


def _get_item_group(jewelry_type: str) -> str:
	"""Map jewelry type to ERPNext Item Group."""
	group_map = {
		"Rings": "Rings",
		"Chains": "Products",
		"Necklaces": "Products",
		"Earrings": "Earrings",
		"Bracelets": "Bracelets",
		"Pendants": "Pendants",
		"Watches": "Products",
		"Other": "Products",
	}
	group = group_map.get(jewelry_type, "Products")

	# Ensure group exists, fallback to Products
	if not frappe.db.exists("Item Group", group):
		return "Products"
	return group


def _create_stock_entry(item_code: str, warehouse: str, qty: int) -> bool:
	"""Create a Material Receipt stock entry for the new item. Returns True on success."""
	if not frappe.db.exists("Warehouse", warehouse):
		frappe.log_error(
			f"Stock entry skipped for {item_code}: warehouse '{warehouse}' not found",
			"Item Entry Warning",
		)
		return False

	se = frappe.get_doc(
		{
			"doctype": "Stock Entry",
			"stock_entry_type": "Material Receipt",
			"posting_date": nowdate(),
			"items": [
				{
					"item_code": item_code,
					"t_warehouse": warehouse,
					"qty": qty,
				}
			],
		}
	)
	se.insert()
	se.submit()
	return True


@frappe.whitelist(methods=["POST"])
def pos_quick_add_item(
	item_name: str,
	metal_type: str | None = None,
	purity: str | None = None,
	jewelry_type: str = "Other",
	gross_weight: float = 0,
	msrp: float = 0,
	warehouse: str | None = None,
	qty: int = 1,
) -> dict:
	"""
	POS-specific item creation with relaxed permissions for Sales User role.

	Allows POS operators to create items directly from the terminal.
	Delegates to quick_add_item after role validation.
	"""
	allowed_roles = {"Sales User", "Sales Manager", "Store Manager", "POS Manager", "System Manager"}
	if not (allowed_roles & set(frappe.get_roles())):
		frappe.throw(_("You don't have permission to create items from POS."), frappe.PermissionError)

	return quick_add_item(
		item_name=item_name,
		metal_type=metal_type,
		purity=purity,
		jewelry_type=jewelry_type,
		gross_weight=gross_weight,
		msrp=msrp,
		warehouse=warehouse,
		qty=qty,
	)


@frappe.whitelist(methods=["POST"])
def update_item(
	item_code: str,
	item_name: str | None = None,
	vendor: str | None = None,
	vendor_sku: str | None = None,
	metal_type: str | None = None,
	purity: str | None = None,
	jewelry_type: str | None = None,
	jewelry_subtype: str | None = None,
	product_type: str | None = None,
	gender: str | None = None,
	gross_weight: float | None = None,
	stone_weight: float | None = None,
	msrp: float | None = None,
	cost_price: float | None = None,
	barcode: str | None = None,
	rfid_epc: str | None = None,
	description: str | None = None,
	country_of_origin: str | None = None,
	material_color: str | None = None,
	finish: str | None = None,
	plating: str | None = None,
	size: str | None = None,
	chain_type: str | None = None,
	clasp_type: str | None = None,
	length_value: float | None = None,
	length_unit: str | None = None,
	width_value: float | None = None,
	width_unit: str | None = None,
	standard_rate: float | None = None,
	image: str | None = None,
	gemstones: str | None = None,
	**_kwargs,
) -> dict:
	allowed_roles = {"Sales Manager", "Store Manager", "System Manager"}
	if not (allowed_roles & set(frappe.get_roles())):
		frappe.throw(_("You don't have permission to update items."), frappe.PermissionError)

	if not frappe.db.exists("Item", item_code):
		frappe.throw(_("Item {0} not found").format(item_code))

	doc = frappe.get_doc("Item", item_code)

	field_map = {
		"item_name": item_name,
		"custom_vendor": vendor,
		"custom_vendor_sku": vendor_sku,
		"custom_metal_type": metal_type,
		"custom_purity": purity,
		"custom_jewelry_type": jewelry_type,
		"custom_jewelry_subtype": jewelry_subtype,
		"custom_product_type": product_type,
		"custom_gender": gender,
		"custom_gross_weight_g": gross_weight,
		"custom_stone_weight_g": stone_weight,
		"custom_msrp": msrp,
		"custom_cost_price": cost_price,
		"custom_barcode": barcode,
		"custom_rfid_epc": rfid_epc,
		"description": description,
		"custom_country_of_origin": country_of_origin,
		"custom_material_color": material_color,
		"custom_finish": finish,
		"custom_plating": plating,
		"custom_size": size,
		"custom_chain_type": chain_type,
		"custom_clasp_type": clasp_type,
		"custom_length_value": length_value,
		"custom_length_unit": length_unit,
		"custom_width_value": width_value,
		"custom_width_unit": width_unit,
		"standard_rate": standard_rate,
		"image": image,
	}

	if jewelry_type:
		doc.item_group = _get_item_group(jewelry_type)

	for field, value in field_map.items():
		if value is not None:
			setattr(doc, field, value)

	if gemstones:
		import json

		gem_list = json.loads(gemstones) if isinstance(gemstones, str) else gemstones
		existing_child_field = None
		for fname in ["custom_gemstones", "gemstones"]:
			if hasattr(doc, fname):
				existing_child_field = fname
				break
		if existing_child_field:
			getattr(doc, existing_child_field).clear()
			for g in gem_list:
				doc.append(
					existing_child_field,
					{
						"gem_type": g.get("gem_type"),
						"carat": flt(g.get("carat", 0), 3),
						"count": cint(g.get("count", 1)),
						"cut": g.get("cut"),
						"color": g.get("color"),
						"clarity": g.get("clarity"),
						"rate": flt(g.get("rate", 0)),
					},
				)

	doc.save()

	from frappe.utils import flt as _flt

	return {"success": True, "item_code": doc.name, "item_name": doc.item_name}
