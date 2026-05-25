app_name = "zevar_core"
app_title = "Unified Retail Management System"
app_publisher = "Zevar"
app_description = "A centralized solution for POS operations, real-time inventory management, dynamic pricing, and CRM for Zevar Jewelery."
app_email = "akshay@arijentek.com"
app_license = "mit"
app_logo_url = "/assets/zevar_core/images/pos_logo.svg"
splash_image = "/assets/zevar_core/images/pos_logo.svg"

# NOTE: add_to_apps_screen only supports ONE entry per app.
# Frappe core uses apps[0] only (boot.py line 180).
# For additional desk shortcuts (e.g. Employee Portal), create Desktop Icons
# via install.py or a patch instead.
add_to_apps_screen = [
	{
		"name": "zevar_pos",
		"logo": "/assets/zevar_core/images/pos_logo.svg",
		"title": "Zevar POS",
		"route": "/pos",
	},
]

boot_session = "zevar_core.api.desk.boot_session"

app_include_js = [
	"/assets/zevar_core/js/desk_customization.js",
	"/assets/zevar_core/js/layaway_desk.js",
]
app_include_css = ["/assets/zevar_core/css/desk.css"]

# Jinja
jinja = {"methods": ["zevar_core.utils.assets.get_frontend_asset"]}

# Routing
website_route_rules = [
	{"from_route": "/employee-portal/<path:app_path>", "to_route": "employee-portal"},
	{"from_route": "/pos/<path:app_path>", "to_route": "pos"},
	{"from_route": "/catalogues/<path:app_path>", "to_route": "catalogues"},
]

# Override whitelisted methods for payment gateway webhooks
override_whitelisted_methods = {
	"zevar_core.api.payment_webhooks.stripe_webhook": "zevar_core.api.payment_webhooks.stripe_webhook",
	"zevar_core.api.payment_webhooks.square_webhook": "zevar_core.api.payment_webhooks.square_webhook",
}

# Fixtures
fixtures = ["Item Attribute", "Custom Field", "Property Setter"]

# Document Events
doc_events = {
	"Item": {"validate": "zevar_core.item_events.calculate_net_weight_g"},
	"Sales Invoice": {
		"validate": [
			"zevar_core.tax_events.apply_store_tax",
			"zevar_core.trade_in_events.validate_trade_in_2x_rule",
			"zevar_core.api.inventory.validate_serial_sellable_zones",
			"zevar_core.stock_validation.validate_pos_stock_qty",
		],
		"before_submit": [
				"zevar_core.api.repair_accounting.validate_sales_invoice_stream",
				"zevar_core.api.tax_exemption.validate_exemption_on_submit",
			],
		"on_submit": [
			"zevar_core.api.commission.calculate_commissions",
			"zevar_core.services.stock_reduction.detect_stock_reduction",
			"zevar_core.services.reservation_manager.release_reservation_for_invoice",
		],
			"on_cancel": [
				"zevar_core.api.commission.reverse_commissions",
			],
	},
}

# Scheduler events
scheduler_events = {
	"cron": {
		"*/60 * * * *": ["zevar_core.tasks.fetch_live_metal_rates"],
		"0 2 1 * *": ["zevar_core.api.finance.apply_finance_charges"],
		"0 8 * * *": [
			"zevar_core.api.layaway.check_overdue_and_forfeit",
			"zevar_core.api.layaway.send_payment_reminders",
		],
		"0 23 * * *": ["zevar_core.tasks.email_eod_brief"],
		"0 6 * * *": [
			"zevar_core.api.compliance.scan_cash_transactions",
			"zevar_core.tasks.reorder_suggestion_job",
			"zevar_core.tasks.audit_cadence_heartbeat",
			"zevar_core.tasks.serial_last_seen_backfill",
			"zevar_core.tasks.consignment_overdue_alert",
			"zevar_core.api.pricing_intelligence.analyze_pricing_opportunities",
		],
		"0 * * * *": [
				"zevar_core.tasks.expire_stale_reservations",
				"zevar_core.api.pos_activation.auto_deactivate_profiles",
			],
		"0 */2 * * *": ["zevar_core.tasks.run_report_subscriptions"],
			"0 9 1 * *": [
				"zevar_core.api.dunning.run_auto_dunning",
				"zevar_core.api.dunning.send_monthly_statements",
			],
	},
}

# Installation hooks
after_install = [
	"zevar_core.install.create_required_modes_of_payment",
	"zevar_core.install.import_desktop_icons",
	"zevar_core.install.import_workspaces",
	"zevar_core.install.create_default_desk_shortcuts",
]

# Run after migrate to ensure desktop icons and shortcuts are imported
after_migrate = [
	"zevar_core.fix_desktop_icons.execute",
	"zevar_core.install.import_desktop_icons",
	"zevar_core.install.import_workspaces",
	"zevar_core.install.create_default_desk_shortcuts",
]

# Bench Commands
bench_commands = [
	"zevar_core.migration.commands.import_legacy_data",
	"zevar_core.migration.commands.show_mapping_info",
	"zevar_core.migration.items_transfer.export_items",
	"zevar_core.migration.items_transfer.import_items",
	"zevar_core.stock_cli.stock_cli",
]
