"""
Repair broken Desktop Layout parent state and invalid custom app shortcuts.

This patch restores app-parent groupings that were dropped from saved layout JSON
and converts custom external "App" shortcuts without a backing installed app into
normal Desktop Icon links so they render and save correctly.
"""

from __future__ import annotations

import json

import frappe


def execute() -> None:
	"""Repair broken desktop layout parent state and invalid external app shortcuts."""
	converted_labels = _repair_invalid_external_app_shortcuts()
	repair_layouts(converted_labels)
	frappe.db.commit()  # nosemgrep


def _repair_invalid_external_app_shortcuts() -> set[str]:
	"""Convert invalid external App shortcuts without backing apps into Link icons."""
	converted_labels: set[str] = set()
	icons = frappe.get_all(
		"Desktop Icon",
		fields=["name", "label", "icon_type", "link_type", "app"],
		filters={"icon_type": "App", "link_type": "External"},
	)

	for icon in icons:
		if icon.app:
			continue

		frappe.db.set_value("Desktop Icon", icon.name, "icon_type", "Link", update_modified=False)
		if icon.label:
			converted_labels.add(icon.label)

	return converted_labels


def repair_layouts(converted_labels: set[str]) -> None:
	"""Restore app-parent groupings in saved Desktop Layout JSON and update icon types."""
	icon_rows = frappe.get_all(
		"Desktop Icon",
		fields=[
			"label",
			"parent_icon",
			"icon_type",
			"link_type",
			"app",
			"link",
			"bg_color",
			"logo_url",
			"icon_image",
			"standard",
			"restrict_removal",
		],
	)
	icon_map = {row.label: row for row in icon_rows if row.label}
	valid_parents = {row.label for row in icon_rows if row.label and row.icon_type in ("App", "Folder")}

	layout_docs = frappe.get_all("Desktop Layout", fields=["name", "layout"])

	for layout_doc in layout_docs:
		if not layout_doc.layout:
			continue

		try:
			layout = json.loads(layout_doc.layout)
		except json.JSONDecodeError:
			frappe.log_error(
				f"Invalid JSON in Desktop Layout {layout_doc.name}",
				"repair_desktop_layout_and_shortcuts",
			)
			continue

		changed = False
		for item in layout:
			label = item.get("label")
			if not label or label not in icon_map:
				continue

			icon_row = icon_map[label]
			record_parent = icon_row.parent_icon
			layout_parent = item.get("parent_icon")

			if label in converted_labels and item.get("icon_type") == "App":
				item["icon_type"] = "Link"
				changed = True

			if layout_parent and layout_parent not in valid_parents:
				item["parent_icon"] = record_parent if record_parent in valid_parents else None
				layout_parent = item.get("parent_icon")
				changed = True

			if not layout_parent and record_parent and record_parent in valid_parents:
				parent_row = icon_map.get(record_parent)
				if parent_row and parent_row.icon_type in ("App", "Folder"):
					item["parent_icon"] = record_parent
					changed = True

		if changed:
			frappe.db.set_value(
				"Desktop Layout",
				layout_doc.name,
				"layout",
				json.dumps(layout),
				update_modified=False,
			)
