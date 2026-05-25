"""
Employee Live Monitor API — Personalized real-time view for each employee.

Strict user-scoping: employees can only see their own data plus
store-level anonymized aggregates. No cross-employee data exposed.
"""

import frappe
from frappe import _
from frappe.utils import flt, cint, getdate, nowdate, add_days, now_datetime


def _get_current_employee():
	"""Map session user to Employee record. Returns employee doc name or None."""
	user = frappe.session.user
	emp = frappe.db.get_value("Employee", {"user_id": user, "status": "Active"}, "name")
	return emp


@frappe.whitelist()
def get_my_performance():
	"""Current employee's sales metrics for today: revenue, items, vs yesterday."""
	emp = _get_current_employee()
	if not emp:
		frappe.throw(_("No active employee record found for your user."))

	today = nowdate()
	yesterday = add_days(today, -1)

	# Today's revenue via commission splits
	today_data = frappe.db.sql(
		"""SELECT
			COALESCE(SUM(scs.allocated_amount), 0) AS revenue,
			COUNT(DISTINCT scs.sales_invoice) AS txn_count
		FROM `tabSales Commission Split` scs
		JOIN `tabSales Invoice` si ON scs.sales_invoice = si.name
		WHERE scs.employee = %s AND si.docstatus = 1 AND si.is_pos = 1
		AND si.posting_date = %s""",
		(emp, today),
		as_dict=True,
	)
	t = today_data[0] if today_data else {}

	# Yesterday's revenue for comparison
	yest_data = frappe.db.sql(
		"""SELECT
			COALESCE(SUM(scs.allocated_amount), 0) AS revenue
		FROM `tabSales Commission Split` scs
		JOIN `tabSales Invoice` si ON scs.sales_invoice = si.name
		WHERE scs.employee = %s AND si.docstatus = 1 AND si.is_pos = 1
		AND si.posting_date = %s""",
		(emp, yesterday),
		as_dict=True,
	)
	y = yest_data[0] if yest_data else {}
	yest_rev = flt(y.get("revenue", 0))

	today_rev = flt(t.get("revenue", 0))
	change_pct = ((today_rev - yest_rev) / yest_rev * 100) if yest_rev else 0

	# Items sold today
	items_sold = cint(frappe.db.sql(
		"""SELECT COALESCE(SUM(sii.qty), 0)
		FROM `tabSales Commission Split` scs
		JOIN `tabSales Invoice` si ON scs.sales_invoice = si.name
		JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
		WHERE scs.employee = %s AND si.docstatus = 1 AND si.is_pos = 1
		AND si.posting_date = %s""",
		(emp, today),
	)[0][0])

	# Active POS session
	active_session = frappe.db.get_value(
		"POS Opening Entry",
		filters={"user": frappe.session.user, "status": "Open"},
		fieldname="name",
	)

	# Employee info
	emp_name = frappe.db.get_value("Employee", emp, "employee_name") or ""

	return {
		"employee": emp,
		"employee_name": emp_name,
		"today_revenue": today_rev,
		"txn_count": cint(t.get("txn_count", 0)),
		"items_sold": items_sold,
		"yesterday_revenue": yest_rev,
		"change_pct": flt(change_pct, 1),
		"has_active_session": bool(active_session),
	}


@frappe.whitelist()
def get_store_activity(hours=4):
	"""Store-level activity feed — anonymized for employee visibility.

	Returns transaction counts and item counts by hour, NOT individual
	customer data or amounts (employees don't see other employees' sales).
	"""
	frappe.has_permission("Sales Invoice", ptype="read", throw=True)

	today = nowdate()

	# Hourly transaction distribution (counts only, no amounts)
	rows = frappe.db.sql(
		"""SELECT
			HOUR(si.posting_time) AS hour,
			COUNT(*) AS txn_count,
			SUM(sii.qty) AS items_sold
		FROM `tabSales Invoice` si
		JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
		WHERE si.docstatus = 1 AND si.is_pos = 1
		AND si.posting_date = %s AND si.posting_time IS NOT NULL
		GROUP BY hour
		ORDER BY hour""",
		(today,),
		as_dict=True,
	)

	hour_map = {r.hour: r for r in rows}
	result = []
	for h in range(9, 21):
		r = hour_map.get(h, {})
		result.append({
			"hour": h,
			"label": _fmt_hour(h),
			"txn_count": cint(r.get("txn_count", 0)),
			"items_sold": cint(r.get("items_sold", 0)),
		})

	# Recent activity (last N hours, anonymized)
	hours_ago = frappe.utils.add_to_date(now_datetime(), hours=-int(hours))
	recent = frappe.db.sql(
		"""SELECT
			si.name,
			si.posting_time,
			si.posting_date,
			COALESCE(si.custom_transaction_stream, 'Sale') AS stream,
			(SELECT COUNT(*) FROM `tabSales Invoice Item` WHERE parent = si.name) AS item_count
		FROM `tabSales Invoice` si
		WHERE si.docstatus = 1 AND si.is_pos = 1
		AND si.creation >= %s
		ORDER BY si.creation DESC
		LIMIT 30""",
		(str(hours_ago),),
		as_dict=True,
	)

	# Anonymize: remove invoice name, keep only time and counts
	feed = []
	for r in recent:
		ts = r.posting_time
		if hasattr(ts, "strftime"):
			ts = ts.strftime("%I:%M %p")
		feed.append({
			"time": str(ts) if ts else "",
			"stream": r.stream,
			"item_count": cint(r.item_count),
		})

	return {
		"hourly": result,
		"recent_feed": feed,
		"store_txn_count_today": sum(r.txn_count for r in result),
	}


@frappe.whitelist()
def get_my_tasks():
	"""Get tasks assigned to the current employee: pending repairs and layaway follow-ups."""
	emp = _get_current_employee()
	if not emp:
		frappe.throw(_("No active employee record found for your user."))

	today = nowdate()

	# Assigned repairs
	repairs = frappe.db.sql(
		"""SELECT
			ro.name,
			ro.customer_name,
			ro.repair_type_name,
			ro.status,
			ro.promised_date,
			DATEDIFF(%(today)s, ro.promised_date) AS days_overdue
		FROM `tabRepair Order` ro
		WHERE ro.assigned_to = %(emp)s
		AND ro.status NOT IN ('Delivered', 'Cancelled')
		ORDER BY
			CASE WHEN ro.promised_date < %(today)s THEN 0 ELSE 1 END,
			ro.promised_date ASC
		LIMIT 20""",
		{"today": today, "emp": emp},
		as_dict=True,
	)

	# Layaway follow-ups due (deposits needed, payments overdue)
	layaways = frappe.db.sql(
		"""SELECT
			si.name,
			si.customer,
			si.customer_name,
			si.outstanding_amount,
			si.due_date,
			DATEDIFF(%(today)s, si.due_date) AS days_overdue
		FROM `tabSales Invoice` si
		WHERE si.docstatus = 1
		AND si.custom_transaction_stream = 'Layaway Deposit'
		AND si.outstanding_amount > 0
		AND si.sales_partner = %(emp)s
		ORDER BY si.due_date ASC
		LIMIT 10""",
		{"today": today, "emp": emp},
		as_dict=True,
	)

	# Personal todos
	todos = frappe.db.sql(
		"""SELECT name, description, status, priority, date
		FROM `tabToDo`
		WHERE allocated_to = %(user)s AND status = 'Open'
		ORDER BY
			CASE priority WHEN 'High' THEN 0 WHEN 'Medium' THEN 1 ELSE 2 END,
			date ASC
		LIMIT 10""",
		{"user": frappe.session.user},
		as_dict=True,
	)

	# Repair queue summary
	queue = frappe.db.sql(
		"""SELECT
			status,
			COUNT(*) AS cnt,
			AVG(DATEDIFF(%(today)s, creation)) AS avg_age_days
		FROM `tabRepair Order`
		WHERE assigned_to = %(emp)s
		AND status NOT IN ('Delivered', 'Cancelled')
		GROUP BY status""",
		{"today": today, "emp": emp},
		as_dict=True,
	)

	return {
		"repairs": repairs,
		"layaways": layaways,
		"todos": todos,
		"queue_summary": queue,
		"pending_count": len(repairs) + len(layaways) + len(todos),
	}


@frappe.whitelist()
def get_employee_dashboard():
	"""Single-call payload for the Employee Live Monitor page."""
	return {
		"performance": get_my_performance(),
		"store": get_store_activity(),
		"tasks": get_my_tasks(),
	}


def _fmt_hour(h):
	if h == 0:
		return "12a"
	if h < 12:
		return f"{h}a"
	if h == 12:
		return "12p"
	return f"{h - 12}p"
