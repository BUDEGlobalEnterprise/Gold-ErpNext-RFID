"""
Trending Items API - Trending and featured items
"""

import frappe
from frappe import _


def _check_rate_limit(key, max_calls=60, period=60):
	"""Simple Redis-based rate limiter. Returns True if rate-limited."""
	cache_key = f"rate_limit:{key}:{frappe.session.user}"
	current = frappe.cache.get_value(cache_key) or 0
	if current >= max_calls:
		return True
	frappe.cache.set_value(cache_key, current + 1, expires_in_sec=period)
	return False


@frappe.whitelist()
def get_trending_items(category: str | None = None, limit: int = 20):
	"""
	Fetch trending items for catalog display.

	Args:
	    category: Filter by jewelry category
	    limit: Maximum number of items to return

	Returns:
	    List of trending items
	"""
	limit = min(int(limit), 100)  # Cap at 100
	filters = {"is_active": 1}

	if category and category != "all":
		filters["category"] = category

	# Try to get from Trending Item DocType
	trending = frappe.get_all(
		"Trending Item",
		filters=filters,
		fields=[
			"name",
			"item_name",
			"category",
			"partner",
			"price",
			"is_hot",
			"product_url",
			"image_url",
			"view_count",
			"last_clicked",
		],
		order_by="is_hot desc, view_count desc, last_clicked desc",
		limit=limit,
	)

	# If no trending items, fallback to recent/featured items
	if not trending:
		trending = _get_fallback_items(category, limit)

	return trending


@frappe.whitelist()
def track_trending_click(item_id: str):
	"""
	Track click on trending item (rate-limited: 60 calls/min per user).

	Args:
	    item_id: Trending Item ID

	Returns:
	    Success status
	"""
	if _check_rate_limit("trending_click"):
		frappe.throw(_("Too many requests. Please slow down."), frappe.RateLimitExceededError)

	try:
		doc = frappe.get_doc("Trending Item", item_id)
		doc.view_count = (doc.view_count or 0) + 1
		doc.last_clicked = frappe.utils.now()
		doc.flags.ignore_validate_update_after_submit = True
		doc.save(ignore_permissions=True)
		frappe.db.commit()  # nosemgrep: frappe-semgrep-rules.rules.frappe-manual-commit

		return {"success": True, "view_count": doc.view_count}
	except Exception as e:
		frappe.log_error(f"Failed to track trending click: {e!s}")
		return {"success": False, "error": str(e)}


def _get_fallback_items(category: str | None = None, limit: int = 20):
	"""Get fallback items when no trending items exist."""
	filters = {"disabled": 0, "has_variants": 0}

	if category and category != "all":
		filters["custom_jewelry_type"] = category

	items = frappe.get_all(
		"Item",
		filters=filters,
		fields=[
			"name as item_name",
			"item_name",
			"custom_jewelry_type as category",
			"custom_msrp as price",
			"image as image_url",
			"custom_is_featured as is_hot",
		],
		order_by="custom_is_featured desc, modified desc",
		limit=limit,
	)

	return items
