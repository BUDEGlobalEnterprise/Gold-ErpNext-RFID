"""
Clean up legacy desktop folder state.

This patch normalizes custom Desktop Icon folders created during the broken
edit-mode flow by renaming legacy "Untitled" folders and fixing saved layout
references that still point to stale folder labels.
"""

from __future__ import annotations

import json

import frappe


def execute() -> None:
	"""Rename legacy Untitled folders and update Desktop Layout references."""
	rename_map = _rename_untitled_folders()
	_update_desktop_layouts(rename_map)
	frappe.db.commit()  # nosemgrep


def _rename_untitled_folders() -> dict[str, str]:
	"""Find and rename all 'Untitled' folders to sequential 'Folder N' labels."""
	folders = frappe.get_all(
		"Desktop Icon",
		fields=["name", "label"],
		filters={"icon_type": "Folder"},
		order_by="creation asc",
	)
	existing_labels = {folder.label for folder in folders if folder.label}
	rename_map: dict[str, str] = {}

	for folder in folders:
		if not folder.label or not folder.label.startswith("Untitled"):
			continue

		new_label = _get_next_folder_label(existing_labels)
		frappe.rename_doc(
			"Desktop Icon",
			folder.name,
			new_label,
			force=True,
			ignore_if_exists=True,
			show_alert=False,
		)
		rename_map[folder.label] = new_label
		existing_labels.add(new_label)

	return rename_map


_next_folder_index: int = 1


def _get_next_folder_label(existing_labels: set[str]) -> str:
	"""Return the next available 'Folder N' label not in existing_labels."""
	global _next_folder_index
	while f"Folder {_next_folder_index}" in existing_labels:
		_next_folder_index += 1
	label = f"Folder {_next_folder_index}"
	_next_folder_index += 1
	return label


def _update_desktop_layouts(rename_map: dict[str, str]) -> None:
	"""Update all Desktop Layout docs to reference renamed folders and remove stale parents."""
	layout_docs = frappe.get_all("Desktop Layout", fields=["name", "layout"])
	valid_folders = set(
		frappe.get_all(
			"Desktop Icon",
			filters={"icon_type": ["in", ["Folder", "App"]]},
			pluck="label",
		)
	)

	for layout_doc in layout_docs:
		if not layout_doc.layout:
			continue

		try:
			layout = json.loads(layout_doc.layout)
		except json.JSONDecodeError:
			continue

		changed = False
		for icon in layout:
			if not isinstance(icon, dict):
				continue

			old_label = icon.get("label")
			if old_label in rename_map:
				icon["label"] = rename_map[old_label]
				changed = True

			parent_icon = icon.get("parent_icon")
			if parent_icon in rename_map:
				icon["parent_icon"] = rename_map[parent_icon]
				parent_icon = icon["parent_icon"]
				changed = True

			if parent_icon and parent_icon not in valid_folders:
				icon["parent_icon"] = None
				changed = True

		if changed:
			frappe.db.set_value(
				"Desktop Layout",
				layout_doc.name,
				"layout",
				json.dumps(layout),
				update_modified=False,
			)
