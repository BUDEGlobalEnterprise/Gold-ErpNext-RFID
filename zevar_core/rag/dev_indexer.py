"""
Zev RAG Indexer - Build vector index for the project.

This script scans the codebase, chunks files, and generates embeddings
to power Zev's context-aware RAG system.
- Python files: chunked by function/class with docstrings
- Vue files: chunked by component (template/script/style)
- DocType JSON: chunked by field definitions
- Config files: indexed as whole documents
"""

import ast
import json
import os
import re

import chromadb
from sentence_transformers import SentenceTransformer

# Paths
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_NAME = "zevar_core"
COLLECTION_NAME = "zevar_dev"

# ChromaDB storage for dev index (separate from app RAG)
CHROMA_DEV_DIR = os.path.join(APP_ROOT, ".chroma_dev")

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
BATCH_SIZE = 50


def build_index():
	"""Build or rebuild the dev codebase index."""
	print(f"Loading embedding model: {MODEL_NAME}...")
	model = SentenceTransformer(MODEL_NAME)

	print(f"Initializing ChromaDB at {CHROMA_DEV_DIR}...")
	client = chromadb.PersistentClient(path=CHROMA_DEV_DIR)

	# Drop existing collection for clean rebuild
	try:
		client.delete_collection(COLLECTION_NAME)
		print(f"Dropped existing collection '{COLLECTION_NAME}'")
	except Exception:
		pass

	collection = client.get_or_create_collection(
		name=COLLECTION_NAME,
		metadata={"hnsw:space": "cosine", "dimension": EMBEDDING_DIM},
	)

	# Collect all chunks
	chunks = []

	# 1. Index Python files
	print("Indexing Python files...")
	for root, _dirs, files in os.walk(APP_ROOT):
		# Skip hidden dirs, __pycache__, migrations, pyc
		if any(part.startswith(".") or part == "__pycache__" for part in root.split(os.sep)):
			continue
		for fname in files:
			if not fname.endswith(".py"):
				continue
			fpath = os.path.join(root, fname)
			rel_path = os.path.relpath(fpath, APP_ROOT)
			chunks.extend(_parse_python_file(fpath, rel_path))

	# 2. Index Vue/JS files
	print("Indexing Vue/JS files...")
	frontend_dir = os.path.join(os.path.dirname(APP_ROOT), "frontend", "zevar_ui", "src")
	if os.path.isdir(frontend_dir):
		for root, _dirs, files in os.walk(frontend_dir):
			if any(part.startswith(".") or part == "node_modules" for part in root.split(os.sep)):
				continue
			for fname in files:
				if fname.endswith((".vue", ".js")):
					fpath = os.path.join(root, fname)
					rel_path = os.path.relpath(fpath, os.path.dirname(APP_ROOT))
					chunks.extend(_parse_vue_file(fpath, rel_path))

	# 3. Index DocType JSON files
	print("Indexing DocType JSON files...")
	for root, _dirs, files in os.walk(APP_ROOT):
		if any(part.startswith(".") or part == "__pycache__" for part in root.split(os.sep)):
			continue
		for fname in files:
			if fname.endswith(".json") and "/doctype/" in root:
				fpath = os.path.join(root, fname)
				rel_path = os.path.relpath(fpath, APP_ROOT)
				chunks.extend(_parse_doctype_json(fpath, rel_path))

	# 4. Index hooks.py and config files
	for config_file in ["hooks.py", "modules.txt", "patches.txt"]:
		fpath = os.path.join(APP_ROOT, config_file)
		if os.path.exists(fpath):
			rel_path = config_file
			with open(fpath) as f:
				content = f.read()
			chunks.append({
				"id": f"config_{config_file.replace('.', '_')}",
				"text": f"File: {config_file}\n{content[:2000]}",
				"metadata": {"file_path": rel_path, "type": "config", "name": config_file},
			})

	print(f"\nTotal chunks to index: {len(chunks)}")

	if not chunks:
		print("No chunks found. Check the paths.")
		return

	# Embed and store in batches
	for i in range(0, len(chunks), BATCH_SIZE):
		batch = chunks[i : i + BATCH_SIZE]
		texts = [c["text"] for c in batch]
		embeddings = model.encode(texts, show_progress_bar=False).tolist()

		collection.upsert(
			ids=[c["id"] for c in batch],
			documents=texts,
			embeddings=embeddings,
			metadatas=[c["metadata"] for c in batch],
		)
		print(f"  Indexed {min(i + BATCH_SIZE, len(chunks))}/{len(chunks)} chunks")

	print(f"\nDone! Collection '{COLLECTION_NAME}' has {collection.count()} documents.")


def search_code(query: str, n_results: int = 10, file_type: str | None = None) -> list[dict]:
	"""Search the dev codebase index.

	Args:
		query: Natural language search query.
		n_results: Max results to return.
		file_type: Optional filter (python, vue, js, doctype, config).

	Returns:
		List of result dicts with text, metadata, similarity.
	"""
	client = chromadb.PersistentClient(path=CHROMA_DEV_DIR)
	model = SentenceTransformer(MODEL_NAME)

	try:
		collection = client.get_collection(COLLECTION_NAME)
	except Exception:
		return []

	embedding = model.encode([query], show_progress_bar=False).tolist()
	where = {"type": file_type} if file_type else None

	results = collection.query(
		query_embeddings=embedding,
		n_results=n_results,
		where=where,
		include=["documents", "metadatas", "distances"],
	)

	output = []
	if results and results["ids"] and results["ids"][0]:
		for i, doc_id in enumerate(results["ids"][0]):
			distance = results["distances"][0][i]
			similarity = 1.0 - (distance / 2.0)
			output.append({
				"id": doc_id,
				"text": results["documents"][0][i] if results.get("documents") else "",
				"metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
				"similarity": round(similarity, 4),
			})

	return output


# ---------- Parsers ----------


def _parse_python_file(fpath: str, rel_path: str) -> list[dict]:
	"""Parse a Python file into chunks by top-level functions and classes."""
	chunks = []
	try:
		with open(fpath) as f:
			source = f.read()
		tree = ast.parse(source)
	except Exception:
		return chunks

	module_doc = ast.get_docstring(tree)
	if module_doc:
		chunks.append({
			"id": f"py:{rel_path}:module",
			"text": f"File: {rel_path}\nModule docstring: {module_doc}",
			"metadata": {"file_path": rel_path, "type": "python", "name": rel_path, "kind": "module"},
		})

	for node in ast.iter_child_nodes(tree):
		if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
			chunks.append(_chunk_from_ast_node(node, rel_path, "function", source))
		elif isinstance(node, (ast.ClassDef,)):
			# Add class itself
			chunks.append(_chunk_from_ast_node(node, rel_path, "class", source))
			# Add methods
			for method in node.body:
				if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
					chunks.append(_chunk_from_ast_node(method, rel_path, "method", source, parent=node.name))

	return chunks


def _chunk_from_ast_node(node, rel_path, kind, source, parent=None) -> dict:
	"""Create a chunk from an AST node."""
	name = node.name
	docstring = ast.get_docstring(node) or ""

	# Get the source lines for this node
	start_line = node.lineno
	end_line = node.end_lineno or start_line
	lines = source.split("\n")
	code_snippet = "\n".join(lines[start_line - 1 : min(end_line, start_line + 30)])

	parts = [f"File: {rel_path}", f"Line {start_line}-{end_line}"]
	if parent:
		parts.append(f"{parent}.{name} ({kind})")
	else:
		parts.append(f"{name} ({kind})")
	if docstring:
		parts.append(f"Docstring: {docstring}")
	parts.append(f"Code:\n{code_snippet}")

	chunk_id = f"py:{rel_path}:{start_line}"
	if parent:
		chunk_id = f"py:{rel_path}:{parent}.{name}:{start_line}"

	return {
		"id": chunk_id,
		"text": "\n".join(parts),
		"metadata": {
			"file_path": rel_path,
			"type": "python",
			"name": name,
			"kind": kind,
			"parent": parent or "",
			"line_start": start_line,
			"line_end": end_line,
		},
	}


def _parse_vue_file(fpath: str, rel_path: str) -> list[dict]:
	"""Parse a Vue file into chunks by template, script, and style sections."""
	chunks = []
	try:
		with open(fpath) as f:
			content = f.read()
	except Exception:
		return chunks

	# Split by top-level blocks
	sections = {"template": "", "script": "", "style": ""}
	for section in sections:
		match = re.search(rf"<{section}[^>]*>(.*?)</{section}>", content, re.DOTALL)
		if match:
			sections[section] = match.group(1).strip()

	component_name = os.path.splitext(os.path.basename(fpath))[0]

	# Index script section (most useful for code search)
	if sections["script"]:
		chunks.append({
			"id": f"vue:{rel_path}:script",
			"text": f"File: {rel_path}\nComponent: {component_name}\nScript:\n{sections['script'][:3000]}",
			"metadata": {"file_path": rel_path, "type": "vue", "name": component_name, "kind": "script"},
		})

	# Index template (useful for finding UI patterns)
	if sections["template"]:
		chunks.append({
			"id": f"vue:{rel_path}:template",
			"text": f"File: {rel_path}\nComponent: {component_name}\nTemplate:\n{sections['template'][:2000]}",
			"metadata": {"file_path": rel_path, "type": "vue", "name": component_name, "kind": "template"},
		})

	return chunks


def _parse_doctype_json(fpath: str, rel_path: str) -> list[dict]:
	"""Parse a DocType JSON file into a searchable chunk."""
	chunks = []
	try:
		with open(fpath) as f:
			data = json.load(f)
	except Exception:
		return chunks

	doctype_name = data.get("name", os.path.basename(os.path.dirname(fpath)))

	# Build field summary
	fields = data.get("fields", [])
	field_summary = []
	for field in fields:
		parts = [field.get("fieldname", "")]
		if field.get("fieldtype"):
			parts.append(f"({field['fieldtype']})")
		if field.get("label"):
			parts.append(f"label: {field['label']}")
		if field.get("options"):
			parts.append(f"options: {field['options']}")
		field_summary.append(" ".join(parts))

	text_parts = [
		f"DocType: {doctype_name}",
		f"Module: {data.get('module', '')}",
		f"Type: {'Single' if data.get('issingle') else 'Document'}",
	]
	if field_summary:
		text_parts.append(f"Fields ({len(field_summary)}):\n" + "\n".join(field_summary[:50]))
	if data.get("permissions"):
		perms = [f"{p.get('role', '')} ({'R' if p.get('read') else ''}{'W' if p.get('write') else ''}{'C' if p.get('create') else ''}{'D' if p.get('delete') else ''})" for p in data["permissions"][:10]]
		text_parts.append(f"Permissions: {', '.join(perms)}")

	chunks.append({
		"id": f"doctype:{rel_path}",
		"text": "\n".join(text_parts),
		"metadata": {
			"file_path": rel_path,
			"type": "doctype",
			"name": doctype_name,
			"kind": "schema",
			"field_count": len(fields),
		},
	})

	return chunks


if __name__ == "__main__":
	build_index()
