import frappe
from frappe.model.document import Document

CRON_LABELS = {
	"0 22 * * *": "Daily at 10 PM",
	"0 8 * * 1": "Weekly Monday 8 AM",
	"0 8 1 * *": "Monthly 1st 8 AM",
	"0 8 1 1 *": "Yearly Jan 1st 8 AM",
}


class ReportSubscription(Document):
	def validate(self):
		self._resolve_report_title()
		self._set_schedule_label()
		self._set_next_run()
		self._set_recipient_defaults()

	def _resolve_report_title(self):
		if self.report_id and not self.report_title:
			from zevar_core.api.reports import REPORT_CATALOG

			for r in REPORT_CATALOG:
				if r["id"] == self.report_id:
					self.report_title = r["title"]
					return
			self.report_title = self.report_id

	def _set_schedule_label(self):
		self.schedule_label = CRON_LABELS.get(self.cron_expression, self.cron_expression)

	def _set_next_run(self):
		from croniter import croniter

		now = frappe.utils.now_datetime()
		try:
			cron = croniter(self.cron_expression, now)
			self.next_run = cron.get_next(frappe.utils.Datetime)
		except Exception:
			self.next_run = None

	def _set_recipient_defaults(self):
		if not self.recipient_email and self.user:
			self.recipient_email = frappe.db.get_value("User", self.user, "email") or ""
