"""Bench command registrations for Zevar Core."""

import click
from frappe.commands import get_site, pass_context

from zevar_core.migration.commands import import_legacy_data, show_mapping_info
from zevar_core.rag.commands import build_dev_index, build_rag_index, rag_stats


@click.command("fix-desktop-icons")
@click.option("--verbose", is_flag=True, help="Show detailed output")
@pass_context
def fix_desktop_icons(context, verbose=False):
	"""Fix desktop icons, apps screen, and shortcuts for Zevar POS."""
	import frappe

	site = get_site(context)

	frappe.init(site=site)
	frappe.connect()

	try:
		if verbose:
			click.echo("Starting desktop icons fix...")

		from zevar_core.fix_desktop_icons import (
			create_missing_app_icons,
			create_missing_desktop_icons_for_workspaces,
			import_all_desktop_icons,
			verify_and_fix_shortcuts,
		)

		# Import all desktop icons
		if verbose:
			click.echo("Importing desktop icons from all apps...")
		imported, updated, errors = import_all_desktop_icons()

		# Create missing app icons
		if verbose:
			click.echo("Creating missing app icons...")
		create_missing_app_icons()

		# Create desktop icons for workspaces
		if verbose:
			click.echo("Creating desktop icons for workspaces...")
		create_missing_desktop_icons_for_workspaces()

		# Verify shortcuts
		if verbose:
			click.echo("Verifying shortcuts...")
		shortcut_count = verify_and_fix_shortcuts()

		click.echo(f"Desktop icons: {imported} imported, {updated} updated, {errors} errors")
		click.echo(f"Shortcuts: {shortcut_count} shortcuts configured")
		click.echo("Fix complete! Please clear your browser cache.")

	finally:
		frappe.destroy()


commands = [
	import_legacy_data,
	show_mapping_info,
	fix_desktop_icons,
	build_rag_index,
	rag_stats,
	build_dev_index,
]
