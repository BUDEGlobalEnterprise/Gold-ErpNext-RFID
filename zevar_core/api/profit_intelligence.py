"""
Profit Intelligence API - Cost attribution, margin analysis, and pricing insights.

Hooks into Sales Invoice on_submit to auto-generate Sale Cost Breakdown records
that capture every cost component: metal COGS, gemstone value, labor, commission,
payment processing fees, and overhead allocation.
"""

import json

import frappe
from frappe import _
from frappe.utils import flt, today, now_datetime, add_days, getdate


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

	log = {"steps": [], "invoice": doc.name}

	# --- Revenue ---
	total_revenue = flt(doc.base_grand_total) or flt(doc.grand_total)
	total_qty = sum(flt(item.qty) for item in doc.items)
	log["steps"].append({"step": "revenue", "total_revenue": total_revenue, "total_qty": total_qty})

	# --- Metal & Gemstone COGS ---
	metal_cogs, gemstone_cogs, gold_rate, gold_source, gold_ts = _calculate_item_cogs(doc)
	item_cogs = flt(metal_cogs) + flt(gemstone_cogs)
	log["steps"].append({
		"step": "cogs",
		"metal_cogs": metal_cogs,
		"gemstone_cogs": gemstone_cogs,
		"item_cogs": item_cogs,
		"gold_rate_used": gold_rate,
		"gold_rate_source": gold_source,
	})

	# --- Labor Cost ---
	labor_cost, labor_detail = _allocate_labor(doc)
	log["steps"].append({"step": "labor", "total_labor": labor_cost, "detail": labor_detail})

	# --- Commission ---
	commission_total = _get_commission_total(doc.name)
	log["steps"].append({"step": "commission", "total_commission": commission_total})

	# --- Payment Processing Cost ---
	payment_cost, payment_detail = _calculate_payment_costs(doc)
	log["steps"].append({"step": "payment", "total_cost": payment_cost, "detail": payment_detail})

	# --- Overhead Allocation ---
	overhead_cost, overhead_method = _allocate_overhead(total_revenue, doc.posting_date)
	log["steps"].append({"step": "overhead", "overhead_cost": overhead_cost, "method": overhead_method})

	# --- Totals ---
	total_cost = flt(item_cogs) + flt(labor_cost) + flt(commission_total) + flt(payment_cost) + flt(overhead_cost)
	gross_profit = flt(total_revenue) - flt(total_cost)
	gross_margin_pct = (flt(gross_profit) / flt(total_revenue) * 100) if total_revenue else 0

	# --- Create Breakdown Record ---
	breakdown = frappe.new_doc("Sale Cost Breakdown")
	breakdown.sales_invoice = doc.name
	breakdown.posting_date = doc.posting_date or today()
	breakdown.customer = doc.customer

	breakdown.total_revenue = total_revenue
	breakdown.total_qty = total_qty

	breakdown.gold_rate_at_sale = gold_rate
	breakdown.gold_rate_source = gold_source
	breakdown.gold_rate_timestamp = gold_ts
	breakdown.total_metal_cogs = metal_cogs
	breakdown.total_gemstone_cogs = gemstone_cogs
	breakdown.total_item_cogs = item_cogs

	breakdown.total_labor_cost = labor_cost
	breakdown.labor_allocation_detail = json.dumps(labor_detail, default=str) if labor_detail else ""
	breakdown.total_commission = commission_total

	breakdown.total_payment_cost = payment_cost
	breakdown.payment_cost_detail = json.dumps(payment_detail, default=str) if payment_detail else ""

	breakdown.overhead_per_invoice = overhead_cost
	breakdown.overhead_method = overhead_method

	breakdown.total_cost = total_cost
	breakdown.gross_profit = gross_profit
	breakdown.gross_margin_pct = flt(gross_margin_pct, 2)

	breakdown.calculation_log = json.dumps(log, default=str, indent=2)
	breakdown.calculated_by = doc.owner or frappe.session.user
	breakdown.calculated_at = now_datetime()

	breakdown.insert(ignore_permissions=True)

	log["result"] = {
		"total_cost": total_cost,
		"gross_profit": gross_profit,
		"margin_pct": flt(gross_margin_pct, 2),
	}
	frappe.logger().info(
		"Sale Cost Breakdown created for %s: profit=$%.2f margin=%.1f%%",
		doc.name, gross_profit, gross_margin_pct,
	)


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

		# Metal COGS: net weight × gold rate per gram
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
		if hasattr(row, "employee") and row.employee and hasattr(row, "split_percent") and flt(row.split_percent) > 0:
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
			allocation_detail.append({
				"pool": pool.name,
				"role": "Sales Associate",
				"minutes": minutes,
				"hourly_rate": flt(pool.hourly_rate),
				"cost": flt(cost),
			})
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

		allocation_detail.append({
			"employee": sp["employee"],
			"split_percent": sp["split_percent"],
			"pool": p.name,
			"hourly_rate": flt(p.hourly_rate),
			"allocated_minutes": flt(allocated_minutes, 2),
			"cost": flt(cost),
		})

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

		detail.append({
			"mode": mode,
			"amount": amount,
			"rate_pct": rate,
			"flat_fee": flat,
			"processing_fee": flt(fee),
		})

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
		month_revenue = flt(frappe.db.sql(
			"""SELECT COALESCE(SUM(base_grand_total), 0)
			FROM `tabSales Invoice`
			WHERE posting_date >= %s AND posting_date < DATE_ADD(%s, INTERVAL 1 MONTH)
			AND docstatus = 1 AND is_pos = 1""",
			(month_start, month_start),
		)[0][0])

		if month_revenue > 0:
			overhead = total_monthly_overhead * (flt(invoice_revenue) / month_revenue)
		else:
			# Fallback to equal split
			invoice_count = frappe.db.count(
				"Sales Invoice",
				filters={
					"posting_date": [">=", month_start],
					"posting_date": ["<", add_days(month_start, 30)],
					"docstatus": 1,
					"is_pos": 1,
				},
			) or 1
			overhead = total_monthly_overhead / max(invoice_count, 1)
			method = "Equal Per Invoice (fallback)"
	else:
		# Equal Per Invoice
		month_start = getdate(invoice_date).replace(day=1)
		invoice_count = frappe.db.count(
			"Sales Invoice",
			filters={
				"posting_date": [">=", month_start],
				"posting_date": ["<", add_days(month_start, 30)],
				"docstatus": 1,
				"is_pos": 1,
			},
		) or 1
		overhead = total_monthly_overhead / max(invoice_count, 1)

	return flt(overhead), method


# ---------------------------------------------------------------------------
# Query Endpoints
# ---------------------------------------------------------------------------


@frappe.whitelist(methods=["GET"])
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
			frappe.qb.fn.Sum(scb.total_revenue).as_("total_revenue"),
			frappe.qb.fn.Sum(scb.total_metal_cogs).as_("total_metal_cogs"),
			frappe.qb.fn.Sum(scb.total_gemstone_cogs).as_("total_gemstone_cogs"),
			frappe.qb.fn.Sum(scb.total_item_cogs).as_("total_item_cogs"),
			frappe.qb.fn.Sum(scb.total_labor_cost).as_("total_labor_cost"),
			frappe.qb.fn.Sum(scb.total_commission).as_("total_commission"),
			frappe.qb.fn.Sum(scb.total_payment_cost).as_("total_payment_cost"),
			frappe.qb.fn.Sum(scb.overhead_per_invoice).as_("total_overhead"),
			frappe.qb.fn.Sum(scb.total_cost).as_("total_cost"),
			frappe.qb.fn.Sum(scb.gross_profit).as_("gross_profit"),
			frappe.qb.fn.Count(scb.name).as_("invoice_count"),
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
			frappe.qb.fn.Sum(scb.gross_profit).as_("gross_profit"),
			frappe.qb.fn.Sum(scb.total_revenue).as_("total_revenue"),
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


@frappe.whitelist(methods=["GET"])
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
				frappe.qb.fn.Sum(scb.total_revenue).as_("revenue"),
				frappe.qb.fn.Sum(scb.total_cost).as_("total_cost"),
				frappe.qb.fn.Sum(scb.gross_profit).as_("gross_profit"),
				frappe.qb.fn.Count(scb.name).as_("count"),
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
				frappe.qb.fn.Sum(scb.total_revenue).as_("revenue"),
				frappe.qb.fn.Sum(scb.total_cost).as_("total_cost"),
				frappe.qb.fn.Sum(scb.gross_profit).as_("gross_profit"),
				frappe.qb.fn.Count(scb.name).as_("count"),
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


@frappe.whitelist(methods=["GET"])
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
			"Item", item_row.item_code,
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


@frappe.whitelist(methods=["GET"])
def get_profit_trends(period="monthly", months=12):
	"""Return time-series data for profit trends."""
	frappe.only_for(["System Manager", "Store Manager", "Sales Manager", "Accounts Manager"])

	from_date = add_days(today(), -int(months) * 30)

	scb = frappe.qb.DocType("Sale Cost Breakdown")

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


@frappe.whitelist(methods=["POST"])
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


@frappe.whitelist(methods=["GET"])
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

	for r in results:
		r["avg_margin"] = flt(r.get("avg_margin"), 2)

	return {"data": results, "period": {"from_date": from_date, "to_date": to_date}}


@frappe.whitelist(methods=["GET"])
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

	return {"data": results, "granularity": granularity, "period": {"from_date": from_date, "to_date": to_date}}


@frappe.whitelist(methods=["GET"])
def get_recommendations(status="Pending Review", limit=20):
	"""Get pricing recommendations for the dashboard."""
	frappe.only_for(["System Manager", "Store Manager", "Sales Manager", "Accounts Manager"])

	recommendations = frappe.get_all(
		"Pricing Recommendation",
		filters={"status": status},
		fields=[
			"name", "item_code", "item_name", "recommendation_type",
			"current_price", "recommended_price", "projected_margin_pct",
			"price_change_pct", "confidence_level", "reasoning",
			"generated_by", "creation", "valid_until",
		],
		order_by="creation desc",
		limit_page_length=int(limit),
	)

	return {"recommendations": recommendations, "total": len(recommendations)}


@frappe.whitelist(methods=["POST"])
def review_recommendation(recommendation, action, notes=None):
	"""Approve or reject a pricing recommendation."""
	frappe.only_for(["System Manager", "Store Manager", "Sales Manager"])

	if not frappe.db.exists("Pricing Recommendation", recommendation):
		frappe.throw(_("Pricing Recommendation '{0}' not found.").format(recommendation))

	doc = frappe.get_doc("Pricing Recommendation", recommendation)

	if action == "approve":
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
	elif action == "reject":
		doc.status = "Rejected"
		doc.reviewed_by = frappe.session.user
		doc.reviewed_at = now_datetime()
		if notes:
			doc.notes = notes
		doc.save(ignore_permissions=True)
	else:
		frappe.throw(_("Invalid action. Use 'approve' or 'reject'."))

	return {"success": True, "status": doc.status, "recommendation": doc.name}
