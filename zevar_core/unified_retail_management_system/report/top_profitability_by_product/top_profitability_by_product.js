frappe.query_reports["Top Profitability by Product"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
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
			fieldname: "jewelry_type",
			label: __("Jewelry Type"),
			fieldtype: "Data",
		},
		{
			fieldname: "limit",
			label: __("Limit"),
			fieldtype: "Int",
			default: 20,
		},
	],
};
