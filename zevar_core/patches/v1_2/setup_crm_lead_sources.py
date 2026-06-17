"""Seed CRM Lead Sources, Lead Statuses, and Deal Statuses for POS integration.

Ensures the CRM master data required for the POS <-> CRM integration exists.
Idempotent -- checks before inserting.
"""

import frappe

LEAD_SOURCES = [
	{"source_name": "Walk-in", "details": "Customer walked into the store"},
	{"source_name": "POS Referral", "details": "Referred by a sales associate at POS"},
	{"source_name": "Existing Customer", "details": "Already an existing customer"},
]

LEAD_STATUSES = [
	{"lead_status": "Open", "color": "blue", "position": 1, "type": "Open"},
	{"lead_status": "Contacted", "color": "amber", "position": 2, "type": "Ongoing"},
	{"lead_status": "Qualified", "color": "green", "position": 3, "type": "Ongoing"},
	{"lead_status": "Converted", "color": "teal", "position": 4, "type": "Won"},
	{"lead_status": "Lost", "color": "red", "position": 5, "type": "Lost"},
]

DEAL_STATUSES = [
	{"deal_status": "Qualification", "color": "blue", "position": 1, "probability": 20, "type": "Open"},
	{"deal_status": "Proposal", "color": "amber", "position": 2, "probability": 50, "type": "Ongoing"},
	{"deal_status": "Negotiation", "color": "orange", "position": 3, "probability": 70, "type": "Ongoing"},
	{"deal_status": "Won", "color": "green", "position": 4, "probability": 100, "type": "Won"},
	{"deal_status": "Lost", "color": "red", "position": 5, "probability": 0, "type": "Lost"},
]


def execute():
	if "crm" not in frappe.get_installed_apps():
		return
	_seed_lead_sources()
	_seed_lead_statuses()
	_seed_deal_statuses()


def _seed_lead_sources():
	for s in LEAD_SOURCES:
		if frappe.db.exists("CRM Lead Source", s["source_name"]):
			continue
		frappe.get_doc({"doctype": "CRM Lead Source", **s}).insert(ignore_permissions=True)


def _seed_lead_statuses():
	for s in LEAD_STATUSES:
		if frappe.db.exists("CRM Lead Status", s["lead_status"]):
			continue
		frappe.get_doc({"doctype": "CRM Lead Status", **s}).insert(ignore_permissions=True)


def _seed_deal_statuses():
	for s in DEAL_STATUSES:
		if frappe.db.exists("CRM Deal Status", s["deal_status"]):
			continue
		frappe.get_doc({"doctype": "CRM Deal Status", **s}).insert(ignore_permissions=True)
