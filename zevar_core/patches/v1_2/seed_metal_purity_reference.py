"""Seed Zevar Metal + Zevar Purity reference tables from hard-coded constants.

Migrates PURITY_VALUES from constants.py into proper DB records.
Idempotent — checks before inserting.
"""

import frappe


METALS = [
	{"metal_code": "YG", "metal_name": "Yellow Gold", "metal_type": "Precious", "color_hex": "#FFD700", "default_purity": "18Kt"},
	{"metal_code": "WG", "metal_name": "White Gold", "metal_type": "Precious", "color_hex": "#E8E4D4", "default_purity": "18Kt"},
	{"metal_code": "RG", "metal_name": "Rose Gold", "metal_type": "Precious", "color_hex": "#B76E4F", "default_purity": "18Kt"},
	{"metal_code": "PT", "metal_name": "Platinum", "metal_type": "Precious", "color_hex": "#E5E4E2"},
	{"metal_code": "SR", "metal_name": "Silver", "metal_type": "Precious", "color_hex": "#C0C0C0"},
]

GOLD_PURITIES = [
	{"purity_code": "24Kt", "purity_name": "24 Karat", "fine_metal_content": 0.999, "aliases": "24K, 24k, 999"},
	{"purity_code": "22Kt", "purity_name": "22 Karat", "fine_metal_content": 0.916, "aliases": "22K, 22k"},
	{"purity_code": "18Kt", "purity_name": "18 Karat", "fine_metal_content": 0.750, "aliases": "18K, 18k"},
	{"purity_code": "14Kt", "purity_name": "14 Karat", "fine_metal_content": 0.585, "aliases": "14K, 14k"},
	{"purity_code": "10Kt", "purity_name": "10 Karat", "fine_metal_content": 0.417, "aliases": "10K, 10k"},
]

SILVER_PURITIES = [
	{"purity_code": "999 Fine", "purity_name": "999 Fine Silver", "fine_metal_content": 0.999, "is_millesimal": 1, "aliases": "fine silver"},
	{"purity_code": "925 Sterling", "purity_name": "925 Sterling Silver", "fine_metal_content": 0.925, "is_millesimal": 1, "aliases": "sterling, 925"},
]

PLATINUM_PURITIES = [
	{"purity_code": "950 Plat", "purity_name": "950 Platinum", "fine_metal_content": 0.950, "is_millesimal": 1},
	{"purity_code": "900 Plat", "purity_name": "900 Platinum", "fine_metal_content": 0.900, "is_millesimal": 1},
]

GEMSTONE_TYPES = [
	{"gemstone_type_name": "Diamond", "category": "Precious", "hardness_mohs": 10.0, "color_hex": "#E8E8E8"},
	{"gemstone_type_name": "Sapphire", "category": "Precious", "hardness_mohs": 9.0, "color_hex": "#0F52BA"},
	{"gemstone_type_name": "Ruby", "category": "Precious", "hardness_mohs": 9.0, "color_hex": "#E0115F"},
	{"gemstone_type_name": "Emerald", "category": "Precious", "hardness_mohs": 7.5, "color_hex": "#50C878"},
	{"gemstone_type_name": "Amethyst", "category": "Semi-Precious", "hardness_mohs": 7.0, "color_hex": "#9966CC"},
	{"gemstone_type_name": "Topaz", "category": "Semi-Precious", "hardness_mohs": 8.0, "color_hex": "#FFC87C"},
	{"gemstone_type_name": "Opal", "category": "Semi-Precious", "hardness_mohs": 6.0, "color_hex": "#A8C3BC"},
	{"gemstone_type_name": "Pearl", "category": "Organic", "hardness_mohs": 3.0, "color_hex": "#FDEEF4"},
	{"gemstone_type_name": "Tanzanite", "category": "Semi-Precious", "hardness_mohs": 6.5, "color_hex": "#4169E1"},
	{"gemstone_type_name": "Garnet", "category": "Semi-Precious", "hardness_mohs": 7.0, "color_hex": "#722F37"},
	{"gemstone_type_name": "Aquamarine", "category": "Semi-Precious", "hardness_mohs": 7.5, "color_hex": "#7FFFD4"},
	{"gemstone_type_name": "Moissanite", "category": "Synthetic", "hardness_mohs": 9.25, "color_hex": "#F5F5F5"},
]

APPRAISAL_TEMPLATES = [
	{"template_name": "Insurance Appraisal", "template_type": "Insurance", "default_validity_months": 24},
	{"template_name": "Estate Appraisal", "template_type": "Estate", "default_validity_months": 12},
	{"template_name": "Replacement Appraisal", "template_type": "Replacement", "default_validity_months": 24},
	{"template_name": "Retail Appraisal", "template_type": "Retail", "default_validity_months": 18},
]


def execute():
	_seed_metals()
	_seed_purities()
	_seed_gemstone_types()
	_seed_appraisal_templates()
	_link_default_purities()


def _seed_metals():
	for m in METALS:
		if frappe.db.exists("Zevar Metal", m["metal_name"]):
			continue
		doc = frappe.get_doc({"doctype": "Zevar Metal", **m})
		doc.insert(ignore_permissions=True)


def _seed_purities():
	for gold_metal in ("Yellow Gold", "White Gold", "Rose Gold"):
		for p in GOLD_PURITIES:
			name = f"{p['purity_code']} {gold_metal}"
			if frappe.db.exists("Zevar Purity", name):
				continue
			frappe.get_doc({
				"doctype": "Zevar Purity",
				"purity_code": p["purity_code"],
				"purity_name": f"{p['purity_name']} {gold_metal}",
				"metal": gold_metal,
				"fine_metal_content": p["fine_metal_content"],
				"is_millesimal": p.get("is_millesimal", 0),
				"aliases": p.get("aliases", ""),
			}).insert(ignore_permissions=True)

	for p in SILVER_PURITIES:
		if frappe.db.exists("Zevar Purity", p["purity_name"]):
			continue
		frappe.get_doc({
			"doctype": "Zevar Purity",
			"purity_code": p["purity_code"],
			"purity_name": p["purity_name"],
			"metal": "Silver",
			"fine_metal_content": p["fine_metal_content"],
			"is_millesimal": p.get("is_millesimal", 0),
			"aliases": p.get("aliases", ""),
		}).insert(ignore_permissions=True)

	for p in PLATINUM_PURITIES:
		if frappe.db.exists("Zevar Purity", p["purity_name"]):
			continue
		frappe.get_doc({
			"doctype": "Zevar Purity",
			"purity_code": p["purity_code"],
			"purity_name": p["purity_name"],
			"metal": "Platinum",
			"fine_metal_content": p["fine_metal_content"],
			"is_millesimal": p.get("is_millesimal", 0),
		}).insert(ignore_permissions=True)


def _link_default_purities():
	for m in METALS:
		if "default_purity" not in m:
			continue
		purity_name = f"{m['default_purity']} {m['metal_name']}"
		if frappe.db.exists("Zevar Purity", purity_name):
			frappe.db.set_value("Zevar Metal", m["metal_name"], "default_purity", purity_name)


def _seed_gemstone_types():
	for g in GEMSTONE_TYPES:
		if frappe.db.exists("Zevar Gemstone Type", g["gemstone_type_name"]):
			continue
		frappe.get_doc({"doctype": "Zevar Gemstone Type", **g}).insert(ignore_permissions=True)


def _seed_appraisal_templates():
	for t in APPRAISAL_TEMPLATES:
		if frappe.db.exists("Appraisal Template", {"template_name": t["template_name"]}):
			continue
		frappe.get_doc({"doctype": "Appraisal Template", **t}).insert(ignore_permissions=True)
