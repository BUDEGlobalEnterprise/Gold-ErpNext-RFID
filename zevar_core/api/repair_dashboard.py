# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import add_days, flt, getdate, today


@frappe.whitelist()
def get_repair_dashboard_stats(warehouse: str | None = None):
	"""
	Get repair dashboard statistics for POS terminal.
	Returns widget data for:
	- Overdue repairs count
	- Today's pickups scheduled
	- Revenue this week/month
	- Average turnaround time
	- Technician workload distribution
	"""
	today_date = today()
	week_start = add_days(today_date, -7)
	month_start = today_date[:7] + "-01"  # First day of current month

	conditions = ""
	values = {}
	if warehouse:
		conditions = "AND warehouse = %(warehouse)s"
		values["warehouse"] = warehouse

	stats = {}

	# 1. Overdue repairs count
	stats["overdue_count"] = frappe.db.sql(  # nosemgrep
		f"""
		SELECT COUNT(*) as count
		FROM `tabRepair Order`
		WHERE docstatus < 2
			AND promised_date < %(today)s
			AND status NOT IN ('Delivered', 'Cancelled')
			{conditions}
		""",
		values={**values, "today": today_date},
		as_dict=True,
	)[0].count

	# 2. Today's pickups (Ready for Pickup)
	stats["ready_pickup_count"] = frappe.db.sql(  # nosemgrep
		f"""
		SELECT COUNT(*) as count
		FROM `tabRepair Order`
		WHERE docstatus < 2
			AND status = 'Ready for Pickup'
			{conditions}
		""",
		values=values,
		as_dict=True,
	)[0].count

	# 3. Revenue this week
	weekly_revenue = (
		frappe.db.sql(  # nosemgrep
			f"""
		SELECT SUM(total_cost) as revenue
		FROM `tabRepair Order`
		WHERE docstatus < 2
			AND received_date >= %(week_start)s
			AND received_date <= %(today)s
			{conditions}
		""",
			values={**values, "week_start": week_start, "today": today_date},
			as_dict=True,
		)[0].revenue
		or 0
	)
	stats["weekly_revenue"] = flt(weekly_revenue, 2)

	# 4. Revenue this month
	monthly_revenue = (
		frappe.db.sql(  # nosemgrep
			f"""
		SELECT SUM(total_cost) as revenue
		FROM `tabRepair Order`
		WHERE docstatus < 2
			AND received_date >= %(month_start)s
			AND received_date <= %(today)s
			{conditions}
		""",
			values={**values, "month_start": month_start, "today": today_date},
			as_dict=True,
		)[0].revenue
		or 0
	)
	stats["monthly_revenue"] = flt(monthly_revenue, 2)

	# 5. Average turnaround time (for delivered repairs in last 30 days)
	avg_turnaround = (
		frappe.db.sql(  # nosemgrep
			f"""
		SELECT AVG(TIMESTAMPDIFF(HOUR, received_date, delivered_date) / 24) as avg_days
		FROM `tabRepair Order`
		WHERE docstatus < 2
			AND status = 'Delivered'
			AND delivered_date IS NOT NULL
			AND received_date >= DATE_SUB(%(today)s, INTERVAL 30 DAY)
			{conditions}
		""",
			values={**values, "today": today_date},
			as_dict=True,
		)[0].avg_days
		or 0
	)
	stats["avg_turnaround_days"] = flt(avg_turnaround, 1) if avg_turnaround else 0

	# 6. Active repairs by status
	status_breakdown = frappe.db.sql(  # nosemgrep
		f"""
		SELECT status, COUNT(*) as count
		FROM `tabRepair Order`
		WHERE docstatus < 2
			AND status NOT IN ('Delivered', 'Cancelled')
			{conditions}
		GROUP BY status
		ORDER BY count DESC
		""",
		values=values,
		as_dict=True,
	)
	stats["status_breakdown"] = {row.status: row.count for row in status_breakdown}

	# 7. Technician workload
	technician_workload = frappe.db.sql(  # nosemgrep
		f"""
		SELECT
			assigned_to,
			COUNT(*) as count,
			SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress
		FROM `tabRepair Order`
		WHERE docstatus < 2
			AND assigned_to IS NOT NULL
			AND status NOT IN ('Delivered', 'Cancelled')
			{conditions}
		GROUP BY assigned_to
		ORDER BY count DESC
		LIMIT 5
		""",
		values=values,
		as_dict=True,
	)
	stats["technician_workload"] = technician_workload

	# 8. Recent overdue repairs (top 5)
	stats["recent_overdue"] = frappe.db.sql(  # nosemgrep
		f"""
		SELECT
			name,
			customer,
			promised_date,
			DATEDIFF(%(today)s, promised_date) as days_overdue,
			status,
			priority
		FROM `tabRepair Order`
		WHERE docstatus < 2
			AND promised_date < %(today)s
			AND status NOT IN ('Delivered', 'Cancelled')
			{conditions}
		ORDER BY promised_date ASC
		LIMIT 5
		""",
		values={**values, "today": today_date},
		as_dict=True,
	)

	# 9. Top repair types this month
	top_repair_types = frappe.db.sql(  # nosemgrep
		f"""
		SELECT
			repair_type,
			COUNT(*) as count
		FROM `tabRepair Order`
		WHERE docstatus < 2
			AND received_date >= %(month_start)s
			{conditions}
		GROUP BY repair_type
		ORDER BY count DESC
		LIMIT 5
		""",
		values={**values, "month_start": month_start},
		as_dict=True,
	)
	stats["top_repair_types"] = top_repair_types

	# 10. Pending collections (balance due)
	pending_collections = frappe.db.sql(  # nosemgrep
		f"""
		SELECT
			SUM(balance_due) as total_pending,
			COUNT(*) as count
		FROM `tabRepair Order`
		WHERE docstatus < 2
			AND status IN ('Ready for Pickup', 'Delivered')
			AND balance_due > 0
			{conditions}
		""",
		values=values,
		as_dict=True,
	)[0]
	stats["pending_collections_amount"] = flt(pending_collections.total_pending or 0, 2)
	stats["pending_collections_count"] = pending_collections.count or 0

	return stats


@frappe.whitelist()
def get_repair_chart_data(warehouse: str | None = None, period: int = 30):
	"""
	Get repair chart data for dashboard visualization.
	Returns data for:
	- Repairs by day (last N days)
	- Repairs by type
	- Revenue trend
	"""
	from datetime import timedelta

	from frappe.utils import add_days

	today_date = getdate(today())
	from_date = add_days(today_date, -(period - 1))

	conditions = ""
	values = {"from_date": from_date, "to_date": today_date}
	if warehouse:
		conditions = "AND warehouse = %(warehouse)s"
		values["warehouse"] = warehouse

	# Daily repair counts
	daily_data = frappe.db.sql(  # nosemgrep
		f"""
		SELECT
			DATE(received_date) as date,
			COUNT(*) as count
		FROM `tabRepair Order`
		WHERE docstatus < 2
			AND received_date >= %(from_date)s
			AND received_date <= %(to_date)s
			{conditions}
		GROUP BY DATE(received_date)
		ORDER BY date
		""",
		values=values,
		as_dict=True,
	)

	# Fill in missing dates with 0
	daily_dict = {row.date: row.count for row in daily_data}
	labels = []
	values_list = []
	current = from_date
	while current <= today_date:
		labels.append(current.strftime("%m-%d"))
		values_list.append(daily_dict.get(current, 0))
		current = add_days(current, 1)

	chart_data = {
		"daily_repairs": {
			"labels": labels,
			"values": values_list,
		}
	}

	# Repairs by status
	status_data = frappe.db.sql(  # nosemgrep
		f"""
		SELECT
			status,
			COUNT(*) as count
		FROM `tabRepair Order`
		WHERE docstatus < 2
			AND received_date >= %(from_date)s
			AND received_date <= %(to_date)s
			{conditions}
		GROUP BY status
		ORDER BY count DESC
		""",
		values=values,
		as_dict=True,
	)

	chart_data["by_status"] = {
		"labels": [row.status for row in status_data],
		"values": [row.count for row in status_data],
	}

	# Revenue trend
	revenue_data = frappe.db.sql(  # nosemgrep
		f"""
		SELECT
			DATE(received_date) as date,
			SUM(total_cost) as revenue
		FROM `tabRepair Order`
		WHERE docstatus < 2
			AND received_date >= %(from_date)s
			AND received_date <= %(to_date)s
			{conditions}
		GROUP BY DATE(received_date)
		ORDER BY date
		""",
		values=values,
		as_dict=True,
	)

	revenue_dict = {row.date: flt(row.revenue, 2) for row in revenue_data}
	revenue_values = []
	current = from_date
	while current <= today_date:
		revenue_values.append(revenue_dict.get(current, 0))
		current = add_days(current, 1)

	chart_data["revenue_trend"] = {
		"labels": labels,
		"values": revenue_values,
	}

	return chart_data
