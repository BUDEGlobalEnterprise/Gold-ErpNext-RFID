import random

import frappe


def run():
	frappe.set_user("Administrator")  # nosemgrep: frappe-semgrep-rules.rules.security.frappe-setuser
	print("💎 Generating 100+ High-Quality Items...")

	# --- 1. CONFIGURATION ---

	# EXACT Valid Metal/Purity Pairs
	valid_pairs = [
		("Yellow Gold", "24Kt"),
		("Yellow Gold", "22Kt"),
		("Yellow Gold", "18Kt"),
		("Rose Gold", "18Kt"),
		("White Gold", "18Kt"),
		("White Gold", "14Kt"),
		("Silver", "925 Sterling"),
		("Silver", "999 Fine"),
		("Platinum", "950"),
	]

	# Full Gemstone Options
	gem_types = ["Diamond", "Ruby", "Sapphire", "Emerald", "Polki", "Kundan"]
	cuts = ["Excellent", "Very Good", "Good"]
	colors = [
		"D",
		"E",
		"F",
		"G",
		"H",
		"I",
		"J",
		"K",
		"L",
		"M",
		"N-Z (Yellow Tint)",
		"Other",
	]
	clarities = [
		"FL (Flawless)",
		"IF (Internally Flawless)",
		"VVS1",
		"VVS2",
		"VS1",
		"VS2",
		"SI1",
		"SI2",
		"I1",
		"I2",
		"I3",
	]

	jewelry_types = ["Ring", "Necklace", "Bracelet", "Earrings", "Pendant", "Bangle"]

	# --- 2. GENERATION LOOP ---
	created_items = []

	# Ensure Item Group exists
	if not frappe.db.exists("Item Group", "Products"):
		frappe.get_doc(
			{
				"doctype": "Item Group",
				"item_group_name": "Products",
				"is_group": 0,
				"parent_item_group": "All Item Groups",
			}
		).insert()

	for _i in range(100):
		# Pick Metal
		metal, purity = random.choice(valid_pairs)
		j_type = random.choice(jewelry_types)

		# 50% chance of having stones (higher for Gold/Platinum)
		has_stones = False
		if "Gold" in metal or "Platinum" in metal:
			has_stones = random.random() < 0.6
		elif "Silver" in metal:
			has_stones = random.random() < 0.2

		# Smart Naming
		main_gem = ""
		if has_stones:
			main_gem = random.choice(gem_types)
			item_name = f"{metal} {main_gem} {j_type} {purity}"
		else:
			item_name = f"{metal} {j_type} {purity}"

		# Unique Code
		item_code = f"{metal[0]}-{purity[:3]}-{random.randint(10000, 99999)}"

		if not frappe.db.exists("Item", item_code):
			gross_weight = round(random.uniform(3.0, 20.0), 3)

			doc = frappe.get_doc(
				{
					"doctype": "Item",
					"item_code": item_code,
					"item_name": item_name,
					"item_group": "Products",
					"stock_uom": "Nos",
					"is_stock_item": 1,
					"valuation_rate": random.randint(200, 1000),
					"custom_metal_type": metal,
					"custom_purity": purity,
					"custom_gross_weight_g": gross_weight,
					"custom_making_charge_type": "Fixed Amount",
					"custom_making_charge_value": random.randint(40, 250),
				}
			)

			# Add Gemstones
			stone_weight_total = 0.0

			if has_stones:
				# Add 1-5 stones
				for _ in range(random.randint(1, 5)):
					# Logic: Higher quality for better metals
					g_cut = random.choice(cuts)
					g_color = random.choice(colors[:6]) if "18Kt" in purity else random.choice(colors)
					g_clarity = random.choice(clarities[:6]) if "Diamond" == main_gem else "SI1"

					g_carat = round(random.uniform(0.1, 2.0), 2)
					g_rate = random.randint(1000, 8000)  # Price per carat

					doc.append(
						"gemstones",
						{
							"gem_type": (
								main_gem if _ == 0 else random.choice(gem_types)
							),  # Main stone matches name
							"carat": g_carat,
							"count": 1,
							"cut": g_cut,
							"color": g_color,
							"clarity": g_clarity,
							"rate": g_rate,
							"amount": g_carat * g_rate,
						},
					)
					stone_weight_total += g_carat * 0.2  # 1ct = 0.2g

			# Final Weights
			doc.custom_stone_weight_g = round(stone_weight_total, 3)
			doc.custom_net_weight_g = round(gross_weight - stone_weight_total, 3)

			doc.insert(ignore_permissions=True)
			created_items.append(item_code)

	print(f"✅ Generated {len(created_items)} Items.")

	# --- 3. ADD STOCK ---
	print("📦 Adding Stock...")
	warehouse = frappe.db.get_value("Warehouse", {"name": ["like", "%Store 2%"]}, "name")

	if warehouse and created_items:
		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Material Receipt"

		for item in created_items:
			se.append(
				"items",
				{
					"item_code": item,
					"t_warehouse": warehouse,
					"qty": random.randint(1, 3),
					"basic_rate": 100,
				},
			)

		se.insert()
		se.submit()
		print(f"✅ Stock Added to {warehouse}!")

	frappe.db.commit()  # nosemgrep: frappe-semgrep-rules.rules.frappe-manual-commit
