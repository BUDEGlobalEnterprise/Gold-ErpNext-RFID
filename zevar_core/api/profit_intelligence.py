"""
Profit Intelligence API - Cost attribution, margin analysis, and pricing insights.

Hooks into Sales Invoice on_submit to auto-generate Sale Cost Breakdown records
that capture every cost component: metal COGS, gemstone value, labor, commission,
payment processing fees, and overhead allocation.
"""

import json

import frappe
from frappe import _
from frappe.query_builder.functions import Count, Sum
from frappe.utils import add_days, flt, getdate, now_datetime, today

# ---------------------------------------------------------------------------
# Sales Invoice on_submit Hook
# ---------------------------------------------------------------------------


def calculate_sale_cost_breakdown(doc, method=None):
	"""Hook: Sales Invoice on_submit. Auto-generates a Sale Cost Breakdown.

	Order matters: this runs AFTER commission.calculate_commissions so
	commission splits are already available.
	"""
	if not doc.is_pos:
		return

	# Clean previous breakdown (handles amend scenarios)
	frappe.db.delete("Sale Cost Breakdown", {"sales_invoice": doc.name})

	# Single source of truth: profit_math.compute_invoice_margin (Phase 0 / M0 gate).
	# The SCB simply persists its result so every surface reads one number.
	from zevar_core.services.profit_math import compute_invoice_margin

	m = compute_invoice_margin(doc)

	breakdown = frappe.new_doc("Sale Cost Breakdown")
	breakdown.sales_invoice = doc.name
	breakdown.posting_date = doc.posting_date or today()
	breakdown.customer = doc.customer

	breakdown.total_revenue = m["revenue"]
	breakdown.total_qty = m["total_qty"]

	breakdown.gold_rate_at_sale = m["gold_rate_at_sale"]
	breakdown.gold_rate_source = m["gold_rate_source"]
	breakdown.gold_rate_timestamp = m["gold_rate_timestamp"]
	breakdown.total_metal_cogs = m["metal_cogs"]
	breakdown.total_gemstone_cogs = m["gemstone_cogs"]
	breakdown.total_item_cogs = m["item_cogs"]

	breakdown.total_labor_cost = m["labor"]
	breakdown.labor_allocation_detail = json.dumps(m["labor_detail"], default=str) if m["labor_detail"] else ""
	breakdown.total_commission = m["commission"]

	breakdown.total_payment_cost = m["payment_cost"]
	breakdown.payment_cost_detail = json.dumps(m["payment_detail"], default=str) if m["payment_detail"] else ""

	breakdown.overhead_per_invoice = m["overhead"]
	breakdown.overhead_method = m["overhead_method"]

	breakdown.total_cost = m["total_cost"]
	breakdown.gross_profit = m["gross_profit"]
	breakdown.gross_margin_pct = m["gross_margin_pct"]

	breakdown.calculation_log = json.dumps(
		{"invoice": doc.name, "source": "profit_math.compute_invoice_margin", "breakdown": m},
		default=str,
		indent=2,
	)
	breakdown.calculated_by = doc.owner or frappe.session.user
	breakdown.calculated_at = now_datetime()

	breakdown.insert(ignore_permissions=True)

	frappe.logger().info(
		"Sale Cost Breakdown created for %s (via profit_math): profit=$%.2f margin=%.1f%%",
		doc.name,
		m["gross_profit"],
		m["gross_margin_pct"],
	)


def cancel_sale_cost_breakdown(doc, method=None):
	"""Hook: Sales Invoice on_cancel. Remove the Sale Cost Breakdown for this invoice.

	Sale Cost Breakdown is a non-submittable (draft-only) record kept in sync 1:1 with
	its invoice (``sales_invoice`` is unique), so it cannot be set to docstatus=2.
	On cancel we delete the row so profit reports never reflect a cancelled sale.
	This mirrors the amend-cleanup ``db.delete`` already performed at the top of
	``calculate_sale_cost_breakdown``.
	"""
	if not doc.is_pos:
		return

	frappe.db.delete("Sale Cost Breakdown", {"sales_invoice": doc.name})


# ---------------------------------------------------------------------------
# Private Helpers — Cost Calculation
# ---------------------------------------------------------------------------


def _calculate_item_cogs(invoice_doc):
	"""Calculate metal COGS using gold rate at time of sale + gemstone COGS.

	Returns: (metal_cogs, gemstone_cogs, gold_rate, gold_source, gold_timestamp)
	"""
	from zevar_core.api.pricing import _get_gold_rate

	total_metal_cogs = 0.0
	total_gemstone_cogs = 0.0
	primary_gold_rate = 0.0
	gold_source = ""
	gold_ts = None

	for item in invoice_doc.items:
		item_doc = frappe.get_cached_value(
			"Item",
			item.item_code,
			[
				"custom_net_weight_g",
				"custom_metal_type",
				"custom_purity",
				"custom_gross_weight_g",
				"valuation_rate",
			],
			as_dict=True,
		)
		if not item_doc:
			continue

		# Metal COGS: net weight x gold rate per gram
		metal_cogs = 0.0
		net_weight = flt(item_doc.custom_net_weight_g)
		if net_weight > 0 and item_doc.custom_metal_type and item_doc.custom_purity:
			gold_rate = _get_gold_rate(item_doc.custom_metal_type, item_doc.custom_purity)
			metal_cogs = net_weight * flt(gold_rate) * flt(item.qty)
			if gold_rate > 0 and primary_gold_rate == 0:
				primary_gold_rate = gold_rate
				# Get source and timestamp
				latest_log = frappe.get_all(
					"Gold Rate Log",
					filters={"metal": item_doc.custom_metal_type, "purity": item_doc.custom_purity},
					fields=["source", "timestamp"],
					order_by="timestamp desc",
					limit=1,
				)
				if latest_log:
					gold_source = latest_log[0].source or ""
					gold_ts = latest_log[0].timestamp
		else:
			# Fallback: use valuation_rate from stock ledger
			vr = flt(item_doc.valuation_rate) or flt(item.get("valuation_rate", 0))
			metal_cogs = vr * flt(item.qty)

		total_metal_cogs += flt(metal_cogs)

		# Gemstone COGS: sum gemstone child table amounts
		gemstone_value = _get_gemstone_value(item.item_code)
		total_gemstone_cogs += flt(gemstone_value) * flt(item.qty)

	return total_metal_cogs, total_gemstone_cogs, primary_gold_rate, gold_source, gold_ts


def _get_gemstone_value(item_code):
	"""Sum gemstone amounts from Item's gemstones child table."""
	try:
		gems = frappe.get_all(
			"Item Gemstone",
			filters={"parent": item_code, "parenttype": "Item"},
			fields=["amount"],
		)
		return sum(flt(g.amount) for g in gems)
	except Exception:
		return 0.0


def _allocate_labor(invoice_doc):
	"""Allocate labor cost from Labor Cost Pool based on salesperson splits.

	Returns: (total_labor_cost, allocation_detail_list)
	"""
	allocation_detail = []
	total_labor = 0.0

	# Get salesperson splits from the invoice
	salespersons = []
	for row in invoice_doc.get("custom_salesperson_splits") or []:
		if (
			hasattr(row, "employee")
			and row.employee
			and hasattr(row, "split_percent")
			and flt(row.split_percent) > 0
		):
			salespersons.append({"employee": row.employee, "split_percent": flt(row.split_percent)})

	if not salespersons:
		# If no salesperson splits, use a default pool
		default_pools = frappe.get_all(
			"Labor Cost Pool",
			filters={"is_active": 1, "role": "Sales Associate"},
			fields=["name", "hourly_rate", "default_minutes_per_sale"],
			limit=1,
		)
		if default_pools:
			pool = default_pools[0]
			minutes = flt(pool.default_minutes_per_sale) or 30
			cost = flt(pool.hourly_rate) * (minutes / 60)
			total_labor = cost
			allocation_detail.append(
				{
					"pool": pool.name,
					"role": "Sales Associate",
					"minutes": minutes,
					"hourly_rate": flt(pool.hourly_rate),
					"cost": flt(cost),
				}
			)
		return total_labor, allocation_detail

	# Map employees to their labor pools
	for sp in salespersons:
		# Try employee-specific pool first
		pool = frappe.get_all(
			"Labor Cost Pool",
			filters={"employee": sp["employee"], "is_active": 1},
			fields=["name", "hourly_rate", "default_minutes_per_sale", "allocation_method"],
			limit=1,
		)
		if not pool:
			# Fall back to role-based pool
			emp_designation = frappe.get_cached_value("Employee", sp["employee"], "designation") or ""
			role_map = {
				"Sales Associate": "Sales Associate",
				"Store Manager": "Store Manager",
				"Sales Manager": "Manager",
				"Manager": "Manager",
			}
			role = role_map.get(emp_designation, "Sales Associate")
			pool = frappe.get_all(
				"Labor Cost Pool",
				filters={"role": role, "is_active": 1},
				fields=["name", "hourly_rate", "default_minutes_per_sale", "allocation_method"],
				limit=1,
			)

		if not pool:
			continue

		p = pool[0]
		minutes = flt(p.default_minutes_per_sale) or 30
		# Scale time by split percentage
		allocated_minutes = minutes * (sp["split_percent"] / 100)
		cost = flt(p.hourly_rate) * (allocated_minutes / 60)
		total_labor += cost

		allocation_detail.append(
			{
				"employee": sp["employee"],
				"split_percent": sp["split_percent"],
				"pool": p.name,
				"hourly_rate": flt(p.hourly_rate),
				"allocated_minutes": flt(allocated_minutes, 2),
				"cost": flt(cost),
			}
		)

	return total_labor, allocation_detail


def _get_commission_total(sales_invoice):
	"""Sum commission amounts from Sales Commission Split for this invoice."""
	result = frappe.get_all(
		"Sales Commission Split",
		filters={"sales_invoice": sales_invoice},
		fields=["commission_amount"],
	)
	return sum(flt(r.commission_amount) for r in result)


def _calculate_payment_costs(invoice_doc):
	"""Calculate payment processing fees based on payment modes and configured rates.

	Returns: (total_cost, detail_list)
	"""
	detail = []
	total_cost = 0.0

	# Get payment entries for this invoice
	payments = []
	if hasattr(invoice_doc, "payments") and invoice_doc.payments:
		for p in invoice_doc.payments:
			payments.append({"mode": p.mode_of_payment, "amount": flt(p.amount)})
	else:
		# Try Sales Invoice Payment child table
		try:
			sip = frappe.qb.DocType("Sales Invoice Payment")
			si = frappe.qb.DocType("Sales Invoice")
			result = (
				frappe.qb.from_(sip)
				.join(si)
				.on(sip.parent == si.name)
				.select(sip.mode_of_payment, sip.amount)
				.where((si.name == invoice_doc.name) & (si.docstatus == 1))
			).run(as_dict=True)
			payments = [{"mode": r.mode_of_payment, "amount": flt(r.amount)} for r in result]
		except Exception:
			pass

	if not payments:
		return 0.0, []

	# Get configured rates from Cost Center Allocation
	try:
		settings = frappe.get_single("Cost Center Allocation")
	except Exception:
		settings = None

	for pmt in payments:
		mode = pmt["mode"] or ""
		amount = pmt["amount"]
		rate = 0.0
		flat = 0.0

		if settings:
			mode_lower = mode.lower()
			if "credit" in mode_lower:
				rate = flt(settings.credit_card_rate) or 0
				flat = flt(settings.credit_card_flat) or 0
			elif "debit" in mode_lower:
				rate = flt(settings.debit_card_rate) or 0
			elif "cash" in mode_lower:
				rate = flt(settings.cash_handling_rate) or 0
			elif "wire" in mode_lower or "transfer" in mode_lower:
				flat = flt(settings.wire_flat) or 0
			elif "gift" in mode_lower:
				rate = flt(settings.gift_card_rate) or 0
			elif "financing" in mode_lower or "affirm" in mode_lower or "klarna" in mode_lower:
				rate = flt(settings.financing_partner_rate) or 0

		fee = (amount * rate / 100) + flat
		total_cost += fee

		detail.append(
			{
				"mode": mode,
				"amount": amount,
				"rate_pct": rate,
				"flat_fee": flat,
				"processing_fee": flt(fee),
			}
		)

	return total_cost, detail


def _allocate_overhead(invoice_revenue, invoice_date):
	"""Calculate overhead allocation from Cost Center Allocation settings.

	Returns: (overhead_cost, method_used)
	"""
	try:
		settings = frappe.get_single("Cost Center Allocation")
	except Exception:
		return 0.0, "no_settings"

	total_monthly_overhead = (
		flt(settings.rent_monthly)
		+ flt(settings.utilities_monthly)
		+ flt(settings.insurance_monthly)
		+ flt(settings.marketing_monthly)
		+ flt(settings.depreciation_monthly)
		+ flt(settings.miscellaneous_monthly)
	)

	if total_monthly_overhead <= 0:
		return 0.0, "zero_overhead"

	method = settings.overhead_allocation_method or "Equal Per Invoice"

	if method == "Proportional to Revenue":
		# Total revenue for the month
		month_start = getdate(invoice_date).replace(day=1)
		month_revenue = flt(
			frappe.db.sql(
				"""SELECT COALESCE(SUM(base_grand_total), 0)
			FROM `tabSales Invoice`
			WHERE posting_date >= %s AND posting_date < DATE_ADD(%s, INTERVAL 1 MONTH)
			AND docstatus = 1 AND is_pos = 1""",
				(month_start, month_start),
			)[0][0]
		)

		if month_revenue > 0:
			overhead = total_monthly_overhead * (flt(invoice_revenue) / month_revenue)
		else:
			# Fallback to equal split
			invoice_count = (
				frappe.db.count(
					"Sales Invoice",
					filters=[
						["posting_date", ">=", month_start],
						["posting_date", "<", add_days(month_start, 30)],
						["docstatus", "=", 1],
						["is_pos", "=", 1],
					],
				)
				or 1
			)
			overhead = total_monthly_overhead / max(invoice_count, 1)
			method = "Equal Per Invoice (fallback)"
	else:
		# Equal Per Invoice
		month_start = getdate(invoice_date).replace(day=1)
		invoice_count = (
			frappe.db.count(
				"Sales Invoice",
				filters=[
					["posting_date", ">=", month_start],
					["posting_date", "<", add_days(month_start, 30)],
					["docstatus", "=", 1],
					["is_pos", "=", 1],
				],
			)
			or 1
		)
		overhead = total_monthly_overhead / max(invoice_count, 1)

	return flt(overhead), method


# ---------------------------------------------------------------------------
# Query Endpoints
# ---------------------------------------------------------------------------


@frappe.whitelist()
def get_profit_summary(from_date=None, to_date=None):
	"""Return aggregated profit KPIs for a date range."""
	frappe.only_for(["System Manager", "Store Manager", "Sales Manager", "Accounts Manager"])

	if not from_date:
		from_date = add_days(today(), -30)
	if not to_date:
		to_date = today()

	scb = frappe.qb.DocType("Sale Cost Breakdown")

	summary = (
		frappe.qb.from_(scb)
		.select(
			Sum(scb.total_revenue).as_("total_revenue"),
			Sum(scb.total_metal_cogs).as_("total_metal_cogs"),
			Sum(scb.total_gemstone_cogs).as_("total_gemstone_cogs"),
			Sum(scb.total_item_cogs).as_("total_item_cogs"),
			Sum(scb.total_labor_cost).as_("total_labor_cost"),
			Sum(scb.total_commission).as_("total_commission"),
			Sum(scb.total_payment_cost).as_("total_payment_cost"),
			Sum(scb.overhead_per_invoice).as_("total_overhead"),
			Sum(scb.total_cost).as_("total_cost"),
			Sum(scb.gross_profit).as_("gross_profit"),
			Count(scb.name).as_("invoice_count"),
		)
		.where((scb.posting_date >= from_date) & (scb.posting_date <= to_date))
	).run(as_dict=True)

	row = summary[0] if summary else {}
	total_rev = flt(row.get("total_revenue"))
	avg_margin = (flt(row.get("gross_profit")) / total_rev * 100) if total_rev else 0

	# Previous period comparison
	prev_start = add_days(from_date, -(getdate(to_date) - getdate(from_date)).days)
	prev_end = add_days(from_date, -1)
	prev = (
		frappe.qb.from_(scb)
		.select(
			Sum(scb.gross_profit).as_("gross_profit"),
			Sum(scb.total_revenue).as_("total_revenue"),
		)
		.where((scb.posting_date >= prev_start) & (scb.posting_date <= prev_end))
	).run(as_dict=True)

	prev_row = prev[0] if prev else {}
	prev_rev = flt(prev_row.get("total_revenue"))
	prev_margin = (flt(prev_row.get("gross_profit")) / prev_rev * 100) if prev_rev else 0

	return {
		"total_revenue": total_rev,
		"total_cost": flt(row.get("total_cost")),
		"gross_profit": flt(row.get("gross_profit")),
		"avg_margin_pct": flt(avg_margin, 2),
		"invoice_count": row.get("invoice_count") or 0,
		"cost_breakdown": {
			"metal_cogs": flt(row.get("total_metal_cogs")),
			"gemstone_cogs": flt(row.get("total_gemstone_cogs")),
			"labor": flt(row.get("total_labor_cost")),
			"commission": flt(row.get("total_commission")),
			"payment_cost": flt(row.get("total_payment_cost")),
			"overhead": flt(row.get("total_overhead")),
		},
		"previous_period": {
			"total_revenue": prev_rev,
			"gross_profit": flt(prev_row.get("gross_profit")),
			"margin_pct": flt(prev_margin, 2),
		},
		"period": {"from_date": from_date, "to_date": to_date},
	}


@frappe.whitelist()
def get_margin_analysis(from_date=None, to_date=None, group_by="jewelry_type"):
	"""Group margins by jewelry_type, metal_type, purity, or salesperson."""
	frappe.only_for(["System Manager", "Store Manager", "Sales Manager", "Accounts Manager"])

	if not from_date:
		from_date = add_days(today(), -30)
	if not to_date:
		to_date = today()

	valid_groups = ["jewelry_type", "metal_type", "purity", "salesperson", "invoice"]
	if group_by not in valid_groups:
		group_by = "jewelry_type"

	scb = frappe.qb.DocType("Sale Cost Breakdown")
	si = frappe.qb.DocType("Sales Invoice")
	sii = frappe.qb.DocType("Sales Invoice Item")
	item = frappe.qb.DocType("Item")

	if group_by == "salesperson":
		# Join through commission splits
		scs = frappe.qb.DocType("Sales Commission Split")
		emp = frappe.qb.DocType("Employee")

		results = (
			frappe.qb.from_(scb)
			.join(si)
			.on(scb.sales_invoice == si.name)
			.join(scs)
			.on(scs.sales_invoice == si.name)
			.join(emp)
			.on(scs.employee == emp.name)
			.select(
				emp.employee_name.as_("group_name"),
				Sum(scb.total_revenue).as_("revenue"),
				Sum(scb.total_cost).as_("total_cost"),
				Sum(scb.gross_profit).as_("gross_profit"),
				Count(scb.name).as_("count"),
			)
			.where((scb.posting_date >= from_date) & (scb.posting_date <= to_date))
			.groupby(emp.employee_name)
		).run(as_dict=True)

	elif group_by == "invoice":
		results = (
			frappe.qb.from_(scb)
			.select(
				scb.sales_invoice.as_("group_name"),
				scb.total_revenue.as_("revenue"),
				scb.total_cost.as_("total_cost"),
				scb.gross_profit.as_("gross_profit"),
				scb.gross_margin_pct.as_("margin_pct"),
			)
			.where((scb.posting_date >= from_date) & (scb.posting_date <= to_date))
			.orderby(scb.posting_date, order=frappe.qb.desc)
		).run(as_dict=True)
	else:
		# Group by item attribute
		field_map = {
			"jewelry_type": "custom_jewelry_type",
			"metal_type": "custom_metal_type",
			"purity": "custom_purity",
		}
		item_field = field_map[group_by]

		results = (
			frappe.qb.from_(scb)
			.join(si)
			.on(scb.sales_invoice == si.name)
			.join(sii)
			.on(sii.parent == si.name)
			.join(item)
			.on(item.name == sii.item_code)
			.select(
				getattr(item, item_field).as_("group_name"),
				Sum(scb.total_revenue).as_("revenue"),
				Sum(scb.total_cost).as_("total_cost"),
				Sum(scb.gross_profit).as_("gross_profit"),
				Count(scb.name).as_("count"),
			)
			.where((scb.posting_date >= from_date) & (scb.posting_date <= to_date))
			.groupby(getattr(item, item_field))
		).run(as_dict=True)

	# Calculate margin for each group
	for r in results:
		rev = flt(r.get("revenue"))
		cost = flt(r.get("total_cost"))
		r["margin_pct"] = flt((rev - cost) / rev * 100, 2) if rev else 0

	return {"group_by": group_by, "data": results, "period": {"from_date": from_date, "to_date": to_date}}


@frappe.whitelist()
def get_cost_breakdown_detail(sales_invoice):
	"""Return full cost breakdown for a single Sales Invoice."""
	frappe.only_for(["System Manager", "Store Manager", "Sales Manager", "Accounts Manager"])

	if not sales_invoice or not frappe.db.exists("Sales Invoice", sales_invoice):
		frappe.throw(_("Sales Invoice '{0}' not found.").format(sales_invoice))

	breakdown = frappe.get_all(
		"Sale Cost Breakdown",
		filters={"sales_invoice": sales_invoice},
		fields=["*"],
		limit=1,
	)

	if not breakdown:
		return {"exists": False, "sales_invoice": sales_invoice}

	bd = breakdown[0]

	# Parse JSON fields
	for field in ["labor_allocation_detail", "payment_cost_detail", "calculation_log"]:
		if bd.get(field):
			try:
				bd[field] = json.loads(bd[field])
			except (json.JSONDecodeError, TypeError):
				pass

	# Enrich with item-level details
	items = frappe.get_all(
		"Sales Invoice Item",
		filters={"parent": sales_invoice},
		fields=["item_code", "item_name", "qty", "rate", "amount"],
	)
	for item_row in items:
		item_meta = frappe.get_cached_value(
			"Item",
			item_row.item_code,
			["custom_metal_type", "custom_purity", "custom_net_weight_g", "custom_jewelry_type"],
			as_dict=True,
		)
		if item_meta:
			item_row["metal_type"] = item_meta.custom_metal_type
			item_row["purity"] = item_meta.custom_purity
			item_row["net_weight_g"] = flt(item_meta.custom_net_weight_g)
			item_row["jewelry_type"] = item_meta.custom_jewelry_type

	bd["items"] = items
	bd["exists"] = True

	return bd


@frappe.whitelist()
def get_profit_trends(period="monthly", months=12):
	"""Return time-series data for profit trends."""
	frappe.only_for(["System Manager", "Store Manager", "Sales Manager", "Accounts Manager"])

	from_date = add_days(today(), -int(months) * 30)

	if period == "weekly":
		date_format = "%Y-%u"
	elif period == "quarterly":
		date_format = "%Y-Q%q"
	else:
		date_format = "%Y-%m"

	results = frappe.db.sql(
		"""SELECT
			DATE_FORMAT(posting_date, %s) as period,
			SUM(total_revenue) as revenue,
			SUM(total_cost) as total_cost,
			SUM(gross_profit) as gross_profit,
			AVG(gross_margin_pct) as avg_margin,
			COUNT(*) as invoice_count
		FROM `tabSale Cost Breakdown`
		WHERE posting_date >= %s
		GROUP BY period
		ORDER BY period""",
		(date_format, from_date),
		as_dict=True,
	)

	for r in results:
		r["avg_margin"] = flt(r.get("avg_margin"), 2)

	return {"period": period, "months": int(months), "data": results}


@frappe.whitelist()
def recalculate_breakdown(sales_invoice):
	"""Force recalculation of a Sale Cost Breakdown. System Manager only."""
	frappe.only_for("System Manager")

	if not frappe.db.exists("Sales Invoice", sales_invoice):
		frappe.throw(_("Sales Invoice '{0}' not found.").format(sales_invoice))

	doc = frappe.get_doc("Sales Invoice", sales_invoice)
	if doc.docstatus != 1:
		frappe.throw(_("Sales Invoice must be submitted."))

	# Delete existing and recalculate
	frappe.db.delete("Sale Cost Breakdown", {"sales_invoice": doc.name})
	calculate_sale_cost_breakdown(doc)

	return {"success": True, "message": f"Breakdown recalculated for {sales_invoice}"}


@frappe.whitelist()
def get_margin_heatmap(from_date=None, to_date=None):
	"""Return margin data structured for heatmap: jewelry_type x metal_type."""
	frappe.only_for(["System Manager", "Store Manager", "Sales Manager", "Accounts Manager"])

	if not from_date:
		from_date = add_days(today(), -30)
	if not to_date:
		to_date = today()

	results = frappe.db.sql(
		"""SELECT
			i.custom_jewelry_type as jewelry_type,
			i.custom_metal_type as metal_type,
			SUM(scb.total_revenue) as revenue,
			SUM(scb.gross_profit) as gross_profit,
			AVG(scb.gross_margin_pct) as avg_margin,
			COUNT(*) as count
		FROM `tabSale Cost Breakdown` scb
		JOIN `tabSales Invoice` si ON scb.sales_invoice = si.name
		JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
		JOIN `tabItem` i ON i.name = sii.item_code
		WHERE scb.posting_date >= %s AND scb.posting_date <= %s
		AND i.custom_jewelry_type IS NOT NULL
		AND i.custom_metal_type IS NOT NULL
		GROUP BY i.custom_jewelry_type, i.custom_metal_type
		ORDER BY i.custom_jewelry_type, i.custom_metal_type""",
		(from_date, to_date),
		as_dict=True,
	)

	# Pivot into the shape components/profit/MarginHeatmap.vue expects:
	# [ { jewelry_type, margins: { <metal_type>: { margin_pct, revenue, gross_profit, count } } }, ... ]
	pivot = {}
	row_order = []
	for r in results:
		jtype = r.get("jewelry_type") or "Unknown"
		metal = r.get("metal_type") or "Unknown"
		if jtype not in pivot:
			pivot[jtype] = {"jewelry_type": jtype, "margins": {}}
			row_order.append(jtype)
		pivot[jtype]["margins"][metal] = {
			"margin_pct": flt(r.get("avg_margin"), 2),
			"revenue": flt(r.get("revenue"), 2),
			"gross_profit": flt(r.get("gross_profit"), 2),
			"count": r.get("count") or 0,
		}

	return [pivot[j] for j in row_order]


@frappe.whitelist()
def get_cost_component_trends(from_date=None, to_date=None, granularity="weekly"):
	"""Return cost component time series for stacked bar charts."""
	frappe.only_for(["System Manager", "Store Manager", "Sales Manager", "Accounts Manager"])

	if not from_date:
		from_date = add_days(today(), -90)
	if not to_date:
		to_date = today()

	date_format = "%Y-%u" if granularity == "weekly" else "%Y-%m"

	results = frappe.db.sql(
		"""SELECT
			DATE_FORMAT(posting_date, %s) as period,
			SUM(total_metal_cogs) as metal_cogs,
			SUM(total_gemstone_cogs) as gemstone_cogs,
			SUM(total_labor_cost) as labor,
			SUM(total_commission) as commission,
			SUM(total_payment_cost) as payment_cost,
			SUM(overhead_per_invoice) as overhead,
			SUM(total_revenue) as revenue,
			SUM(total_cost) as total_cost,
			COUNT(*) as invoice_count
		FROM `tabSale Cost Breakdown`
		WHERE posting_date >= %s AND posting_date <= %s
		GROUP BY period
		ORDER BY period""",
		(date_format, from_date, to_date),
		as_dict=True,
	)

	return {
		"data": results,
		"granularity": granularity,
		"period": {"from_date": from_date, "to_date": to_date},
	}


_CONFIDENCE_SCORES = {"high": 90, "medium": 70, "low": 50}


def _confidence_to_score(level):
	"""Map a High/Medium/Low confidence label to a 0-100 score for the UI badge."""
	return _CONFIDENCE_SCORES.get((level or "").strip().lower(), 0)


@frappe.whitelist()
def create_recommendation(
	item_code, new_price, simulation_data=None, recommendation_type=None, notes=None
):
	"""Create a Pricing Recommendation from a What-If simulation.

	Consumed by components/pricing/WhatIfSimulator.vue (item_code, new_price,
	simulation_data). Previously this endpoint did not exist, so saving a
	simulated price 404'd.
	"""
	frappe.only_for(["System Manager", "Store Manager", "Sales Manager"])

	if not item_code or new_price in (None, ""):
		frappe.throw(_("Item code and new price are required."))

	if not frappe.db.exists("Item", item_code):
		frappe.throw(_("Item {0} not found.").format(item_code))

	item_name, current_price = frappe.db.get_value(
		"Item", item_code, ["item_name", "custom_msrp"]
	) or (None, 0)
	current_price = flt(current_price)
	recommended_price = flt(new_price)

	if recommendation_type:
		rec_type = recommendation_type
	elif recommended_price > current_price:
		rec_type = "Price Increase"
	elif recommended_price < current_price:
		rec_type = "Price Decrease"
	else:
		rec_type = "Premium Positioning"

	price_change_pct = (
		((recommended_price - current_price) / current_price * 100) if current_price else 0
	)

	reasoning = ["Created from What-If simulator."]
	projected_margin = None
	if simulation_data:
		try:
			sim = json.loads(simulation_data) if isinstance(simulation_data, str) else simulation_data
			if isinstance(sim, dict):
				projected_margin = flt(sim.get("margin_pct") or sim.get("projected_margin_pct"))
				reasoning.append("Simulation data attached.")
		except Exception:
			reasoning.append("Simulation data attached.")

	if notes:
		reasoning.append(notes)

	doc = frappe.new_doc("Pricing Recommendation")
	doc.item_code = item_code
	doc.item_name = item_name
	doc.recommendation_type = rec_type
	doc.current_price = current_price
	doc.recommended_price = recommended_price
	doc.price_change_pct = flt(price_change_pct, 2)
	if projected_margin is not None:
		doc.projected_margin_pct = flt(projected_margin, 2)
	doc.confidence_level = "Medium"
	doc.reasoning = " ".join(reasoning)
	doc.generated_by = frappe.session.user
	doc.status = "Pending Review"
	doc.insert(ignore_permissions=True)

	return {"success": True, "name": doc.name}


@frappe.whitelist()
def get_recommendations(status="Pending Review", limit=20):
	"""Get pricing recommendations for the dashboard."""
	frappe.only_for(["System Manager", "Store Manager", "Sales Manager", "Accounts Manager"])

	recommendations = frappe.get_all(
		"Pricing Recommendation",
		filters={"status": status},
		fields=[
			"name",
			"item_code",
			"item_name",
			"recommendation_type",
			"current_price",
			"recommended_price",
			"projected_margin_pct",
			"price_change_pct",
			"confidence_level",
			"reasoning",
			"generated_by",
			"creation",
			"valid_until",
		],
		order_by="creation desc",
		limit_page_length=int(limit),
	)

	for rec in recommendations:
		# PricingRecommendationsPanel reads `confidence` as a 0-100 number for the
		# badge width/colour; the doctype stores High/Medium/Low in confidence_level.
		rec["confidence"] = _confidence_to_score(rec.get("confidence_level"))

	return {"recommendations": recommendations, "total": len(recommendations)}


@frappe.whitelist()
def review_recommendation(recommendation, action, notes=None):
	"""Approve or reject a pricing recommendation."""
	frappe.only_for(["System Manager", "Store Manager", "Sales Manager"])

	if not frappe.db.exists("Pricing Recommendation", recommendation):
		frappe.throw(_("Pricing Recommendation '{0}' not found.").format(recommendation))

	doc = frappe.get_doc("Pricing Recommendation", recommendation)

	# Accept any casing/tense the UI sends: approve, approved, reject, rejected.
	action_norm = (action or "").strip().lower()
	if action_norm in ("approve", "approved"):
		doc.status = "Approved"
		doc.reviewed_by = frappe.session.user
		doc.reviewed_at = now_datetime()
		if notes:
			doc.notes = notes
		doc.save(ignore_permissions=True)
		# Auto-apply the price
		if doc.item_code and doc.recommended_price:
			frappe.db.set_value("Item", doc.item_code, "custom_msrp", doc.recommended_price)
			doc.status = "Applied"
			doc.applied_at = now_datetime()
			doc.save(ignore_permissions=True)
	elif action_norm in ("reject", "rejected"):
		doc.status = "Rejected"
		doc.reviewed_by = frappe.session.user
		doc.reviewed_at = now_datetime()
		if notes:
			doc.notes = notes
		doc.save(ignore_permissions=True)
	else:
		frappe.throw(_("Invalid action {0}. Use 'approve' or 'reject'.").format(action))

	return {"success": True, "status": doc.status, "recommendation": doc.name}
