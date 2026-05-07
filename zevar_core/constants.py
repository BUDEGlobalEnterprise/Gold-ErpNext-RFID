"""
Zevar Core Constants
"""

# Pagination
DEFAULT_PAGE_LENGTH = 20
MAX_PAGE_LENGTH = 100

# Item Sources
PARTNER_SOURCES = ["QGold", "Stuller", "Demo"]

# Metal Types
METAL_TYPES = ["Yellow Gold", "White Gold", "Rose Gold", "Silver", "Platinum"]

PURITY_VALUES = {
	"24Kt": 0.999,
	"22Kt": 0.916,
	"18Kt": 0.750,
	"14Kt": 0.585,
	"10Kt": 0.417,
	"999 Fine": 0.999,
	"925 Sterling": 0.925,
}

PURITY_ALIASES = {
	"24k": "24Kt",
	"22k": "22Kt",
	"18k": "18Kt",
	"14k": "14Kt",
	"10k": "10Kt",
	"24kt": "24Kt",
	"22kt": "22Kt",
	"18kt": "18Kt",
	"14kt": "14Kt",
	"10kt": "10Kt",
	"24 karat": "24Kt",
	"22 karat": "22Kt",
	"18 karat": "18Kt",
	"14 karat": "14Kt",
	"10 karat": "10Kt",
	"999 sterling": "999 Fine",
	"925": "925 Sterling",
	"sterling": "925 Sterling",
	"fine silver": "999 Fine",
}

GOLD_PURITY_RATES = {
	"24Kt": 0.999,
	"22Kt": 0.916,
	"18Kt": 0.750,
	"14Kt": 0.585,
	"10Kt": 0.417,
}

GOLD_PURITY_ALIASES = {
	"24K": "24Kt",
	"22K": "22Kt",
	"18K": "18Kt",
	"14K": "14Kt",
	"10K": "10Kt",
}

# Silver purities used by rate fetcher
SILVER_PURITY_RATES = {
	"999 Fine": 0.999,
	"925 Sterling": 0.925,
}

# Additional PURITY_ALIASES for direct Kt variants (e.g., "18K" -> "18Kt")
# Note: These values override the earlier lowercase aliases - this is intentional
# as we want "18K" to map to "18Kt", not "18k"
PURITY_ALIASES_DIRECT = {
	"18K": "18Kt",
	"14K": "14Kt",
	"10K": "10Kt",
}

# Unit Conversions
TROY_OZ_TO_GRAMS = 31.1035

# Tax Rates (keys match warehouse name substrings, case-insensitive)
DEFAULT_TAX_RATES = {
	"new york": 8.875,
	"miami": 7.00,
	"los angeles": 9.50,
	"houston": 8.25,
	"chicago": 10.25,
}

# Payment Modes
PAYMENT_MODES = [
	"Cash",
	"Credit Card",
	"Debit Card",
	"Check",
	"Wire Transfer",
	"Zelle",
	"Gift Card",
	"Trade-In",
	"Apple Pay",
	"Google Pay",
	"Venmo",
	"Cash App",
	"Synchrony",
	"AFF",
	"CIMA",
	"Progressive",
	"Snap",
	"In-House Finance",
]

# Financing Provider Waterfall (prime -> subprime)
FINANCING_WATERFALL = ["Synchrony", "AFF", "Progressive", "Snap", "Acima"]

# IRS Form 8300 threshold
CASH_REPORTING_THRESHOLD = 10000.00

LAYAWAY_DURATION_OPTIONS = [1, 2, 3, 6, 9, 12]

LAYAWAY_DURATION_LABELS = {
	1: "30 Days",
	2: "60 Days",
	3: "90 Days",
	6: "6 Months",
	9: "9 Months",
	12: "12 Months",
}

LAYAWAY_PLAN_SUGGESTIONS = [
	{"max_price": 500, "suggested_duration": 1, "suggested_down_percent": 30},
	{"max_price": 1000, "suggested_duration": 2, "suggested_down_percent": 25},
	{"max_price": 2500, "suggested_duration": 3, "suggested_down_percent": 20},
	{"max_price": 5000, "suggested_duration": 6, "suggested_down_percent": 20},
	{"max_price": 10000, "suggested_duration": 9, "suggested_down_percent": 20},
	{"max_price": float("inf"), "suggested_duration": 12, "suggested_down_percent": 25},
]

DEFAULT_CANCELLATION_FEE_PERCENT = 10
DEFAULT_AUTO_FORFEIT_DAYS = 15
MAX_EXTENSIONS_ALLOWED = 2

# Inventory Zones (per store warehouse tree)
INVENTORY_ZONES = [
	"Showcase",
	"Back Stock",
	"Safe",
	"Repair Bench",
	"Layaway Hold",
	"Reserved",
	"Transit Out",
	"Transit In",
	"Quarantine",
	"Shrinkage",
]

# Store codes and names
STORE_LOCATIONS = {
	"NY-01": "New York",
	"Miami-01": "Miami",
	"LA-01": "Los Angeles",
	"Houston-01": "Houston",
	"Chicago-01": "Chicago",
}

# Zones that are valid for selling (before_submit check)
SELLABLE_ZONES = ["Showcase", "Reserved"]

# Audit cadence by theft risk class (in days)
AUDIT_CADENCE_DAYS = {
	"High": 7,
	"Medium": 30,
	"Low": 90,
}

# Default reservation hold hours
DEFAULT_RESERVATION_HOURS = 48

# Reorder safety stock days
REORDER_SAFETY_DAYS = 14

# Inventory event types for POS Audit Log
INVENTORY_EVENT_TYPES = [
	"piece_reserved",
	"reservation_expired",
	"transfer_dispatched",
	"transfer_received",
	"damage_written_off",
	"gift_out",
	"consignment_out",
	"consignment_back",
	"piece_recovered",
	"bulk_push_completed",
	"repair_in",
	"repair_out",
	"trade_in_accepted",
	"shrinkage_detected",
	"vendor_return",
	"consignment_overdue",
	"stock_auto_reduced",
	"stock_cli_adjustment",
]
