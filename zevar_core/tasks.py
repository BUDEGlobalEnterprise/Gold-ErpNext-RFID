"""Scheduled tasks for Zevar Core"""

import frappe
import requests
from frappe.utils import flt, get_pdf

from zevar_core.constants import (
	GOLD_PURITY_RATES,
	SILVER_PURITY_RATES,
	TROY_OZ_TO_GRAMS,
)

GOLD_API_BASE = "https://api.gold-api.com/price"
METALS_LIVE_SPOT_URL = "https://api.metals.live/v1/spot"
GOLDPRICE_ORG_URL = "https://data-asg.goldprice.org/dbXRates/USD"

_UA = {"User-Agent": "Zevar-POS/1.0 (Zevar Jewelers; gold-rate-sync)"}


def _try_gold_api():
	"""Fetch spot prices from gold-api.com (free, no key, reliable).

	Returns (gold_per_oz, silver_per_oz) or None.
	"""
	gold_resp = requests.get(f"{GOLD_API_BASE}/XAU", headers=_UA, timeout=10)
	gold_resp.raise_for_status()
	gold_data = gold_resp.json()
	gold = gold_data.get("price")

	silver_resp = requests.get(f"{GOLD_API_BASE}/XAG", headers=_UA, timeout=10)
	silver_resp.raise_for_status()
	silver_data = silver_resp.json()
	silver = silver_data.get("price")

	if gold and silver:
		return float(gold), float(silver)
	return None


def _try_metals_live():
	"""Fetch spot prices from metals.live (free, no key).

	Returns (gold_per_oz, silver_per_oz) or None.
	"""
	resp = requests.get(METALS_LIVE_SPOT_URL, headers=_UA, timeout=10)
	resp.raise_for_status()
	data = resp.json()
	gold = silver = None
	for item in data:
		if item.get("metal") == "gold":
			gold = item.get("price")
		elif item.get("metal") == "silver":
			silver = item.get("price")
	if gold and silver:
		return float(gold), float(silver)
	return None


def _try_goldprice_org():
	"""Fetch spot prices from goldprice.org.

	Returns (gold_per_oz, silver_per_oz) or None.
	"""
	resp = requests.get(GOLDPRICE_ORG_URL, headers=_UA, timeout=10)
	resp.raise_for_status()
	data = resp.json()
	gold = data.get("items", [{}])[0].get("xauPrice")
	silver = data.get("items", [{}])[0].get("xagPrice")
	if gold and silver:
		return float(gold), float(silver)
	return None


_API_SOURCES = [
	("gold-api.com", _try_gold_api),
	("metals.live", _try_metals_live),
	("goldprice.org", _try_goldprice_org),
]


def fetch_live_metal_rates():
	"""
	Fetches live gold and silver rates from free APIs with automatic fallback.

	API priority:
	  1. gold-api.com (free, no key, most reliable)
	  2. metals.live (free, no key)
	  3. goldprice.org (original source)
	  4. Custom endpoint from Gold Settings (if configured)
	  5. Hardcoded fallback rates

	Stores rates under canonical Kt names (22Kt, 18Kt, etc.) only.
	Old K-form entries are cleaned up automatically.

	Returns:
		dict: Current rates with metals, purities, and metadata.
	"""
	rates = {"gold": {}, "silver": {}, "source": "live", "error": None}
	prices = None
	source_label = "gold-api.com"

	try:
		if frappe.db.exists("Gold Settings", "Gold Settings"):
			settings = frappe.get_single("Gold Settings")
			if settings.api_endpoint:
				resp = requests.get(settings.api_endpoint, headers=_UA, timeout=10)
				resp.raise_for_status()
				prices = _parse_custom_api(resp.json())
				source_label = "custom"

		if not prices:
			for name, fn in _API_SOURCES:
				try:
					prices = fn()
					if prices:
						source_label = name
						break
				except Exception:
					frappe.logger().info(f"{name} unreachable, trying next source")

		if prices:
			gold_per_gram = prices[0] / TROY_OZ_TO_GRAMS
			silver_per_gram = prices[1] / TROY_OZ_TO_GRAMS
			rates["source"] = source_label

			_update_all_rates(gold_per_gram, silver_per_gram, rates)

			frappe.db.commit()  # nosemgrep: frappe-semgrep-rules/rules.frappe-manual-commit
			_cleanup_legacy_k_entries()
			frappe.logger().info(
				f"Metal rates updated from {source_label}: Gold 22Kt=${gold_per_gram * 0.916:.2f}/g, Silver 925=${silver_per_gram * 0.925:.2f}/g"
			)
			return rates

	except Exception as e:
		frappe.logger().error(f"Metal rate fetch failed: {e!s}")

	rates["source"] = "fallback"
	rates["error"] = "All APIs unreachable"

	_update_all_rates(
		4400.0 / TROY_OZ_TO_GRAMS,
		33.0 / TROY_OZ_TO_GRAMS,
		rates,
	)
	frappe.db.commit()

	return rates


def _parse_custom_api(data):
	"""Try to extract (gold_oz, silver_oz) from a custom API response."""
	if isinstance(data, list):
		gold = silver = None
		for item in data:
			if item.get("metal") == "gold":
				gold = item.get("price") or item.get("xauPrice")
			elif item.get("metal") == "silver":
				silver = item.get("price") or item.get("xagPrice")
		if gold and silver:
			return float(gold), float(silver)
	if isinstance(data, dict):
		items = data.get("items", [data])
		g = items[0].get("xauPrice") or items[0].get("gold_price")
		s = items[0].get("xagPrice") or items[0].get("silver_price")
		if g and s:
			return float(g), float(s)
	return None


def _update_all_rates(gold_per_gram, silver_per_gram, rates):
	"""Update Gold Rate Log for all purities (canonical + alias entries)."""
	source = rates.get("source", "live")

	for purity, multiplier in GOLD_PURITY_RATES.items():
		rate = round(gold_per_gram * multiplier, 2)
		_update_rate("Yellow Gold", purity, rate, source)
		rates["gold"][purity] = rate

	for purity, multiplier in SILVER_PURITY_RATES.items():
		rate = round(silver_per_gram * multiplier, 2)
		_update_rate("Silver", purity, rate, source)
		rates["silver"][purity] = rate

	rates["gold_per_gram_raw"] = round(gold_per_gram, 2)
	rates["silver_per_gram_raw"] = round(silver_per_gram, 2)


def _update_rate(metal, purity, rate, source="live"):
	"""Helper to update or create a rate entry."""
	from frappe.utils import now_datetime

	existing = frappe.db.exists("Gold Rate Log", {"metal": metal, "purity": purity})

	if existing:
		frappe.db.set_value(
			"Gold Rate Log",
			existing,
			{"rate_per_gram": rate, "source": source, "timestamp": now_datetime()},
		)
	else:
		frappe.get_doc(
			{
				"doctype": "Gold Rate Log",
				"metal": metal,
				"purity": purity,
				"rate_per_gram": rate,
				"source": source,
			}
		).insert(ignore_permissions=True)


# Keep the old function name for backward compatibility
def fetch_live_gold_rate():
	"""Alias for backward compatibility."""
	fetch_live_metal_rates()


def _cleanup_legacy_k_entries():
	"""Remove old K-form Gold Rate Log entries that are superseded by Kt canonical entries."""
	for old_purity in ["24K", "22K", "18K", "14K", "10K"]:
		for name in frappe.get_all(
			"Gold Rate Log",
			filters={"purity": old_purity},
			pluck="name",
		):
			frappe.delete_doc("Gold Rate Log", name, ignore_permissions=True, force=True)
	frappe.db.commit()


def email_eod_brief():
	"""Emails the EOD Daily Brief to owners."""
	owners = frappe.get_all("Has Role", filters={"role": "Owner", "parenttype": "User"}, fields=["parent"])
	recipients = [o.parent for o in owners]

	if not recipients:
		return

	html = frappe.get_print("Company", "Zevar Jewelers", "EOD Daily Brief", as_pdf=False)

	frappe.sendmail(
		recipients=recipients,
		subject=f"End of Day Brief - {frappe.utils.formatdate(frappe.utils.today())}",
		message=html,
	)


def expire_stale_reservations():
	now = frappe.utils.now_datetime()

	expired = frappe.get_all(
		"Stock Reservation",
		filters={
			"status": "Active",
			"hold_until": ["<", now],
			"docstatus": 1,
		},
		fields=["name", "serial_no", "customer"],
	)

	for res in expired:
		try:
			doc = frappe.get_doc("Stock Reservation", res.name)
			doc.cancel()
			frappe.db.commit()

			assoc_email = frappe.db.get_value("User", {"full_name": res.customer}, "email")
			if assoc_email:
				frappe.sendmail(
					recipients=[assoc_email],
					subject=f"Reservation Expired: {res.serial_no}",
					message=f"Reservation {res.name} for {res.serial_no} has expired and stock has been released.",
				)
		except Exception:
			frappe.log_error(
				title=f"Failed to expire reservation {res.name}",
				message=frappe.get_traceback(),
			)


def reorder_suggestion_job():
	from frappe.utils import add_days, today

	cutoff = add_days(today(), -30)
	company = frappe.defaults.get_global_default("company") or "Zevar Jewelers"
	cost_center = frappe.get_cached_value("Company", company, "cost_center")

	items = frappe.get_all(
		"Item",
		filters={"is_stock_item": 1, "disabled": 0},
		fields=["name", "item_name", "item_group"],
	)

	for item in items:
		velocity = frappe.db.sql(
			"""
			SELECT COUNT(*) as sold
			FROM `tabSales Invoice Item` sii
			JOIN `tabSales Invoice` si ON sii.parent = si.name
			WHERE sii.item_code = %s AND si.posting_date >= %s AND si.docstatus = 1
			""",
			(item.name, cutoff),
			as_dict=True,
		)
		daily_vel = flt(velocity[0].sold) / 30.0 if velocity else 0

		if daily_vel <= 0:
			continue

		total_on_hand = flt(
			frappe.db.sql(
				"SELECT SUM(actual_qty) FROM `tabBin` WHERE item_code = %s AND actual_qty > 0",
				(item.name,),
			)[0][0]
			or 0
		)

		safety_stock = daily_vel * REORDER_SAFETY_DAYS

		if total_on_hand < safety_stock:
			existing = frappe.db.exists(
				"Material Request",
				{"item_code": item.name, "status": ["in", ["Draft", "Open"]]},
			)
			if existing:
				continue

			mr = frappe.new_doc("Material Request")
			mr.material_request_type = "Purchase"
			mr.company = company
			mr.cost_center = cost_center
			mr.schedule_date = add_days(today(), 7)
			mr.append(
				"items",
				{
					"item_code": item.name,
					"qty": max(1, int(safety_stock - total_on_hand)),
					"schedule_date": add_days(today(), 7),
					"cost_center": cost_center,
				},
			)
			mr.insert(ignore_permissions=True)


def audit_cadence_heartbeat():
	"""Generate Audit Plans based on Audit Policy cadence settings.

	Runs daily at 05:00. For each store, checks when the last audit of each scope
	was completed and creates a new Audit Plan if the cadence interval has elapsed.
	"""
	from frappe.utils import add_days, getdate, today

	policy_data = _get_audit_policy_for_scheduler()

	if not policy_data.get("enable_audit_schedule"):
		return

	cadence_map = {
		"Weekly Showcase": policy_data["showcase_cadence_days"],
		"Monthly Backstock": policy_data["backstock_cadence_days"],
		"Quarterly Full": policy_data["full_store_cadence_days"],
	}

	stores = _get_stores_for_audit()

	for store in stores:
		for scope, cadence_days in cadence_map.items():
			# Skip if a pending plan already exists
			existing = frappe.get_all(
				"Audit Plan",
				filters={
					"store_location": store,
					"scope": scope,
					"status": ["in", ["Scheduled", "In Progress"]],
				},
				limit=1,
			)
			if existing:
				continue

			# Check last completed audit for this scope+store
			last_audit = frappe.get_all(
				"Case Audit Session",
				filters={
					"store_location": store,
					"scope": scope,
					"docstatus": 1,
				},
				fields=["MAX(completed_at) as last_completed"],
				limit=1,
			)

			last_completed = None
			if last_audit and last_audit[0].get("last_completed"):
				last_completed = getdate(last_audit[0]["last_completed"])

			# Determine if a new audit is due
			if last_completed:
				next_due = add_days(last_completed, cadence_days)
				if getdate(today()) < next_due:
					continue

			assigned_user = _get_store_manager()

			plan = frappe.new_doc("Audit Plan")
			plan.store_location = store
			plan.scope = scope
			plan.scheduled_for = today()
			plan.assigned_to = assigned_user or ""
			plan.status = "Scheduled"
			plan.notes = f"Auto-generated by audit cadence heartbeat. Cadence: {cadence_days} days."
			plan.insert(ignore_permissions=True)

			frappe.logger().info(f"Created Audit Plan {plan.name} for {store} - {scope}")

	# Mark overdue plans as Missed
	overdue = frappe.get_all(
		"Audit Plan",
		filters={
			"status": "Scheduled",
			"scheduled_for": ["<", today()],
		},
	)
	for p in overdue:
		frappe.db.set_value("Audit Plan", p["name"], "status", "Missed")

	# Daily spot check for the designated high-value case
	spot_case = policy_data.get("daily_spot_case")
	if spot_case and frappe.db.exists("Display Case", spot_case):
		today_spot = frappe.get_all(
			"Audit Plan",
			filters={
				"scope": "Daily Spot",
				"scheduled_for": today(),
				"status": ["in", ["Scheduled", "In Progress"]],
			},
			limit=1,
		)
		if not today_spot:
			case_wh = frappe.db.get_value("Display Case", spot_case, "warehouse")
			if case_wh:
				plan = frappe.new_doc("Audit Plan")
				plan.store_location = case_wh
				plan.scope = "Daily Spot"
				plan.scheduled_for = today()
				plan.status = "Scheduled"
				plan.notes = f"Daily spot-check for {spot_case}"
				plan.insert(ignore_permissions=True)


def _get_audit_policy_for_scheduler():
	"""Safely get audit policy settings for the scheduler, returning defaults on error."""
	defaults = {
		"enable_audit_schedule": 1,
		"showcase_cadence_days": 7,
		"backstock_cadence_days": 30,
		"full_store_cadence_days": 90,
		"daily_spot_case": None,
		"variance_threshold_dollars": 500,
		"variance_pieces_hard_stop": 3,
	}
	try:
		if not frappe.db.exists("DocType", "Audit Policy"):
			return defaults
		doc = frappe.get_single("Audit Policy")
		return {
			"enable_audit_schedule": doc.enable_audit_schedule,
			"showcase_cadence_days": doc.showcase_cadence_days or 7,
			"backstock_cadence_days": doc.backstock_cadence_days or 30,
			"full_store_cadence_days": doc.full_store_cadence_days or 90,
			"daily_spot_case": doc.daily_spot_case,
			"variance_threshold_dollars": doc.variance_threshold_dollars or 500,
			"variance_pieces_hard_stop": doc.variance_pieces_hard_stop or 3,
		}
	except Exception:
		return defaults


def _get_stores_for_audit():
	"""Get store warehouse names for audit scheduling."""
	if frappe.db.exists("DocType", "Store Location"):
		stores = frappe.get_all("Store Location", fields=["default_warehouse"], limit=50)
		wh_list = [s.default_warehouse for s in stores if s.default_warehouse]
		if wh_list:
			return wh_list

	# Fallback: group warehouses matching store pattern
	stores = frappe.get_all(
		"Warehouse", filters={"is_group": 1, "name": ["like", "%-01"]}, pluck="name", limit=50
	)
	if stores:
		return stores

	# Last resort: all group warehouses
	return frappe.get_all("Warehouse", filters={"is_group": 1}, pluck="name", limit=50)


def _get_store_manager():
	"""Get a store manager user to assign audits to."""
	managers = frappe.get_all(
		"Has Role",
		filters={"role": ["in", ["Sales Manager", "Store Manager"]], "parenttype": "User"},
		fields=["parent"],
		limit=1,
	)
	if managers:
		return managers[0]["parent"]
	return None


def consignment_overdue_alert():
	consignment_warehouses = frappe.get_all(
		"Warehouse",
		filters={"warehouse_name": ["like", "Consignment%"]},
		fields=["name", "warehouse_name"],
	)

	for wh in consignment_warehouses:
		bins = frappe.get_all(
			"Bin",
			filters={"warehouse": wh.name, "actual_qty": [">", 0]},
			fields=["item_code", "actual_qty"],
		)
		if not bins:
			continue

		owners = frappe.get_all(
			"Has Role",
			filters={"role": "Owner", "parenttype": "User"},
			fields=["parent"],
		)
		recipients = [o.parent for o in owners]
		if recipients:
			frappe.sendmail(
				recipients=recipients,
				subject=f"Overdue Consignment: {wh.warehouse_name}",
				message=f"Consignment warehouse {wh.warehouse_name} still has {len(bins)} items. Please reconcile.",
			)

		from zevar_core.services.inventory_events import _log_inventory_event

		_log_inventory_event(
			"consignment_overdue",
			"Warehouse",
			wh.name,
			f"Consignment {wh.warehouse_name} has {len(bins)} items overdue for return",
		)


def serial_last_seen_backfill():
	now = frappe.utils.now_datetime()
	yesterday = frappe.utils.add_days(frappe.utils.today(), -1)

	sles = frappe.get_all(
		"Stock Ledger Entry",
		filters={"posting_date": [">=", yesterday], "docstatus": 1},
		fields=["serial_no"],
		limit=5000,
	)

	serials_seen = set()
	for sle in sles:
		if sle.serial_no:
			for sn in sle.serial_no.split("\n"):
				sn = sn.strip()
				if sn and sn not in serials_seen:
					serials_seen.add(sn)
					frappe.db.set_value(
						"Serial No",
						sn,
						{
							"custom_last_seen_at": now,
							"custom_last_seen_by": "System",
						},
						update_modified=False,
					)


REORDER_SAFETY_DAYS = 14


def run_report_subscriptions():
	"""Evaluate due Report Subscriptions and deliver via email/WhatsApp."""
	from frappe.utils import now_datetime

	now = now_datetime()
	subs = frappe.get_all(
		"Report Subscription",
		filters={"enabled": 1, "next_run": ["<=", now]},
		fields=[
			"name",
			"user",
			"report_id",
			"report_title",
			"delivery_method",
			"export_format",
			"filters_json",
			"recipient_email",
			"recipient_phone",
			"cron_expression",
		],
	)

	for sub in subs:
		try:
			_deliver_report_subscription(sub)
			frappe.db.set_value(
				"Report Subscription",
				sub.name,
				{
					"last_run": now,
				},
			)
			_update_next_run(sub.name, sub.cron_expression)
			frappe.db.commit()
		except Exception:
			frappe.log_error(
				title=f"Report Subscription failed: {sub.name}",
				message=frappe.get_traceback(),
			)


def _deliver_report_subscription(sub):
	report_id = sub.report_id
	report_name = _resolve_frappe_report_name(report_id)
	if not report_name:
		return

	filters = {}
	if sub.filters_json:
		try:
			import json

			filters = json.loads(sub.filters_json)
		except Exception:
			filters = {}

	if sub.delivery_method in ("Email", "Both"):
		fmt = sub.export_format or "PDF"
		if fmt == "PDF":
			content = _generate_report_pdf(report_name, filters)
			_attach = [{"fname": f"{report_id}.pdf", "fcontent": content}]
		elif fmt == "CSV":
			data = _generate_report_csv(report_name, filters)
			_attach = [{"fname": f"{report_id}.csv", "fcontent": data}]
		else:
			data = _generate_report_csv(report_name, filters)
			_attach = [{"fname": f"{report_id}.xlsx", "fcontent": data}]

		recipients = (
			[sub.recipient_email] if sub.recipient_email else [frappe.db.get_value("User", sub.user, "email")]
		)
		frappe.sendmail(
			recipients=recipients,
			subject=f"Scheduled Report: {sub.report_title or report_id}",
			message=f"Your scheduled report <strong>{sub.report_title}</strong> is attached.",
			attachments=_attach,
		)

	if sub.delivery_method in ("WhatsApp", "Both"):
		pass


def _resolve_frappe_report_name(report_id):
	from zevar_core.api.reports import REPORT_CATALOG

	for r in REPORT_CATALOG:
		if r["id"] == report_id:
			return r.get("report_name")
	return None


def _generate_report_pdf(report_name, filters):
	report = frappe.get_doc("Report", report_name)
	data = report.get_data(filters=filters) if hasattr(report, "get_data") else []
	html = (
		frappe.render_template("templates/report.html", {"data": data, "title": report_name})
		if data
		else f"<p>Report: {report_name}</p>"
	)
	return get_pdf(html)


def _generate_report_csv(report_name, filters):
	report = frappe.get_doc("Report", report_name)
	data = report.get_data(filters=filters) if hasattr(report, "get_data") else []
	return frappe.as_csv(data) if data else ""


def _update_next_run(name, cron_expression):
	try:
		from croniter import croniter
		from frappe.utils import now_datetime

		cron = croniter(cron_expression, now_datetime())
		frappe.db.set_value("Report Subscription", name, "next_run", cron.get_next(frappe.utils.Datetime))
	except Exception:
		frappe.db.set_value("Report Subscription", name, "next_run", None)
