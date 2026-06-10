frappe.query_fields = [
	{ fieldtype: "Date", label: "As of Date", fieldname: "as_of_date" },
	{ fieldtype: "Int", label: "Min Days Since Sale", fieldname: "min_days", default: 90 },
	{ fieldtype: "Link", options: "Warehouse", label: "Warehouse", fieldname: "warehouse" },
	{ fieldtype: "Link", options: "Item Group", label: "Item Group", fieldname: "item_group" },
];
