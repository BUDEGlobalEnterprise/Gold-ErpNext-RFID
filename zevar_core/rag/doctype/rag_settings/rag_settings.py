"""
RAG Settings - Single DocType Controller

Stores configuration for the RAG system: embedding model, LLM providers,
and indexing parameters.
"""

import frappe
from frappe.model.document import Document


class RAGSettings(Document):
	def validate(self):
		# Update embedding dimension based on model selection
		dimensions = {
			"all-MiniLM-L6-v2": 384,
			"all-mpnet-base-v2": 768,
		}
		self.embedding_dimension = dimensions.get(self.embedding_model, 384)
