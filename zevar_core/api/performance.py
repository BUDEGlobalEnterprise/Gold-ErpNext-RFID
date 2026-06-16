"""
Performance API — Performance-based compensation and workforce intelligence engine.

Phase 1: Event logging hooks + target/compensation queries
Phase 2: Quarterly review generation + management
"""

import json

import frappe
from frappe import _
from frappe.utils import add_days, cint, flt, getdate, now_datetime, today

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_employee_from_user(user: str) -> str | None:
	"""Map a Frappe User to their Employee record."""
	if not user:
		return None
	return frappe.db.get_value("Employee", {"user_id": user}, "name")


def _resolve_employee_from_sales_person(sales_person: str) -> str | None:
	"""Map a Sales Person to their Employee record (ERPNext Sales Person has an employee field)."""
	if not sales_person:
		return None
	return frappe.db.get_value("Sales Person", sales_person, "employee")


def _resolve_store_location_from_warehouse(warehouse: str | None) -> str | None:
	"""Map a Warehouse to the Store Location whose ``default_warehouse`` it is.

	``Performance Log.store_location`` is a Link to the ``Store Location`` doctype
	(not ``Warehouse``), so we must resolve the store from the invoice's warehouse
	rather than storing the warehouse id directly. This is the same resolution used
	by the POS receipt print formats. Returns ``None`` when no Store Location maps
	to this warehouse (``store_location`` is non-mandatory on Performance Log).
	"""
	if not warehouse:
		return None
	return frappe.db.get_value("Store Location", {"default_warehouse": warehouse}, "name")


def _get_active_target(employee: str, date=None) -> str | None:
	"""Find the active Performance Target for an employee on a given date."""
	if not date:
		date = today()

	targets = frappe.get_all(
		"Performance Target",
		filters={
			"employee": employee,
			"docstatus": 1,
			"status": "Active",
			"period_start": ["<=", date],
			"period_end": [">=", date],
		},
		fields=["name", "period_type"],
		limit=1,
	)
	if targets:
		return targets[0]
	return None


def _create_performance_log(
	employee: str,
	event_type: str,
	event_date,
	reference_doctype: str | None = None,
	reference_document: str | None = None,
	revenue_amount: float = 0,
	item_count: int = 0,
	customer: str | None = None,
	commission_amount: float = 0,
	hours_worked: float = 0,
	store_location: str | None = None,
	performance_target: str | None = None,
	period_type: str | None = None,
	custom_data: dict | None = None,
):
	"""Create an immutable Performance Log entry."""
	if not employee:
		return

	log = frappe.new_doc("Performance Log")
	log.employee = employee
	log.event_type = event_type
	log.event_date = event_date or now_datetime()
	log.reference_doctype = reference_doctype
	log.reference_document = reference_document
	log.revenue_amount = flt(revenue_amount)
	log.item_count = cint(item_count)
	log.customer = customer
	log.commission_amount = flt(commission_amount)
	log.hours_worked = flt(hours_worked)
	log.store_location = store_location
	log.performance_target = performance_target
	log.period_type = period_type
	if custom_data:
		log.custom_data = json.dumps(custom_data)
	log.insert(ignore_permissions=True)
	return log.name


# ---------------------------------------------------------------------------
# Hook: Sales Invoice on_submit → "Sale Completed" logs
# ---------------------------------------------------------------------------


def log_sale_event(doc, method=None):
	"""Hook: Sales Invoice on_submit. Creates Performance Log for each salesperson."""
	if not getattr(doc, "is_pos", False):
		return

	splits = doc.get("custom_salesperson_splits") or []
	net_total = flt(doc.base_net_total)

	if net_total <= 0 or not splits:
		return

	# Fetch commission splits for this invoice (just created by commission hook)
	commission_map = _get_commission_map(doc.name)

	for row in splits:
		employee = getattr(row, "employee", None)
		split_pct = flt(getattr(row, "split_percent", 0))
		if not employee or split_pct <= 0:
			continue

		sp_revenue = net_total * (split_pct / 100)
		sp_commission = commission_map.get(employee, 0)

		target_info = _get_active_target(employee)
		performance_target = target_info["name"] if target_info else None
		period_type = target_info["period_type"] if target_info else None

		_create_performance_log(
			employee=employee,
			event_type="Sale Completed",
			event_date=doc.posting_date or today(),
			reference_doctype="Sales Invoice",
			reference_document=doc.name,
			revenue_amount=sp_revenue,
			item_count=len(doc.items) if hasattr(doc, "items") else 0,
			customer=doc.customer,
			commission_amount=sp_commission,
			store_location=_resolve_store_location_from_warehouse(getattr(doc, "set_warehouse", None)),
			performance_target=performance_target,
			period_type=period_type,
		)


def log_sale_cancel_event(doc, method=None):
	"""Hook: Sales Invoice on_cancel. Creates 'Return Processed' log for each salesperson."""
	if not getattr(doc, "is_pos", False):
		return

	splits = doc.get("custom_salesperson_splits") or []
	net_total = flt(doc.base_net_total)

	for row in splits:
		employee = getattr(row, "employee", None)
		split_pct = flt(getattr(row, "split_percent", 0))
		if not employee or split_pct <= 0:
			continue

		sp_revenue = net_total * (split_pct / 100)

		target_info = _get_active_target(employee)
		performance_target = target_info["name"] if target_info else None
		period_type = target_info["period_type"] if target_info else None

		_create_performance_log(
			employee=employee,
			event_type="Return Processed",
			event_date=now_datetime(),
			reference_doctype="Sales Invoice",
			reference_document=doc.name,
			revenue_amount=-(abs(sp_revenue)),  # Negative to indicate return
			store_location=_resolve_store_location_from_warehouse(getattr(doc, "set_warehouse", None)),
			performance_target=performance_target,
			period_type=period_type,
		)


# ---------------------------------------------------------------------------
# Hook: Layaway Contract on_submit → "Layaway Created" log
# ---------------------------------------------------------------------------


def log_layaway_event(doc, method=None):
	"""Hook: Layaway Contract on_submit. Creates Performance Log for the sales person."""
	sales_person = getattr(doc, "sales_person", None)
	employee = _resolve_employee_from_sales_person(sales_person) if sales_person else None

	# Fallback: check if owner is an employee
	if not employee:
		employee = _resolve_employee_from_user(doc.owner)

	if not employee:
		return

	target_info = _get_active_target(employee)
	performance_target = target_info["name"] if target_info else None
	period_type = target_info["period_type"] if target_info else None

	_create_performance_log(
		employee=employee,
		event_type="Layaway Created",
		event_date=doc.creation or now_datetime(),
		reference_doctype="Layaway Contract",
		reference_document=doc.name,
		revenue_amount=flt(getattr(doc, "total_amount", 0)),
		customer=getattr(doc, "customer", None),
		store_location=getattr(doc, "store_location", None),
		performance_target=performance_target,
		period_type=period_type,
	)


# ---------------------------------------------------------------------------
# Hook: Repair Order on_submit → "Repair Completed" log
# ---------------------------------------------------------------------------


def log_repair_event(doc, method=None):
	"""Hook: Repair Order on_submit. Creates Performance Log for assigned technician."""
	assigned_to = getattr(doc, "assigned_to", None)
	employee = _resolve_employee_from_user(assigned_to) if assigned_to else None

	if not employee:
		return

	target_info = _get_active_target(employee)
	performance_target = target_info["name"] if target_info else None
	period_type = target_info["period_type"] if target_info else None

	_create_performance_log(
		employee=employee,
		event_type="Repair Completed",
		event_date=now_datetime(),
		reference_doctype="Repair Order",
		reference_document=doc.name,
		revenue_amount=flt(getattr(doc, "total_charges", 0) or getattr(doc, "repair_cost", 0)),
		customer=getattr(doc, "customer", None),
		performance_target=performance_target,
		period_type=period_type,
	)


# ---------------------------------------------------------------------------
# Hook: Attendance on_submit → "Shift Complete" log
# ---------------------------------------------------------------------------


def log_attendance_event(doc, method=None):
	"""Hook: Attendance on_submit. Creates 'Shift Complete' log with working hours."""
	employee = getattr(doc, "employee", None)
	if not employee:
		return

	working_hours = flt(getattr(doc, "working_hours", 0))

	target_info = _get_active_target(employee, doc.attendance_date)
	performance_target = target_info["name"] if target_info else None
	period_type = target_info["period_type"] if target_info else None

	event_type = "Shift Complete"
	status = getattr(doc, "status", "")
	if status == "Absent":
		event_type = "No-Show"
	elif status == "Half Day":
		event_type = "Shift Complete"

	late_entry = getattr(doc, "late_entry", False)
	if late_entry:
		event_type = "Late Arrival"

	_create_performance_log(
		employee=employee,
		event_type=event_type,
		event_date=doc.attendance_date or today(),
		reference_doctype="Attendance",
		reference_document=doc.name,
		hours_worked=working_hours,
		performance_target=performance_target,
		period_type=period_type,
	)


# ---------------------------------------------------------------------------
# Helper: commission map for a Sales Invoice
# ---------------------------------------------------------------------------


def _get_commission_map(sales_invoice: str) -> dict:
	"""Return {employee: commission_amount} from Sales Commission Split."""
	commissions = frappe.get_all(
		"Sales Commission Split",
		filters={"sales_invoice": sales_invoice},
		fields=["employee", "commission_amount"],
	)
	return {c.employee: flt(c.commission_amount) for c in commissions}


# ---------------------------------------------------------------------------
# API: Query endpoints
# ---------------------------------------------------------------------------


@frappe.whitelist(methods=["GET"])
def get_employee_performance_summary(
	employee: str, period_start: str | None = None, period_end: str | None = None
) -> dict:
	"""Return aggregated performance metrics for an employee in a period."""
	frappe.only_for(["System Manager", "HR Manager", "Store Manager", "Sales Manager", "HR User"])

	if not employee or not frappe.db.exists("Employee", employee):
		frappe.throw(_("Employee not found"))

	# Default to current month if no period specified
	if not period_start:
		period_start = getdate(today()).replace(day=1)
	if not period_end:
		period_end = today()

	logs = frappe.get_all(
		"Performance Log",
		filters={
			"employee": employee,
			"event_date": ["between", [period_start, period_end]],
		},
		fields=["event_type", "revenue_amount", "item_count", "commission_amount", "hours_worked"],
	)

	# Aggregate
	total_revenue = 0
	total_transactions = 0
	total_items = 0
	total_commission = 0
	total_hours = 0
	late_arrivals = 0
	no_shows = 0

	for log in logs:
		if log.event_type == "Sale Completed":
			total_revenue += flt(log.revenue_amount)
			total_transactions += 1
			total_items += cint(log.item_count)
			total_commission += flt(log.commission_amount)
		elif log.event_type == "Return Processed":
			total_revenue += flt(log.revenue_amount)  # negative
		elif log.event_type in ("Shift Complete", "Late Arrival", "Overtime"):
			total_hours += flt(log.hours_worked)
		elif log.event_type == "Late Arrival":
			late_arrivals += 1
		elif log.event_type == "No-Show":
			no_shows += 1

	avg_transaction = total_revenue / total_transactions if total_transactions > 0 else 0

	# Get active target for comparison
	target_info = _get_active_target(employee)
	target_data = None
	achievement_pct = None
	if target_info:
		target_doc = frappe.get_doc("Performance Target", target_info["name"])
		target_data = {
			"revenue_target": flt(target_doc.revenue_target),
			"revenue_weight": flt(target_doc.revenue_weight),
			"activity_weight": flt(target_doc.activity_weight),
			"quality_weight": flt(target_doc.quality_weight),
			"guaranteed_hourly_rate": flt(target_doc.guaranteed_hourly_rate),
			"target_hourly_rate": flt(target_doc.target_hourly_rate),
			"superior_hourly_rate": flt(target_doc.superior_hourly_rate),
			"minimum_performance_pct": flt(target_doc.minimum_performance_pct),
		}
		if target_doc.revenue_target and target_doc.revenue_target > 0:
			achievement_pct = (total_revenue / flt(target_doc.revenue_target)) * 100

	return {
		"employee": employee,
		"employee_name": frappe.db.get_value("Employee", employee, "employee_name"),
		"period_start": str(period_start),
		"period_end": str(period_end),
		"total_revenue": flt(total_revenue, 2),
		"total_transactions": total_transactions,
		"total_items": total_items,
		"total_commission": flt(total_commission, 2),
		"total_hours": flt(total_hours, 2),
		"avg_transaction_value": flt(avg_transaction, 2),
		"late_arrivals": late_arrivals,
		"no_shows": no_shows,
		"target": target_data,
		"revenue_achievement_pct": flt(achievement_pct, 2) if achievement_pct else None,
	}


@frappe.whitelist(methods=["GET"])
def get_team_performance(store_location: str | None = None, date: str | None = None) -> list:
	"""Return all employees' performance data for a store on a given date."""
	frappe.only_for(["System Manager", "HR Manager", "Store Manager", "Sales Manager"])

	if not date:
		date = today()

	# Get all employees with active performance targets
	filters = {"docstatus": 1, "status": "Active", "period_start": ["<=", date], "period_end": [">=", date]}
	if store_location:
		filters["store_location"] = store_location

	targets = frappe.get_all(
		"Performance Target",
		filters=filters,
		fields=["name", "employee", "employee_name", "period_start", "period_end", "revenue_target"],
	)

	result = []
	for t in targets:
		summary = get_employee_performance_summary(t.employee, str(t.period_start), str(t.period_end))
		summary["target_name"] = t.name
		summary["revenue_target"] = flt(t.revenue_target)
		result.append(summary)

	# Sort by revenue descending
	result.sort(key=lambda x: x.get("total_revenue", 0), reverse=True)
	return result


@frappe.whitelist(methods=["GET"])
def get_live_scoreboard(store_location: str | None = None) -> list:
	"""Real-time current-period scoreboard for all active associates."""
	frappe.only_for(["System Manager", "HR Manager", "Store Manager", "Sales Manager"])

	return get_team_performance(store_location, today())


@frappe.whitelist(methods=["GET"])
def get_performance_history(employee: str, limit: int = 12) -> list:
	"""Return past Compensation Calculations for an employee."""
	frappe.only_for(["System Manager", "HR Manager", "Store Manager", "HR User"])

	if not employee or not frappe.db.exists("Employee", employee):
		frappe.throw(_("Employee not found"))

	calculations = frappe.get_all(
		"Compensation Calculation",
		filters={"employee": employee, "docstatus": 1},
		fields=[
			"name",
			"period_start",
			"period_end",
			"period_type",
			"overall_performance_score",
			"effective_hourly_rate",
			"final_calculated_pay",
			"commission_earned",
			"status",
		],
		order_by="period_end desc",
		limit=cint(limit),
	)
	return calculations


@frappe.whitelist(methods=["GET"])
def get_performance_trend(employee: str, periods_back: int = 4) -> dict:
	"""Trend data for last N periods — used in charts."""
	frappe.only_for(["System Manager", "HR Manager", "Store Manager", "HR User"])

	calculations = get_performance_history(employee, cint(periods_back))

	if not calculations:
		return {"employee": employee, "trend": []}

	return {
		"employee": employee,
		"trend": [
			{
				"period": c.period_start,
				"period_end": c.period_end,
				"score": flt(c.overall_performance_score),
				"hourly_rate": flt(c.effective_hourly_rate),
				"total_pay": flt(c.final_calculated_pay),
				"commission": flt(c.commission_earned),
			}
			for c in calculations
		],
	}


# ---------------------------------------------------------------------------
# API: Compensation Calculation (Batch 4 — core algorithm)
# ---------------------------------------------------------------------------


@frappe.whitelist(methods=["POST"])
def run_compensation_calculation(employee: str, period_start: str, period_end: str) -> dict:
	"""Run the full compensation calculation for an employee in a period."""
	frappe.only_for(["System Manager", "HR Manager", "Store Manager"])

	if not employee or not frappe.db.exists("Employee", employee):
		frappe.throw(_("Employee not found"))

	# Get active target overlapping the period
	target = frappe.get_all(
		"Performance Target",
		filters={
			"employee": employee,
			"docstatus": 1,
			"period_start": ["<=", period_end],
			"period_end": [">=", period_start],
		},
		fields=["name"],
		limit=1,
	)
	if not target:
		frappe.throw(_("No active Performance Target found for this employee in the given period"))

	target_doc = frappe.get_doc("Performance Target", target[0]["name"])

	# Check for existing calculation
	existing = frappe.get_all(
		"Compensation Calculation",
		filters={
			"employee": employee,
			"performance_target": target_doc.name,
			"docstatus": ["!=", 2],
		},
		limit=1,
	)
	if existing:
		frappe.throw(
			_("Compensation Calculation {0} already exists for this period").format(existing[0]["name"])
		)

	# Aggregate Performance Logs
	logs = frappe.get_all(
		"Performance Log",
		filters={
			"employee": employee,
			"event_date": ["between", [period_start, period_end]],
		},
		fields=["event_type", "revenue_amount", "item_count", "commission_amount", "hours_worked"],
	)

	# --- Revenue Metrics ---
	total_revenue = sum(flt(l.revenue_amount) for l in logs if l.event_type == "Sale Completed")
	total_transactions = sum(1 for l in logs if l.event_type == "Sale Completed")
	total_items = sum(cint(l.item_count) for l in logs if l.event_type == "Sale Completed")
	layaway_count = sum(1 for l in logs if l.event_type == "Layaway Created")
	return_count = sum(1 for l in logs if l.event_type == "Return Processed")

	# --- Activity Metrics ---
	repair_count = sum(1 for l in logs if l.event_type == "Repair Completed")

	# --- Hours ---
	total_hours = sum(
		flt(l.hours_worked) for l in logs if l.event_type in ("Shift Complete", "Late Arrival", "Overtime")
	)

	# --- Commission ---
	total_commission = sum(flt(l.commission_amount) for l in logs if l.event_type == "Sale Completed")

	# --- Calculate Achievement Percentages ---
	revenue_target = flt(target_doc.revenue_target)
	revenue_achievement_pct = (total_revenue / revenue_target * 100) if revenue_target > 0 else 100

	items_sold_target = cint(target_doc.items_sold_target)
	items_achievement_pct = (total_items / items_sold_target * 100) if items_sold_target > 0 else 100

	customers_served_target = cint(target_doc.customers_served_target)
	# Approximate: total unique transactions ≈ customers served
	customers_achievement_pct = (
		(total_transactions / customers_served_target * 100) if customers_served_target > 0 else 100
	)

	repair_target = cint(target_doc.repair_orders_target)
	repair_achievement_pct = (repair_count / repair_target * 100) if repair_target > 0 else 100

	activity_achievement_pct = (
		items_achievement_pct + customers_achievement_pct + repair_achievement_pct
	) / 3

	# --- Quality Metrics ---
	return_rate = (return_count / total_transactions * 100) if total_transactions > 0 else 0
	return_rate_max = flt(target_doc.return_rate_max) or 100
	quality_achievement_pct = max(0, 100 - (return_rate / return_rate_max * 100))

	# --- Overall Performance Score (weighted) ---
	revenue_weight = flt(target_doc.revenue_weight) / 100
	activity_weight = flt(target_doc.activity_weight) / 100
	quality_weight = flt(target_doc.quality_weight) / 100

	overall_score = (
		revenue_achievement_pct * revenue_weight
		+ activity_achievement_pct * activity_weight
		+ quality_achievement_pct * quality_weight
	)

	# --- Pay Calculation (the core algorithm) ---
	guaranteed_rate = flt(target_doc.guaranteed_hourly_rate)
	target_rate = flt(target_doc.target_hourly_rate)
	superior_rate = flt(target_doc.superior_hourly_rate)
	min_pct = flt(target_doc.minimum_performance_pct)

	if overall_score >= 100:
		effective_rate = superior_rate
	elif overall_score >= min_pct:
		# Linear interpolation between guaranteed and target
		effective_rate = guaranteed_rate + (overall_score - min_pct) / (100 - min_pct) * (
			target_rate - guaranteed_rate
		)
	else:
		effective_rate = guaranteed_rate

	guaranteed_pay = total_hours * guaranteed_rate
	performance_bonus = max(0, total_hours * effective_rate - guaranteed_pay)
	performance_deduction = (
		max(0, guaranteed_pay - total_hours * effective_rate) if overall_score < 100 else 0
	)
	final_pay = total_hours * effective_rate + total_commission

	# --- Create Compensation Calculation record ---
	calc = frappe.new_doc("Compensation Calculation")
	calc.performance_target = target_doc.name
	calc.employee = employee
	calc.employee_name = target_doc.employee_name
	calc.period_type = target_doc.period_type
	calc.period_start = target_doc.period_start
	calc.period_end = target_doc.period_end
	calc.calculation_date = today()
	calc.calculated_by = frappe.session.user

	# Hours
	calc.total_hours_worked = flt(total_hours, 2)
	calc.scheduled_hours = 0  # Would need roster data
	calc.attendance_percentage = 0

	# Revenue Metrics
	calc.revenue_achieved = flt(total_revenue, 2)
	calc.revenue_target = revenue_target
	calc.revenue_achievement_pct = flt(revenue_achievement_pct, 2)
	calc.average_transaction_value = flt(total_revenue / total_transactions, 2) if total_transactions else 0
	calc.high_ticket_sales = 0  # Would need item-level analysis
	calc.layaway_conversions = layaway_count

	# Activity Metrics
	calc.customers_served = total_transactions
	calc.items_sold = total_items
	calc.repair_orders_completed = repair_count
	calc.upsells = 0
	calc.activity_achievement_pct = flt(activity_achievement_pct, 2)

	# Quality Metrics
	calc.return_rate = flt(return_rate, 2)
	calc.customer_satisfaction = 100
	calc.layaway_default_rate = 0
	calc.quality_achievement_pct = flt(quality_achievement_pct, 2)

	# Pay
	calc.overall_performance_score = flt(overall_score, 2)
	calc.effective_hourly_rate = flt(effective_rate, 2)
	calc.guaranteed_pay = flt(guaranteed_pay, 2)
	calc.performance_bonus = flt(performance_bonus, 2)
	calc.performance_deduction = flt(performance_deduction, 2)
	calc.commission_earned = flt(total_commission, 2)
	calc.final_calculated_pay = flt(final_pay, 2)

	calc.insert(ignore_permissions=True)

	return {
		"calculation": calc.name,
		"overall_score": flt(overall_score, 2),
		"effective_hourly_rate": flt(effective_rate, 2),
		"final_pay": flt(final_pay, 2),
		"commission": flt(total_commission, 2),
	}


@frappe.whitelist(methods=["POST"])
def bulk_calculate_compensation(period_start: str, period_end: str) -> dict:
	"""Calculate compensation for all employees with active targets in a period."""
	frappe.only_for(["System Manager", "HR Manager"])

	targets = frappe.get_all(
		"Performance Target",
		filters={
			"docstatus": 1,
			"status": "Active",
			"period_start": ["<=", period_end],
			"period_end": [">=", period_start],
		},
		fields=["employee"],
	)

	results = {"success": [], "errors": []}
	for t in targets:
		try:
			result = run_compensation_calculation(t.employee, period_start, period_end)
			results["success"].append(result)
		except Exception as e:
			results["errors"].append({"employee": t.employee, "error": str(e)})

	return results


# ---------------------------------------------------------------------------
# API: Quarterly Review (Phase 2)
# ---------------------------------------------------------------------------


@frappe.whitelist(methods=["GET"])
def get_quarterly_review(employee: str, quarter: str, year: int) -> dict:
	"""Get quarterly performance review for an employee."""
	frappe.only_for(["System Manager", "HR Manager", "Store Manager", "HR User"])

	review = frappe.get_all(
		"Quarterly Performance Review",
		filters={"employee": employee, "review_period": quarter, "review_year": cint(year)},
		fields=["*"],
		limit=1,
	)
	if not review:
		return {"exists": False}

	review_doc = review[0]
	review_doc["exists"] = True
	return review_doc


@frappe.whitelist(methods=["POST"])
def finalize_review(review_name: str, manager_comments: str | None = None, recommendation: str | None = None):
	"""Finalize a quarterly review with manager input."""
	frappe.only_for(["System Manager", "HR Manager", "Store Manager"])

	if not frappe.db.exists("Quarterly Performance Review", review_name):
		frappe.throw(_("Review not found"))

	doc = frappe.get_doc("Quarterly Performance Review", review_name)
	if manager_comments:
		doc.manager_comments = manager_comments
	if recommendation:
		doc.recommendation = recommendation
	doc.reviewer = frappe.session.user
	doc.status = "Finalized"
	doc.save(ignore_permissions=True)
	doc.submit()

	return {"name": doc.name, "status": "Finalized"}


@frappe.whitelist(methods=["POST"])
def acknowledge_review(review_name: str):
	"""Employee acknowledges their quarterly review."""
	review = frappe.get_doc("Quarterly Performance Review", review_name)

	# Verify the current user is the employee
	employee = _resolve_employee_from_user(frappe.session.user)
	if not employee or employee != review.employee:
		frappe.throw(_("You can only acknowledge your own reviews"))

	review.acknowledged_by_employee = 1
	review.acknowledgment_date = now_datetime()
	review.status = "Acknowledged"
	review.save(ignore_permissions=True)

	return {"name": review.name, "status": "Acknowledged"}


@frappe.whitelist(methods=["GET"])
def get_review_history(employee: str, limit: int = 8) -> list:
	"""Return all quarterly reviews for an employee."""
	frappe.only_for(["System Manager", "HR Manager", "Store Manager", "HR User"])

	return frappe.get_all(
		"Quarterly Performance Review",
		filters={"employee": employee, "docstatus": 1},
		fields=[
			"name",
			"review_period",
			"review_year",
			"overall_score",
			"performance_tier",
			"recommendation",
			"status",
		],
		order_by="review_year desc, review_period desc",
		limit=cint(limit),
	)


@frappe.whitelist(methods=["GET"])
def get_team_review_summary(store_location: str, quarter: str, year: int) -> list:
	"""Aggregate team review summary for a store."""
	frappe.only_for(["System Manager", "HR Manager", "Store Manager"])

	filters = {"review_period": quarter, "review_year": cint(year), "docstatus": 1}

	reviews = frappe.get_all(
		"Quarterly Performance Review",
		filters=filters,
		fields=[
			"employee",
			"employee_name",
			"overall_score",
			"performance_tier",
			"recommendation",
			"quarterly_revenue",
			"attendance_rate",
		],
		order_by="overall_score desc",
	)

	return reviews


# ---------------------------------------------------------------------------
# Scheduler: Generate Quarterly Reviews
# ---------------------------------------------------------------------------


def generate_quarterly_reviews():
	"""Scheduler task: generate quarterly reviews at the start of each quarter.

	Cron: 0 2 1 1,4,7,10 *
	Runs at 2 AM on Jan 1, Apr 1, Jul 1, Oct 1.
	"""
	today_date = getdate(today())

	# Determine the completed quarter
	month = today_date.month
	if month == 1:  # Jan 1 → review Q4 of prev year
		quarter = "Q4"
		year = today_date.year - 1
		q_start = getdate(f"{year}-10-01")
		q_end = getdate(f"{year}-12-31")
	elif month == 4:  # Apr 1 → review Q1
		quarter = "Q1"
		year = today_date.year
		q_start = getdate(f"{year}-01-01")
		q_end = getdate(f"{year}-03-31")
	elif month == 7:  # Jul 1 → review Q2
		quarter = "Q2"
		year = today_date.year
		q_start = getdate(f"{year}-04-01")
		q_end = getdate(f"{year}-06-30")
	elif month == 10:  # Oct 1 → review Q3
		quarter = "Q3"
		year = today_date.year
		q_start = getdate(f"{year}-07-01")
		q_end = getdate(f"{year}-09-30")
	else:
		return  # Not a quarter start month

	# Get all employees who had active targets in this quarter
	employees = frappe.get_all(
		"Performance Target",
		filters={
			"docstatus": 1,
			"period_start": ["<=", q_end],
			"period_end": [">=", q_start],
		},
		fields=["DISTINCT employee as employee"],
	)

	for emp in employees:
		try:
			_create_quarterly_review(emp.employee, quarter, year, q_start, q_end)
		except Exception:
			frappe.log_error(
				title=f"Quarterly Review generation failed for {emp.employee}",
				message=frappe.get_traceback(),
			)

	frappe.db.commit()


def _create_quarterly_review(employee: str, quarter: str, year: int, q_start, q_end):
	"""Generate a single quarterly performance review."""
	# Check if review already exists
	existing = frappe.db.exists(
		"Quarterly Performance Review",
		{"employee": employee, "review_period": quarter, "review_year": year},
	)
	if existing:
		return

	# Aggregate data from Compensation Calculations in this period
	calculations = frappe.get_all(
		"Compensation Calculation",
		filters={
			"employee": employee,
			"period_start": [">=", q_start],
			"period_end": ["<=", q_end],
			"docstatus": 1,
		},
		fields=[
			"overall_performance_score",
			"effective_hourly_rate",
			"final_calculated_pay",
			"commission_earned",
			"revenue_achieved",
			"total_hours_worked",
			"return_rate",
			"attendance_percentage",
		],
	)

	# Aggregate from Performance Logs
	logs = frappe.get_all(
		"Performance Log",
		filters={"employee": employee, "event_date": ["between", [q_start, q_end]]},
		fields=["event_type", "revenue_amount"],
	)

	total_revenue = sum(flt(l.revenue_amount) for l in logs if l.event_type == "Sale Completed")
	total_transactions = sum(1 for l in logs if l.event_type == "Sale Completed")
	avg_transaction = total_revenue / total_transactions if total_transactions else 0

	# Calculate overall score (average of monthly calculations or from logs)
	if calculations:
		avg_score = sum(flt(c.overall_performance_score) for c in calculations) / len(calculations)
		total_hours = sum(flt(c.total_hours_worked) for c in calculations)
		avg_hourly = (
			sum(flt(c.final_calculated_pay) for c in calculations) / total_hours if total_hours else 0
		)
		avg_return_rate = sum(flt(c.return_rate) for c in calculations) / len(calculations)
		avg_attendance = sum(flt(c.attendance_percentage) for c in calculations) / len(calculations)
	else:
		avg_score = 0
		total_hours = 0
		avg_hourly = 0
		avg_return_rate = 0
		avg_attendance = 0

	# Determine performance tier
	if avg_score >= 120:
		tier = "Exceptional"
		recommendation = "Retain & Promote"
	elif avg_score >= 100:
		tier = "Strong"
		recommendation = "Retain & Develop"
	elif avg_score >= 70:
		tier = "Meets Expectations"
		recommendation = "Retain & Develop"
	elif avg_score >= 50:
		tier = "Below Expectations"
		recommendation = "Performance Improvement Plan"
	else:
		tier = "Unsatisfactory"
		recommendation = "Counsel Out"

	# Get previous quarter score for QoQ change
	prev_quarter_map = {"Q1": ("Q4", year - 1), "Q2": ("Q1", year), "Q3": ("Q2", year), "Q4": ("Q3", year)}
	prev_q, prev_y = prev_quarter_map.get(quarter, ("Q1", year))
	prev_review = frappe.get_all(
		"Quarterly Performance Review",
		filters={"employee": employee, "review_period": prev_q, "review_year": prev_y},
		fields=["overall_score"],
		limit=1,
	)
	qoq_change = None
	if prev_review:
		qoq_change = flt(avg_score - flt(prev_review[0].overall_score), 2)

	# Generate strengths/weaknesses text
	strengths, improvements = _generate_review_insights(
		employee,
		avg_score,
		total_revenue,
		avg_transaction,
		avg_return_rate,
		avg_attendance,
		total_transactions,
	)

	# Create the review
	review = frappe.new_doc("Quarterly Performance Review")
	review.employee = employee
	review.employee_name = frappe.db.get_value("Employee", employee, "employee_name")
	review.review_period = quarter
	review.review_year = year
	review.review_date = today()
	review.status = "Generated"

	# Performance Summary
	review.overall_score = flt(avg_score, 2)
	review.performance_tier = tier
	review.qoq_change = qoq_change
	review.revenue_score = flt(avg_score, 2)  # Simplified — could compute separately
	review.activity_score = 0
	review.quality_score = 0

	# Revenue Summary
	review.quarterly_revenue = flt(total_revenue, 2)
	review.quarterly_target = 0
	review.revenue_achievement_pct = 0
	review.avg_transaction_value = flt(avg_transaction, 2)
	review.total_transactions = total_transactions

	# Behavioral
	review.attendance_rate = flt(avg_attendance, 2)
	review.punctuality_score = 0
	review.average_hours_per_week = flt(total_hours / 13, 2) if total_hours else 0

	# Intelligence
	review.auto_identified_strengths = strengths
	review.auto_identified_improvements = improvements
	review.recommendation = recommendation
	review.recommendation_rationale = f"Based on overall performance score of {avg_score:.1f}%"

	# Compensation Impact
	review.current_hourly_rate = flt(avg_hourly, 2)

	review.insert(ignore_permissions=True)


def _generate_review_insights(
	employee, score, revenue, avg_transaction, return_rate, attendance, transactions
):
	"""Generate data-driven strengths and improvements text."""
	strengths_parts = []
	improvements_parts = []

	if score >= 100:
		strengths_parts.append(
			f"Consistently exceeds performance targets with an overall score of {score:.1f}%."
		)
	elif score >= 80:
		strengths_parts.append(f"Strong performer at {score:.1f}% of target.")
	elif score < 60:
		improvements_parts.append(
			f"Overall performance at {score:.1f}% is below the minimum threshold of 60%."
		)

	if revenue > 0:
		strengths_parts.append(f"Generated ${revenue:,.2f} in revenue this quarter.")

	if avg_transaction > 0:
		strengths_parts.append(f"Average transaction value of ${avg_transaction:,.2f}.")

	if return_rate > 5:
		improvements_parts.append(
			f"Return rate of {return_rate:.1f}% is above the 5% target — focus on customer needs assessment."
		)

	if attendance < 90:
		improvements_parts.append(f"Attendance rate of {attendance:.1f}% needs improvement.")

	if transactions > 0 and transactions < 30:
		improvements_parts.append(
			f"Only {transactions} transactions completed — consider increasing customer engagement."
		)

	if not improvements_parts:
		improvements_parts.append("Continue developing product knowledge and upselling skills.")

	strengths = (
		"\n".join(f"- {s}" for s in strengths_parts) if strengths_parts else "- Meets baseline expectations."
	)
	improvements = "\n".join(f"- {s}" for s in improvements_parts)

	return strengths, improvements
