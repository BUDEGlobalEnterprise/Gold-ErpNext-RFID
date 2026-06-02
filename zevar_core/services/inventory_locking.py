"""Pessimistic inventory locking for the POS hot path.

Uses SELECT...FOR UPDATE on Serial No rows to prevent race conditions
during concurrent POS transactions. Also provides Redis-based lock tokens
for real-time conflict detection.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import now_datetime

import time
import uuid


# Redis lock TTL (seconds)
_LOCK_TTL = 300  # 5 minutes
_LOCK_PREFIX = "zevar:serial_lock:"


def acquire_serial_lock(
	serial_no: str,
	lock_owner: str | None = None,
	timeout_seconds: int = 10,
) -> dict:
	"""Acquire a pessimistic lock on a serial number.

	Returns {success, lock_token} on success, throws on failure.
	"""
	if not serial_no:
		return {"success": True, "lock_token": None}

	lock_owner = lock_owner or frappe.session.user
	token = str(uuid.uuid4())
	lock_key = f"{_LOCK_PREFIX}{serial_no}"

	# Try Redis lock first (fast path)
	existing = frappe.cache().get(lock_key)
	if existing:
		existing_data = frappe.parse_json(existing) if isinstance(existing, str) else existing
		if existing_data.get("owner") != lock_owner:
			frappe.throw(
				_("Serial No {0} is currently locked by {1} (since {2})").format(
					serial_no,
					existing_data.get("owner", "unknown"),
					existing_data.get("acquired_at", "unknown"),
				)
			)

	# Database-level pessimistic lock (SELECT FOR UPDATE)
	start = time.time()
	locked = False

	while time.time() - start < timeout_seconds:
		try:
			row = frappe.db.sql(
				"SELECT name, warehouse, status FROM `tabSerial No` WHERE name = %s FOR UPDATE",
				(serial_no,),
				as_dict=True,
			)
			if row:
				if not row[0].warehouse:
					frappe.throw(_("Serial No {0} has no warehouse").format(serial_no))
				locked = True
				break
			else:
				frappe.throw(_("Serial No {0} not found").format(serial_no))
		except frappe.ValidationError:
			raise
		except Exception:
			time.sleep(0.5)

	if not locked:
		frappe.throw(_("Could not acquire lock on Serial No {0} within {1}s").format(
			serial_no, timeout_seconds
		))

	# Set Redis token
	frappe.cache().set(lock_key, frappe.as_json({
		"owner": lock_owner,
		"token": token,
		"acquired_at": str(now_datetime()),
	}), expires_in_sec=_LOCK_TTL)

	return {"success": True, "lock_token": token, "serial_no": serial_no}


def release_serial_lock(serial_no: str, lock_token: str | None = None) -> dict:
	"""Release a previously acquired serial lock."""
	if not serial_no:
		return {"success": True}

	lock_key = f"{_LOCK_PREFIX}{serial_no}"

	if lock_token:
		existing = frappe.cache().get(lock_key)
		if existing:
			data = frappe.parse_json(existing) if isinstance(existing, str) else existing
			if data.get("token") != lock_token:
				frappe.throw(_("Lock token mismatch for Serial No {0}").format(serial_no))

	frappe.cache().delete(lock_key)
	frappe.db.commit()

	return {"success": True, "serial_no": serial_no}


def check_serial_locked(serial_no: str) -> dict | None:
	"""Check if a serial number is currently locked. Returns lock info or None."""
	if not serial_no:
		return None

	lock_key = f"{_LOCK_PREFIX}{serial_no}"
	existing = frappe.cache().get(lock_key)
	if existing:
		data = frappe.parse_json(existing) if isinstance(existing, str) else existing
		return {
			"locked": True,
			"owner": data.get("owner"),
			"acquired_at": data.get("acquired_at"),
		}
	return None


def acquire_batch_locks(
	serial_nos: list[str],
	lock_owner: str | None = None,
	timeout_seconds: int = 15,
) -> dict:
	"""Acquire locks on multiple serial numbers. All-or-nothing."""
	lock_owner = lock_owner or frappe.session.user
	acquired_tokens = {}
	failed = []

	for sn in serial_nos:
		try:
			result = acquire_serial_lock(sn, lock_owner, timeout_seconds)
			if result.get("lock_token"):
				acquired_tokens[sn] = result["lock_token"]
		except Exception as e:
			failed.append({"serial_no": sn, "error": str(e)})

	if failed:
		# Roll back all acquired locks
		for sn, token in acquired_tokens.items():
			try:
				release_serial_lock(sn, token)
			except Exception:
				pass
		frappe.throw(
			_("Failed to lock {0} serial(s): {1}").format(
				len(failed),
				", ".join(f["serial_no"] for f in failed),
			)
		)

	return {"success": True, "locks": acquired_tokens}


def release_batch_locks(locks: dict[str, str]) -> dict:
	"""Release multiple serial locks."""
	released = []
	for sn, token in locks.items():
		try:
			release_serial_lock(sn, token)
			released.append(sn)
		except Exception:
			frappe.log_error(f"Failed to release lock for {sn}", frappe.get_traceback())

	return {"success": True, "released": released}
