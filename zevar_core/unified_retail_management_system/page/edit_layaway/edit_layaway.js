frappe.pages["edit-layaway"].on_page_load = function (wrapper) {
	new zevar.layaway.EditLayawayPage(wrapper);
};

zevar.layaway.EditLayawayPage = class EditLayawayPage {
	constructor(wrapper) {
		this.wrapper = wrapper;
		this.selectedContract = null;
		this.contractDetail = null;
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __("Edit Layaway"),
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
					<h2>Edit an active layaway</h2>
					<p>Locate an eligible layaway and update its operational details.</p>
				</div></div>
				<div class="zevar-la-panel zevar-la-stack-gap">
					<div class="zevar-la-eyebrow">Find Contract</div>
					<div class="zevar-la-form-grid compact"><div data-field="search-query"></div></div>
					<div class="zevar-la-inline-actions">
						<button type="button" class="btn btn-primary" data-action="search">${__("Search")}</button>
					</div>
					<div data-region="search-results"></div>
				</div>
				<div data-region="edit-section" style="display: none;">
					<div class="zevar-la-panel zevar-la-stack-gap">
						<div class="zevar-la-eyebrow">Contract Details</div>
						<div data-region="contract-summary"></div>
					</div>
					<div class="zevar-la-panel zevar-la-stack-gap">
						<div class="zevar-la-eyebrow">Editable Fields</div>
						<div class="zevar-la-form-grid">
							<div data-field="customer_contact"></div>
							<div data-field="customer_id_number"></div>
							<div data-field="store_location"></div>
							<div data-field="sales_person"></div>
							<div data-field="pos_profile"></div>
							<div class="zevar-la-form-span" data-field="notes"></div>
							<div data-field="terms_accepted"></div>
						</div>
						<div class="zevar-la-inline-actions">
							<button type="button" class="btn btn-primary" data-action="submit-edits">${__(
								"Save Changes"
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
			customer_contact: zevar.layaway.makeControl(
				bodyEl.querySelector('[data-field="customer_contact"]'),
				{ fieldtype: "Data", fieldname: "customer_contact", label: __("Customer Contact") }
			),
			customer_id_number: zevar.layaway.makeControl(
				bodyEl.querySelector('[data-field="customer_id_number"]'),
				{
					fieldtype: "Data",
					fieldname: "customer_id_number",
					label: __("Customer ID Number"),
				}
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
				}
			),
		};

		this.$resultsRegion = this.$body.find('[data-region="search-results"]');
		this.$body.find('[data-action="search"]').on("click", () => this.search());
		this.$body.find('[data-action="submit-edits"]').on("click", () => this.submitEdits());
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
			if (!["Draft", "Active", "Overdue"].includes(this.contractDetail.status)) {
				frappe.msgprint(
					__("Cannot edit layaway in {0} status.", [this.contractDetail.status])
				);
				return;
			}
			this.$body
				.find('[data-region="contract-summary"]')
				.html(zevar.layaway.renderSummary(this.contractDetail));
			this.fields.customer_contact.set_value(this.contractDetail.customer_contact || "");
			this.fields.customer_id_number.set_value(this.contractDetail.customer_id_number || "");
			this.fields.store_location.set_value(this.contractDetail.store_location || "");
			this.fields.sales_person.set_value(this.contractDetail.sales_person || "");
			this.fields.pos_profile.set_value(this.contractDetail.pos_profile || "");
			this.fields.notes.set_value(this.contractDetail.notes || "");
			this.fields.terms_accepted.set_value(this.contractDetail.terms_accepted || 0);
			this.$body.find('[data-region="edit-section"]').show();
			frappe.show_alert({
				message: __("Contract {0} loaded for editing", [name]),
				indicator: "green",
			});
		} catch (error) {
			frappe.msgprint({
				title: __("Load Failed"),
				message: __("Could not load contract details."),
				indicator: "red",
			});
		}
	}

	async submitEdits() {
		if (!this.selectedContract) {
			frappe.msgprint(__("Select a layaway contract first."));
			return;
		}
		const $btn = this.$body.find('[data-action="submit-edits"]');
		try {
			$btn.prop("disabled", true).text(__("Saving..."));
			const updates = {
				customer_contact: this.fields.customer_contact.get_value(),
				customer_id_number: this.fields.customer_id_number.get_value(),
				store_location: this.fields.store_location.get_value(),
				sales_person: this.fields.sales_person.get_value(),
				pos_profile: this.fields.pos_profile.get_value(),
				notes: this.fields.notes.get_value(),
				terms_accepted: this.fields.terms_accepted.get_value(),
			};
			const result = await zevar.layaway.call(
				"zevar_core.api.layaway.update_layaway_contract",
				{
					layaway_id: this.selectedContract,
					updates: JSON.stringify(updates),
				}
			);
			frappe.show_alert({ message: result.message, indicator: "green" });
			this.contractDetail = await zevar.layaway.call(
				"zevar_core.api.layaway.get_layaway_details",
				{ layaway_id: this.selectedContract }
			);
			this.$body
				.find('[data-region="contract-summary"]')
				.html(zevar.layaway.renderSummary(this.contractDetail));
		} catch (error) {
			frappe.msgprint({
				title: __("Update Failed"),
				message: __("Failed to save changes."),
				indicator: "red",
			});
		} finally {
			$btn.prop("disabled", false).text(__("Save Changes"));
		}
	}
};
