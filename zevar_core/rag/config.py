"""
RAG Configuration Constants

Centralized configuration for the RAG system: embedding models, vector store
settings, collection names, and LLM provider endpoints.
"""

import os

# ---------------------------------------------------------------------------
# Embedding Model
# ---------------------------------------------------------------------------
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384  # all-MiniLM-L6-v2 output dimension
EMBEDDING_CACHE_DIR = os.path.join(
	os.environ.get("FRAPPE_BENCH_DIR", "/home/frappe/frappe-bench"),
	"sites",
	"{}.{}".format(os.environ.get("FRAPPE_SITE_NAME", "zevar"), "chroma_data"),
	"models",
)

# ---------------------------------------------------------------------------
# ChromaDB Vector Store
# ---------------------------------------------------------------------------
CHROMA_PERSIST_DIR = os.path.join(
	os.environ.get("FRAPPE_BENCH_DIR", "/home/frappe/frappe-bench"),
	"sites",
	"{}.{}".format(os.environ.get("FRAPPE_SITE_NAME", "zevar"), "chroma_data"),
)

# Collection names
COLLECTION_PRODUCTS = "zevar_products"
COLLECTION_CUSTOMERS = "zevar_customers"
COLLECTION_KNOWLEDGE = "zevar_knowledge"

# Indexing defaults
BATCH_SIZE = 100  # Number of documents to embed per batch
CHUNK_SIZE_TOKENS = 200
CHUNK_OVERLAP_TOKENS = 50

# ---------------------------------------------------------------------------
# LLM Provider - Self-hosted Qwen (OpenAI-compatible)
# ---------------------------------------------------------------------------
QWEN_DEFAULT_ENDPOINT = "http://172.18.20.151:4000/v1/chat/completions"
QWEN_DEFAULT_MODEL = "openai/Qwen3.6-35B-A3B-UD-Q4_K_S.gguf"
QWEN_DEFAULT_API_KEY = "sk-ynWSXoIn74HZcn2WV-ySSg"

# Generation settings
DEFAULT_MAX_TOKENS = 2048
DEFAULT_TEMPERATURE = 0.3

# ---------------------------------------------------------------------------
# Redis Cache (for embedding cache & query cache)
# ---------------------------------------------------------------------------
EMBEDDING_CACHE_PREFIX = "zevar_rag:emb:"
QUERY_CACHE_PREFIX = "zevar_rag:query:"
EMBEDDING_CACHE_TTL = 86400 * 7  # 7 days
QUERY_CACHE_TTL = 3600  # 1 hour

# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------
DEFAULT_TOP_K = 10  # Number of results from vector search
DEFAULT_RERANK_TOP_N = 10  # Final results after re-ranking
SIMILARITY_THRESHOLD = 0.3  # Minimum cosine similarity to include

# Query classification keywords
QUERY_DOMAINS = {
	"product": [
		"ring", "necklace", "chain", "bracelet", "earring", "pendant", "gold",
		"silver", "platinum", "diamond", "gemstone", "carat", "price", "cost",
		"show", "find", "looking", "search", "item", "jewelry", "metal",
		"purity", "weight", "stock", "available",
	],
	"customer": [
		"customer", "client", "purchase history", "buying", "bought",
		"preference", "recommend", "suggest", "ring size", "anniversary",
		"birthday", "gift",
	],
	"repair": [
		"repair", "fix", "resize", "polish", "clean", "solder", "stone",
		"reset", "estimate", "repair time", "repair status",
	],
	"policy": [
		"policy", "return", "exchange", "layaway", "cancellation", "refund",
		"warranty", "guarantee", "financing", "payment plan", "sop",
		"procedure", "guideline", "rule",
	],
	"general": [],
}

# ---------------------------------------------------------------------------
# DocType -> Collection Mapping
# ---------------------------------------------------------------------------
DOCTYPE_COLLECTION_MAP = {
	"Item": COLLECTION_PRODUCTS,
	"Customer": COLLECTION_CUSTOMERS,
	"RAG Knowledge Article": COLLECTION_KNOWLEDGE,
}
