# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

# Daily Store Sales Rollup is a materialized aggregate (one row per
# date x store x salesperson x category x metal) rebuilt nightly and on demand
# by sales_monitor.rebuild_daily_rollup for sub-100ms dashboard queries.


from frappe.model.document import Document


class DailyStoreSalesRollup(Document):
	pass
