"""
Inventory Dashboard API — Stock value by warehouse, aging buckets,
shrinkage trend, and velocity classification.
"""

import frappe
from frappe import _
from frappe.utils import add_days, add_months, flt, getdate, nowdate


@frappe.whitelist()
def get_dashboard_data():
	"""Single-call payload for the Inventory Dashboard page."""
	frappe.only_for(
		["System Manager", "Store Manager", "Stock Manager", "Inventory Manager", "Sales Manager"]
	)
	today = nowdate()
	return {
		"kpi": _get_kpi_summary(today),
		"store_values": _get_stock_by_warehouse(),
		"aging": _get_aging_buckets(today),
		"shrinkage": _get_shrinkage_trend(today),
	}


@frappe.whitelist()
def get_kpi_summary():
	"""Total items, total value, low stock count, in-transit count."""
	frappe.only_for(
		["System Manager", "Store Manager", "Stock Manager", "Inventory Manager", "Sales Manager"]
	)
	return _get_kpi_summary(nowdate())


@frappe.whitelist()
def get_stock_by_warehouse():
	"""Stock valuation grouped by warehouse."""
	frappe.only_for(
		["System Manager", "Store Manager", "Stock Manager", "Inventory Manager", "Sales Manager"]
	)
	return _get_stock_by_warehouse()


@frappe.whitelist()
def get_aging_buckets():
	"""Item count grouped by days since last movement."""
	frappe.only_for(
		["System Manager", "Store Manager", "Stock Manager", "Inventory Manager", "Sales Manager"]
	)
	return _get_aging_buckets(nowdate())


@frappe.whitelist()
def get_shrinkage_trend():
	"""Monthly shrinkage (write-offs / stock reconciliation variance) for 6 months."""
	frappe.only_for(
		["System Manager", "Store Manager", "Stock Manager", "Inventory Manager", "Sales Manager"]
	)
	return _get_shrinkage_trend(nowdate())


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _get_kpi_summary(today):
	"""Aggregate inventory KPIs."""
	# Total active items
	total_items = frappe.db.count("Item", filters={"disabled": 0, "is_stock_item": 1})

	# Total stock value from Bin
	bin_val = frappe.db.sql(
		"""SELECT
			COALESCE(SUM(stock_value), 0) as total_value,
			COUNT(CASE WHEN actual_qty <= 2 AND actual_qty > 0 THEN 1 END) as low_stock
		FROM `tabBin`
		WHERE actual_qty > 0""",
		as_dict=True,
	)
	r = bin_val[0] if bin_val else {}

	# In transit: items on active Material Request or Purchase Order
	in_transit = frappe.db.sql(
		"""SELECT COUNT(*) as cnt FROM `tabPurchase Order Item` poi
		JOIN `tabPurchase Order` po ON poi.parent = po.name
		WHERE po.docstatus = 1 AND po.status = 'To Receive and Bill'""",
		as_dict=True,
	)
	transit_count = in_transit[0].cnt if in_transit else 0

	return {
		"total_items": total_items,
		"total_value": flt(r.get("total_value", 0)),
		"low_stock": r.get("low_stock", 0) or 0,
		"in_transit": transit_count,
	}


def _get_stock_by_warehouse():
	"""Stock value by non-group, non-disabled warehouses."""
	rows = frappe.db.sql(
		"""SELECT
			w.name AS warehouse,
			w.warehouse_name AS name,
			COALESCE(SUM(b.stock_value), 0) AS value
		FROM `tabWarehouse` w
		LEFT JOIN `tabBin` b ON b.warehouse = w.name AND b.actual_qty > 0
		WHERE w.is_group = 0 AND w.disabled = 0
		GROUP BY w.name
		HAVING value > 0
		ORDER BY value DESC""",
		as_dict=True,
	)

	grand = sum(flt(r.value) for r in rows) or 1
	for r in rows:
		r["value"] = flt(r.value)
		r["pct"] = flt(flt(r.value) / grand * 100, 1)

	return rows


def _get_aging_buckets(today):
	"""Items grouped by days since last Stock Ledger Entry movement."""
	buckets = [
		{"label": "< 30 days", "min_days": 0, "max_days": 30},
		{"label": "30-90 days", "min_days": 30, "max_days": 90},
		{"label": "90-180 days", "min_days": 90, "max_days": 180},
		{"label": "> 180 days", "min_days": 180, "max_days": None},
	]

	# Get last movement date per item
	last_moves = frappe.db.sql(
		"""SELECT
			sle.item_code,
			MAX(sle.posting_date) AS last_move
		FROM `tabStock Ledger Entry` sle
		WHERE sle.docstatus = 1
		GROUP BY sle.item_code""",
		as_dict=True,
	)

	today_dt = getdate(today)
	item_ages = {}
	for row in last_moves:
		days = (today_dt - getdate(row.last_move)).days
		item_ages[row.item_code] = days

	for b in buckets:
		if b["max_days"] is None:
			count = sum(1 for d in item_ages.values() if d >= b["min_days"])
		else:
			count = sum(1 for d in item_ages.values() if b["min_days"] <= d < b["max_days"])
		b["count"] = count

	return buckets


def _get_shrinkage_trend(today):
	"""Monthly shrinkage from Stock Reconciliation for 6 months."""
	rows = frappe.db.sql(
		"""SELECT
			DATE_FORMAT(sr.posting_date, '%%b') AS label,
			COALESCE(SUM(ABS(sri.qty - sri.current_qty) * COALESCE(i.valuation_rate, 0)), 0) AS value
		FROM `tabStock Reconciliation` sr
		JOIN `tabStock Reconciliation Item` sri ON sri.parent = sr.name
		LEFT JOIN `tabItem` i ON i.name = sri.item_code
		WHERE sr.docstatus = 1
		AND sr.posting_date >= DATE_SUB(%s, INTERVAL 6 MONTH)
		GROUP BY label, DATE_FORMAT(sr.posting_date, '%%Y-%%m')
		ORDER BY DATE_FORMAT(sr.posting_date, '%%Y-%%m')""",
		(today,),
		as_dict=True,
	)

	max_val = max(flt(r.value) for r in rows) if rows else 1
	max_val = max_val or 1

	for r in rows:
		r["value"] = flt(r.value)
		r["height"] = flt(flt(r.value) / max_val * 100, 1) if max_val else 0

	# Fill in missing months
	month_labels = []
	for i in range(5, -1, -1):
		dt = add_months(getdate(today), -i)
		month_labels.append(dt.strftime("%b"))

	result_map = {r.label: r for r in rows}
	result = []
	for lbl in month_labels:
		if lbl in result_map:
			result.append(result_map[lbl])
		else:
			result.append({"label": lbl, "value": 0, "height": 0})

	return result
