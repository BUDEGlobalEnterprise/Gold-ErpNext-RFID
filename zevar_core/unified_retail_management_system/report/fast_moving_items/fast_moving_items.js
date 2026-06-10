frappe.query_fields = [
	{ fieldtype: "Date", label: "From Date", fieldname: "from_date" },
	{ fieldtype: "Date", label: "To Date", fieldname: "to_date" },
	{ fieldtype: "Link", options: "Warehouse", label: "Warehouse", fieldname: "warehouse" },
	{ fieldtype: "Data", label: "Jewelry Type", fieldname: "jewelry_type" },
	{ fieldtype: "Int", label: "Limit", fieldname: "limit", default: 50 },
];
