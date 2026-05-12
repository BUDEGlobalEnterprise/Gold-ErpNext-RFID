frappe.query_reports["COGS Trend"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -3),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "granularity",
			label: __("Granularity"),
			fieldtype: "Select",
			options: "Daily\nWeekly\nMonthly",
			default: "Monthly",
			reqd: 1,
		},
	],
};
