frappe.query_fields = [
	{ fieldtype: "Date", label: "As of Date", fieldname: "as_of_date" },
	{ fieldtype: "Link", options: "Warehouse", label: "Warehouse", fieldname: "warehouse" },
	{ fieldtype: "Link", options: "Item Group", label: "Item Group", fieldname: "item_group" },
	{ fieldtype: "Data", label: "Metal Type", fieldname: "metal_type" },
	{ fieldtype: "Int", label: "Max Days on Hand", fieldname: "max_days" },
];
