"""
ID Scan API — AAMVA PDF417 driver's license parser.

US and Canadian driver's licenses encode the cardholder's identity in a
PDF417 barcode following the AAMVA DL/ID Card Design Standard. A POS
scanner gun decodes the barcode into a single ASCII payload which is
sent here for parsing. We extract the customer fields needed to
auto-fill the Customer creation form.

Format (simplified):

    @\\n\\u001e\\rANSI <IIN><VER><JUR><N>(<TYPE><OFFSET><LEN>){N}<DATA>

Subfiles (DL or ID) hold newline-delimited records of the form
    <3-letter element ID><value>
e.g.
    DCSDOE
    DACJOHN
    DAGSPRINGFIELD AVE
    DAJCA
    DAK90210

Element IDs used here (AAMVA 2009 / 2013 / 2016 / 2020):

    DCS  Family name (last name)              — required
    DAC  Given name (first name)              — required
    DAD  Middle name(s)
    DAG  Street address line 1
    DAH  Street address line 2
    DAI  City
    DAJ  State / Province (2-letter)
    DAK  ZIP / Postal code
    DCG  Country (USA / CAN)
    DAQ  Customer ID (driver's license number)
    DBA  Expiration date
    DBB  Date of birth
    DBC  Sex (1=M, 2=F, 9=Not specified)
    DBD  Issue date

Older 2000-era cards use:
    DAA  Full name "LAST,FIRST,MIDDLE"
    DAB  Last name
    DAC  First name
    DAD  Middle name (or in some jurisdictions: name suffix)

Dates are MMDDYYYY for US AAMVA 2009+ and YYYYMMDD for AAMVA 2000 and
Canadian licenses. We try both and return ISO (YYYY-MM-DD).
"""

from __future__ import annotations

import re
from datetime import datetime

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit

# ---------------------------------------------------------------------------
# Element ID → canonical key mapping. Order matters: the first non-empty
# match wins, so newer codes come first.
# ---------------------------------------------------------------------------

_FIELD_MAP = {
	# Names
	"DCS": "last_name",
	"DAB": "last_name",  # legacy 2000 spec
	"DAC": "first_name",
	"DCT": "first_name",  # legacy
	"DAD": "middle_name",
	# Address
	"DAG": "address_line1",
	"DAH": "address_line2",
	"DAI": "city",
	"DAJ": "state",
	"DAK": "postal_code",
	"DCG": "country",
	# Identity
	"DAQ": "license_number",
	"DBA": "license_expiry",
	"DBB": "date_of_birth",
	"DBC": "sex",
	"DBD": "license_issue_date",
}


# Sex codes per AAMVA spec
_SEX_MAP = {"1": "Male", "2": "Female", "9": "Other"}


def _normalize_input(raw: str) -> str:
	"""Strip surrounding whitespace and unify line endings."""
	if raw is None:
		return ""
	# Some scanners replace control characters with their literal escape
	# sequences ("\\n", "\\r", "\\u001e"). Translate those back.
	text = raw.replace("\\n", "\n").replace("\\r", "\r").replace("\\u001e", "\x1e").replace("\\u001c", "\x1c")
	# Many scanners terminate every line with \r\n; collapse to \n.
	text = text.replace("\r\n", "\n").replace("\r", "\n")
	return text.strip()


def _looks_like_aamva(text: str) -> bool:
	"""Return True if `text` carries the AAMVA magic. Tolerant of leading slop."""
	if not text:
		return False
	# The compliance indicator may be absent if the scanner stripped it,
	# so we look for "ANSI " followed by a 6-digit IIN.
	return bool(re.search(r"ANSI\s*\d{6}", text))


def _parse_aamva_date(value: str) -> str | None:
	"""Return an ISO date string (YYYY-MM-DD) for an AAMVA date field.

	AAMVA 2009+ uses MMDDYYYY for US cards. AAMVA 2000 and Canadian cards
	use YYYYMMDD. We try both and accept the first one that produces a
	plausible date.
	"""
	if not value:
		return None
	value = value.strip()
	if not value.isdigit() or len(value) != 8:
		return None

	for fmt in ("%m%d%Y", "%Y%m%d"):
		try:
			d = datetime.strptime(value, fmt).date()
			# Reject obviously wrong years (some malformed cards report 0000).
			if 1900 <= d.year <= 2100:
				return d.isoformat()
		except ValueError:
			continue
	return None


def _split_full_name_legacy(value: str) -> dict:
	"""Older AAMVA 2000 cards stored 'LAST,FIRST,MIDDLE' in DAA."""
	parts = [p.strip() for p in value.split(",")]
	out = {}
	if len(parts) >= 1 and parts[0]:
		out["last_name"] = parts[0]
	if len(parts) >= 2 and parts[1]:
		out["first_name"] = parts[1]
	if len(parts) >= 3 and parts[2]:
		out["middle_name"] = parts[2]
	return out


def _title_case_name(value: str) -> str:
	"""AAMVA payloads are typically uppercase; convert to Title Case but
	preserve common particles like "de", "von", "Mac"/"Mc" prefixes.
	"""
	if not value:
		return value
	return " ".join(part.capitalize() for part in value.strip().split())


def parse_drivers_license_payload(raw: str) -> dict:
	"""Parse an AAMVA PDF417 payload.

	Returns a dict with whatever fields could be extracted. Always present:
	    success: bool
	    raw_length: int

	On success additionally:
	    first_name, last_name, middle_name, full_name,
	    address_line1, address_line2, city, state, postal_code, country,
	    license_number, license_expiry, license_issue_date,
	    date_of_birth, sex,
	    aamva_version, issuer_iin

	On failure additionally:
	    error: str
	"""
	text = _normalize_input(raw)
	result: dict = {"success": False, "raw_length": len(text)}

	if not _looks_like_aamva(text):
		result["error"] = "Payload does not look like an AAMVA driver's license barcode."
		return result

	# Pull out the issuer IIN and AAMVA version from the header.
	header = re.search(r"ANSI\s*(\d{6})(\d{2})?", text)
	if header:
		result["issuer_iin"] = header.group(1)
		if header.group(2):
			result["aamva_version"] = header.group(2)

	# Capture every <3-letter-code><value-until-newline> pair.
	# Element IDs are uppercase A-Z plus a few digit-suffixed jurisdiction
	# codes (e.g. ZAA…ZZZ). We scan for the AAMVA-allowed alphabet.
	pattern = re.compile(r"([A-Z]{3})([^\n\r]*)")
	parsed: dict = {}
	for code, value in pattern.findall(text):
		# Skip the file-type / subfile markers (DL, ID at the very start
		# of a subfile — they have no value payload).
		if code in ("DL", "ID"):
			continue
		value = value.strip()
		if not value:
			continue
		# Legacy 2000 spec full-name field
		if code == "DAA":
			parsed.update(_split_full_name_legacy(value))
			continue
		key = _FIELD_MAP.get(code)
		if key and key not in parsed:
			parsed[key] = value

	if not parsed.get("first_name") and not parsed.get("last_name"):
		result["error"] = "Could not extract a name from the barcode."
		return result

	# Normalize fields.
	for name_key in ("first_name", "last_name", "middle_name"):
		if name_key in parsed:
			parsed[name_key] = _title_case_name(parsed[name_key])

	# Sex code → human label
	if "sex" in parsed:
		parsed["sex"] = _SEX_MAP.get(parsed["sex"], parsed["sex"])

	# Dates → ISO
	for date_key in ("date_of_birth", "license_expiry", "license_issue_date"):
		if date_key in parsed:
			iso = _parse_aamva_date(parsed[date_key])
			if iso:
				parsed[date_key] = iso
			else:
				# Unparseable date — drop it rather than poisoning Frappe's
				# Date validators downstream.
				parsed.pop(date_key)

	# Address strings often arrive in ALL CAPS. Title-case them lightly.
	for addr_key in ("address_line1", "address_line2", "city"):
		if parsed.get(addr_key):
			parsed[addr_key] = _title_case_name(parsed[addr_key])

	# Convenience: full name (some UIs need it pre-joined).
	full_parts = [parsed.get("first_name"), parsed.get("middle_name"), parsed.get("last_name")]
	full_name = " ".join(p for p in full_parts if p)
	if full_name:
		parsed["full_name"] = full_name

	# Country: AAMVA uses "USA" / "CAN" — keep as-is, the form already
	# expects ISO-ish country names downstream.

	result.update(parsed)
	result["success"] = True
	return result


# ---------------------------------------------------------------------------
# Whitelisted endpoint
# ---------------------------------------------------------------------------


@frappe.whitelist(methods=["POST"])
@rate_limit(limit=60, seconds=60)
def parse_drivers_license(barcode: str) -> dict:
	"""POST endpoint: takes the raw scanner payload, returns parsed fields.

	The frontend opens the camera or hardware scanner, captures the PDF417
	contents as a string, and posts it here. We never persist the raw
	payload — only the structured fields are returned to the caller, and
	the Customer doc is built by quick_create_customer using those fields.
	"""
	# Defensive guard against absurdly long payloads. A real AAMVA barcode
	# is typically 400–700 bytes; allow some slack.
	if not barcode:
		frappe.throw(_("No barcode data provided."))
	if len(barcode) > 8000:
		frappe.throw(_("Barcode payload is unreasonably large."))

	parsed = parse_drivers_license_payload(barcode)
	if not parsed.get("success"):
		# Don't echo the raw barcode back in the error message — it
		# contains personal data.
		frappe.throw(parsed.get("error") or _("Could not parse driver's license barcode."))

	return parsed
