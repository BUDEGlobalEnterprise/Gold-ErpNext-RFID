"""
Overage scoring service — Plan §10.2.

Stub for Phase 9. The full implementation will be added in Phase 9:
  - compute_overage_score formula
  - nightly recalculation of the overage queue
  - clearance ROI tracking
"""

from __future__ import annotations

import frappe


def recalculate_scores(days_threshold: int = 90, min_score: int = 50) -> dict:
	"""Phase 9 will implement the full scoring formula. For now, no-op."""
	frappe.logger().info("overage_service.recalculate_scores: stub (Phase 9 implements)")
	return {"ok": True, "phase": "stub"}


def compute_overage_score(item: dict) -> int:
	"""Phase 9 stub — returns 0. Real formula:
	- days_in_inventory (0-40 pts)
	- sell_through_decline (0-20 pts)
	- margin_opportunity_cost (0-20 pts)
	- seasonality (0-10 pts)
	- carrying_cost (0-10 pts)
	"""
	return 0
