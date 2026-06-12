// Copyright (c) 2026, Zevar and contributors
// For license information, please see license.txt

frappe.ui.form.on("Performance Target", {
	refresh(frm) {
		// Show status indicator
		if (frm.doc.docstatus === 1 && frm.doc.status === "Active") {
			frm.dashboard.add_comment("Active Target", "green", true);
		}
	},

	employee(frm) {
		if (frm.doc.employee) {
			frappe.db
				.get_value("Employee", frm.doc.employee, ["employee_name", "designation"])
				.then((r) => {
					if (r && r.message) {
						frm.set_value("employee_name", r.message.employee_name);
						frm.set_value("designation", r.message.designation);
					}
				});
		}
	},

	period_type(frm) {
		// Auto-set period dates based on period type
		if (!frm.doc.period_type || frm.doc.period_start) return;

		const today = frappe.datetime.nowdate();
		let start, end;

		if (frm.doc.period_type === "Weekly") {
			start = frappe.datetime.nowdate();
			end = frappe.datetime.add_days(start, 6);
		} else if (frm.doc.period_type === "Monthly") {
			start = frappe.datetime.nowdate();
			end = frappe.datetime.add_months(start, 1);
			end = frappe.datetime.add_days(end, -1);
		} else if (frm.doc.period_type === "Quarterly") {
			start = frappe.datetime.nowdate();
			end = frappe.datetime.add_months(start, 3);
			end = frappe.datetime.add_days(end, -1);
		} else if (frm.doc.period_type === "Annually") {
			start = frappe.datetime.nowdate();
			end = frappe.datetime.add_months(start, 12);
			end = frappe.datetime.add_days(end, -1);
		}

		if (start && end) {
			frm.set_value("period_start", start);
			frm.set_value("period_end", end);
		}
	},
});
