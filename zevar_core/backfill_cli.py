"""
Backfill CLI — populate Sale Cost Breakdown and Performance Log from history.

These commands exist because the on_submit hooks that create Sale Cost Breakdown
(Q1) and Performance Logs (Q2) were only wired now, so all historical submitted
POS invoices are missing those records. The backfills replay history using the
*same* hook logic, so backfilled numbers match freshly-created ones.

Both commands are IDEMPOTENT and safe to re-run:
  - SCB is keyed 1:1 by ``sales_invoice`` (unique); existing rows are skipped.
  - Performance Log is keyed by (employee, event_type, reference_document); the
    hook ``log_sale_event`` already skips any (employee, invoice) that has a log.
    Performance Logs are immutable (no on_trash delete), so we never recreate.

Usage:
    bench --site <site> zevar-backfill scb [--dry-run] [--from-date 2025-01-01] [--to-date 2025-12-31] [--limit N] [--batch-size N]
    bench --site <site> zevar-backfill performance-logs [--dry-run] [--from-date ...] [--to-date ...] [--limit N] [--batch-size N]

Recommended: always run with --dry-run first and review the counts.
"""

from __future__ import annotations

import click
import frappe
from frappe.commands import get_site, pass_context

COMMIT_BATCH_DEFAULT = 100


# ---------------------------------------------------------------------------
# group
# ---------------------------------------------------------------------------


@click.group("zevar-backfill")
def backfill_cli():
	"""Backfill historical Sale Cost Breakdown and Performance Log records."""


# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------


def _echo(label, value, fg=None):
	msg = f"  {label + ':':24} {value}"
	click.echo(click.style(msg, fg=fg) if fg else msg)


def _invoice_query(*, from_date, to_date, limit, missing_scb):
	"""Return submitted POS invoices, optionally excluding those that already have an SCB.

	Ordering by posting_date/name so reruns are deterministic and resumable.
	"""
	conditions = ["si.docstatus = 1", "si.is_pos = 1"]
	params = []
	if from_date:
		conditions.append("si.posting_date >= %s")
		params.append(from_date)
	if to_date:
		conditions.append("si.posting_date <= %s")
		params.append(to_date)
	if missing_scb:
		conditions.append("NOT EXISTS (SELECT 1 FROM `tabSale Cost Breakdown` scb WHERE scb.sales_invoice = si.name)")

	sql = (
		"SELECT si.name, si.posting_date, si.customer, si.base_net_total "
		"FROM `tabSales Invoice` si "
		"WHERE " + " AND ".join(conditions) + " "
		"ORDER BY si.posting_date ASC, si.name ASC"
	)
	if limit:
		sql += " LIMIT %s"
		params.append(limit)

	return frappe.db.sql(sql, tuple(params), as_dict=True)


# ---------------------------------------------------------------------------
# scb
# ---------------------------------------------------------------------------


@backfill_cli.command("scb")
@click.option("--dry-run", is_flag=True, default=False, help="Report what would be created without writing.")
@click.option("--from-date", default=None, help="Posting date lower bound (YYYY-MM-DD).")
@click.option("--to-date", default=None, help="Posting date upper bound (YYYY-MM-DD).")
@click.option("--limit", type=int, default=None, help="Max invoices to process (for trialing on a slice).")
@click.option("--batch-size", type=int, default=COMMIT_BATCH_DEFAULT, help="Commit every N invoices.")
@pass_context
def backfill_scb(context, dry_run, from_date, to_date, limit, batch_size):
	"""Backfill Sale Cost Breakdown for submitted POS invoices that lack one."""
	from zevar_core.api.profit_intelligence import calculate_sale_cost_breakdown

	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()

	click.echo(click.style("\nSale Cost Breakdown backfill", bold=True, fg="cyan"))
	if dry_run:
		click.echo(click.style("  (DRY RUN — no records will be written)", fg="yellow"))
	if from_date or to_date:
		click.echo(f"  range: {from_date or '…'} → {to_date or '…'}")

	created = 0
	skipped_existing = 0
	errors = 0

	try:
		invoices = _invoice_query(from_date=from_date, to_date=to_date, limit=limit, missing_scb=True)
		total = len(invoices)
		click.echo(f"  invoices missing SCB: {total}")

		for i, row in enumerate(invoices, start=1):
			if dry_run:
				created += 1  # would-create
				continue
			try:
				doc = frappe.get_doc("Sales Invoice", row.name)
				calculate_sale_cost_breakdown(doc)  # idempotent (cleans prior row, then inserts)
				created += 1
				if created % batch_size == 0:
					frappe.db.commit()
					click.echo(f"    …{i}/{total} committed ({created} created)")
			except Exception:
				errors += 1
				frappe.log_error(title=f"SCB backfill failed: {row.name}", message=frappe.get_traceback())
				frappe.db.rollback()

		if not dry_run:
			frappe.db.commit()

		click.echo(click.style("\n  result", bold=True))
		_echo("would create" if dry_run else "created", created, fg="green")
		_echo("skipped (already had SCB)", skipped_existing)
		_echo("errors", errors, fg="red" if errors else None)
	finally:
		frappe.destroy()


# ---------------------------------------------------------------------------
# performance-logs
# ---------------------------------------------------------------------------


@backfill_cli.command("performance-logs")
@click.option("--dry-run", is_flag=True, default=False, help="Report what would be created without writing.")
@click.option("--from-date", default=None, help="Posting date lower bound (YYYY-MM-DD).")
@click.option("--to-date", default=None, help="Posting date upper bound (YYYY-MM-DD).")
@click.option("--limit", type=int, default=None, help="Max invoices to process (for trialing on a slice).")
@click.option("--batch-size", type=int, default=COMMIT_BATCH_DEFAULT, help="Commit every N invoices.")
@pass_context
def backfill_performance_logs(context, dry_run, from_date, to_date, limit, batch_size):
	"""Backfill 'Sale Completed' Performance Logs for submitted POS invoices.

	Uses the live hook ``log_sale_event`` (now idempotent), so backfilled logs are
	identical to freshly-created ones and reruns create no duplicates.
	"""
	from zevar_core.api.performance import log_sale_event

	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()

	click.echo(click.style("\nPerformance Log backfill", bold=True, fg="cyan"))
	if dry_run:
		click.echo(click.style("  (DRY RUN — no records will be written)", fg="yellow"))
	if from_date or to_date:
		click.echo(f"  range: {from_date or '…'} → {to_date or '…'}")

	invoices_processed = 0
	invoices_skipped = 0
	logs_created = 0
	errors = 0

	try:
		# All submitted POS invoices with at least one salesperson split.
		invoices = frappe.db.sql(
			"""
			SELECT DISTINCT si.name
			FROM `tabSales Invoice` si
			INNER JOIN `tabSalesperson Split Detail` ss ON ss.parent = si.name AND ss.parenttype = 'Sales Invoice'
			WHERE si.docstatus = 1 AND si.is_pos = 1
			  AND (%(from)s = '' OR si.posting_date >= %(from)s)
			  AND (%(to)s = '' OR si.posting_date <= %(to)s)
			ORDER BY si.posting_date ASC, si.name ASC
			""",
			{"from": from_date or "", "to": to_date or ""},
			as_dict=True,
		)
		if limit:
			invoices = invoices[:limit]
		total = len(invoices)
		click.echo(f"  submitted POS invoices with splits: {total}")

		for i, row in enumerate(invoices, start=1):
			try:
				doc = frappe.get_doc("Sales Invoice", row.name)
				before = frappe.db.count(
					"Performance Log",
					{"event_type": "Sale Completed", "reference_document": row.name},
				)
				if not dry_run:
					log_sale_event(doc)  # idempotent: skips (employee, invoice) that already have a log
					frappe.db.commit()
				after = before  # in dry-run nothing is written
				if not dry_run:
					after = frappe.db.count(
						"Performance Log",
						{"event_type": "Sale Completed", "reference_document": row.name},
					)
				delta = (after - before) if not dry_run else _expected_logs_for_invoice(doc)
				if delta > 0:
					logs_created += delta
					invoices_processed += 1
				else:
					invoices_skipped += 1
				if not dry_run and invoices_processed % batch_size == 0:
					click.echo(f"    …{i}/{total} ({logs_created} logs created)")
			except Exception:
				errors += 1
				frappe.log_error(title=f"Performance Log backfill failed: {row.name}", message=frappe.get_traceback())
				frappe.db.rollback()

		click.echo(click.style("\n  result", bold=True))
		_echo("logs would create" if dry_run else "logs created", logs_created, fg="green")
		_echo("invoices processed", invoices_processed)
		_echo("invoices skipped (already logged)", invoices_skipped)
		_echo("errors", errors, fg="red" if errors else None)
	finally:
		frappe.destroy()


def _expected_logs_for_invoice(doc) -> int:
	"""Dry-run helper: count salesperson splits that DON'T already have a 'Sale Completed' log."""
	splits = doc.get("custom_salesperson_splits") or []
	count = 0
	for row in splits:
		employee = getattr(row, "employee", None)
		split_pct = float(getattr(row, "split_percent", 0) or 0)
		if not employee or split_pct <= 0:
			continue
		if not frappe.db.exists(
			"Performance Log",
			{"employee": employee, "event_type": "Sale Completed", "reference_document": doc.name},
		):
			count += 1
	return count


commands = [backfill_cli]
