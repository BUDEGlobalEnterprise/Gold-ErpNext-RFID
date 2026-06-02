# Copyright (c) 2026, Zevar Core
# License: GNU General Public License v3.0

from frappe.model.document import Document


class RAGInsightFeedback(Document):
	"""User feedback on a RAG-generated insight.

	Plan §9.9: weekly cron aggregates these to identify low-rated patterns
	and surface to admin. Used to tune the prompt template, not for fine-tuning.
	"""

	pass
