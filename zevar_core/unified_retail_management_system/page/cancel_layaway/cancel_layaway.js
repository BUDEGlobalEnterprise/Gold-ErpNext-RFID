frappe.pages["cancel-layaway"].on_page_load = function (wrapper) {
	new zevar.layaway.CancelLayawayPage(wrapper);
};

zevar.layaway.CancelLayawayPage = class CancelLayawayPage {
	constructor(wrapper) {
		this.wrapper = wrapper;
		this.selectedContract = null;
		this.contractDetail = null;
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __("Cancel Layaway"),
			single_column: true,
		});
		this.$body = zevar.layaway.getBody(this.page);
		this.page.set_secondary_action(__("Layaway Hub"), () => zevar.layaway.goToHub());
		this.render();
	}

	render() {
		this.$body.html(`
			<div class="zevar-la-shell">
				<div class="zevar-la-hero"><div>
					<div class="zevar-la-eyebrow">Desk Workflow</div>
					<h2>Cancel a layaway contract</h2>
					<p>Locate an active layaway and process cancellation with store credit refund.</p>
				</div></div>
				<div class="zevar-la-panel zevar-la-stack-gap">
					<div class="zevar-la-eyebrow">Find Contract</div>
					<div class="zevar-la-form-grid compact"><div data-field="search-query"></div></div>
					<div class="zevar-la-inline-actions">
						<button type="button" class="btn btn-primary" data-action="search">${__("Search")}</button>
					</div>
					<div data-region="search-results"></div>
				</div>
				<div data-region="cancel-section" style="display: none;">
					<div class="zevar-la-panel zevar-la-stack-gap">
						<div class="zevar-la-eyebrow">Contract Summary</div>
						<div data-region="contract-summary"></div>
					</div>
					<div class="zevar-la-panel zevar-la-stack-gap zevar-la-warning-panel">
						<div class="zevar-la-eyebrow">⚠️ Cancellation Warning</div>
						<p>Cancelling this layaway will:</p>
						<ul>
							<li>Set the contract status to <strong>Cancelled</strong></li>
							<li>Issue a gift card for the total amount paid</li>
							<li>This action cannot be undone</li>
						</ul>
						<div class="zevar-la-form-grid">
							<div class="zevar-la-form-span" data-field="cancellation_reason"></div>
						</div>
						<div class="zevar-la-inline-actions">
							<button type="button" class="btn btn-danger" data-action="confirm-cancel">${__(
								"Confirm Cancellation"
							)}</button>
						</div>
					</div>
				</div>
			</div>`);

		const bodyEl = this.$body[0];
		this.fields = {
			search_query: zevar.layaway.makeControl(
				bodyEl.querySelector('[data-field="search-query"]'),
				{
					fieldtype: "Data",
					fieldname: "search_query",
					label: __("Contract / Customer / Phone / ID"),
				}
			),
			cancellation_reason: zevar.layaway.makeControl(
				bodyEl.querySelector('[data-field="cancellation_reason"]'),
				{
					fieldtype: "Text",
					fieldname: "cancellation_reason",
					label: __("Cancellation Reason"),
					reqd: 1,
				}
			),
		};

		this.$resultsRegion = this.$body.find('[data-region="search-results"]');
		this.$body.find('[data-action="search"]').on("click", () => this.search());
		this.$body.find('[data-action="confirm-cancel"]').on("click", () => this.confirmCancel());
	}

	async search() {
		const query = this.fields.search_query.get_value();
		if (!query || !query.trim()) {
			frappe.msgprint(__("Enter a search term."));
			return;
		}
		try {
			zevar.layaway.showLoading(this.$resultsRegion[0], __("Searching..."));
			const contracts = await zevar.layaway.call(
				"zevar_core.api.layaway.search_layaway_contracts",
				{ query: query.trim() }
			);
			zevar.layaway.renderSearchResults(this.$resultsRegion[0], contracts, (name) =>
				this.selectContract(name)
			);
		} catch (error) {
			zevar.layaway.showError(this.$resultsRegion[0], __("Search failed."));
		}
	}

	async selectContract(name) {
		try {
			this.selectedContract = name;
			this.contractDetail = await zevar.layaway.call(
				"zevar_core.api.layaway.get_layaway_details",
				{ layaway_id: name }
			);
			if (!["Active", "Overdue"].includes(this.contractDetail.status)) {
				frappe.msgprint(
					__("Cannot cancel layaway in {0} status.", [this.contractDetail.status])
				);
				return;
			}
			this.$body
				.find('[data-region="contract-summary"]')
				.html(zevar.layaway.renderSummary(this.contractDetail));
			this.fields.cancellation_reason.set_value("");
			this.$body.find('[data-region="cancel-section"]').show();
			frappe.show_alert({
				message: __("Contract {0} loaded for cancellation review", [name]),
				indicator: "orange",
			});
		} catch (error) {
			frappe.msgprint({
				title: __("Load Failed"),
				message: __("Could not load contract details."),
				indicator: "red",
			});
		}
	}

	confirmCancel() {
		if (!this.selectedContract) {
			frappe.msgprint(__("Select a layaway contract first."));
			return;
		}
		const reason = this.fields.cancellation_reason.get_value();
		if (!reason || !reason.trim()) {
			frappe.msgprint(__("Cancellation reason is required."));
			return;
		}
		frappe.confirm(
			__(
				"Are you sure you want to cancel layaway {0}?<br><br>Total paid: <strong>{1}</strong><br><br>This will issue a gift card and cannot be undone.",
				[this.selectedContract, zevar.layaway.toCurrency(this.contractDetail.total_paid)]
			),
			() => this.executeCancellation(reason.trim())
		);
	}

	async executeCancellation(reason) {
		const $btn = this.$body.find('[data-action="confirm-cancel"]');
		try {
			$btn.prop("disabled", true).text(__("Cancelling..."));
			const result = await zevar.layaway.call("zevar_core.api.layaway.cancel_layaway", {
				layaway_id: this.selectedContract,
				cancellation_reason: reason,
			});
			frappe.show_alert({
				message: __("Layaway cancelled. Gift card {0} issued with {1}.", [
					result.store_credit_id,
					zevar.layaway.toCurrency(result.amount_refunded),
				]),
				indicator: "orange",
			});
			this.selectedContract = null;
			this.contractDetail = null;
			this.fields.search_query.set_value("");
			this.fields.cancellation_reason.set_value("");
			this.$resultsRegion.empty();
			this.$body.find('[data-region="cancel-section"]').hide();
		} catch (error) {
			frappe.msgprint({
				title: __("Cancellation Failed"),
				message: __("Failed to cancel layaway."),
				indicator: "red",
			});
		} finally {
			$btn.prop("disabled", false).text(__("Confirm Cancellation"));
		}
	}
};
