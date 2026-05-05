"""
Bench Commands for RAG System

Usage:
    bench --site <site> build-rag-index [--doctype Item] [--rebuild]
    bench --site <site> rag-stats
    bench --site <site> build-dev-index
"""

import click
import frappe
from frappe.commands import get_site, pass_context


@click.command("build-rag-index")
@click.option("--doctype", default=None, help="Index only this DocType (Item, Customer)")
@click.option("--rebuild", is_flag=True, default=False, help="Drop and rebuild from scratch")
@pass_context
def build_rag_index(context, doctype=None, rebuild=False):
	"""Build or rebuild the RAG vector index for AI-powered search.

	Indexes products, customers, and knowledge articles into ChromaDB
	for semantic similarity search.

	Examples:
	    bench --site zevar build-rag-index
	    bench --site zevar build-rag-index --doctype Item
	    bench --site zevar build-rag-index --rebuild
	"""
	from zevar_core.rag.indexing.pipeline import IndexingPipeline

	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()

	try:
		pipeline = IndexingPipeline()

		if doctype:
			if rebuild:
				click.echo(f"Rebuilding index for {doctype}...")
				count = pipeline.rebuild_collection(doctype)
			else:
				click.echo(f"Indexing {doctype}...")
				count = pipeline.bulk_index_doctype(doctype)
			click.echo(f"Done: {count} documents indexed.")
		else:
			if rebuild:
				click.echo("Rebuilding all indexes...")
				results = pipeline.rebuild_all()
			else:
				click.echo("Indexing all DocTypes...")
				results = {}
				for dt in ["Item", "Customer"]:
					results[dt] = pipeline.bulk_index_doctype(dt)

			for dt, count in results.items():
				click.echo(f"  {dt}: {count} documents indexed")

		click.echo("RAG index build complete.")
	finally:
		frappe.destroy()


@click.command("rag-stats")
@pass_context
def rag_stats(context):
	"""Show RAG index statistics (collection counts vs database counts).

	Example:
	    bench --site zevar rag-stats
	"""
	from zevar_core.rag.indexing.store import VectorStore

	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()

	try:
		store = VectorStore()
		stats = store.get_all_collection_stats()

		click.echo("\nRAG Index Statistics:")
		click.echo("-" * 40)
		for name, info in stats.items():
			click.echo(f"  {name}: {info['count']} documents")
		click.echo()
	finally:
		frappe.destroy()


@click.command("build-dev-index")
@pass_context
def build_dev_index(context):
	"""Build the dev codebase index for MCP semantic code search.

	Indexes Python, Vue, and DocType JSON files so Claude Code
	can search the codebase semantically.

	Example:
	    bench build-dev-index
	"""
	click.echo("Building dev codebase index...")
	click.echo("Indexing Python, Vue, and DocType files into ChromaDB.\n")

	from zevar_core.rag.dev_indexer import build_index

	build_index()

	click.echo("\nDev index complete. MCP server can now search the codebase.")


commands = [
	build_rag_index,
	rag_stats,
	build_dev_index,
]
