// Copyright (c) 2026, Zevar and contributors
// For license information, please see license.txt

frappe.query_reports["Performance Target Progress"] = {
	filters: [
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
		},
		{
			fieldname: "store_location",
			label: __("Store Location"),
			fieldtype: "Link",
			options: "Store Location",
		},
	],
};
