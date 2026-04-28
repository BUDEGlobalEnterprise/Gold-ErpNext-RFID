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
					<label>Select Store / Warehouse to Audit</label>
					<div id="warehouse-control"></div>
				</div>
				<button class="btn btn-primary" id="start-audit-btn">Start Audit</button>
			</div>
		</div>

		<div id="audit-active" style="display: none;">
			<div class="row">
				<div class="col-sm-8">
					<div class="panel panel-info">
						<div class="panel-heading">
							<h3 class="panel-title">Scanner Input</h3>
						</div>
						<div class="panel-body">
							<p>Scan barcodes or RFID tags here. (Focus must be in the field below)</p>
							<div class="form-group">
								<input type="text" id="scanner-input" class="form-control input-lg" placeholder="Scan Barcode or EPC..." autofocus autocomplete="off">
							</div>

							<div id="scan-messages" style="margin-top: 15px; height: 100px; overflow-y: auto; background: #f9f9f9; padding: 10px; border-radius: 4px;">
								<!-- Scan results appear here -->
							</div>
						</div>
					</div>
				</div>
				<div class="col-sm-4">
					<div class="panel panel-default">
						<div class="panel-heading">
							<h3 class="panel-title">Audit Status</h3>
						</div>
						<div class="panel-body">
							<h4 id="session-name-display" class="text-primary"></h4>
							<table class="table table-bordered">
								<tr>
									<th>Expected Items</th>
									<td id="expected-count" class="text-right">0</td>
								</tr>
								<tr>
									<th>Scanned Items</th>
									<td id="scanned-count" class="text-right">0</td>
								</tr>
								<tr>
									<th>Missing Items</th>
									<td id="missing-count" class="text-right">0</td>
								</tr>
								<tr>
									<th>Unexpected Items</th>
									<td id="unexpected-count" class="text-right text-warning">0</td>
								</tr>
							</table>
							<button class="btn btn-success btn-block" id="finalize-audit-btn">Finalize Audit</button>
							<button class="btn btn-default btn-block" id="cancel-audit-btn" style="margin-top: 10px;">Close / Cancel</button>
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
	let scanned_items = [];

	page.body.find("#start-audit-btn").on("click", function () {
		let warehouse = warehouse_field.get_value();
		if (!warehouse) {
			frappe.msgprint("Please select a warehouse");
			return;
		}

		frappe.call({
			method: "zevar_core.api.inventory_audit.start_audit",
			args: { store_location: warehouse },
			callback: function (r) {
				if (r.message && r.message.success) {
					current_session = r.message.session_name;
					expected_items = r.message.expected_items || [];
					scanned_items = [];

					page.body.find("#audit-setup").hide();
					page.body.find("#audit-active").show();

					page.body.find("#session-name-display").text(current_session);
					page.body.find("#expected-count").text(r.message.expected_count);
					page.body.find("#scanned-count").text("0");
					page.body.find("#missing-count").text(r.message.expected_count);
					page.body.find("#unexpected-count").text("0");
					page.body.find("#scan-messages").empty();

					setTimeout(() => {
						page.body.find("#scanner-input").focus();
					}, 100);
				}
			},
		});
	});

	let scan_input = page.body.find("#scanner-input");
	scan_input.on("keypress", function (e) {
		if (e.which === 13) {
			// Enter key
			e.preventDefault();
			let barcode = $(this).val().trim();
			if (!barcode) return;

			$(this).val(""); // Clear input quickly

			frappe.call({
				method: "zevar_core.api.inventory_audit.submit_scan",
				args: {
					session_name: current_session,
					barcode_or_epc: barcode,
				},
				callback: function (r) {
					if (r.message && r.message.success) {
						let status_color = "green";
						if (r.message.match_status === "Unexpected") status_color = "orange";

						let msg = `<div style="color: ${status_color}; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-bottom: 5px;">
							<strong>${r.message.match_status}:</strong> ${barcode}
							${r.message.item_name ? `(${r.message.item_name})` : ""}
						</div>`;

						let msg_container = page.body.find("#scan-messages");
						msg_container.prepend(msg);

						// Update counts visually
						scanned_items.push({ barcode: barcode, status: r.message.match_status });

						let matched_count = scanned_items.filter(
							(s) => s.status === "Matched",
						).length;
						let unexpected_count = scanned_items.filter(
							(s) => s.status === "Unexpected",
						).length;
						let expected_total = parseInt(page.body.find("#expected-count").text());

						page.body.find("#scanned-count").text(matched_count + unexpected_count);
						page.body
							.find("#missing-count")
							.text(Math.max(0, expected_total - matched_count));
						page.body.find("#unexpected-count").text(unexpected_count);
					}
				},
			});
		}
	});

	// Keep focus on scanner input
	scan_input.on("blur", function () {
		if (current_session) {
			setTimeout(() => {
				$(this).focus();
			}, 2000);
		}
	});

	page.body.find("#finalize-audit-btn").on("click", function () {
		frappe.confirm(
			"Are you sure you want to finalize this audit? Any missing items will be marked as shrinkage.",
			function () {
				frappe.call({
					method: "zevar_core.api.inventory_audit.finalize_audit",
					args: { session_name: current_session },
					callback: function (r) {
						if (r.message && r.message.success) {
							let msg = `Audit Finalized with status: ${r.message.status}.`;
							if (r.message.missing_count > 0) {
								msg += `<br>Created Shrinkage Entry: <a href="/app/stock-entry/${r.message.shrinkage_entry}">${r.message.shrinkage_entry}</a>`;
							}
							frappe.msgprint(msg);

							// Reset
							current_session = null;
							page.body.find("#audit-active").hide();
							page.body.find("#audit-setup").show();
						}
					},
				});
			},
		);
	});

	page.body.find("#cancel-audit-btn").on("click", function () {
		current_session = null;
		page.body.find("#audit-active").hide();
		page.body.find("#audit-setup").show();
	});
}
