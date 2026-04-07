import frappe


def fix_item_groups():
	frappe.db.sql(
		"UPDATE tabItem SET item_group='All Item Groups' WHERE item_group IS NULL OR item_group='' OR item_group='None'"
	)
	frappe.db.commit()
	print("Fixed item groups")


def restock_failed():
	from dbfread import DBF

	DBF_PATH = "/workspace/development/Zevar_URMS/JCSWIN 1(1)/JCSWIN/inventor.DBF"
	WAREHOUSE = "Zevar New York - AS"

	table = DBF(DBF_PATH, encoding="cp1252", ignore_missing_memofile=True)

	company = frappe.defaults.get_global_default("company")
	expense_account = frappe.get_cached_value(
		"Company", company, "stock_adjustment_account"
	) or frappe.get_cached_value("Company", company, "default_expense_account")

	items_with_stock = []
	for record in table:
		barcode = (record.get("BARCODE") or "").strip()
		stockno = (record.get("STOCKNO") or "").strip()
		abr = (record.get("ABR") or "").strip()
		qty = record.get("QTY") or 0
		cost = record.get("COST") or 0

		if qty <= 0:
			continue

		item_code = barcode if barcode else f"{abr}-{stockno}" if abr and stockno else stockno
		if not item_code or not frappe.db.exists("Item", item_code):
			continue

		actual_qty = (
			frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": WAREHOUSE}, "actual_qty") or 0
		)
		if actual_qty > 0:
			continue

		items_with_stock.append(
			{
				"item_code": item_code,
				"qty": float(qty),
				"valuation_rate": float(cost) if cost and cost > 0 else 0,
			}
		)

	print(f"Found {len(items_with_stock)} items still needing stock")

	batch_size = 50
	created = 0
	errors = 0

	for i in range(0, len(items_with_stock), batch_size):
		batch = items_with_stock[i : i + batch_size]
		try:
			se = frappe.new_doc("Stock Entry")
			se.stock_entry_type = "Material Receipt"
			se.company = company
			se.posting_date = "2026-04-01"

			for item in batch:
				rate = item["valuation_rate"] if item["valuation_rate"] > 0 else 1
				se.append(
					"items",
					{
						"item_code": item["item_code"],
						"qty": item["qty"],
						"uom": "Nos",
						"t_warehouse": WAREHOUSE,
						"basic_rate": rate,
						"expense_account": expense_account,
					},
				)

			se.insert(ignore_permissions=True)
			se.submit()
			created += len(batch)

			if (i + batch_size) % 500 == 0:
				frappe.db.commit()
				print(f"  Stocked {created}/{len(items_with_stock)} items...")

		except Exception as e:
			errors += len(batch)
			print(f"  Batch {i // batch_size} error: {str(e)[:120]}")
			frappe.db.rollback()

	frappe.db.commit()
	print(f"\nDone: {created} items stocked, {errors} errors")
