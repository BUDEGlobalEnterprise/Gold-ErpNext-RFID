"""
Zevar Core API Module

Centralized API endpoints for the Zevar POS system.
Organized into logical submodules for maintainability.
"""

# Import all API functions to maintain backward compatibility
from zevar_core.api.attendance import (
	clock_in,
	clock_out,
	get_attendance_history,
	get_current_employee,
	get_employee_roster,
	get_today_checkin_status,
)
from zevar_core.api.catalog import (
	get_catalog_filters,
	get_catalog_items,
	get_catalog_vendors,
	get_display_cases,
	get_item_details,
	get_pos_items,
)
from zevar_core.api.crud import (
	create_brand,
	create_item,
	create_item_group,
	create_warehouse,
	delete_brand,
	delete_item,
	delete_item_group,
	delete_warehouse,
	get_item,
	get_item_groups_for_select,
	get_items_for_brand,
	get_items_in_group,
	get_warehouses_for_select,
	update_brand,
	update_item,
	update_item_group,
	update_warehouse,
)
from zevar_core.api.customer import get_customer_details, quick_create_customer, search_customers
from zevar_core.api.customer_dashboard import (
	get_dashboard_data as get_customer_dashboard,
)
from zevar_core.api.customer_dashboard import (
	get_kpi_summary as get_customer_kpi,
)
from zevar_core.api.customer_dashboard import (
	get_layaway_cohort as get_customer_layaway_cohort,
)
from zevar_core.api.customer_dashboard import (
	get_new_vs_returning as get_customer_new_vs_returning,
)
from zevar_core.api.customer_dashboard import (
	get_top_customers as get_customer_top,
)
from zevar_core.api.employee_live_monitor import (
	get_employee_dashboard,
	get_my_performance,
	get_my_tasks,
)
from zevar_core.api.employee_live_monitor import (
	get_store_activity as get_employee_store_activity,
)
from zevar_core.api.expense import (
	create_expense_claim,
	get_expense_claims,
	get_expense_types,
	submit_expense_claim,
)
from zevar_core.api.helpdesk import (
	add_ticket_reply,
	create_attendance_issue,
	get_employee_tickets,
	get_issue_types,
	get_ticket_details,
	get_ticket_stats,
)
from zevar_core.api.inventory_dashboard import (
	get_aging_buckets as get_inventory_aging,
)
from zevar_core.api.inventory_dashboard import (
	get_dashboard_data as get_inventory_dashboard,
)
from zevar_core.api.inventory_dashboard import (
	get_kpi_summary as get_inventory_kpi,
)
from zevar_core.api.inventory_dashboard import (
	get_shrinkage_trend as get_inventory_shrinkage,
)
from zevar_core.api.inventory_dashboard import (
	get_stock_by_warehouse as get_inventory_by_warehouse,
)
from zevar_core.api.item_entry import get_next_vendor_sku, quick_add_item
from zevar_core.api.live_monitor import (
	get_command_center_data,
	get_repair_live_feed,
	run_anomaly_detection,
)
from zevar_core.api.payroll import get_payroll_summary, get_salary_slip_details, get_salary_slips
from zevar_core.api.pos import calculate_invoice_totals, cancel_pos_invoice, create_pos_invoice, get_pos_settings, initiate_online_checkout, simulate_payment_success
from zevar_core.api.pricing import (
	get_item_price,
	get_live_metal_rates,
	get_live_rate_history,
	refresh_gold_rates,
)
from zevar_core.api.quick_layaway import (
	create_quick_layaway as create_quick_layaway_shim,
)
from zevar_core.api.quick_layaway import (
	get_layaway_preview as get_layaway_preview_shim,
)
from zevar_core.api.repair import (
	add_repair_payment,
	attach_repair_photo,
	create_repair_order,
	get_customer_repair_history,
	get_dashboard_stats,
	get_estimate_details_for_approval,
	get_multi_store_stats,
	get_repair_order_details,
	get_repair_orders,
	get_repair_receipt_html,
	get_repair_stats,
	get_repair_types,
	get_thermal_receipt_html,
	lookup_repair_by_number,
	lookup_repair_by_phone,
	public_estimate_approval,
	update_repair_status,
)
from zevar_core.api.repair_analytics import get_ai_insights, get_repair_analytics
from zevar_core.api.repair_timeline import (
	get_repair_timeline,
	get_technician_workload,
	log_status_change,
	predict_repair_eta,
	suggest_technician,
)
from zevar_core.api.reports import (
	get_eod_summary,
	get_report_catalog,
	get_report_defaults,
	get_report_summary,
)
from zevar_core.api.revenue_dashboard import (
	get_category_breakdown as get_revenue_categories,
)
from zevar_core.api.revenue_dashboard import (
	get_dashboard_data as get_revenue_dashboard,
)
from zevar_core.api.revenue_dashboard import (
	get_hourly_distribution as get_revenue_hourly,
)
from zevar_core.api.revenue_dashboard import (
	get_today_summary as get_revenue_today_summary,
)
from zevar_core.api.revenue_dashboard import (
	get_top_salespersons as get_revenue_top_salespersons,
)
from zevar_core.api.tasks import (
	create_personal_todo,
	delete_todo,
	get_employee_tasks,
	get_personal_todos,
	get_recent_activities,
	get_task_stats,
	update_todo_status,
)
from zevar_core.api.trending import get_trending_items, track_trending_click

__all__ = [
	"add_repair_payment",
	"add_ticket_reply",
	"attach_repair_photo",
	"calculate_invoice_totals",
	"cancel_pos_invoice",
	"clock_in",
	"clock_out",
	"create_attendance_issue",
	"create_brand",
	"create_expense_claim",
	"create_item",
	"create_item_group",
	"create_personal_todo",
	"create_pos_invoice",
	"create_quick_layaway_shim",
	"create_warehouse",
	"delete_brand",
	"delete_item",
	"delete_item_group",
	"delete_todo",
	"delete_warehouse",
	"get_ai_insights",
	"get_attendance_history",
	"get_catalog_filters",
	"get_catalog_items",
	"get_catalog_vendors",
	"get_command_center_data",
	"get_current_employee",
	"get_customer_dashboard",
	"get_customer_details",
	"get_customer_kpi",
	"get_customer_layaway_cohort",
	"get_customer_new_vs_returning",
	"get_customer_repair_history",
	"get_customer_top",
	"get_dashboard_stats",
	"get_display_cases",
	"get_employee_dashboard",
	"get_employee_roster",
	"get_employee_store_activity",
	"get_employee_tasks",
	"get_employee_tickets",
	"get_eod_summary",
	"get_estimate_details_for_approval",
	"get_expense_claims",
	"get_expense_types",
	"get_inventory_aging",
	"get_inventory_by_warehouse",
	"get_inventory_dashboard",
	"get_inventory_kpi",
	"get_inventory_shrinkage",
	"get_issue_types",
	"get_item",
	"get_item_details",
	"get_item_groups_for_select",
	"get_item_price",
	"get_items_for_brand",
	"get_items_in_group",
	"get_layaway_preview_shim",
	"initiate_online_checkout",
	"get_live_metal_rates",
	"get_live_rate_history",
	"get_multi_store_stats",
	"get_my_performance",
	"get_my_tasks",
	"get_next_vendor_sku",
	"get_payroll_summary",
	"get_personal_todos",
	"get_pos_items",
	"get_pos_settings",
	"get_recent_activities",
	"get_repair_analytics",
	"get_repair_live_feed",
	"get_repair_order_details",
	"get_repair_orders",
	"get_repair_receipt_html",
	"get_repair_stats",
	"get_repair_timeline",
	"get_repair_types",
	"get_report_catalog",
	"get_report_defaults",
	"get_report_summary",
	"get_revenue_categories",
	"get_revenue_dashboard",
	"get_revenue_hourly",
	"get_revenue_today_summary",
	"get_revenue_top_salespersons",
	"get_salary_slip_details",
	"get_salary_slips",
	"get_task_stats",
	"get_technician_workload",
	"get_thermal_receipt_html",
	"get_ticket_details",
	"get_ticket_stats",
	"get_today_checkin_status",
	"get_trending_items",
	"get_warehouses_for_select",
	"log_status_change",
	"lookup_repair_by_number",
	"lookup_repair_by_phone",
	"predict_repair_eta",
	"public_estimate_approval",
	"quick_add_item",
	"quick_create_customer",
	"refresh_gold_rates",
	"run_anomaly_detection",
	"search_customers",
	"simulate_payment_success",
	"submit_expense_claim",
	"suggest_technician",
	"track_trending_click",
	"update_brand",
	"update_item",
	"update_item_group",
	"update_repair_status",
	"update_todo_status",
	"update_warehouse",
]
