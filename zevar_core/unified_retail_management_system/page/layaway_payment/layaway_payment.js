frappe.pages["layaway-payment"].on_page_load = function (wrapper) {
	new zevar.layaway.LayawayPaymentPage(wrapper);
};

zevar.layaway.LayawayPaymentPage = class LayawayPaymentPage {
	constructor(wrapper) {
		this.wrapper = wrapper;
		this.selectedContract = null;
		this.contractDetail = null;
		this.page = frappe.ui.make_app_page({ parent: wrapper, title: __("Layaway Payment"), single_column: true });
		this.$body = zevar.layaway.getBody(this.page);
		this.page.set_secondary_action(__("Layaway Hub"), () => zevar.layaway.goToHub());
		this.render();
	}

	render() {
		this.$body.html(`
			<div class="zevar-la-shell">
				<div class="zevar-la-hero"><div>
					<div class="zevar-la-eyebrow">Desk Workflow</div>
					<h2>Post a layaway payment</h2>
					<p>Search for an active layaway contract and record a payment.</p>
				</div></div>
				<div class="zevar-la-panel zevar-la-stack-gap">
					<div class="zevar-la-eyebrow">Find Contract</div>
					<div class="zevar-la-form-grid compact"><div data-field="search-query"></div></div>
					<div class="zevar-la-inline-actions">
						<button type="button" class="btn btn-primary" data-action="search">${__("Search")}</button>
					</div>
					<div data-region="search-results"></div>
				</div>
				<div data-region="contract-section" style="display: none;">
					<div class="zevar-la-panel zevar-la-stack-gap">
						<div class="zevar-la-eyebrow">Contract Summary</div>
						<div data-region="contract-summary"></div>
					</div>
					<div class="zevar-la-panel zevar-la-stack-gap">
						<div class="zevar-la-eyebrow">Payment Details</div>
						<div class="zevar-la-form-grid">
							<div data-field="payment_amount"></div>
							<div data-field="mode_of_payment"></div>
							<div data-field="reference_number"></div>
						</div>
						<div class="zevar-la-inline-actions">
							<button type="button" class="btn btn-primary" data-action="submit-payment">${__("Process Payment")}</button>
						</div>
					</div>
				</div>
			</div>`);

		const bodyEl = this.$body[0];
		this.fields = {
			search_query: zevar.layaway.makeControl(bodyEl.querySelector('[data-field="search-query"]'),
				{ fieldtype: "Data", fieldname: "search_query", label: __("Contract / Customer / Phone / ID") }),
			payment_amount: zevar.layaway.makeControl(bodyEl.querySelector('[data-field="payment_amount"]'),
				{ fieldtype: "Currency", fieldname: "payment_amount", label: __("Payment Amount"), reqd: 1 }, 0),
			mode_of_payment: zevar.layaway.makeControl(bodyEl.querySelector('[data-field="mode_of_payment"]'),
				{ fieldtype: "Link", fieldname: "mode_of_payment", label: __("Mode of Payment"), options: "Mode of Payment", reqd: 1 }),
			reference_number: zevar.layaway.makeControl(bodyEl.querySelector('[data-field="reference_number"]'),
				{ fieldtype: "Data", fieldname: "reference_number", label: __("Reference Number (Optional)") }),
		};

		this.$resultsRegion = this.$body.find('[data-region="search-results"]');
		this.$body.find('[data-action="search"]').on("click", () => this.search());
		this.$body.find('[data-action="submit-payment"]').on("click", () => this.submitPayment());
	}

	async search() {
		const query = this.fields.search_query.get_value();
		if (!query || !query.trim()) { frappe.msgprint(__("Enter a search term.")); return; }
		try {
			zevar.layaway.showLoading(this.$resultsRegion[0], __("Searching..."));
			const contracts = await zevar.layaway.call("zevar_core.api.layaway.search_layaway_contracts", { query: query.trim() });
			zevar.layaway.renderSearchResults(this.$resultsRegion[0], contracts, (name) => this.selectContract(name));
		} catch (error) {
			zevar.layaway.showError(this.$resultsRegion[0], __("Search failed."));
		}
	}

	async selectContract(name) {
		try {
			this.selectedContract = name;
			this.contractDetail = await zevar.layaway.call("zevar_core.api.layaway.get_layaway_details", { layaway_id: name });
			this.$body.find('[data-region="contract-summary"]').html(zevar.layaway.renderSummary(this.contractDetail));
			this.$body.find('[data-region="contract-section"]').show();
			this.fields.payment_amount.set_value(this.contractDetail.balance_amount);
			frappe.show_alert({ message: __("Contract {0} selected", [name]), indicator: "green" });
		} catch (error) {
			frappe.msgprint({ title: __("Load Failed"), message: __("Could not load contract details."), indicator: "red" });
		}
	}

	async submitPayment() {
		if (!this.selectedContract) { frappe.msgprint(__("Select a layaway contract first.")); return; }
		const amount = Number(this.fields.payment_amount.get_value() || 0);
		const mode = this.fields.mode_of_payment.get_value();
		const reference = this.fields.reference_number.get_value();
		if (amount <= 0) { frappe.msgprint(__("Payment amount must be greater than zero.")); return; }
		if (!mode) { frappe.msgprint(__("Mode of payment is required.")); return; }

		const $btn = this.$body.find('[data-action="submit-payment"]');
		try {
			$btn.prop("disabled", true).text(__("Processing..."));
			const result = await zevar.layaway.call("zevar_core.api.layaway.process_layaway_payment", {
				layaway_id: this.selectedContract, payment_amount: amount, mode_of_payment: mode, reference_number: reference,
			});
			frappe.show_alert({ message: __("Payment successful. New balance: {0}", [zevar.layaway.toCurrency(result.new_balance)]), indicator: "green" });
			this.contractDetail = await zevar.layaway.call("zevar_core.api.layaway.get_layaway_details", { layaway_id: this.selectedContract });
			this.$body.find('[data-region="contract-summary"]').html(zevar.layaway.renderSummary(this.contractDetail));
			this.fields.payment_amount.set_value(0);
			this.fields.mode_of_payment.set_value("");
			this.fields.reference_number.set_value("");
			if (result.status === "Completed") {
				frappe.msgprint({ title: __("Layaway Completed!"), message: __("The layaway {0} is now fully paid.", [this.selectedContract]), indicator: "green" });
			}
		} catch (error) {
			frappe.msgprint({ title: __("Payment Failed"), message: __("Failed to process payment."), indicator: "red" });
		} finally {
			$btn.prop("disabled", false).text(__("Process Payment"));
		}
	}
};
