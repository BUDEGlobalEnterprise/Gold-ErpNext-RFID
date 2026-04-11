"""
Production Export Script for Zevar
===================================
Exports ALL data needed for production deployment:
- Items with full jewelry metadata + stock quantities
- Random jewelry images for items missing images
- Item Groups, Brands, Suppliers, Customers
- Warehouses, Store Locations, Gold Rates
- Validated stock quantities

Usage:
    bench --site zevar.localhost execute zevar_core.migration.production_export.run_export

Output:
    /tmp/zevar_production_export/zevar_production_data.json
    /tmp/zevar_production_export/zevar_images_manifest.json
"""

import hashlib
import json
import os
import random
import urllib.request
from pathlib import Path

import frappe
from frappe.utils import flt, now_datetime

EXPORT_DIR = "/tmp/zevar_production_export"
OUTPUT_FILE = os.path.join(EXPORT_DIR, "zevar_production_data.json")
IMAGES_MANIFEST = os.path.join(EXPORT_DIR, "zevar_images_manifest.json")
IMAGES_DIR = os.path.join(EXPORT_DIR, "item_images")

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
	"custom_cost_price",
]

TEST_ITEM_PATTERNS = [
	"TEST",
	"LEGACY-ITEM",
	"Sample",
	"Demo",
	"Dummy",
	"test-",
	"fake-",
	"_Test",
	"COMM-",
	"PRICING-",
	"LAY-",
	"SESS-",
	"HISTORY-",
	"RETURN-",
	"LAYAWAY-",
	"138-CMS",
]

JEWELRY_IMAGES_BY_TYPE = {
	"Rings": [
		"https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800&h=800&fit=crop&q=80",
	],
	"Chains": [
		"https://images.unsplash.com/photo-1589674781759-c21c37956a44?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1599458448510-59aecaea4752?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1610694955371-d4a3e0ce4b52?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1635767798638-3e25273a8236?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1603974372039-adc49044b6bd?w=800&h=800&fit=crop&q=80",
	],
	"Necklaces": [
		"https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1611955167811-4711904bb9f8?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1599458448510-59aecaea4752?w=800&h=800&fit=crop&q=80",
	],
	"Earrings": [
		"https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1588444837495-c6cfee53f5?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1630019852942-f89202989a59?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1602173574767-37ac01994b2a?w=800&h=800&fit=crop&q=80",
	],
	"Bracelets": [
		"https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1602524816025-faae4dab1002?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=800&h=800&fit=crop&q=80",
	],
	"Pendants": [
		"https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=800&h=800&fit=crop&q=80",
	],
	"Watches": [
		"https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1587836374828-4dbafa94cf0e?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1547996160-81dfa63595aa?w=800&h=800&fit=crop&q=80",
	],
	"Other": [
		"https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=800&h=800&fit=crop&q=80",
		"https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=800&h=800&fit=crop&q=80",
	],
}

DEFAULT_IMAGES = JEWELRY_IMAGES_BY_TYPE["Other"]


def _is_test_item(item):
	name = (item.get("item_name") or "").lower()
	code = (item.get("item_code") or item.get("name") or "").lower()
	for pattern in TEST_ITEM_PATTERNS:
		if pattern.lower() in name or pattern.lower() in code:
			return True
	return False


def _get_random_image(jewelry_type):
	pool = JEWELRY_IMAGES_BY_TYPE.get(jewelry_type, DEFAULT_IMAGES)
	return random.choice(pool)


def _download_image(url, dest_path, timeout=30):
	try:
		req = urllib.request.Request(url, headers={"User-Agent": "Zevar Export/1.0"})
		with urllib.request.urlopen(req, timeout=timeout) as resp:
			if resp.status == 200:
				with open(dest_path, "wb") as f:
					f.write(resp.read())
				return True
	except Exception:
		pass
	return False


def run_export(download_images=True, assign_missing_images=True):
	print("=" * 60)
	print("ZEVAR PRODUCTION EXPORT")
	print("=" * 60)

	os.makedirs(EXPORT_DIR, exist_ok=True)
	if download_images:
		os.makedirs(IMAGES_DIR, exist_ok=True)

	start = now_datetime()
	export_data = {
		"version": "2.0",
		"exported_from": frappe.local.site,
		"exported_at": str(start),
	}

	stats = {
		"items": 0,
		"items_with_image": 0,
		"items_missing_image": 0,
		"images_assigned": 0,
		"images_downloaded": 0,
		"images_failed": 0,
		"customers": 0,
		"suppliers": 0,
		"item_groups": 0,
		"warehouses": 0,
		"store_locations": 0,
		"gold_rates": 0,
		"stock_records": 0,
		"gemstone_details": 0,
		"quantity_issues": [],
	}

	# 1. Export Item Groups
	print("\n[1/9] Exporting Item Groups...")
	item_groups = frappe.get_all("Item Group", fields=["item_group_name", "parent_item_group", "is_group"])
	export_data["item_groups"] = item_groups
	stats["item_groups"] = len(item_groups)
	print(f"  Item Groups: {len(item_groups)}")

	# 2. Export Brands
	print("\n[2/9] Exporting Brands...")
	brands = frappe.get_all("Brand", fields=["brand"])
	export_data["brands"] = brands
	print(f"  Brands: {len(brands)}")

	# 3. Export Suppliers
	print("\n[3/9] Exporting Suppliers...")
	suppliers = frappe.get_all(
		"Supplier", fields=["supplier_name", "supplier_group", "supplier_type", "country"]
	)
	export_data["suppliers"] = suppliers
	stats["suppliers"] = len(suppliers)
	print(f"  Suppliers: {len(suppliers)}")

	# 4. Export Customers
	print("\n[4/9] Exporting Customers...")
	customers = frappe.get_all(
		"Customer",
		fields=[
			"name",
			"customer_name",
			"customer_group",
			"territory",
			"email_id",
			"mobile_no",
			"customer_type",
			"default_currency",
		],
	)
	export_data["customers"] = customers
	stats["customers"] = len(customers)
	print(f"  Customers: {len(customers)}")

	# 5. Export Warehouses
	print("\n[5/9] Exporting Warehouses...")
	warehouses = frappe.get_all(
		"Warehouse",
		fields=[
			"name",
			"warehouse_name",
			"warehouse_type",
			"is_group",
			"parent_warehouse",
			"company",
		],
	)
	export_data["warehouses"] = warehouses
	stats["warehouses"] = len(warehouses)
	print(f"  Warehouses: {len(warehouses)}")

	# 6. Export Store Locations
	print("\n[6/9] Exporting Store Locations...")
	if frappe.db.exists("DocType", "Store Location"):
		store_locations = frappe.get_all("Store Location", fields=["*"])
		export_data["store_locations"] = store_locations
		stats["store_locations"] = len(store_locations)
		print(f"  Store Locations: {len(store_locations)}")
	else:
		export_data["store_locations"] = []
		print("  Store Locations: DocType not found, skipping")

	# 7. Export Gold Rate Logs
	print("\n[7/9] Exporting Gold Rates...")
	if frappe.db.exists("DocType", "Gold Rate Log"):
		gold_rates = frappe.get_all("Gold Rate Log", fields=["*"], order_by="timestamp desc", limit=500)
		export_data["gold_rates"] = gold_rates
		stats["gold_rates"] = len(gold_rates)
		print(f"  Gold Rate Logs: {len(gold_rates)}")
	else:
		export_data["gold_rates"] = []

	# 8. Export Items with Stock + Images
	print("\n[8/9] Exporting Items with stock validation...")

	filters = [["is_stock_item", "=", 1], ["disabled", "=", 0]]
	all_items = frappe.get_all("Item", filters=filters, fields=POS_ITEM_FIELDS, order_by="item_name asc")

	before = len(all_items)
	items = [i for i in all_items if not _is_test_item(i)]
	print(f"  Total stock items: {before}, filtered test items: {before - len(items)}")

	bin_data = frappe.db.sql(
		"""
		SELECT item_code, warehouse, actual_qty, reserved_qty, projected_qty, valuation_rate
		FROM `tabBin`
		WHERE actual_qty > 0
	""",
		as_dict=True,
	)

	stock_map = {}
	for b in bin_data:
		stock_map.setdefault(b.item_code, []).append(
			{
				"warehouse": b.warehouse,
				"actual_qty": flt(b.actual_qty),
				"reserved_qty": flt(b.reserved_qty),
				"projected_qty": flt(b.projected_qty),
				"valuation_rate": flt(b.valuation_rate),
			}
		)

	gemstone_data = frappe.db.sql(
		"""
		SELECT parent, gem_type, carat, count, cut, color, clarity, rate, amount
		FROM `tabZevar Gemstone Detail`
	""",
		as_dict=True,
	)

	gemstone_map = {}
	for g in gemstone_data:
		gemstone_map.setdefault(g.parent, []).append(
			{
				"gem_type": g.gem_type,
				"carat": flt(g.carat),
				"count": g.count,
				"cut": g.cut,
				"color": g.color,
				"clarity": g.clarity,
				"rate": flt(g.rate),
				"amount": flt(g.amount),
			}
		)

	images_manifest = {}
	exported_items = []

	for item in items:
		item_code = item.get("item_code") or item.get("name")
		jewelry_type = item.get("custom_jewelry_type") or "Other"

		clean_item = {}
		for key in POS_ITEM_FIELDS:
			if key in item and item[key] is not None:
				val = item[key]
				if hasattr(val, "isoformat"):
					val = val.isoformat()
				clean_item[key] = val

		has_image = bool(item.get("image"))
		stats["items_with_image" if has_image else "items_missing_image"] += 1

		if not has_image and assign_missing_images:
			img_url = _get_random_image(jewelry_type)
			clean_item["image"] = img_url
			clean_item["_image_assigned"] = True
			stats["images_assigned"] += 1

		item_stocks = stock_map.get(item_code, [])
		clean_item["stock"] = item_stocks
		stats["stock_records"] += len(item_stocks)

		if not item_stocks:
			stats["quantity_issues"].append(
				{
					"item_code": item_code,
					"item_name": item.get("item_name"),
					"issue": "No stock (Bin) record found - qty is 0",
				}
			)

		item_gems = gemstone_map.get(item_code, [])
		if item_gems:
			clean_item["gemstones"] = item_gems
			stats["gemstone_details"] += len(item_gems)

		msrp = flt(item.get("custom_msrp"))
		std_rate = flt(item.get("standard_rate"))
		total_stock = sum(s["actual_qty"] for s in item_stocks)
		if msrp == 0 and std_rate == 0:
			stats["quantity_issues"].append(
				{
					"item_code": item_code,
					"item_name": item.get("item_name"),
					"issue": f"No pricing (MSRP=0, standard_rate=0), stock={total_stock}",
				}
			)

		if item.get("image"):
			images_manifest[item_code] = {
				"image_url": clean_item.get("image", ""),
				"local_filename": None,
				"downloaded": False,
			}

		exported_items.append(clean_item)

	export_data["items"] = exported_items
	stats["items"] = len(exported_items)
	print(f"  Production items exported: {len(exported_items)}")
	print(f"  With images: {stats['items_with_image']}")
	print(f"  Missing images (assigned): {stats['images_assigned']}")
	print(f"  Stock records: {stats['stock_records']}")
	print(f"  Gemstone details: {stats['gemstone_details']}")
	print(f"  Quantity/pricing issues: {len(stats['quantity_issues'])}")

	# 9. Download images
	if download_images:
		print("\n[9/9] Downloading item images...")
		unique_urls = set()
		for item in exported_items:
			img = item.get("image", "")
			if img and img.startswith("http"):
				unique_urls.add(img)

		print(f"  Unique image URLs to download: {len(unique_urls)}")

		url_to_local = {}
		for i, url in enumerate(unique_urls):
			url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
			ext = "jpg"
			if ".png" in url.lower():
				ext = "png"
			elif ".webp" in url.lower():
				ext = "webp"
			local_filename = f"jewelry_{url_hash}.{ext}"
			local_path = os.path.join(IMAGES_DIR, local_filename)

			if os.path.exists(local_path):
				url_to_local[url] = local_filename
				stats["images_downloaded"] += 1
				continue

			if _download_image(url, local_path):
				url_to_local[url] = local_filename
				stats["images_downloaded"] += 1
			else:
				stats["images_failed"] += 1

			if (i + 1) % 10 == 0:
				print(f"    Downloaded {i + 1}/{len(unique_urls)} images...")

		for item in exported_items:
			img = item.get("image", "")
			if img in url_to_local:
				item["_local_image_file"] = url_to_local[img]
				item_code = item.get("item_code") or item.get("name")
				images_manifest[item_code]["local_filename"] = url_to_local[img]
				images_manifest[item_code]["downloaded"] = True

		print(f"  Downloaded: {stats['images_downloaded']}")
		print(f"  Failed: {stats['images_failed']}")
	else:
		print("\n[9/9] Skipping image download (download_images=False)")

	# Save main export
	export_data["stats"] = stats
	export_data["export_summary"] = {
		"items": stats["items"],
		"item_groups": stats["item_groups"],
		"suppliers": stats["suppliers"],
		"customers": stats["customers"],
		"warehouses": stats["warehouses"],
		"stock_records": stats["stock_records"],
		"gemstone_details": stats["gemstone_details"],
		"images_assigned": stats["images_assigned"],
		"images_downloaded": stats["images_downloaded"],
		"quantity_issues_count": len(stats["quantity_issues"]),
	}

	with open(OUTPUT_FILE, "w") as f:
		json.dump(export_data, f, indent=2, default=str)
	print(f"\n  Export saved: {OUTPUT_FILE}")

	with open(IMAGES_MANIFEST, "w") as f:
		json.dump(images_manifest, f, indent=2, default=str)
	print(f"  Images manifest: {IMAGES_MANIFEST}")

	if stats["quantity_issues"]:
		issues_file = os.path.join(EXPORT_DIR, "quantity_issues.json")
		with open(issues_file, "w") as f:
			json.dump(stats["quantity_issues"], f, indent=2, default=str)
		print(f"  Quantity issues: {issues_file}")

	print("\n" + "=" * 60)
	print("EXPORT COMPLETE")
	print("=" * 60)
	print(f"  Items:         {stats['items']}")
	print(f"  Customers:     {stats['customers']}")
	print(f"  Suppliers:     {stats['suppliers']}")
	print(f"  Warehouses:    {stats['warehouses']}")
	print(f"  Stock Records: {stats['stock_records']}")
	print(f"  Images:        {stats['images_downloaded']} downloaded, {stats['images_assigned']} assigned")
	print(f"  Issues:        {len(stats['quantity_issues'])}")
	print(f"\nOutput directory: {EXPORT_DIR}/")
	print("  zevar_production_data.json  - All data for import")
	print("  zevar_images_manifest.json  - Image URL to file mapping")
	print("  item_images/                - Downloaded image files")
	if stats["quantity_issues"]:
		print("  quantity_issues.json        - Items with qty/price issues")
	print("=" * 60)

	return export_data


def run_import(input_path, dry_run=False):
	"""
	Import production data into a target site.

	Usage:
	    bench --site <site> execute zevar_core.migration.production_export.run_import --args '["/tmp/zevar_production_export/zevar_production_data.json"]'
	"""
	if not os.path.isfile(input_path):
		print(f"Error: File not found: {input_path}")
		return

	with open(input_path) as f:
		data = json.load(f)

	prefix = "[DRY RUN] " if dry_run else ""
	print(f"\n{prefix}IMPORTING PRODUCTION DATA")
	print(f"Source: {data.get('exported_from')} at {data.get('exported_at')}")
	print("-" * 60)

	ensure_root_nodes()

	stats = {}

	# 1. Item Groups
	print("\n[1/7] Importing Item Groups...")
	ig_stats = {"total": 0, "imported": 0, "skipped": 0}
	for ig in data.get("item_groups", []):
		ig_stats["total"] += 1
		name = ig.get("item_group_name")
		if not name or frappe.db.exists("Item Group", name):
			ig_stats["skipped"] += 1
			continue
		if dry_run:
			ig_stats["imported"] += 1
			continue
		doc = frappe.new_doc("Item Group")
		doc.item_group_name = name
		doc.parent_item_group = ig.get("parent_item_group", "All Item Groups")
		doc.is_group = ig.get("is_group", 0)
		doc.insert(ignore_permissions=True, ignore_mandatory=True)
		ig_stats["imported"] += 1
	if not dry_run:
		frappe.db.commit()
	stats["item_groups"] = ig_stats
	print(f"  Imported: {ig_stats['imported']}, Skipped: {ig_stats['skipped']}")

	# 2. Brands
	print("\n[2/7] Importing Brands...")
	br_stats = {"total": 0, "imported": 0, "skipped": 0}
	for b in data.get("brands", []):
		br_stats["total"] += 1
		name = b.get("brand")
		if not name or frappe.db.exists("Brand", name):
			br_stats["skipped"] += 1
			continue
		if dry_run:
			br_stats["imported"] += 1
			continue
		doc = frappe.new_doc("Brand")
		doc.brand = name
		doc.insert(ignore_permissions=True)
		br_stats["imported"] += 1
	if not dry_run:
		frappe.db.commit()
	stats["brands"] = br_stats
	print(f"  Imported: {br_stats['imported']}, Skipped: {br_stats['skipped']}")

	# 3. Warehouses
	print("\n[3/7] Importing Warehouses...")
	wh_stats = {"total": 0, "imported": 0, "skipped": 0}
	for w in data.get("warehouses", []):
		wh_stats["total"] += 1
		name = w.get("name")
		if not name or frappe.db.exists("Warehouse", name):
			wh_stats["skipped"] += 1
			continue
		if dry_run:
			wh_stats["imported"] += 1
			continue
		doc = frappe.new_doc("Warehouse")
		doc.warehouse_name = w.get("warehouse_name", name)
		doc.warehouse_type = w.get("warehouse_type")
		doc.is_group = w.get("is_group", 0)
		doc.parent_warehouse = w.get("parent_warehouse")
		doc.company = w.get("company")
		doc.insert(ignore_permissions=True, ignore_mandatory=True)
		wh_stats["imported"] += 1
	if not dry_run:
		frappe.db.commit()
	stats["warehouses"] = wh_stats
	print(f"  Imported: {wh_stats['imported']}, Skipped: {wh_stats['skipped']}")

	# 4. Suppliers
	print("\n[4/7] Importing Suppliers...")
	su_stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}
	for s in data.get("suppliers", []):
		su_stats["total"] += 1
		name = s.get("supplier_name")
		if not name or frappe.db.exists("Supplier", {"supplier_name": name}):
			su_stats["skipped"] += 1
			continue
		if dry_run:
			su_stats["imported"] += 1
			continue
		try:
			doc = frappe.new_doc("Supplier")
			doc.supplier_name = name
			doc.supplier_group = s.get("supplier_group", "All Supplier Groups")
			doc.supplier_type = s.get("supplier_type", "Company")
			doc.insert(ignore_permissions=True, ignore_mandatory=True)
			su_stats["imported"] += 1
		except Exception as e:
			su_stats["errors"].append(f"{name}: {str(e)[:100]}")
	if not dry_run:
		frappe.db.commit()
	stats["suppliers"] = su_stats
	print(f"  Imported: {su_stats['imported']}, Skipped: {su_stats['skipped']}")

	# 5. Customers
	print("\n[5/7] Importing Customers...")
	cu_stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}
	for c in data.get("customers", []):
		cu_stats["total"] += 1
		name = c.get("name")
		if not name or frappe.db.exists("Customer", name):
			cu_stats["skipped"] += 1
			continue
		if dry_run:
			cu_stats["imported"] += 1
			continue
		try:
			doc = frappe.new_doc("Customer")
			doc.customer_name = c.get("customer_name", name)
			doc.customer_group = c.get("customer_group", "All Customer Groups")
			doc.territory = c.get("territory", "All Territories")
			doc.customer_type = c.get("customer_type", "Individual")
			doc.email_id = c.get("email_id")
			doc.mobile_no = c.get("mobile_no")
			doc.insert(ignore_permissions=True, ignore_mandatory=True)
			cu_stats["imported"] += 1
		except Exception as e:
			cu_stats["errors"].append(f"{name}: {str(e)[:100]}")
	if not dry_run:
		frappe.db.commit()
	stats["customers"] = cu_stats
	print(f"  Imported: {cu_stats['imported']}, Skipped: {cu_stats['skipped']}")

	# 6. Items
	print("\n[6/7] Importing Items...")
	it_stats = {"total": 0, "imported": 0, "skipped": 0, "errors": []}
	for idx, item_data in enumerate(data.get("items", [])):
		it_stats["total"] += 1
		item_code = item_data.get("item_code") or item_data.get("name")
		if not item_code:
			it_stats["skipped"] += 1
			continue
		if frappe.db.exists("Item", item_code):
			it_stats["skipped"] += 1
			continue
		if dry_run:
			it_stats["imported"] += 1
			continue
		try:
			doc = frappe.new_doc("Item")
			doc.item_code = item_code
			doc.item_name = item_data.get("item_name", item_code)[:140]
			doc.stock_uom = item_data.get("stock_uom", "Nos")
			doc.is_stock_item = item_data.get("is_stock_item", 1)
			doc.has_variants = item_data.get("has_variants", 0)
			doc.disabled = item_data.get("disabled", 0)
			doc.item_group = item_data.get("item_group", "All Item Groups")
			doc.brand = item_data.get("brand")
			doc.description = (item_data.get("description") or "")[:140]

			if item_data.get("standard_rate"):
				doc.standard_rate = float(item_data["standard_rate"])
			if item_data.get("valuation_rate"):
				doc.valuation_rate = float(item_data["valuation_rate"])

			local_image = item_data.get("_local_image_file")
			if local_image:
				doc.image = f"/files/items/{local_image}"
			elif item_data.get("image"):
				doc.image = item_data["image"]

			for field in POS_ITEM_FIELDS:
				if field.startswith("custom_") and field in item_data and item_data[field]:
					if frappe.get_meta("Item").has_field(field):
						doc.set(field, item_data[field])

			doc.insert(ignore_permissions=True, ignore_mandatory=True)
			it_stats["imported"] += 1

			if (idx + 1) % 50 == 0:
				frappe.db.commit()
				print(f"  ... {idx + 1}/{it_stats['total']} processed")

		except Exception as e:
			it_stats["errors"].append(f"{item_code}: {str(e)[:120]}")

	if not dry_run:
		frappe.db.commit()
	stats["items"] = it_stats
	print(
		f"  Imported: {it_stats['imported']}, Skipped: {it_stats['skipped']}, Errors: {len(it_stats['errors'])}"
	)

	# 7. Stock Entries (Material Receipt)
	print("\n[7/7] Creating Stock Entries...")
	se_stats = {"total": 0, "created": 0, "skipped": 0, "errors": []}

	items_with_stock = [i for i in data.get("items", []) if i.get("stock")]

	if not items_with_stock:
		print("  No stock data to import")
	else:
		company = frappe.defaults.get_global_default("company")
		if not company:
			companies = frappe.get_all("Company", pluck="name", limit=1)
			company = companies[0] if companies else None

		if not company:
			print("  ERROR: No company found. Cannot create stock entries.")
		else:
			expense_account = frappe.get_cached_value("Company", company, "stock_adjustment_account")
			if not expense_account:
				expense_account = frappe.get_cached_value("Company", company, "default_expense_account")

			all_stock_entries = []
			for item_data in items_with_stock:
				item_code = item_data.get("item_code") or item_data.get("name")
				for stock in item_data.get("stock", []):
					if flt(stock.get("actual_qty", 0)) > 0:
						all_stock_entries.append(
							{
								"item_code": item_code,
								"warehouse": stock["warehouse"],
								"qty": flt(stock["actual_qty"]),
								"valuation_rate": flt(stock.get("valuation_rate", 0)),
							}
						)

			se_stats["total"] = len(all_stock_entries)
			batch_size = 50

			for i in range(0, len(all_stock_entries), batch_size):
				batch = all_stock_entries[i : i + batch_size]
				if dry_run:
					se_stats["created"] += len(batch)
					continue
				try:
					se = frappe.new_doc("Stock Entry")
					se.stock_entry_type = "Material Receipt"
					se.company = company
					se.posting_date = frappe.utils.today()

					for s in batch:
						if not frappe.db.exists("Item", s["item_code"]):
							continue
						if not frappe.db.exists("Warehouse", s["warehouse"]):
							continue
						rate = s["valuation_rate"] if s["valuation_rate"] > 0 else 1
						se.append(
							"items",
							{
								"item_code": s["item_code"],
								"qty": s["qty"],
								"uom": "Nos",
								"t_warehouse": s["warehouse"],
								"basic_rate": rate,
								"expense_account": expense_account,
							},
						)

					if se.items:
						se.insert(ignore_permissions=True)
						se.submit()
						se_stats["created"] += len(se.items)
					else:
						se_stats["skipped"] += len(batch)

					if (i + batch_size) % 500 == 0:
						frappe.db.commit()
						print(f"  ... Stocked {se_stats['created']}/{se_stats['total']} records...")

				except Exception as e:
					se_stats["errors"].append(f"Batch {i // batch_size}: {str(e)[:120]}")
					frappe.db.rollback()

			if not dry_run:
				frappe.db.commit()

	stats["stock_entries"] = se_stats
	print(
		f"  Created: {se_stats['created']}, Skipped: {se_stats['skipped']}, Errors: {len(se_stats['errors'])}"
	)

	# Summary
	print("\n" + "=" * 60)
	print(f"{prefix}IMPORT SUMMARY")
	print("=" * 60)
	for category, s in stats.items():
		if isinstance(s, dict):
			print(
				f"  {category.replace('_', ' ').title()}: {s.get('imported', s.get('created', 0))} created, {s.get('skipped', 0)} skipped"
			)
			if s.get("errors"):
				print(f"    Errors: {len(s['errors'])}")
				for err in s["errors"][:3]:
					print(f"      - {err}")

	if dry_run:
		print("\n[DRY RUN] No records were actually created.")

	return stats


def ensure_root_nodes():
	for doctype, name in [
		("Item Group", "All Item Groups"),
		("Supplier Group", "All Supplier Groups"),
		("Customer Group", "All Customer Groups"),
		("Territory", "All Territories"),
	]:
		if not frappe.db.exists(doctype, name):
			try:
				doc = frappe.new_doc(doctype)
				if doctype == "Item Group":
					doc.item_group_name = name
				elif doctype == "Supplier Group":
					doc.supplier_group_name = name
				elif doctype == "Customer Group":
					doc.customer_group_name = name
				elif doctype == "Territory":
					doc.territory_name = name
				doc.is_group = 1
				doc.insert(ignore_permissions=True)
			except frappe.DuplicateEntryError:
				pass
	frappe.db.commit()
