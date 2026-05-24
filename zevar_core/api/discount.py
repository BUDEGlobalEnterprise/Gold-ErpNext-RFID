"""
Discount Validation API - Rule-based discount limits and validation

Provides:
- Discount rule lookup by customer, category, role, or global
- Validation of proposed discounts against active rules
- Max allowed discount query for POS frontend
"""

import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def validate_discount(
	discount_amount: float,
	discount_pct: float,
	subtotal: float = 0,
	customer: str | None = None,
	user: str | None = None,
) -> dict:
	"""Validate a proposed discount against all applicable active rules.

	Returns {valid, max_allowed_pct, max_allowed_amt, requires_override, reason}.
	"""
	if not user:
		user = frappe.session.user

	rules = frappe.get_all(
		"Discount Rule",
		filters={"is_active": 1},
		fields=["*"],
		order_by="priority desc",
	)

	if not rules:
		# No rules configured — fall back to the 10% hard limit for non-managers
		user_roles = frappe.get_roles(user)
		if "Sales Manager" in user_roles or "Store Manager" in user_roles or "System Manager" in user_roles:
			return {"valid": True, "max_allowed_pct": 100, "max_allowed_amt": 0, "requires_override": False, "reason": ""}
		return {"valid": flt(discount_pct) <= 10, "max_allowed_pct": 10, "max_allowed_amt": 0, "requires_override": flt(discount_pct) > 10, "reason": ""}

	user_roles = frappe.get_roles(user)
	max_pct = 0.0
	max_amt = 0.0

	for rule in rules:
		if not _rule_applies(rule, customer, user_roles):
			continue

		if rule.discount_method == "Percentage" and flt(rule.max_discount_pct) > max_pct:
			max_pct = flt(rule.max_discount_pct)
		elif rule.discount_method == "Flat Amount" and flt(rule.max_discount_amt) > max_amt:
			max_amt = flt(rule.max_discount_amt)

	# Check percentage limit
	if max_pct > 0 and flt(discount_pct) > max_pct:
		return {
			"valid": False,
			"max_allowed_pct": max_pct,
			"max_allowed_amt": max_amt,
			"requires_override": True,
			"reason": _("Discount {0}% exceeds maximum {1}%").format(flt(discount_pct, 1), max_pct),
		}

	# Check flat amount limit
	if max_amt > 0 and flt(discount_amount) > max_amt:
		return {
			"valid": False,
			"max_allowed_pct": max_pct,
			"max_allowed_amt": max_amt,
			"requires_override": True,
			"reason": _("Discount amount ${0} exceeds maximum ${1}").format(flt(discount_amount), max_amt),
		}

	return {"valid": True, "max_allowed_pct": max_pct, "max_allowed_amt": max_amt, "requires_override": False, "reason": ""}


@frappe.whitelist()
def get_max_discount(customer: str | None = None, user: str | None = None) -> dict:
	"""Return the maximum discount allowed for the current user/customer combo.

	Used by POS frontend to show the limit before applying.
	"""
	if not user:
		user = frappe.session.user

	result = validate_discount(discount_amount=0, discount_pct=0, customer=customer, user=user)
	return {
		"max_pct": result["max_allowed_pct"],
		"max_amt": result["max_allowed_amt"],
	}


def _rule_applies(rule, customer, user_roles) -> bool:
	"""Check whether a discount rule applies given the context."""
	if rule.rule_type == "Global":
		return True
	if rule.rule_type == "Per Customer":
		return rule.customer and rule.customer == customer
	if rule.rule_type == "Per Employee Role":
		return rule.role and rule.role in user_roles
	if rule.rule_type == "Per Category":
		# Category rules are checked at line-item level; at invoice level they always apply
		return True
	return False
