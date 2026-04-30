import os

import frappe
from frappe.utils import get_files_path


def create_print_format():
	format_name = "EOD Daily Brief"
	if not frappe.db.exists("Print Format", format_name):
		doc = frappe.new_doc("Print Format")
		doc.name = format_name
		doc.doc_type = "Sales Invoice"  # Or what doc type? The plan doesn't specify. EOD Daily Brief probably doesn't attach to a specific doctype easily unless it's just a general print format or attached to "POS Closing Entry"? Let's assume it's a Server Script or just a Print Format we render manually. Wait, if it's emailed daily, it's rendered by passing HTML, perhaps attaching it to nothing specific, or attaching to "POS Closing Entry". Let's attach it to "POS Profile" as a dummy or "Company". Let's use "Company".
		doc.doc_type = "Company"
		doc.module = "Unified Retail Management System"
		doc.print_format_builder = 0
		doc.print_format_type = "Jinja"
		doc.standard = "Yes"

		# We will set the html later by editing the file in the directory.
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
		print(f"Created Print Format: {format_name}")


create_print_format()
