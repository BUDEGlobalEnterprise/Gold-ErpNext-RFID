# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

CACHE_KEYS = ("zevar_shortcuts_registry", "zevar_desk_shortcuts")


class ZevarDeskShortcut(Document):
	# pylint: disable=no-member

	def validate(self):
		self.section_name = (self.section_name or "Quick Access").strip()
		self.validate_keyboard_shortcut()
		self.validate_link()

	def validate_keyboard_shortcut(self):
		"""Validate keyboard shortcut format."""
		if self.keyboard_shortcut:
			shortcut = self.keyboard_shortcut.lower().strip()
			valid_modifiers = ["alt", "ctrl", "shift", "meta"]
			parts = shortcut.split("+")

			if len(parts) < 2:
				frappe.throw(_("Keyboard shortcut must include at least one modifier key (alt, ctrl, shift)"))

			for part in parts[:-1]:
				if part.strip() not in valid_modifiers:
					frappe.throw(_("Invalid modifier key '{0}'. Use: alt, ctrl, shift, or meta").format(part))

	def validate_link(self):
		"""Validate link based on link type."""
		if self.link_type == "DocType":
			if not frappe.db.exists("DocType", self.link_to):
				frappe.throw(_("DocType '{0}' does not exist").format(self.link_to))
		elif self.link_type == "Page":
			if not frappe.db.exists("Page", self.link_to):
				frappe.throw(_("Page '{0}' does not exist").format(self.link_to))
		elif self.link_type == "Report":
			if not frappe.db.exists("Report", self.link_to):
				frappe.throw(_("Report '{0}' does not exist").format(self.link_to))

	def on_trash(self):
		"""Clear cache when shortcut is deleted."""
		clear_shortcut_cache()

	def on_update(self):
		"""Clear cache when shortcut is updated."""
		clear_shortcut_cache()


def clear_shortcut_cache():
	for cache_key in CACHE_KEYS:
		frappe.cache.delete_key(cache_key)
