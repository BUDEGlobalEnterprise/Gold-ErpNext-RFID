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

# Purity Values
PURITY_VALUES = {
	"24K": 0.999,
	"22K": 0.916,
	"18Kt": 0.750,
	"14Kt": 0.585,
	"10k": 0.417,
	"999 Sterling": 0.999,
	"925 Sterling": 0.925,
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
]

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
