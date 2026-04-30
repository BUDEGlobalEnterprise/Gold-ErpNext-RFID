import frappe


def execute():
	serials = frappe.get_all(
		"Serial No",
		filters={"custom_last_seen_at": ["is", "not set"]},
		fields=["name"],
		limit=5000,
	)

	for s in serials:
		last_sle = frappe.db.get_value(
			"Stock Ledger Entry",
			{"serial_no": s.name},
			["posting_date", "posting_time"],
			order_by="creation desc",
			as_dict=True,
		)
		if last_sle:
			last_seen = f"{last_sle.posting_date} {last_sle.posting_time}"
			frappe.db.set_value(
				"Serial No",
				s.name,
				"custom_last_seen_at",
				last_seen,
				update_modified=False,
			)
