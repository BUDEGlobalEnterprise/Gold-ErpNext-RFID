# Copyright (c) 2026, Zevar Core and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def check_overdue_repairs():
	"""Check for overdue repairs and send notifications.

	This function is called hourly by the Frappe scheduler.
	It checks for repairs that are past their promised date but not yet delivered.
	"""
	# Get all active repairs (not delivered or cancelled)
	# that have a promised_date in the past
	from frappe.utils import add_days, getdate, nowdate

	today = getdate(nowdate())

	# Find repairs that are:
	# 1. Not Delivered or Cancelled
	# 2. Have a promised_date
	# 3. promised_date is in the past
	# 4. Haven't had an overdue notification sent in the last 24 hours
	overdue_repairs = frappe.get_all(
		"Repair Order",
		filters={
			"status": ["not in", ["Delivered", "Cancelled"]],
			"promised_date": ["<", today],
		},
		fields=["name", "customer", "customer_phone", "promised_date", "status"],
	)

	if not overdue_repairs:
		return

	# Check if we've already sent an overdue notification recently
	# (to avoid spamming customers multiple times a day)
	one_day_ago = add_days(today, -1)

	for repair in overdue_repairs:
		try:
			# Check if an overdue notification was sent recently
			recent_overdue = frappe.db.exists(
				"Repair Communication",
				{
					"parent": repair["name"],
					"parenttype": "Repair Order",
					"parentfield": "communications",
					"communication_type": ["in", ["SMS", "Email"]],
					"content": ["like", "%overdue%"],
					"timestamp": [">", one_day_ago],
				},
			)

			if recent_overdue:
				# Already notified recently, skip
				continue

			# Send overdue notification
			doc = frappe.get_doc("Repair Order", repair["name"])
			doc._send_overdue_notification()

			frappe.logger().info(f"Sent overdue notification for repair {repair['name']}")

		except Exception as e:
			frappe.log_error(
				f"Failed to send overdue notification for {repair['name']}: {e}",
				"Overdue Repair Notification Error",
			)

	return len(overdue_repairs) if overdue_repairs else 0
