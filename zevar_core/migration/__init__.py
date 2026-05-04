"""
Zevar Core Data Migration Module

This module provides utilities for importing legacy data from
Visual FoxPro (DBF) format into Zevar DocTypes.

Main Components:
- foxpro_import: DBF file parser and field mappers
- foxpro_import_extended: Extended imports (appraisals, layaway, etc.)
- commands: Bench commands for running migrations

Usage:
    bench --site <site> zevar-import-legacy /path/to/backup
    bench --site <site> zevar-mapping-info
"""

from .commands import get_legacy_backup_path
from .foxpro_import import (
	get_mapping_info,
	import_all,
	import_appraisals,
	import_customers,
	import_employees,
	import_inventory,
	import_stores,
	import_suppliers,
)

__all__ = [
	"get_legacy_backup_path",
	"get_mapping_info",
	"import_all",
	"import_appraisals",
	"import_customers",
	"import_employees",
	"import_inventory",
	"import_stores",
	"import_suppliers",
]
