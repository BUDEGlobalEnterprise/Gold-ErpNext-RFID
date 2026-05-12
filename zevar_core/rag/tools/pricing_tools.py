"""
Pricing Agent Tools - Whitelisted functions for the AI assistant pricing capabilities.

These tools are registered into the AI assistant so management can ask pricing
questions conversationally: "Should I increase prices on 14k gold chains?"
"""

import frappe
from frappe import _
from frappe.utils import add_days, flt, getdate, today

# Tool Registry for LLM
AGENT_TOOLS_PRICING = [
	"get_current_gold_rate",
	"get_item_margin_history",
	"simulate_price_change",
	"get_slow_moving_inventory",
	"get_pricing_action_items",
]


@frappe.whitelist(allow_guest=False)
def get_current_gold_rate(metal="Yellow Gold", purity="22Kt") -> dict:
	"""Get current gold/silver rate with 7-day trend.

	Args:
		metal: Metal type (default: Yellow Gold)
		purity: Purity level (default: 22Kt)

	Returns:
		Dict with rate, source, trend data
	"""
	from zevar_core.api.pricing import _get_gold_rate, get_live_rate_history

	rate = _get_gold_rate(metal, purity)
	history = get_live_rate_history(metal=metal, days=7)

	# Calculate 7-day trend
	series = history.get("series", {}).get(purity, [])
	rates_list = [s["rate"] for s in series if s.get("rate")]
	trend = "flat"
	if len(rates_list) >= 2:
		change = rates_list[-1] - rates_list[0]
		if change > 0.01:
			trend = "up"
		elif change < -0.01:
			trend = "down"

	return {
		"status": "success",
		"metal": metal,
		"purity": purity,
		"rate_per_gram": flt(rate),
		"trend_7d": trend,
		"history_points": len(rates_list),
		"message": f"Current {purity} {metal} rate: ${flt(rate):.2f}/g (7-day trend: {trend})",
	}


@frappe.whitelist(allow_guest=False)
def get_item_margin_history(item_code: str, months: int = 6) -> dict:
	"""Get historical margin data for a specific item.

	Args:
		item_code: The Item code to analyze
		months: How many months to look back (default: 6)

	Returns:
		Dict with item details and margin history
	"""
	if not frappe.db.exists("Item", item_code):
		return {"status": "error", "message": f"Item '{item_code}' not found."}

	since = add_days(today(), -int(months) * 30)

	# Get item details
	item = frappe.get_cached_value(
		"Item",
		item_code,
		[
			"item_name",
			"custom_metal_type",
			"custom_purity",
			"custom_net_weight_g",
			"custom_msrp",
			"custom_jewelry_type",
		],
		as_dict=True,
	)

	# Get sales history through Sale Cost Breakdown
	history = frappe.db.sql(
		"""SELECT
			scb.posting_date,
			scb.gross_margin_pct as invoice_margin,
			scb.total_revenue as invoice_revenue,
			scb.gold_rate_at_sale,
			sii.qty,
			sii.rate as selling_price,
			sii.amount
		FROM `tabSale Cost Breakdown` scb
		JOIN `tabSales Invoice` si ON scb.sales_invoice = si.name
		JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
		WHERE sii.item_code = %s AND scb.posting_date >= %s
		ORDER BY scb.posting_date DESC""",
		(item_code, since),
		as_dict=True,
	)

	sales_count = len(history)
	avg_margin = flt(sum(h.invoice_margin for h in history) / sales_count) if sales_count else 0
	total_revenue = sum(flt(h.amount) for h in history)

	message = f"Item: {item.item_name}\n"
	message += f"Sales in {months} months: {sales_count}\n"
	message += f"Total Revenue: ${total_revenue:,.2f}\n"
	message += f"Average Invoice Margin: {avg_margin:.1f}%\n"
	if item.custom_msrp:
		message += f"MSRP: ${flt(item.custom_msrp):,.2f}"

	return {
		"status": "success",
		"item_code": item_code,
		"item_name": item.item_name,
		"metal_type": item.custom_metal_type,
		"purity": item.custom_purity,
		"msrp": flt(item.custom_msrp) if item.custom_msrp else 0,
		"jewelry_type": item.custom_jewelry_type,
		"sales_count": sales_count,
		"total_revenue": total_revenue,
		"avg_margin": avg_margin,
		"history": [
			{
				"date": str(h.posting_date),
				"margin": flt(h.invoice_margin, 2),
				"qty": flt(h.qty),
				"price": flt(h.selling_price),
				"gold_rate": flt(h.gold_rate_at_sale) if h.gold_rate_at_sale else 0,
			}
			for h in history[:20]
		],
		"message": message,
	}


@frappe.whitelist(allow_guest=False)
def simulate_price_change(item_code: str, new_price: float, gold_rate: float | None = None) -> dict:
	"""Simulate a price change and project the margin impact.

	Args:
		item_code: The Item code
		new_price: Proposed new selling price
		gold_rate: Optional gold rate override (uses current if not provided)

	Returns:
		Dict with current vs projected margin analysis
	"""
	if not frappe.db.exists("Item", item_code):
		return {"status": "error", "message": f"Item '{item_code}' not found."}

	from zevar_core.api.pricing import _get_gold_rate

	item = frappe.get_cached_value(
		"Item",
		item_code,
		[
			"item_name",
			"custom_metal_type",
			"custom_purity",
			"custom_net_weight_g",
			"custom_msrp",
			"custom_jewelry_type",
		],
		as_dict=True,
	)

	current_price = flt(item.custom_msrp) or 0
	if current_price == 0:
		# Try last selling price
		last = frappe.db.sql(
			"""SELECT sii.rate FROM `tabSales Invoice Item` sii
			JOIN `tabSales Invoice` si ON sii.parent = si.name
			WHERE sii.item_code = %s AND si.docstatus = 1
			ORDER BY si.posting_date DESC LIMIT 1""",
			(item_code,),
		)
		if last:
			current_price = flt(last[0][0])

	# Calculate COGS
	net_weight = flt(item.custom_net_weight_g)
	if gold_rate:
		rate = flt(gold_rate)
	else:
		rate = _get_gold_rate(item.custom_metal_type or "Yellow Gold", item.custom_purity or "22Kt")

	metal_cogs = net_weight * rate

	# Get gemstone value
	gemstone_value = 0.0
	try:
		gems = frappe.get_all("Item Gemstone", filters={"parent": item_code}, fields=["amount"])
		gemstone_value = sum(flt(g.amount) for g in gems)
	except Exception:
		pass

	total_cogs = metal_cogs + gemstone_value

	# Calculate margins
	current_margin = ((current_price - total_cogs) / current_price * 100) if current_price else 0
	projected_margin = ((flt(new_price) - total_cogs) / flt(new_price) * 100) if flt(new_price) else 0
	price_change_pct = ((flt(new_price) - current_price) / current_price * 100) if current_price else 0

	# Annual projection (based on recent sales velocity)
	last_90_days = frappe.db.sql(
		"""SELECT COUNT(*) as count FROM `tabSales Invoice Item` sii
		JOIN `tabSales Invoice` si ON sii.parent = si.name
		WHERE sii.item_code = %s AND si.docstatus = 1 AND si.posting_date >= %s""",
		(item_code, add_days(today(), -90)),
	)[0][0]
	annual_velocity = flt(last_90_days) * 4  # Extrapolate

	current_annual_profit = (current_price - total_cogs) * annual_velocity
	projected_annual_profit = (flt(new_price) - total_cogs) * annual_velocity

	direction = "increase" if flt(new_price) > current_price else "decrease"
	message = (
		f"Price {direction}: ${current_price:,.2f} → ${flt(new_price):,.2f} ({abs(price_change_pct):.1f}% {direction})\n"
		f"COGS: ${total_cogs:,.2f} (Metal: ${metal_cogs:,.2f}, Gems: ${gemstone_value:,.2f})\n"
		f"Margin: {current_margin:.1f}% → {projected_margin:.1f}% (+{projected_margin - current_margin:.1f}pp)\n"
		f"Annual profit projection: ${current_annual_profit:,.0f} → ${projected_annual_profit:,.0f}"
	)

	return {
		"status": "success",
		"item_code": item_code,
		"item_name": item.item_name,
		"current_price": current_price,
		"new_price": flt(new_price),
		"price_change_pct": flt(price_change_pct, 2),
		"cogs": {
			"metal": flt(metal_cogs),
			"gemstone": flt(gemstone_value),
			"total": flt(total_cogs),
		},
		"gold_rate_used": flt(rate),
		"current_margin_pct": flt(current_margin, 2),
		"projected_margin_pct": flt(projected_margin, 2),
		"margin_change_pp": flt(projected_margin - current_margin, 2),
		"annual_velocity": annual_velocity,
		"current_annual_profit": flt(current_annual_profit),
		"projected_annual_profit": flt(projected_annual_profit),
		"message": message,
	}


@frappe.whitelist(allow_guest=False)
def get_slow_moving_inventory(days: int = 90, jewelry_type: str | None = None) -> dict:
	"""Find items with no recent sales that may need strategic pricing adjustments.

	Args:
		days: Days threshold for "slow moving" (default: 90)
		jewelry_type: Optional filter by jewelry type

	Returns:
		Dict with slow-moving items and suggested actions
	"""
	cutoff = add_days(today(), -int(days))

	filters = {"disabled": 0, "is_stock_item": 1}
	if jewelry_type:
		filters["custom_jewelry_type"] = jewelry_type

	# Find active items
	items = frappe.get_all(
		"Item",
		filters=filters,
		fields=[
			"name",
			"item_name",
			"custom_msrp",
			"custom_metal_type",
			"custom_purity",
			"custom_jewelry_type",
			"custom_net_weight_g",
		],
		limit=500,
	)

	slow_moving = []
	for item in items:
		# Check for recent sales
		last_sale = frappe.db.sql(
			"""SELECT si.posting_date FROM `tabSales Invoice Item` sii
			JOIN `tabSales Invoice` si ON sii.parent = si.name
			WHERE sii.item_code = %s AND si.docstatus = 1
			ORDER BY si.posting_date DESC LIMIT 1""",
			(item.name,),
		)
		if last_sale and getdate(last_sale[0][0]) >= getdate(cutoff):
			continue  # Has recent sale, not slow-moving

		# Check if in stock
		qty = frappe.db.sql(
			"SELECT COALESCE(SUM(actual_qty), 0) FROM `tabBin` WHERE item_code = %s",
			(item.name,),
		)[0][0]
		if flt(qty) <= 0:
			continue  # Not in stock

		days_since = (getdate(today()) - getdate(last_sale[0][0])).days if last_sale else 999

		slow_moving.append(
			{
				"item_code": item.name,
				"item_name": item.item_name,
				"msrp": flt(item.custom_msrp) if item.custom_msrp else 0,
				"metal_type": item.custom_metal_type,
				"jewelry_type": item.custom_jewelry_type,
				"stock_qty": flt(qty),
				"days_since_last_sale": days_since,
				"suggested_action": "Clearance" if days_since > 180 else "Strategic Markdown",
			}
		)

	# Sort by days since last sale
	slow_moving.sort(key=lambda x: x["days_since_last_sale"], reverse=True)

	message = f"Found {len(slow_moving)} slow-moving items (no sales in {days}+ days)\n"
	if slow_moving[:5]:
		message += "Top 5 oldest:\n"
		for i, s in enumerate(slow_moving[:5]):
			message += f"  {i + 1}. {s['item_name']} - {s['days_since_last_sale']} days, ${s['msrp']:,.2f} ({s['suggested_action']})\n"

	return {
		"status": "success",
		"total_slow_moving": len(slow_moving),
		"items": slow_moving[:50],
		"message": message,
	}


@frappe.whitelist(allow_guest=False)
def get_pricing_action_items() -> dict:
	"""Get a prioritized list of pricing actions for management review.

	Pulls items with eroding margins, items where gold price changed but
	selling price hasn't, and pending recommendations.

	Returns:
		Dict with categorized action items
	"""
	action_items = []

	# 1. Items with declining margins (compare last 30 days vs 30-60 days)
	declining = frappe.db.sql(
		"""SELECT
			sii.item_code,
			i.item_name,
			AVG(CASE WHEN scb.posting_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
				THEN scb.gross_margin_pct END) as recent_margin,
			AVG(CASE WHEN scb.posting_date < DATE_SUB(CURDATE(), INTERVAL 30 DAY)
				AND scb.posting_date >= DATE_SUB(CURDATE(), INTERVAL 60 DAY)
				THEN scb.gross_margin_pct END) as prev_margin
		FROM `tabSale Cost Breakdown` scb
		JOIN `tabSales Invoice` si ON scb.sales_invoice = si.name
		JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
		JOIN `tabItem` i ON i.name = sii.item_code
		WHERE scb.posting_date >= DATE_SUB(CURDATE(), INTERVAL 60 DAY)
		GROUP BY sii.item_code, i.item_name
		HAVING recent_margin IS NOT NULL AND prev_margin IS NOT NULL
		AND recent_margin < prev_margin - 5
		ORDER BY (recent_margin - prev_margin) ASC
		LIMIT 10""",
		as_dict=True,
	)

	for d in declining:
		action_items.append(
			{
				"type": "Declining Margin",
				"priority": "High",
				"item_code": d.item_code,
				"item_name": d.item_name,
				"detail": f"Margin dropped from {flt(d.prev_margin):.1f}% to {flt(d.recent_margin):.1f}%",
				"action": "Review pricing — margin declining",
			}
		)

	# 2. Pending pricing recommendations
	pending = frappe.get_all(
		"Pricing Recommendation",
		filters={"status": "Pending Review"},
		fields=[
			"name",
			"item_code",
			"item_name",
			"recommendation_type",
			"recommended_price",
			"confidence_level",
		],
		limit=10,
	)
	for p in pending:
		action_items.append(
			{
				"type": "Pending Recommendation",
				"priority": "Medium",
				"item_code": p.item_code,
				"item_name": p.item_name,
				"detail": f"{p.recommendation_type}: ${flt(p.recommended_price):,.2f} ({p.confidence_level})",
				"action": "Review and approve/reject",
			}
		)

	# 3. Gold rate changed significantly — items needing repricing
	recent_gold = frappe.db.sql(
		"""SELECT AVG(rate_per_gram) as avg_rate
		FROM `tabGold Rate Log`
		WHERE metal = 'Yellow Gold' AND purity = '22Kt'
		AND timestamp >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)""",
		as_dict=True,
	)
	prev_gold = frappe.db.sql(
		"""SELECT AVG(rate_per_gram) as avg_rate
		FROM `tabGold Rate Log`
		WHERE metal = 'Yellow Gold' AND purity = '22Kt'
		AND timestamp >= DATE_SUB(CURDATE(), INTERVAL 14 DAY)
		AND timestamp < DATE_SUB(CURDATE(), INTERVAL 7 DAY)""",
		as_dict=True,
	)

	if recent_gold and prev_gold and flt(recent_gold[0].avg_rate) > 0 and flt(prev_gold[0].avg_rate) > 0:
		gold_change_pct = (
			(flt(recent_gold[0].avg_rate) - flt(prev_gold[0].avg_rate)) / flt(prev_gold[0].avg_rate)
		) * 100
		if abs(gold_change_pct) > 3:
			action_items.append(
				{
					"type": "Gold Rate Alert",
					"priority": "High" if abs(gold_change_pct) > 5 else "Medium",
					"item_code": "",
					"item_name": "All Gold Items",
					"detail": f"Gold rate {'rose' if gold_change_pct > 0 else 'dropped'} {abs(gold_change_pct):.1f}% in the last week",
					"action": "Review gold item pricing",
				}
			)

	message = f"Pricing Action Items: {len(action_items)} items need attention\n"
	for item in action_items[:10]:
		message += f"  [{item['priority']}] {item['type']}: {item['detail']}\n"

	return {
		"status": "success",
		"total_items": len(action_items),
		"items": action_items,
		"message": message,
	}
