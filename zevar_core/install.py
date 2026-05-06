"""
Zevar Core Installation Utilities

Functions to set up required data on app installation.
"""

import json
import os

import frappe
from frappe import _
from frappe.modules.import_file import import_file_by_path

from zevar_core.shortcut_seed import get_default_shortcuts


def _shortcut_target_exists(shortcut_data):
	link_type = shortcut_data.get("link_type")
	link_to = shortcut_data.get("link_to")

	if link_type == "DocType":
		return frappe.db.exists("DocType", link_to)
	if link_type == "Page":
		return frappe.db.exists("Page", link_to)
	if link_type == "Report":
		return frappe.db.exists("Report", link_to)
	return True


LEGACY_DEFAULT_SHORTCUTS = {
	"POS Terminal",
	"Employee Portal",
	"Layaway Contracts",
	"Repair Orders",
	"Trade-Ins",
	"Gift Cards",
	"Jewelry Appraisal",
	"Commission Tracking",
	"Gold Rate Log",
	"Customer Ledger",
	"Store Locations",
	"Inventory",
}


def _cleanup_managed_shortcuts(default_shortcuts):
	managed_names = {shortcut["shortcut_name"] for shortcut in default_shortcuts}
	target_names = managed_names | LEGACY_DEFAULT_SHORTCUTS
	if not target_names:
		return

	records = frappe.get_all(
		"Zevar Desk Shortcut",
		filters={"shortcut_name": ("in", list(target_names))},
		fields=["name", "shortcut_name", "modified"],
		order_by="shortcut_name asc, modified desc",
	)

	grouped = {}
	for record in records:
		grouped.setdefault(record.shortcut_name, []).append(record)

	for shortcut_name, items in grouped.items():
		if shortcut_name not in managed_names:
			for item in items:
				frappe.delete_doc("Zevar Desk Shortcut", item.name, ignore_permissions=True, force=True)
			continue

		for duplicate in items[1:]:
			frappe.delete_doc("Zevar Desk Shortcut", duplicate.name, ignore_permissions=True, force=True)


def create_required_modes_of_payment():
	"""
	Create all Mode of Payment records required by the POS system.

	The frontend checkout supports these payment methods. Each must exist
	as a Frappe 'Mode of Payment' record for Sales Invoice validation to pass.
	"""
	if not frappe.db.exists("DocType", "Mode of Payment"):
		frappe.logger().warning(
			"Skipping Mode of Payment bootstrap: DocType 'Mode of Payment' does not exist yet."
		)
		return

	company = frappe.db.get_single_value("Global Defaults", "default_company")
	abbr = frappe.get_cached_value("Company", company, "abbr") if company else None

	cash_account = None
	bank_account = None
	if company:
		cash_account = frappe.db.get_value("Account", {"account_type": "Cash", "company": company}, "name")
		if not cash_account:
			cash_account = frappe.db.get_value(
				"Account",
				{"account_name": "Cash", "company": company, "is_group": 0},
				"name",
			)
		bank_accounts = frappe.get_all(
			"Account",
			filters={"account_type": "Bank", "company": company, "is_group": 0},
			pluck="name",
			limit=1,
		)
		bank_account = bank_accounts[0] if bank_accounts else cash_account

	financier_map = {
		"Synchrony": f"Asset — A/R Synchrony - {abbr}" if abbr else None,
		"AFF": f"Asset — A/R AFF - {abbr}" if abbr else None,
		"CIMA": f"Asset — A/R CIMA - {abbr}" if abbr else None,
		"Progressive": f"Asset — A/R Progressive - {abbr}" if abbr else None,
		"Snap": f"Asset — A/R Snap - {abbr}" if abbr else None,
	}

	account_map = {
		"Cash": cash_account,
		"Credit Card": bank_account,
		"Debit Card": bank_account,
		"Check": bank_account,
		"Wire Transfer": bank_account,
		"Zelle": cash_account,
		"Gift Card": cash_account,
		"Trade-In": cash_account,
		"Apple Pay": bank_account,
		"Google Pay": bank_account,
		"Venmo": cash_account,
		"Cash App": cash_account,
		"Synchrony": financier_map.get("Synchrony"),
		"AFF": financier_map.get("AFF"),
		"CIMA": financier_map.get("CIMA"),
		"Progressive": financier_map.get("Progressive"),
		"Snap": financier_map.get("Snap"),
		"In-House Finance": cash_account,
	}

	modes = [
		{"mode_of_payment": "Cash", "type": "Cash"},
		{"mode_of_payment": "Credit Card", "type": "Bank"},
		{"mode_of_payment": "Debit Card", "type": "Bank"},
		{"mode_of_payment": "Check", "type": "Bank"},
		{"mode_of_payment": "Wire Transfer", "type": "Bank"},
		{"mode_of_payment": "Zelle", "type": "General"},
		{"mode_of_payment": "Gift Card", "type": "General"},
		{"mode_of_payment": "Trade-In", "type": "General"},
		{"mode_of_payment": "Apple Pay", "type": "Bank"},
		{"mode_of_payment": "Google Pay", "type": "Bank"},
		{"mode_of_payment": "Venmo", "type": "General"},
		{"mode_of_payment": "Cash App", "type": "General"},
		{"mode_of_payment": "Synchrony", "type": "General"},
		{"mode_of_payment": "AFF", "type": "General"},
		{"mode_of_payment": "CIMA", "type": "General"},
		{"mode_of_payment": "Progressive", "type": "General"},
		{"mode_of_payment": "Snap", "type": "General"},
		{"mode_of_payment": "In-House Finance", "type": "General"},
	]

	for mode in modes:
		mode_name = mode["mode_of_payment"]
		target_account = account_map.get(mode_name)

		if frappe.db.exists("Mode of Payment", mode_name):
			doc = frappe.get_doc("Mode of Payment", mode_name)
		else:
			doc = frappe.new_doc("Mode of Payment")
			doc.mode_of_payment = mode_name
			doc.type = mode["type"]
			doc.enabled = 1

		doc.type = mode["type"]

		if company and target_account and frappe.db.exists("Account", target_account):
			account_exists = False
			for acc in doc.accounts:
				if acc.company == company:
					acc.default_account = target_account
					account_exists = True
					break

			if not account_exists:
				doc.append("accounts", {"company": company, "default_account": target_account})

		try:
			doc.save(ignore_permissions=True)
		except Exception:
			frappe.log_error(f"install: Failed to save Mode of Payment '{mode_name}'")

	frappe.db.commit()  # nosemgrep (manual commit during install)


def import_desktop_icons():
	"""
	Import desktop icons from JSON files in the desktop_icon directory.

	Desktop icons are stored as JSON files but are not automatically imported
	during app installation. This function imports them to make shortcuts
	like Layaway List and Inventory appear on the desk.
	"""
	app_path = frappe.get_app_path("zevar_core")
	icons_dir = os.path.join(app_path, "zevar_core", "desktop_icon")

	if not os.path.exists(icons_dir):
		return

	for fname in os.listdir(icons_dir):
		if fname.endswith(".json"):
			file_path = os.path.join(icons_dir, fname)
			try:
				with open(file_path) as f:  # nosemgrep
					icon_data = json.load(f)

				# Must have doctype key to be valid
				if not icon_data.get("doctype"):
					frappe.log_error(
						f"Desktop icon {fname} missing 'doctype' key",
						"Desktop Icon Import",
					)
					continue

				icon_name = icon_data.get("name")
				if icon_name and not frappe.db.exists("Desktop Icon", icon_name):
					import_file_by_path(file_path)
					frappe.db.commit()  # nosemgrep
			except Exception as e:
				frappe.log_error(f"Failed to import desktop icon {fname}: {e}", "Desktop Icon Import")

	# Clear cache to ensure icons appear immediately
	frappe.cache.delete_key("desktop_icons")
	frappe.cache.delete_key("bootinfo")


def import_workspaces():
	"""
	Import workspace JSON files.

	Workspaces are stored as JSON files and need to be imported
	to appear in the workspace sidebar.
	"""
	import json

	app_path = frappe.get_app_path("zevar_core")
	workspaces_dir = os.path.join(app_path, "zevar_core", "workspace")

	if not os.path.exists(workspaces_dir):
		return

	for workspace_name in os.listdir(workspaces_dir):
		workspace_path = os.path.join(workspaces_dir, workspace_name)
		if os.path.isdir(workspace_path):
			json_file = os.path.join(workspace_path, f"{workspace_name}.json")
			if os.path.exists(json_file):
				try:
					# Read the JSON to get the actual workspace name (not directory name)
					with open(json_file) as f:  # nosemgrep
						workspace_data = json.load(f)
					actual_name = workspace_data.get("name") or workspace_data.get("label") or workspace_name

					if not frappe.db.exists("Workspace", actual_name):
						import_file_by_path(json_file)
						frappe.db.commit()  # nosemgrep
				except Exception as e:
					frappe.log_error(
						f"Failed to import workspace {workspace_name}: {e}",
						"Workspace Import",
					)


def create_default_desk_shortcuts():
	"""
	Create or update the default desk shortcuts for Zevar Core.

	The custom shortcut registry powers both the custom Zevar desk page and
	the injected workspace shortcuts, so we keep it synchronized during install
	and migrate.
	"""
	if not frappe.db.exists("DocType", "Zevar Desk Shortcut"):
		return

	default_shortcuts = get_default_shortcuts()
	_cleanup_managed_shortcuts(default_shortcuts)
	existing_roles = set(frappe.get_all("Role", pluck="name"))

	for shortcut_data in default_shortcuts:
		shortcut_name = shortcut_data["shortcut_name"]
		if not _shortcut_target_exists(shortcut_data):
			frappe.logger().warning(
				"Skipping desk shortcut %s because target %s (%s) is missing",
				shortcut_name,
				shortcut_data.get("link_to"),
				shortcut_data.get("link_type"),
			)
			continue
		existing_name = frappe.db.get_value(
			"Zevar Desk Shortcut",
			{"shortcut_name": shortcut_name},
			"name",
		)
		if existing_name:
			doc = frappe.get_doc("Zevar Desk Shortcut", existing_name)
		else:
			doc = frappe.new_doc("Zevar Desk Shortcut")
			doc.shortcut_name = shortcut_name

		managed_fields = {
			"section_name": shortcut_data.get("section_name") or "Quick Access",
			"link_type": shortcut_data.get("link_type"),
			"link_to": shortcut_data.get("link_to"),
			"description": shortcut_data.get("description", ""),
			"sequence": shortcut_data.get("sequence", 100),
			"keyboard_shortcut": shortcut_data.get("keyboard_shortcut", ""),
			"show_on_desk": 1,
			"show_on_workspace": 1,
		}
		for fieldname, value in managed_fields.items():
			setattr(doc, fieldname, value)

		# Preserve manual visual changes on existing shortcuts where possible.
		if not doc.get("icon_name") or not existing_name:
			doc.icon_name = shortcut_data.get("icon_name", "star")
		if not doc.get("color") or not existing_name:
			doc.color = shortcut_data.get("color", "#2563eb")

		doc.open_in_new_tab = shortcut_data.get("open_in_new_tab", 0)
		doc.set("roles", [])
		for role in shortcut_data.get("roles", []):
			if role in existing_roles:
				doc.append("roles", {"role": role})

		if existing_name:
			doc.save(ignore_permissions=True)
		else:
			doc.insert(ignore_permissions=True)

	frappe.cache.delete_key("zevar_shortcuts_registry")
	frappe.cache.delete_key("zevar_desk_shortcuts")
	frappe.db.commit()  # nosemgrep
