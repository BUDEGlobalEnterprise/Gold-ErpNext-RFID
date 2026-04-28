frappe.query_reports["Payment Method Summary"] = {
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
			fieldname: "mode_of_payment",
			label: __("Mode of Payment"),
			fieldtype: "Link",
			options: "Mode of Payment",
		},
		{
			fieldname: "pos_profile",
			label: __("POS Profile"),
			fieldtype: "Link",
			options: "POS Profile",
		},
		{
			fieldname: "transaction_stream",
			label: __("Transaction Stream"),
			fieldtype: "MultiSelectList",
			get_data: function () {
				return [
					{ value: "Jewelry Sale", description: "Jewelry Sale" },
					{ value: "Repair", description: "Repair" },
					{ value: "Layaway Deposit", description: "Layaway Deposit" },
					{ value: "Layaway Final", description: "Layaway Final" },
				];
			},
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
		},
	],
};
