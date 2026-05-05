"""
Knowledge Base API - CRUD endpoints for RAG Knowledge Articles.

Staff can create, read, update, and delete knowledge base articles.
Articles are automatically indexed into the RAG vector store via doc_events.
"""

import frappe
from frappe.rate_limiter import rate_limit


@frappe.whitelist()
@rate_limit(limit=60, seconds=60)
def list_articles(
	category: str | None = None,
	search: str | None = None,
	visibility: str | None = None,
	start: int = 0,
	page_length: int = 20,
) -> dict:
	"""List knowledge base articles with optional filtering.

	Args:
		category: Filter by category (Policy, SOP, Repair Guide, Product Info, FAQ, Other)
		search: Text search across title and content
		visibility: Filter by visibility (Internal, Public)
		start: Pagination start
		page_length: Number of results

	Returns:
		Dict with articles list and total count.
	"""
	filters = {"is_active": 1}

	if category:
		filters["category"] = category
	if visibility:
		filters["visibility"] = visibility

	or_filters = None
	if search:
		or_filters = [
			["title", "like", f"%{search}%"],
			["content", "like", f"%{search}%"],
			["tags", "like", f"%{search}%"],
		]

	articles = frappe.get_all(
		"RAG Knowledge Article",
		filters=filters,
		or_filters=or_filters,
		fields=["name", "title", "category", "visibility", "tags", "is_active", "creation", "modified"],
		order_by="modified desc",
		start=int(start),
		page_length=int(page_length),
	)

	total = frappe.db.count("RAG Knowledge Article", filters=filters)

	return {"articles": articles, "total": total}


@frappe.whitelist(methods=["POST"])
def create_article(title: str, content: str, category: str = "FAQ", visibility: str = "Internal", tags: str | None = None) -> dict:
	"""Create a new knowledge base article.

	Args:
		title: Article title
		content: Article body (HTML from text editor)
		category: Article category
		visibility: Internal or Public
		tags: Comma-separated tags

	Returns:
		Dict with the new article name.
	"""
	frappe.only_for("System Manager", "Sales Manager")

	article = frappe.get_doc(
		{
			"doctype": "RAG Knowledge Article",
			"title": title.strip(),
			"content": content,
			"category": category,
			"visibility": visibility,
			"tags": tags.strip() if tags else "",
			"is_active": 1,
		}
	)
	article.insert(ignore_permissions=True)

	return {"name": article.name, "title": article.title}


@frappe.whitelist(methods=["POST"])
def update_article(name: str, **kwargs) -> dict:
	"""Update an existing knowledge base article.

	Args:
		name: Article ID
		kwargs: Fields to update (title, content, category, visibility, tags, is_active)

	Returns:
		Dict with updated article info.
	"""
	frappe.only_for("System Manager", "Sales Manager")

	article = frappe.get_doc("RAG Knowledge Article", name)

	updatable = ["title", "content", "category", "visibility", "tags", "is_active"]
	for field in updatable:
		if field in kwargs:
			setattr(article, field, kwargs[field])

	article.save(ignore_permissions=True)

	return {"name": article.name, "title": article.title}


@frappe.whitelist(methods=["POST"])
def delete_article(name: str) -> dict:
	"""Delete a knowledge base article.

	Args:
		name: Article ID

	Returns:
		Dict with status.
	"""
	frappe.only_for("System Manager")

	frappe.delete_doc("RAG Knowledge Article", name, ignore_permissions=True)

	return {"status": "deleted", "name": name}


@frappe.whitelist()
def get_article(name: str) -> dict:
	"""Get a single article with full content.

	Args:
		name: Article ID

	Returns:
		Full article dict.
	"""
	article = frappe.get_doc("RAG Knowledge Article", name)
	return {
		"name": article.name,
		"title": article.title,
		"content": article.content,
		"category": article.category,
		"visibility": article.visibility,
		"tags": article.tags,
		"is_active": article.is_active,
		"created": article.creation,
		"modified": article.modified,
	}


@frappe.whitelist()
def get_categories() -> list[dict]:
	"""Get list of article categories with counts.

	Returns:
		List of {category, count} dicts.
	"""
	categories = frappe.db.sql(
		"""SELECT category, COUNT(*) as count
		FROM `tabRAG Knowledge Article`
		WHERE is_active=1
		GROUP BY category
		ORDER BY count DESC""",
		as_dict=True,
	)
	return categories


@frappe.whitelist()
def get_stats() -> dict:
	"""Get knowledge base statistics.

	Returns:
		Dict with total articles, by category, by visibility.
	"""
	total = frappe.db.count("RAG Knowledge Article", filters={"is_active": 1})

	by_category = frappe.db.sql(
		"""SELECT category, COUNT(*) as count
		FROM `tabRAG Knowledge Article` WHERE is_active=1 GROUP BY category""",
		as_dict=True,
	)

	by_visibility = frappe.db.sql(
		"""SELECT visibility, COUNT(*) as count
		FROM `tabRAG Knowledge Article` WHERE is_active=1 GROUP BY visibility""",
		as_dict=True,
	)

	recent = frappe.get_all(
		"RAG Knowledge Article",
		filters={"is_active": 1},
		fields=["name", "title", "category", "modified"],
		order_by="modified desc",
		limit=5,
	)

	return {
		"total": total,
		"by_category": by_category,
		"by_visibility": by_visibility,
		"recent": recent,
	}
