// Copyright (c) 2026, Zevar Core and contributors
// For license information, please see license.txt

frappe.ui.form.on("Repair Order", {
	setup(frm) {
		frm._repair_previous_status = frm.doc.status || "Draft";
	},

	refresh: function(frm) {
		// Show/hide Parts section based on status
		frm.trigger("show_hide_parts_section");

		// Show/hide After Photos based on status
		frm.trigger("show_hide_after_photos");

		// Add custom button to fetch customer phone
		if (!frm.doc.customer_phone && frm.doc.customer) {
			frm.add_custom_button(__("Fetch Customer Phone"), function() {
				frm.trigger("fetch_customer_phone");
			}, __("Actions"));
		}

		// Add status validation warning for improper transitions
		if (frm.doc.docstatus === 0) {
			let message = frm.trigger("get_status_transition_warning");
			if (message) {
				frm.dashboard.add_warning(message);
			}
		}

		// Show metal weight difference info if non-zero
		if (frm.doc.metal_weight_difference && Math.abs(frm.doc.metal_weight_difference) > 0.01) {
			let diff = frm.doc.metal_weight_difference;
			let message = diff > 0
				? __("Metal added: {0}g", [diff.toFixed(2)])
				: __("Metal lost: {0}g", [Math.abs(diff).toFixed(2)]);
			frm.dashboard.add_indicator(message, diff > 0 ? "blue" : "orange");
		}

		// Show total stone weight
		if (frm.doc.stone_weight && frm.doc.stone_weight > 0) {
			frm.dashboard.add_indicator(__("Total Stones: {0} ct", [frm.doc.stone_weight.toFixed(2)]), "green");
		}
	},

	customer: function(frm) {
		// When customer is selected, fetch phone and auto-populate
		if (frm.doc.customer) {
			frm.trigger("fetch_customer_phone");
		}
	},

	repair_type: function(frm) {
		// Auto-set promised_date based on Repair Type's estimated_days
		if (frm.doc.repair_type) {
			frm.trigger("set_promised_date_from_type");
		}
	},

	status: function(frm) {
		// Show/hide Parts section based on status
		frm.trigger("show_hide_parts_section");

		// Show/hide After Photos based on status
		frm.trigger("show_hide_after_photos");

		// Validate status transitions
		if (frm.doc.status) {
			let warning = frm.trigger("get_status_transition_warning");
			if (warning) {
				frappe.msgprint({
					title: __("Status Transition Warning"),
					message: warning,
					indicator: "orange"
				});
			}
		}
	},

	// Metal weight calculation handlers
	metal_weight_in: function(frm) {
		frm.trigger("calculate_metal_difference");
	},

	metal_weight_out: function(frm) {
		frm.trigger("calculate_metal_difference");
	},

	metal_scrap: function(frm) {
		frm.trigger("calculate_metal_difference");
	},

	calculate_metal_difference: function(frm) {
		let weight_in = flt(frm.doc.metal_weight_in) || 0;
		let weight_out = flt(frm.doc.metal_weight_out) || 0;
		let scrap = flt(frm.doc.metal_scrap) || 0;

		// Net difference: (Weight Out + Scrap) - Weight In
		let difference = (weight_out + scrap) - weight_in;
		frm.set_value("metal_weight_difference", difference);
	},

	fetch_customer_phone: function(frm) {
		if (!frm.doc.customer) return;

		frappe.db.get_value("Customer", frm.doc.customer, "mobile_no")
			.then(r => {
				if (r.message && r.message.mobile_no) {
					frm.set_value("customer_phone", r.message.mobile_no);
				}
			});
	},

	set_promised_date_from_type: function(frm) {
		if (!frm.doc.repair_type) return;

		frappe.db.get_value("Repair Type", frm.doc.repair_type, "estimated_days")
			.then(r => {
				if (r.message && r.message.estimated_days) {
					// Calculate promised date from received_date + estimated_days
					let received_date = frm.doc.received_date || new Date();
					let promised_date = frappe.datetime.add_days(received_date, r.message.estimated_days);
					frm.set_value("promised_date", promised_date);
				}
			});
	},

	show_hide_parts_section: function(frm) {
		// Only show Parts section when Approved or later status
		let show_parts_statuses = ["Approved", "In Progress", "Waiting for Parts", "Quality Check", "Ready for Pickup", "Delivered"];
		let should_show = show_parts_statuses.includes(frm.doc.status);

		frm.toggle_display("section_parts", should_show);
		frm.toggle_display("parts", should_show);
	},

	show_hide_after_photos: function(frm) {
		// Only show After Photos when repair is complete or ready
		let show_photo_statuses = ["Quality Check", "Ready for Pickup", "Delivered"];
		let should_show = show_photo_statuses.includes(frm.doc.status);

		frm.toggle_display("after_photos", should_show);
	},

	get_status_transition_warning: function(frm) {
		// Define valid status transitions
		let valid_transitions = {
			"Draft": ["Received", "Cancelled"],
			"Received": ["Estimated", "In Progress", "Cancelled"],
			"Estimated": ["Approved", "Cancelled"],
			"Approved": ["In Progress", "Cancelled"],
			"In Progress": ["Waiting for Parts", "Quality Check", "Ready for Pickup", "Cancelled"],
			"Waiting for Parts": ["In Progress", "Quality Check", "Ready for Pickup", "Cancelled"],
			"Quality Check": ["Ready for Pickup", "In Progress", "Cancelled"],
			"Ready for Pickup": ["Delivered", "Quality Check"],
			"Delivered": [],
			"Cancelled": []
		};

		let current_status = frm.doc.status;
		let previous_status = frm._repair_previous_status || "Draft";

		if (valid_transitions[previous_status]) {
			if (!valid_transitions[previous_status].includes(current_status)) {
				return __("Warning: Status transition from '{0}' to '{1}' may not be valid. Valid transitions are: {2}",
					[previous_status, current_status, valid_transitions[previous_status].join(", ")]);
			}
		}
		return null;
	},

	after_save(frm) {
		frm._repair_previous_status = frm.doc.status || "Draft";
	}
});

frappe.ui.form.on("Repair Order", {
	gemstones_add: function(frm) {
		frm.trigger("calculate_total_stone_weight");
	},

	gemstones_remove: function(frm) {
		frm.trigger("calculate_total_stone_weight");
	},

	calculate_total_stone_weight: function(frm) {
		if (!frm.doc.gemstones || frm.doc.gemstones.length === 0) {
			frm.set_value("stone_weight", 0);
			return;
		}

		let total_carats = 0;
		frm.doc.gemstones.forEach(function(row) {
			total_carats += flt(row.carat_weight) || 0;
		});

		frm.set_value("stone_weight", total_carats);
	}
});

frappe.ui.form.on("Repair Gemstone", {
	carat_weight: function(frm) {
		frm.trigger("calculate_total_stone_weight");
	}
});
