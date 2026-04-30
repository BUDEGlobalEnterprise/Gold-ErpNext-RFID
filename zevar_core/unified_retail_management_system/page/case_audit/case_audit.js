frappe.pages["case-audit"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Case Audit",
		single_column: true,
	});

	$(wrapper).bind("show", function () {
		render_audit_interface(page);
	});
};

function render_audit_interface(page) {
	page.set_title("Rapid Case Audit");

	let template = `
		<div class="row" id="audit-setup">
			<div class="col-sm-6">
				<div class="form-group">
					<label>Select Display Case or Warehouse to Audit</label>
					<div id="warehouse-control"></div>
				</div>
				<button class="btn btn-primary" id="start-audit-btn">Start Audit</button>
			</div>
		</div>

		<div id="audit-active" style="display: none;">
			<div class="row">
				<div class="col-sm-8">
					<div class="panel panel-info">
						<div class="panel-heading d-flex justify-content-between align-items-center">
							<h3 class="panel-title">Scanner Input</h3>
							<button class="btn btn-sm btn-default" id="connect-rfid-btn">
								<i class="fa fa-usb"></i> Connect RFID Scanner (WebHID)
							</button>
						</div>
						<div class="panel-body">
							<p>Scan barcodes or RFID tags here. (Focus must be in the field below for keyboard-wedge scanners)</p>
							<div class="form-group">
								<input type="text" id="scanner-input" class="form-control input-lg" placeholder="Scan Barcode or EPC..." autofocus autocomplete="off">
							</div>

							<div id="scan-messages" style="margin-top: 15px; height: 150px; overflow-y: auto; background: #f9f9f9; padding: 10px; border-radius: 4px;">
								<!-- Scan results appear here -->
							</div>
						</div>
					</div>

					<div class="panel panel-default mt-4">
						<div class="panel-heading">
							<h3 class="panel-title">Expected Items</h3>
						</div>
						<div class="panel-body p-0" style="max-height: 400px; overflow-y: auto;">
							<table class="table table-bordered table-hover mb-0" id="expected-items-table">
								<thead>
									<tr>
										<th>Status</th>
										<th>Item Code</th>
										<th>Barcode/EPC</th>
										<th>Expected Qty</th>
										<th>Scanned Qty</th>
									</tr>
								</thead>
								<tbody>
								</tbody>
							</table>
						</div>
					</div>
				</div>
				<div class="col-sm-4">
					<div class="panel panel-default">
						<div class="panel-heading">
							<h3 class="panel-title">Audit Status</h3>
						</div>
						<div class="panel-body">
							<h4 id="session-name-display" class="text-primary mb-3"></h4>
							<table class="table table-bordered">
								<tr>
									<th>Expected Items</th>
									<td id="expected-count" class="text-right">0</td>
								</tr>
								<tr>
									<th>Scanned Items</th>
									<td id="scanned-count" class="text-right text-success">0</td>
								</tr>
								<tr>
									<th>Missing Items</th>
									<td id="missing-count" class="text-right text-danger">0</td>
								</tr>
								<tr>
									<th>Unexpected Items</th>
									<td id="unexpected-count" class="text-right text-warning">0</td>
								</tr>
							</table>
							<button class="btn btn-success btn-block btn-lg mt-3" id="finalize-audit-btn">Finalize Audit</button>
							<button class="btn btn-default btn-block mt-2" id="cancel-audit-btn">Cancel Audit</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	`;

	$(page.body).html(template);

	let warehouse_field = frappe.ui.form.make_control({
		parent: page.body.find("#warehouse-control"),
		df: {
			fieldtype: "Link",
			options: "Warehouse",
			fieldname: "warehouse",
			reqd: 1,
			only_select: 1,
		},
		render_input: true,
	});

	let current_session = null;
	let expected_items = [];
	let scanned_items = {};
	let unexpected_scans = 0;
	let hidDevice = null;

	page.body.find("#start-audit-btn").on("click", function () {
		let warehouse = warehouse_field.get_value();
		if (!warehouse) {
			frappe.msgprint("Please select a Display Case or Warehouse");
			return;
		}

		frappe.call({
			method: "zevar_core.api.inventory_audit.start_audit",
			args: { display_case: warehouse },
			callback: function (r) {
				if (r.message && r.message.success) {
					current_session = r.message.session_name;
					expected_items = r.message.expected_items || [];
					scanned_items = {};
					unexpected_scans = 0;

					page.body.find("#audit-setup").hide();
					page.body.find("#audit-active").show();

					page.body.find("#session-name-display").text("Session: " + current_session);
					page.body.find("#expected-count").text(r.message.expected_count);

					update_status_sidebar();
					render_expected_items_table();

					setTimeout(() => {
						page.body.find("#scanner-input").focus();
					}, 100);
				}
			},
		});
	});

	function render_expected_items_table() {
		let tbody = page.body.find("#expected-items-table tbody");
		tbody.empty();

		expected_items.forEach((item) => {
			let scanned_qty = scanned_items[item.item_code] || 0;
			let expected_qty = flt(item.actual_qty);
			let status_icon = '<i class="fa fa-circle-o text-muted"></i>';
			let row_class = "";

			if (scanned_qty >= expected_qty) {
				status_icon = '<i class="fa fa-check-circle text-success"></i>';
				row_class = "success";
			} else if (scanned_qty > 0) {
				status_icon = '<i class="fa fa-adjust text-warning"></i>';
				row_class = "warning";
			}

			let tr = $(`<tr class="${row_class}" data-item="${item.item_code}">
				<td class="text-center">${status_icon}</td>
				<td>${item.item_code}</td>
				<td>${item.custom_rfid_epc || item.barcode || "-"}</td>
				<td class="text-right">${expected_qty}</td>
				<td class="text-right scanned-qty-cell">${scanned_qty}</td>
			</tr>`);

			tbody.append(tr);
		});
	}

	function update_status_sidebar() {
		let total_expected = expected_items.reduce((sum, item) => sum + flt(item.actual_qty), 0);
		let total_scanned_expected = Object.values(scanned_items).reduce(
			(sum, qty) => sum + qty,
			0,
		);
		let missing = Math.max(0, total_expected - total_scanned_expected);

		page.body.find("#expected-count").text(total_expected);
		page.body.find("#scanned-count").text(total_scanned_expected + unexpected_scans);
		page.body.find("#missing-count").text(missing);
		page.body.find("#unexpected-count").text(unexpected_scans);
	}

	function submitScan(barcode) {
		if (!current_session || !barcode) return;

		frappe.call({
			method: "zevar_core.api.inventory_audit.submit_scan",
			args: {
				session: current_session,
				barcode_or_epc: barcode,
			},
			callback: function (r) {
				if (r.message && r.message.success) {
					if (r.message.match_status === "Duplicate") {
						return; // Ignore completely
					}

					let status_color = "green";
					let status_text = r.message.match_status;

					if (r.message.match_status === "Unexpected") {
						status_color = "orange";
						unexpected_scans += 1;
					} else if (r.message.match_status === "Matched") {
						scanned_items[r.message.item_code] =
							(scanned_items[r.message.item_code] || 0) + 1;
					}

					let msg = `<div style="color: ${status_color}; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-bottom: 5px;">
						<strong>${status_text}:</strong> ${barcode}
						${r.message.item_name ? `(${r.message.item_name})` : ""}
					</div>`;

					let msg_container = page.body.find("#scan-messages");
					msg_container.prepend(msg);

					update_status_sidebar();
					render_expected_items_table();
				} else {
					frappe.msgprint("Error processing scan: " + barcode);
				}
			},
		});
	}

	let scan_input = page.body.find("#scanner-input");
	scan_input.on("keypress", function (e) {
		if (e.which === 13) {
			// Enter key
			e.preventDefault();
			let barcode = $(this).val().trim();
			$(this).val(""); // Clear input quickly
			submitScan(barcode);
		}
	});

	// Keep focus on scanner input so keyboard wedges always work
	scan_input.on("blur", function () {
		if (current_session && page.body.find("#audit-active").is(":visible")) {
			setTimeout(() => {
				$(this).focus();
			}, 2000);
		}
	});

	// WebHID setup for RFID Scanner
	page.body.find("#connect-rfid-btn").on("click", async function () {
		if (!navigator.hid) {
			frappe.msgprint(
				"WebHID is not supported by your browser. Please use Chrome/Edge or a keyboard-wedge scanner.",
			);
			return;
		}

		try {
			let devices = await navigator.hid.requestDevice({ filters: [] });
			if (devices.length > 0) {
				hidDevice = devices[0];
				await hidDevice.open();

				frappe.show_alert({ message: "RFID Scanner Connected!", indicator: "green" });
				$(this)
					.removeClass("btn-default")
					.addClass("btn-success")
					.html('<i class="fa fa-check"></i> Scanner Connected');

				hidDevice.addEventListener("inputreport", (event) => {
					const { data } = event;
					// Very naive decode assuming ascii/utf-8 characters from an RFID wedge that doesn't use keyboard buffer
					const textDecoder = new TextDecoder("utf-8");
					let epc = textDecoder
						.decode(data)
						.replace(/[\0\r\n]/g, "")
						.trim();
					if (epc) {
						submitScan(epc);
					}
				});
			}
		} catch (error) {
			console.error(error);
			frappe.msgprint("Failed to connect to RFID scanner: " + error.message);
		}
	});

	page.body.find("#finalize-audit-btn").on("click", function () {
		frappe.confirm(
			"Are you sure you want to finalize this audit? Any missing items will be marked as shrinkage.",
			function () {
				frappe.call({
					method: "zevar_core.api.inventory_audit.finalize_audit",
					args: { session: current_session },
					callback: function (r) {
						if (r.message && r.message.success) {
							let msg = `Audit Finalized. Status: <b>${r.message.status}</b>.`;
							if (r.message.missing_count > 0) {
								msg += `<br><br><span class="text-danger">Missing Items: ${r.message.missing_count}</span>`;
								msg += `<br>Discrepancy Value: ${format_currency(r.message.total_value_discrepancy)}`;
								if (r.message.shrinkage_entry) {
									msg += `<br>Created Shrinkage Entry: <a href="/app/stock-entry/${r.message.shrinkage_entry}">${r.message.shrinkage_entry}</a>`;
								}
							} else {
								msg += `<br><br><span class="text-success">All items successfully accounted for!</span>`;
							}

							frappe.msgprint({
								title: "Audit Complete",
								message: msg,
								indicator: r.message.missing_count > 0 ? "orange" : "green",
							});

							// Reset
							current_session = null;
							page.body.find("#audit-active").hide();
							page.body.find("#audit-setup").show();

							if (hidDevice && hidDevice.opened) {
								hidDevice.close();
								hidDevice = null;
								page.body
									.find("#connect-rfid-btn")
									.removeClass("btn-success")
									.addClass("btn-default")
									.html(
										'<i class="fa fa-usb"></i> Connect RFID Scanner (WebHID)',
									);
							}
						}
					},
				});
			},
		);
	});

	page.body.find("#cancel-audit-btn").on("click", function () {
		frappe.confirm(
			"Are you sure you want to cancel this audit? Progress will be lost.",
			function () {
				if (current_session) {
					frappe.call({
						method: "zevar_core.api.inventory_audit.cancel_audit",
						args: { session: current_session },
						callback: function () {
							current_session = null;
							page.body.find("#audit-active").hide();
							page.body.find("#audit-setup").show();
							frappe.show_alert("Audit Cancelled");
						},
					});
				}
			},
		);
	});
}
