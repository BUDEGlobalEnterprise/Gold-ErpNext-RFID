frappe.pages["layaway"].on_page_load = function (wrapper) {
	new zevar.layaway.LayawayHubPage(wrapper);
};

zevar.layaway.LayawayHubPage = class LayawayHubPage {
	constructor(wrapper) {
		this.wrapper = wrapper;
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __("Layaway"),
			single_column: true,
		});
		this.$body = $(this.page.body);
		this.render();
		this.loadStats();
	}

	render() {
		this.$body.html(`
			<div class="workspace-skeleton">
				<!-- Number Cards Section -->
				<div class="widget-group" data-section="stats">
					<div class="widget-group-head">
						<div class="widget-group-title">${__("Key Metrics")}</div>
					</div>
					<div class="widget-group-body grid-col-4">
						<div class="widget number-widget-box" data-stat-card="active">
							<div class="widget-content">
								<div class="number-card-label text-muted">${__("Active Contracts")}</div>
								<div class="number" data-stat="active">-</div>
							</div>
						</div>
						<div class="widget number-widget-box" data-stat-card="overdue">
							<div class="widget-content">
								<div class="number-card-label text-muted">${__("Overdue")}</div>
								<div class="number text-danger" data-stat="overdue">-</div>
							</div>
						</div>
						<div class="widget number-widget-box" data-stat-card="today-payments">
							<div class="widget-content">
								<div class="number-card-label text-muted">${__("Today's Payments")}</div>
								<div class="number" data-stat="today-payments">-</div>
							</div>
						</div>
						<div class="widget number-widget-box" data-stat-card="outstanding">
							<div class="widget-content">
								<div class="number-card-label text-muted">${__("Outstanding Balance")}</div>
								<div class="number" data-stat="outstanding">-</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Quick Actions Section -->
				<div class="widget-group" data-section="quick-actions">
					<div class="widget-group-head">
						<div class="widget-group-title">${__("Quick Actions")}</div>
					</div>
					<div class="widget-group-body grid-col-4">
						<div class="widget shortcut-widget-box" data-action="new-layaway">
							<div class="widget-content text-center cursor-pointer">
								<div class="shortcut-icon mb-2">
									<svg class="icon icon-md"><use href="#icon-add"></use></svg>
								</div>
								<div class="shortcut-label font-medium">${__("New Layaway")}</div>
								<div class="shortcut-description text-muted small">${__("Create a new contract")}</div>
							</div>
						</div>
						<div class="widget shortcut-widget-box" data-action="payment">
							<div class="widget-content text-center cursor-pointer">
								<div class="shortcut-icon mb-2">
									<svg class="icon icon-md text-success"><use href="#icon-money"></use></svg>
								</div>
								<div class="shortcut-label font-medium">${__("LA Payment")}</div>
								<div class="shortcut-description text-muted small">${__("Post a payment")}</div>
							</div>
						</div>
						<div class="widget shortcut-widget-box" data-action="edit">
							<div class="widget-content text-center cursor-pointer">
								<div class="shortcut-icon mb-2">
									<svg class="icon icon-md text-primary"><use href="#icon-edit"></use></svg>
								</div>
								<div class="shortcut-label font-medium">${__("Edit LA")}</div>
								<div class="shortcut-description text-muted small">${__("Update details")}</div>
							</div>
						</div>
						<div class="widget shortcut-widget-box" data-action="cancel">
							<div class="widget-content text-center cursor-pointer">
								<div class="shortcut-icon mb-2">
									<svg class="icon icon-md text-danger"><use href="#icon-cancel"></use></svg>
								</div>
								<div class="shortcut-label font-medium">${__("Cancel LA")}</div>
								<div class="shortcut-description text-muted small">${__("Cancel & issue credit")}</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Records & Reports Section -->
				<div class="widget-group" data-section="records">
					<div class="widget-group-head">
						<div class="widget-group-title">${__("Records & Reports")}</div>
					</div>
					<div class="widget-group-body grid-col-3">
						<div class="widget links-widget-box">
							<div class="widget-content">
								<div class="link-item" data-route="/app/list/Layaway%20Contract">
									<div class="link-content">
										<div class="link-text ellipsis">
											<svg class="icon icon-sm"><use href="#icon-file"></use></svg>
											<span class="ml-2">${__("Layaway Contracts")}</span>
										</div>
									</div>
									<svg class="icon icon-xs"><use href="#icon-right"></use></svg>
								</div>
								<div class="link-item" data-route="/app/query-report/Layaway%20Status">
									<div class="link-content">
										<div class="link-text ellipsis">
											<svg class="icon icon-sm"><use href="#icon-bar-chart"></use></svg>
											<span class="ml-2">${__("Layaway Status")}</span>
										</div>
									</div>
									<svg class="icon icon-xs"><use href="#icon-right"></use></svg>
								</div>
								<div class="link-item" data-route="/app/query-report/Layaway%20Aging">
									<div class="link-content">
										<div class="link-text ellipsis">
											<svg class="icon icon-sm"><use href="#icon-calendar"></use></svg>
											<span class="ml-2">${__("Layaway Aging")}</span>
										</div>
									</div>
									<svg class="icon icon-xs"><use href="#icon-right"></use></svg>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		`);

		this.$body.find('[data-action="new-layaway"]').on("click", () => {
			frappe.set_route("new-layaway");
		});
		this.$body.find('[data-action="payment"]').on("click", () => {
			frappe.set_route("layaway-payment");
		});
		this.$body.find('[data-action="edit"]').on("click", () => {
			frappe.set_route("edit-layaway");
		});
		this.$body.find('[data-action="cancel"]').on("click", () => {
			frappe.set_route("cancel-layaway");
		});
	}

	async loadStats() {
		try {
			const stats = await zevar.layaway.call("zevar_core.api.layaway.get_layaway_hub_stats");

			const setStat = (attr, value) => {
				const el = this.$body.find(`[data-stat="${attr}"]`);
				if (el.length) el.text(value);
			};

			if (stats) {
				setStat("active", stats.active_count || 0);
				setStat("overdue", stats.overdue_count || 0);
				setStat("outstanding", zevar.layaway.toCurrency(stats.outstanding_balance || 0));
				setStat("today-payments", stats.today_payment_count || 0);
			}
		} catch (error) {
			console.error("Failed to load layaway stats:", error);
		}
	}
};
