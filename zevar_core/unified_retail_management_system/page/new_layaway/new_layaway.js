frappe.pages["new-layaway"].on_page_load = function (wrapper) {
	new zevar.layaway.NewLayawayPage(wrapper);
};

zevar.layaway.NewLayawayPage = class NewLayawayPage {
	constructor(wrapper) {
		this.wrapper = wrapper;
		this.items = [];
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __("New Layaway"),
			single_column: true,
		});
		this.$body = zevar.layaway.getBody(this.page);
		this.page.set_secondary_action(__("Layaway Hub"), () => zevar.layaway.goToHub());
		this.render();
	}

	render() {
		this.$body.html(`
			<div class="zevar-la-shell">
				<div class="zevar-la-hero">
					<div>
						<div class="zevar-la-eyebrow">Desk Workflow</div>
						<h2>Create a layaway contract</h2>
						<p>Select the customer, add reserved items, set the term, and post the opening deposit.</p>
					</div>
				</div>
				<div class="zevar-la-grid two-col">
					<div class="zevar-la-panel">
						<div class="zevar-la-eyebrow">Contract Setup</div>
						<div class="zevar-la-form-grid">
							<div data-field="customer"></div>
							<div data-field="duration"></div>
							<div data-field="store_location"></div>
							<div data-field="sales_person"></div>
							<div data-field="pos_profile"></div>
							<div data-field="deposit_amount"></div>
							<div class="zevar-la-form-span" data-field="notes"></div>
							<div class="zevar-la-form-span" data-field="terms_accepted"></div>
						</div>
					</div>
					<div class="zevar-la-panel zevar-la-stack-gap">
						<div class="zevar-la-eyebrow">Item Entry</div>
						<div class="zevar-la-form-grid compact">
							<div data-field="item_code"></div>
							<div data-field="qty"></div>
							<div data-field="rate"></div>
						</div>
						<div class="zevar-la-inline-actions">
							<button type="button" class="btn btn-default" data-action="add-item">${__("Add Item")}</button>
						</div>
						<div data-region="items"></div>
					</div>
				</div>
				<div class="zevar-la-panel zevar-la-stack-gap">
					<div class="zevar-la-eyebrow">Preview</div>
					<div data-region="preview"></div>
					<div class="zevar-la-inline-actions">
						<button type="button" class="btn btn-primary" data-action="submit">${__("Create Layaway")}</button>
					</div>
				</div>
			</div>`);

		const bodyEl = this.$body[0];
		this.fields = {
			customer: zevar.layaway.makeControl(bodyEl.querySelector('[data-field="customer"]'), {
				fieldtype: "Link",
				fieldname: "customer",
				label: __("Customer"),
				options: "Customer",
				reqd: 1,
			}),
			duration: zevar.layaway.makeControl(
				bodyEl.querySelector('[data-field="duration"]'),
				{
					fieldtype: "Select",
					fieldname: "duration",
					label: __("Duration"),
					options: ["3", "6", "9", "12"],
					reqd: 1,
				},
				"6"
			),
			store_location: zevar.layaway.makeControl(
				bodyEl.querySelector('[data-field="store_location"]'),
				{
					fieldtype: "Link",
					fieldname: "store_location",
					label: __("Store Location"),
					options: "Store Location",
				}
			),
			sales_person: zevar.layaway.makeControl(
				bodyEl.querySelector('[data-field="sales_person"]'),
				{
					fieldtype: "Link",
					fieldname: "sales_person",
					label: __("Sales Person"),
					options: "Sales Person",
				}
			),
			pos_profile: zevar.layaway.makeControl(
				bodyEl.querySelector('[data-field="pos_profile"]'),
				{
					fieldtype: "Link",
					fieldname: "pos_profile",
					label: __("POS Profile"),
					options: "POS Profile",
				}
			),
			deposit_amount: zevar.layaway.makeControl(
				bodyEl.querySelector('[data-field="deposit_amount"]'),
				{
					fieldtype: "Currency",
					fieldname: "deposit_amount",
					label: __("Opening Deposit"),
					reqd: 1,
				},
				0
			),
			notes: zevar.layaway.makeControl(bodyEl.querySelector('[data-field="notes"]'), {
				fieldtype: "Small Text",
				fieldname: "notes",
				label: __("Notes"),
			}),
			terms_accepted: zevar.layaway.makeControl(
				bodyEl.querySelector('[data-field="terms_accepted"]'),
				{
					fieldtype: "Check",
					fieldname: "terms_accepted",
					label: __("Customer accepted layaway terms"),
				},
				1
			),
			item_code: zevar.layaway.makeControl(
				bodyEl.querySelector('[data-field="item_code"]'),
				{
					fieldtype: "Link",
					fieldname: "item_code",
					label: __("Item"),
					options: "Item",
				}
			),
			qty: zevar.layaway.makeControl(
				bodyEl.querySelector('[data-field="qty"]'),
				{
					fieldtype: "Float",
					fieldname: "qty",
					label: __("Qty"),
				},
				1
			),
			rate: zevar.layaway.makeControl(
				bodyEl.querySelector('[data-field="rate"]'),
				{
					fieldtype: "Currency",
					fieldname: "rate",
					label: __("Rate"),
				},
				0
			),
		};

		this.$body.find('[data-action="add-item"]').on("click", () => this.addItem());
		this.$body.find('[data-action="submit"]').on("click", () => this.submit());
		this.$body.find('[data-region="items"]').on("click", (event) => {
			const button = event.target.closest("[data-remove-index]");
			if (!button) return;
			this.items.splice(Number(button.dataset.removeIndex), 1);
			this.renderItems();
		});

		this.renderItems();
	}

	get totals() {
		const total = this.items.reduce((sum, item) => sum + Number(item.amount || 0), 0);
		const deposit = Number(this.fields.deposit_amount.get_value() || 0);
		const balance = Math.max(total - deposit, 0);
		const months = Math.max(Number(this.fields.duration.get_value() || 0) - 1, 1);
		return { total, deposit, balance, monthlyEstimate: balance > 0 ? balance / months : 0 };
	}

	addItem() {
		const itemCode = this.fields.item_code.get_value();
		const qty = Number(this.fields.qty.get_value() || 0);
		const rate = Number(this.fields.rate.get_value() || 0);
		if (!itemCode) {
			frappe.msgprint(__("Select an item before adding it."));
			return;
		}
		if (qty <= 0 || rate <= 0) {
			frappe.msgprint(__("Quantity and rate must both be greater than zero."));
			return;
		}
		this.items.push({ item_code: itemCode, qty, rate, amount: qty * rate });
		this.fields.item_code.set_value("");
		this.fields.qty.set_value(1);
		this.fields.rate.set_value(0);
		this.renderItems();
	}

	renderItems() {
		const $region = this.$body.find('[data-region="items"]');
		if (!this.items.length) {
			$region.html(
				'<div class="zevar-la-empty">Add one or more items to build the contract.</div>'
			);
		} else {
			$region.html(`
				<table class="table table-bordered zevar-la-table">
					<thead><tr><th>Item</th><th>Qty</th><th>Rate</th><th>Amount</th><th></th></tr></thead>
					<tbody>${this.items
						.map(
							(item, index) => `
						<tr>
							<td>${zevar.layaway.escapeHtml(item.item_code)}</td>
							<td>${zevar.layaway.escapeHtml(item.qty)}</td>
							<td>${zevar.layaway.toCurrency(item.rate)}</td>
							<td>${zevar.layaway.toCurrency(item.amount)}</td>
							<td><button type="button" class="btn btn-xs btn-default" data-remove-index="${index}">${__(
								"Remove"
							)}</button></td>
						</tr>`
						)
						.join("")}
					</tbody>
				</table>`);
		}
		const totals = this.totals;
		this.$body.find('[data-region="preview"]').html(`
			<div class="zevar-la-summary-grid compact">
				<div class="zevar-la-panel"><div class="zevar-la-eyebrow">Total</div><h3>${zevar.layaway.toCurrency(
					totals.total
				)}</h3></div>
				<div class="zevar-la-panel"><div class="zevar-la-eyebrow">Deposit</div><h3>${zevar.layaway.toCurrency(
					totals.deposit
				)}</h3></div>
				<div class="zevar-la-panel"><div class="zevar-la-eyebrow">Balance</div><h3>${zevar.layaway.toCurrency(
					totals.balance
				)}</h3></div>
				<div class="zevar-la-panel"><div class="zevar-la-eyebrow">Estimated Monthly</div><h3>${zevar.layaway.toCurrency(
					totals.monthlyEstimate
				)}</h3></div>
			</div>`);
	}

	async submit() {
		try {
			if (!this.fields.customer.get_value()) {
				frappe.msgprint(__("Customer is required."));
				return;
			}
			if (!this.items.length) {
				frappe.msgprint(__("Add at least one item to the contract."));
				return;
			}
			const totals = this.totals;
			if (totals.deposit <= 0 || totals.deposit >= totals.total) {
				frappe.msgprint(
					__("Deposit must be greater than zero and less than the contract total.")
				);
				return;
			}
			const $btn = this.$body.find('[data-action="submit"]');
			$btn.prop("disabled", true).text(__("Creating..."));

			const result = await zevar.layaway.call("zevar_core.api.layaway.create_layaway", {
				customer: this.fields.customer.get_value(),
				items: JSON.stringify(this.items),
				deposit_amount: totals.deposit,
				duration_months: this.fields.duration.get_value(),
				store_location: this.fields.store_location.get_value(),
				sales_person: this.fields.sales_person.get_value(),
				pos_profile: this.fields.pos_profile.get_value(),
				notes: this.fields.notes.get_value(),
				terms_accepted: this.fields.terms_accepted.get_value(),
			});
			frappe.show_alert({
				message: __("Layaway {0} created", [result.layaway_id]),
				indicator: "green",
			});
			frappe.set_route("Form", "Layaway Contract", result.layaway_id);
		} catch (error) {
			console.error("Failed to create layaway:", error);
			frappe.msgprint({
				title: __("Creation Failed"),
				message: __("Failed to create layaway contract."),
				indicator: "red",
			});
		} finally {
			this.$body
				.find('[data-action="submit"]')
				.prop("disabled", false)
				.text(__("Create Layaway"));
		}
	}
};
