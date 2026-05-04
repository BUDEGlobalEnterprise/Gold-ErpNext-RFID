"""
Export/Import Items for POS between dev and production.

Usage (on dev):
    bench --site zevar.localhost zevar-export-items /tmp/zevar_items_export.json

Usage (on production):
    bench --site zevar zevar-import-items /tmp/zevar_items_export.json [--dry-run]
"""

import json
import os

import click
import frappe
from frappe.commands import get_site, pass_context

POS_ITEM_FIELDS = [
	"name",
	"item_code",
	"item_name",
	"item_group",
	"image",
	"description",
	"stock_uom",
	"is_stock_item",
	"has_variants",
	"disabled",
	"brand",
	"standard_rate",
	"valuation_rate",
	"custom_metal_type",
	"custom_purity",
	"custom_gross_weight_g",
	"custom_stone_weight_g",
	"custom_net_weight_g",
	"custom_product_type",
	"custom_jewelry_type",
	"custom_jewelry_subtype",
	"custom_material_color",
	"custom_finish",
	"custom_plating",
	"custom_length_value",
	"custom_length_unit",
	"custom_width_value",
	"custom_width_unit",
	"custom_size",
	"custom_chain_type",
	"custom_clasp_type",
	"custom_vendor_sku",
	"custom_vendor",
	"custom_country_of_origin",
	"custom_msrp",
	"custom_source",
	"custom_gender",
	"custom_is_featured",
	"custom_is_trending",
	"custom_barcode",
	"custom_cost_price",
	"custom_metal_type",
]

TEST_ITEM_PATTERNS = [
	"TEST",
	"LEGACY-ITEM",
	"Sample",
	"Demo",
	"Dummy",
	"test-",
	"fake-",
]


def _is_test_item(item) -> bool:
	name = (item.get("item_name") or "").lower()
	code = (item.get("item_code") or item.get("name") or "").lower()
	for pattern in TEST_ITEM_PATTERNS:
		if pattern.lower() in name or pattern.lower() in code:
			return True
	return False


# ──────────────────────────────────────────────────
# Export
# ──────────────────────────────────────────────────


@click.command("zevar-export-items")
@click.argument("output_path")
@click.option("--include-test", is_flag=True, default=False, help="Include test/sample items")
@click.option("--include-disabled", is_flag=True, default=False, help="Include disabled items")
@pass_context
def export_items(context, output_path, include_test=False, include_disabled=False):
	"""
	Export items from dev as JSON for transfer to production.

	Exports items with all POS-required fields, plus dependent
	Item Groups, Brands, and Suppliers.
	"""
	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()

	try:
		filters = [["is_stock_item", "=", 1]]
		if not include_disabled:
			filters.append(["disabled", "=", 0])

		items = frappe.get_all(
			"Item",
			filters=filters,
			fields=POS_ITEM_FIELDS,
			order_by="item_name asc",
			ignore_permissions=True,
		)

		if not include_test:
			before = len(items)
			items = [item for item in items if not _is_test_item(item)]
			click.echo(f"Filtered out {before - len(items)} test/sample items")

		item_groups = set()
		brands = set()
		vendors = set()

		for item in items:
			if item.get("item_group"):
				item_groups.add(item["item_group"])
			if item.get("brand"):
				brands.add(item["brand"])
			if item.get("custom_vendor"):
				vendors.add(item["custom_vendor"])

		export_data = {
			"version": "1.0",
			"exported_from": frappe.local.site,
			"exported_at": frappe.utils.now(),
			"counts": {
				"items": len(items),
				"item_groups": len(item_groups),
				"brands": len(brands),
				"vendors": len(vendors),
			},
		}

		export_data["item_groups"] = _export_item_groups(item_groups)
		export_data["brands"] = _export_brands(brands)
		export_data["suppliers"] = _export_suppliers(vendors)
		export_data["items"] = [_serialize_item(i) for i in items]

		os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

		with open(output_path, "w") as f:  # nosemgrep
			json.dump(export_data, f, indent=2, default=str)

		click.echo(f"\nExport complete: {output_path}")
		click.echo(f"  Items: {len(items)}")
		click.echo(f"  Item Groups: {len(item_groups)}")
		click.echo(f"  Brands: {len(brands)}")
		click.echo(f"  Suppliers: {len(vendors)}")

	finally:
		frappe.destroy()


def _export_item_groups(names: set) -> list:
	result = []
	for name in names:
		if frappe.db.exists("Item Group", name):
			doc = frappe.get_doc("Item Group", name)
			result.append(
				{
					"item_group_name": doc.item_group_name,
					"parent_item_group": doc.parent_item_group or "All Item Groups",
					"is_group": doc.is_group,
				}
			)
	return result


def _export_brands(names: set) -> list:
	result = []
	for name in names:
		if frappe.db.exists("Brand", name):
			doc = frappe.get_doc("Brand", name)
			result.append({"brand": doc.brand})
	return result


def _export_suppliers(names: set) -> list:
	result = []
	for name in names:
		if frappe.db.exists("Supplier", name):
			doc = frappe.get_doc("Supplier", name)
			result.append(
				{
					"supplier_name": doc.supplier_name,
					"supplier_group": doc.supplier_group or "All Supplier Groups",
					"supplier_type": getattr(doc, "supplier_type", "Company"),
				}
			)
	return result


def _serialize_item(item: dict) -> dict:
	clean = {}
	for key in POS_ITEM_FIELDS:
		if key in item and item[key] is not None:
			val = item[key]
			if hasattr(val, "isoformat"):
				val = val.isoformat()
			clean[key] = val
	return clean


# ──────────────────────────────────────────────────
# Import
# ──────────────────────────────────────────────────


@click.command("zevar-import-items")
@click.argument("input_path")
@click.option("--dry-run", is_flag=True, default=False, help="Preview import without creating records")
@pass_context
def import_items(context, input_path, dry_run=False):
	"""
	Import items from a JSON export into production.

	Depends on zevar-export-items output from dev system.
	"""
	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()

	try:
		if not os.path.isfile(input_path):
			click.echo(f"Error: File not found: {input_path}")
			return

		with open(input_path) as f:  # nosemgrep
			data = json.load(f)

		click.echo(f"\n{'[DRY RUN] ' if dry_run else ''}Importing items from: {input_path}")
		click.echo(
			f"Export source: {data.get('exported_from', 'unknown')} at {data.get('exported_at', 'unknown')}"
		)
		click.echo("-" * 60)

		stats = {
			"item_groups": {"total": 0, "imported": 0, "skipped": 0, "errors": []},
			"brands": {"total": 0, "imported": 0, "skipped": 0, "errors": []},
			"suppliers": {"total": 0, "imported": 0, "skipped": 0, "errors": []},
			"items": {"total": 0, "imported": 0, "skipped": 0, "errors": []},
		}

		_ensure_root_nodes()

		click.echo("\n[1/4] Importing Item Groups...")
		for ig in data.get("item_groups", []):
			stats["item_groups"]["total"] += 1
			try:
				name = ig["item_group_name"]
				if frappe.db.exists("Item Group", name):
					stats["item_groups"]["skipped"] += 1
					continue
				if dry_run:
					stats["item_groups"]["imported"] += 1
					continue
				doc = frappe.new_doc("Item Group")
				doc.item_group_name = name
				doc.parent_item_group = ig.get("parent_item_group", "All Item Groups")
				doc.is_group = ig.get("is_group", 0)
				doc.insert(ignore_permissions=True, ignore_mandatory=True)
				stats["item_groups"]["imported"] += 1
			except Exception as e:
				stats["item_groups"]["errors"].append(f"{ig.get('item_group_name')}: {str(e)[:100]}")

		if not dry_run:
			frappe.db.commit()  # nosemgrep
		click.echo(
			f"  Imported: {stats['item_groups']['imported']}, Skipped: {stats['item_groups']['skipped']}"
		)

		click.echo("\n[2/4] Importing Brands...")
		for b in data.get("brands", []):
			stats["brands"]["total"] += 1
			try:
				name = b["brand"]
				if frappe.db.exists("Brand", name):
					stats["brands"]["skipped"] += 1
					continue
				if dry_run:
					stats["brands"]["imported"] += 1
					continue
				doc = frappe.new_doc("Brand")
				doc.brand = name
				doc.insert(ignore_permissions=True)
				stats["brands"]["imported"] += 1
			except Exception as e:
				stats["brands"]["errors"].append(f"{b.get('brand')}: {str(e)[:100]}")

		if not dry_run:
			frappe.db.commit()  # nosemgrep
		click.echo(f"  Imported: {stats['brands']['imported']}, Skipped: {stats['brands']['skipped']}")

		click.echo("\n[3/4] Importing Suppliers...")
		for s in data.get("suppliers", []):
			stats["suppliers"]["total"] += 1
			try:
				name = s["supplier_name"]
				if frappe.db.exists("Supplier", {"supplier_name": name}):
					stats["suppliers"]["skipped"] += 1
					continue
				if dry_run:
					stats["suppliers"]["imported"] += 1
					continue
				doc = frappe.new_doc("Supplier")
				doc.supplier_name = name
				doc.supplier_group = s.get("supplier_group", "All Supplier Groups")
				doc.supplier_type = s.get("supplier_type", "Company")
				doc.insert(ignore_permissions=True, ignore_mandatory=True)
				stats["suppliers"]["imported"] += 1
			except Exception as e:
				stats["suppliers"]["errors"].append(f"{s.get('supplier_name')}: {str(e)[:100]}")

		if not dry_run:
			frappe.db.commit()  # nosemgrep
		click.echo(f"  Imported: {stats['suppliers']['imported']}, Skipped: {stats['suppliers']['skipped']}")

		click.echo("\n[4/4] Importing Items...")
		for idx, item_data in enumerate(data.get("items", [])):
			stats["items"]["total"] += 1
			try:
				item_code = item_data.get("item_code") or item_data.get("name")
				if not item_code:
					stats["items"]["skipped"] += 1
					continue

				if frappe.db.exists("Item", item_code):
					stats["items"]["skipped"] += 1
					continue

				if dry_run:
					stats["items"]["imported"] += 1
					continue

				doc = frappe.new_doc("Item")
				doc.item_code = item_code
				doc.item_name = item_data.get("item_name", item_code)[:140]
				doc.stock_uom = item_data.get("stock_uom", "Nos")
				doc.is_stock_item = item_data.get("is_stock_item", 1)
				doc.has_variants = item_data.get("has_variants", 0)
				doc.disabled = item_data.get("disabled", 0)

				if item_data.get("item_group"):
					doc.item_group = item_data["item_group"]

				if item_data.get("brand"):
					doc.brand = item_data["brand"]

				if item_data.get("description"):
					doc.description = item_data["description"][:140]

				if item_data.get("standard_rate"):
					doc.standard_rate = float(item_data["standard_rate"])
				if item_data.get("valuation_rate"):
					doc.valuation_rate = float(item_data["valuation_rate"])

				for field in POS_ITEM_FIELDS:
					if field.startswith("custom_") and field in item_data and item_data[field]:
						if frappe.get_meta("Item").has_field(field):
							doc.set(field, item_data[field])

				doc.insert(ignore_permissions=True, ignore_mandatory=True)
				stats["items"]["imported"] += 1

				if (idx + 1) % 50 == 0:
					frappe.db.commit()  # nosemgrep
					click.echo(f"  ... {idx + 1}/{stats['items']['total']} processed")

			except Exception as e:
				stats["items"]["errors"].append(f"Item {item_data.get('item_code', '?')}: {str(e)[:100]}")

		if not dry_run:
			frappe.db.commit()  # nosemgrep
		click.echo(f"  Imported: {stats['items']['imported']}, Skipped: {stats['items']['skipped']}")

		click.echo("\n" + "=" * 60)
		click.echo("Import Summary:")
		for category, s in stats.items():
			label = category.replace("_", " ").title()
			click.echo(f"  {label}: {s['imported']} imported, {s['skipped']} skipped", nl=False)
			if s.get("errors"):
				click.echo(f", {len(s['errors'])} errors")
				for err in s["errors"][:5]:
					click.echo(f"    - {err}")
			else:
				click.echo()

		if dry_run:
			click.echo("\n[DRY RUN] No records were actually created.")

	finally:
		frappe.destroy()


def _ensure_root_nodes():
	for doctype, name in [
		("Item Group", "All Item Groups"),
		("Supplier Group", "All Supplier Groups"),
	]:
		if not frappe.db.exists(doctype, name):
			try:
				doc = frappe.new_doc(doctype)
				if doctype == "Item Group":
					doc.item_group_name = name
				else:
					doc.supplier_group_name = name
				doc.is_group = 1
				doc.insert(ignore_permissions=True)
			except frappe.DuplicateEntryError:
				pass
