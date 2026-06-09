"""
Metal Rate Service — Replaces hard-coded PURITY_VALUES with DB-backed reference lookups.

Provides metal rate resolution, purity math, and gold-rate integration
for the Zevar inventory pricing pipeline.
"""

import frappe
from frappe import _
from frappe.utils import flt, cint, now_datetime, get_datetime
from datetime import timedelta


# Cache TTL: 5 minutes for reference data
CACHE_TTL = 300


def get_metal_rate(metal_code: str, purity_code: str, rate_source: str = "gold_settings") -> float:
    """
    Get the current per-gram rate for a given metal+purity combo.

    Steps:
    1. Look up the Zevar Purity record for fine_metal_content
    2. Get the base 24K rate from Gold Rate Log (latest) or Gold Settings fallback
    3. Multiply base rate × fine_metal_content

    Args:
        metal_code: e.g., 'YG', 'WG', 'PT'
        purity_code: e.g., '18K', '14K', '925'
        rate_source: 'gold_settings' (default) or 'live'

    Returns:
        Per-gram rate in USD
    """
    purity = _get_purity(metal_code, purity_code)
    if not purity:
        frappe.throw(_(f"Purity {purity_code} not found for metal {metal_code}"))

    fine_content = flt(purity.get("fine_metal_content"), 4)
    base_rate = _get_base_rate(metal_code)

    return flt(base_rate * fine_content, 2)


def get_fine_metal_content(purity_code: str, metal: str = None) -> float:
    """
    Look up fine metal content from the Zevar Purity reference table.
    Falls back to constants.PURITY_VALUES for backward compatibility.

    Args:
        purity_code: e.g., '18K', '925'
        metal: optional metal filter

    Returns:
        Fine metal content as a decimal (e.g., 0.750 for 18K)
    """
    filters = {"purity_code": purity_code, "is_active": 1}
    if metal:
        filters["metal"] = metal

    content = frappe.db.get_value("Zevar Purity", filters, "fine_metal_content")
    if content is not None:
        return flt(content, 4)

    # Backward compatibility fallback
    from zevar_core.unified_retail_management_system.constants import PURITY_VALUES
    return flt(PURITY_VALUES.get(purity_code, 0), 4)


def list_metal_rates(active_only: bool = True) -> list[dict]:
    """
    Return all metal × purity combos with their current rates.
    Used by the MetalPurityAdmin page and POS pricing engine.
    """
    cache_key = f"zevar_metal_rates_{int(active_only)}"
    cached = frappe.cache().get_value(cache_key)
    if cached:
        return cached

    filters = {"is_active": 1} if active_only else {}
    purities = frappe.get_all(
        "Zevar Purity",
        filters=filters,
        fields=["name", "purity_code", "purity_name", "metal", "fine_metal_content", "is_millesimal"],
        order_by="metal asc, fine_metal_content desc",
    )

    result = []
    rate_cache = {}  # cache base rates per metal to avoid repeated lookups

    for p in purities:
        metal_code = _get_metal_code(p["metal"])
        if metal_code not in rate_cache:
            rate_cache[metal_code] = _get_base_rate(metal_code)

        base = rate_cache[metal_code]
        rate = flt(base * flt(p["fine_metal_content"], 4), 2)

        result.append({
            "purity": p["name"],
            "purity_code": p["purity_code"],
            "purity_name": p["purity_name"],
            "metal": p["metal"],
            "fine_metal_content": p["fine_metal_content"],
            "base_rate_per_gram": base,
            "rate_per_gram": rate,
        })

    frappe.cache().set_value(cache_key, result, expires_in_sec=CACHE_TTL)
    return result


def calculate_metal_value(weight_grams: float, metal_code: str, purity_code: str) -> float:
    """
    Calculate the metal value of a piece given its weight, metal, and purity.

    Args:
        weight_grams: weight in grams
        metal_code: e.g., 'YG'
        purity_code: e.g., '18K'

    Returns:
        Metal value in USD
    """
    rate = get_metal_rate(metal_code, purity_code)
    return flt(weight_grams * rate, 2)


def convert_troy_oz_to_grams(troy_oz: float, metal: str = None) -> float:
    """
    Convert troy ounces to grams using the metal's conversion factor.
    Defaults to 31.1035 if no metal-specific override.
    """
    factor = 31.1035
    if metal:
        custom_factor = frappe.db.get_value("Zevar Metal", metal, "troy_oz_to_grams")
        if custom_factor:
            factor = flt(custom_factor, 4)
    return flt(troy_oz * factor, 4)


# ─── Internal helpers ──────────────────────────────────────────────


def _get_purity(metal_code: str, purity_code: str) -> dict | None:
    """Look up a Zevar Purity record by code + metal."""
    metal_name = _resolve_metal_name(metal_code)
    if not metal_name:
        return None

    return frappe.db.get_value(
        "Zevar Purity",
        {"purity_code": purity_code, "metal": metal_name, "is_active": 1},
        ["name", "fine_metal_content", "is_millesimal"],
        as_dict=True,
    )


def _get_base_rate(metal_code: str) -> float:
    """
    Get the base (pure/24K) rate per gram for a metal.
    Reads from Gold Rate Log (latest) for gold metals,
    or from Gold Settings for other metals.
    """
    # For gold-based metals, read the latest gold rate
    if metal_code in ("YG", "WG", "RG"):
        latest = frappe.db.get_value(
            "Gold Rate Log",
            filters={"source": ["!=", ""]},
            fieldname=["rate_per_gram"],
            order_by="creation desc",
        )
        if latest:
            return flt(latest, 2)

    # Fallback: Gold Settings
    settings = frappe.get_cached_doc("Gold Settings")
    rate_per_oz = flt(settings.get("gold_rate_per_oz") or settings.get("default_rate_per_oz"), 2)
    if rate_per_oz:
        return flt(rate_per_oz / 31.1035, 2)

    return 0.0


def _resolve_metal_name(metal_code: str) -> str | None:
    """Resolve a short metal code (YG, WG, etc.) to a Zevar Metal name."""
    cache_key = f"zevar_metal_code_{metal_code}"
    cached = frappe.cache().get_value(cache_key)
    if cached:
        return cached

    name = frappe.db.get_value("Zevar Metal", {"metal_code": metal_code, "is_active": 1}, "name")
    if name:
        frappe.cache().set_value(cache_key, name, expires_in_sec=CACHE_TTL)
    return name


def _get_metal_code(metal_name: str) -> str:
    """Resolve a Zevar Metal name to its short code."""
    code = frappe.db.get_value("Zevar Metal", metal_name, "metal_code")
    return code or metal_name
