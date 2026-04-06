"""
Import all desktop icons from all installed apps.

This patch ensures that desktop icons from ERPNext, HRMS, Frappe, and other
apps are properly imported into the database so they appear on the desktop.
"""

import frappe


def execute():
    """Execute the desktop icons import."""
    from zevar_core.fix_desktop_icons import (
        create_missing_app_icons,
        create_missing_desktop_icons_for_workspaces,
        import_all_desktop_icons,
    )

    # Import all desktop icons from all apps
    imported, updated, errors = import_all_desktop_icons()

    # Create missing app icons
    create_missing_app_icons()

    # Create desktop icons for workspaces
    create_missing_desktop_icons_for_workspaces()

    frappe.msgprint(
        f"Desktop icons import complete: {imported} imported, {updated} updated, {errors} errors"
    )
