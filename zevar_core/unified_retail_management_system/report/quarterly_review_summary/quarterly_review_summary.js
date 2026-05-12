// Copyright (c) 2026, Zevar and contributors
// For license information, please see license.txt

frappe.query_reports["Quarterly Review Summary"] = {
	filters: [
		{
			fieldname: "review_period",
			label: __("Review Period"),
			fieldtype: "Select",
			options: "Q1\nQ2\nQ3\nQ4",
			default: function () {
				const month = frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth();
				if (month <= 2) return "Q1";
				if (month <= 5) return "Q2";
				if (month <= 8) return "Q3";
				return "Q4";
			},
			reqd: 1,
		},
		{
			fieldname: "review_year",
			label: __("Review Year"),
			fieldtype: "Int",
			default: function () {
				return frappe.datetime.str_to_obj(frappe.datetime.get_today()).getFullYear();
			},
			reqd: 1,
		},
	],
};
