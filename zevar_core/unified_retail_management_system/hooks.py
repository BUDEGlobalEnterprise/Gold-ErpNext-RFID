# Copyright (c) 2026, Zevar Core and contributors
# For license information, please see license.txt

from . import __version__

app_name = "unified_retail_management_system"
app_title = "Unified Retail Management System"
app_publisher = "Arijentek Solutions"
app_description = "Integrated retail management for jewelry stores"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@arijentek.com"
app_license = "Proprietary"

# Includes in <head>
# include_js = assets/js/repair_order.js
# include_css = assets/css/repair_order.css

# Home Page
# home_page = "repair-orders"

# Website Generators
# website_generators = ["Website Generator"]

# Scheduler Events (hourly, daily, weekly, monthly)
scheduler_events = {
	"hourly": [
		"unified_retail_management_system.scheduler_tasks.check_overdue_repairs",
	],
}

# DocType Events
# doc_events = {
# 	"Repair Order": {"on_update": "unified_retail_management_system.doctype.repair_order.repair_order.on_update"},
# }
