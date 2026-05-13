<template>
	<AppLayout>
		<div class="flex flex-col max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
			<!-- Header -->
			<div class="mb-6 flex items-center justify-between">
				<div>
					<h2 class="text-2xl font-bold text-gray-900 dark:text-white">
						Knowledge Base
					</h2>
					<p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
						Manage articles for AI-powered search and staff assistance
					</p>
				</div>
				<div class="flex items-center gap-3">
					<span class="text-sm text-gray-500 dark:text-gray-400">
						{{ stats.total || 0 }} articles
					</span>
					<button
						class="px-4 py-2 rounded-lg bg-gradient-to-r from-violet-500 to-indigo-500 text-white text-sm font-medium hover:opacity-90 transition-opacity"
						@click="openEditor()"
					>
						+ New Article
					</button>
				</div>
			</div>

			<!-- Stats Cards -->
			<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
				<div
					v-for="cat in stats.by_category || []"
					:key="cat.category"
					class="bg-white dark:bg-warm-card rounded-xl p-4 border border-gray-100 dark:border-warm-border/50"
				>
					<div class="text-2xl font-bold text-gray-900 dark:text-white">
						{{ cat.count }}
					</div>
					<div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
						{{ cat.category }}
					</div>
				</div>
				<div
					v-if="!stats.by_category?.length"
					class="col-span-2 md:col-span-4 bg-white dark:bg-warm-card rounded-xl p-4 border border-gray-100 dark:border-warm-border/50 text-center text-gray-400"
				>
					No articles yet. Create your first knowledge base article.
				</div>
			</div>

			<div class="flex flex-col md:flex-row gap-6 h-[calc(100vh-340px)]">
				<!-- Left: Filters & List -->
				<div
					class="w-full md:w-1/3 bg-white dark:bg-warm-card rounded-2xl p-4 shadow-sm border border-gray-100 dark:border-warm-border/50 overflow-y-auto custom-scrollbar"
				>
					<!-- Search -->
					<div class="relative mb-4">
						<svg
							class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
							width="16"
							height="16"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<circle cx="11" cy="11" r="8" />
							<line x1="21" y1="21" x2="16.65" y2="16.65" />
						</svg>
						<input
							v-model="searchQuery"
							class="w-full pl-9 pr-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-violet-400 focus:border-transparent"
							placeholder="Search articles..."
							@input="debouncedLoad"
						/>
					</div>

					<!-- Category Filter -->
					<div class="flex flex-wrap gap-2 mb-4">
						<button
							v-for="cat in allCategories"
							:key="cat"
							class="px-3 py-1 rounded-full text-xs font-medium transition-colors"
							:class="
								selectedCategory === cat
									? 'bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300'
									: 'bg-gray-100 dark:bg-warm-dark-900 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-warm-dark-800'
							"
							@click="selectedCategory = cat; loadArticles()"
						>
							{{ cat }}
						</button>
						<button
							class="px-3 py-1 rounded-full text-xs font-medium transition-colors"
							:class="
								!selectedCategory
									? 'bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300'
									: 'bg-gray-100 dark:bg-warm-dark-900 text-gray-600 dark:text-gray-400'
							"
							@click="selectedCategory = null; loadArticles()"
						>
							All
						</button>
					</div>

					<!-- Article List -->
					<div class="space-y-2">
						<div
							v-for="article in articles"
							:key="article.name"
							class="p-3 rounded-lg cursor-pointer transition-colors border"
							:class="
								selectedArticle?.name === article.name
									? 'bg-violet-50 dark:bg-violet-900/20 border-violet-200 dark:border-violet-800'
									: 'bg-gray-50 dark:bg-warm-dark-900 border-transparent hover:bg-gray-100 dark:hover:bg-warm-dark-800'
							"
							@click="selectArticle(article)"
						>
							<div class="flex items-start justify-between gap-2">
								<div class="min-w-0">
									<h4
										class="text-sm font-medium text-gray-900 dark:text-white truncate"
									>
										{{ article.title }}
									</h4>
									<div class="flex items-center gap-2 mt-1">
										<span
											class="text-[10px] px-1.5 py-0.5 rounded bg-gray-200 dark:bg-warm-dark-800 text-gray-600 dark:text-gray-400"
										>
											{{ article.category }}
										</span>
										<span
											class="text-[10px] px-1.5 py-0.5 rounded"
											:class="
												article.visibility === 'Public'
													? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
													: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
											"
										>
											{{ article.visibility }}
										</span>
									</div>
								</div>
								<button
									class="p-1 rounded hover:bg-gray-200 dark:hover:bg-warm-dark-700 text-gray-400 hover:text-red-500 transition-colors flex-shrink-0"
									title="Delete"
									@click.stop="confirmDelete(article)"
								>
									<svg
										width="14"
										height="14"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
									>
										<polyline points="3 6 5 6 21 6" />
										<path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
									</svg>
								</button>
							</div>
							<div class="text-[10px] text-gray-400 mt-1">
								{{ formatDate(article.modified) }}
							</div>
						</div>

						<div
							v-if="!articles.length"
							class="text-center py-8 text-gray-400 text-sm"
						>
							{{
								searchQuery
									? 'No articles match your search'
									: 'No articles in this category'
							}}
						</div>
					</div>
				</div>

				<!-- Right: Editor / Preview -->
				<div
					class="flex-1 bg-white dark:bg-warm-card rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-warm-border/50 overflow-y-auto custom-scrollbar"
				>
					<!-- No selection state -->
					<div
						v-if="!editing && !selectedArticle"
						class="flex flex-col items-center justify-center h-full text-gray-400"
					>
						<svg
							width="48"
							height="48"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="1.5"
						>
							<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
							<polyline points="14 2 14 8 20 8" />
							<line x1="16" y1="13" x2="8" y2="13" />
							<line x1="16" y1="17" x2="8" y2="17" />
						</svg>
						<p class="mt-4 text-sm">Select an article to view or edit</p>
						<button
							class="mt-3 px-4 py-2 rounded-lg bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300 text-sm font-medium hover:bg-violet-200 dark:hover:bg-violet-900/50"
							@click="openEditor()"
						>
							Create new article
						</button>
					</div>

					<!-- View mode -->
					<div v-else-if="!editing && selectedArticle" class="space-y-4">
						<div class="flex items-start justify-between">
							<div>
								<h3 class="text-xl font-bold text-gray-900 dark:text-white">
									{{ selectedArticle.title }}
								</h3>
								<div class="flex items-center gap-2 mt-2">
									<span
										class="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-warm-dark-900 text-gray-600 dark:text-gray-400"
									>
										{{ selectedArticle.category }}
									</span>
									<span
										class="text-xs px-2 py-1 rounded"
										:class="
											selectedArticle.visibility === 'Public'
												? 'bg-green-100 dark:bg-green-900/30 text-green-700'
												: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700'
										"
									>
										{{ selectedArticle.visibility }}
									</span>
								</div>
							</div>
							<button
								class="px-3 py-1.5 rounded-lg bg-gray-100 dark:bg-warm-dark-900 text-gray-700 dark:text-gray-300 text-sm font-medium hover:bg-gray-200 dark:hover:bg-warm-dark-800"
								@click="openEditor(selectedArticle)"
							>
								Edit
							</button>
						</div>
						<div
							class="prose dark:prose-invert max-w-none text-sm"
							v-html="selectedArticle.content"
						></div>
					</div>

					<!-- Edit/Create mode -->
					<div v-else class="space-y-4">
						<div class="flex items-center justify-between">
							<h3 class="text-lg font-bold text-gray-900 dark:text-white">
								{{ editForm.name ? 'Edit Article' : 'New Article' }}
							</h3>
							<div class="flex gap-2">
								<button
									class="px-3 py-1.5 rounded-lg bg-gray-100 dark:bg-warm-dark-900 text-gray-700 dark:text-gray-300 text-sm"
									@click="cancelEdit"
								>
									Cancel
								</button>
								<button
									class="px-4 py-1.5 rounded-lg bg-gradient-to-r from-violet-500 to-indigo-500 text-white text-sm font-medium hover:opacity-90 disabled:opacity-50"
									:disabled="
										!editForm.title?.trim() ||
										!editForm.content?.trim() ||
										saving
									"
									@click="saveArticle"
								>
									{{ saving ? 'Saving...' : 'Save' }}
								</button>
							</div>
						</div>

						<!-- Title -->
						<input
							v-model="editForm.title"
							class="w-full px-4 py-3 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-lg font-medium text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-violet-400"
							placeholder="Article title"
						/>

						<!-- Category & Visibility row -->
						<div class="flex gap-3">
							<select
								v-model="editForm.category"
								class="flex-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-gray-100"
							>
								<option value="Policy">Policy</option>
								<option value="SOP">SOP</option>
								<option value="Repair Guide">Repair Guide</option>
								<option value="Product Info">Product Info</option>
								<option value="FAQ">FAQ</option>
								<option value="Other">Other</option>
							</select>
							<select
								v-model="editForm.visibility"
								class="flex-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-gray-100"
							>
								<option value="Internal">Internal (Staff Only)</option>
								<option value="Public">Public (Customer-Facing)</option>
							</select>
						</div>

						<!-- Tags -->
						<input
							v-model="editForm.tags"
							class="w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-gray-100"
							placeholder="Tags (comma-separated, e.g., layaway, return, policy)"
						/>

						<!-- Content Editor -->
						<textarea
							v-model="editForm.content"
							class="w-full min-h-[300px] px-4 py-3 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-violet-400 font-mono leading-relaxed"
							placeholder="Write the article content here. You can use HTML tags for formatting:
<b>bold</b>, <i>italic</i>, <ul><li>lists</li></ul>, <h4>headings</h4>"
						></textarea>

						<p class="text-xs text-gray-400">
							Saved articles are automatically indexed for AI search. The article
							will appear in AI responses when staff ask related questions.
						</p>
					</div>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { createResource } from 'frappe-ui'

const articles = ref([])
const stats = ref({ total: 0, by_category: [], by_visibility: [], recent: [] })
const selectedArticle = ref(null)
const selectedCategory = ref(null)
const searchQuery = ref('')
const editing = ref(false)
const saving = ref(false)
const editForm = ref({
	title: '',
	content: '',
	category: 'FAQ',
	visibility: 'Internal',
	tags: '',
	name: '',
})
let debounceTimer = null

const allCategories = ['Policy', 'SOP', 'Repair Guide', 'Product Info', 'FAQ', 'Other']

// Resources
const listResource = createResource({
	url: 'zevar_core.rag.api.knowledge_base.list_articles',
	onSuccess(data) {
		articles.value = data?.articles || []
	},
})

const statsResource = createResource({
	url: 'zevar_core.rag.api.knowledge_base.get_stats',
	onSuccess(data) {
		stats.value = data || {}
	},
})

const getArticleResource = createResource({
	url: 'zevar_core.rag.api.knowledge_base.get_article',
	onSuccess(data) {
		if (data) {
			selectedArticle.value = data
		}
	},
})

const createResource2 = createResource({
	url: 'zevar_core.rag.api.knowledge_base.create_article',
	onSuccess() {
		saving.value = false
		editing.value = false
		loadArticles()
		loadStats()
	},
	onError() {
		saving.value = false
	},
})

const updateResource = createResource({
	url: 'zevar_core.rag.api.knowledge_base.update_article',
	onSuccess() {
		saving.value = false
		editing.value = false
		loadArticles()
		loadStats()
		if (editForm.value.name) {
			selectArticle({ name: editForm.value.name })
		}
	},
	onError() {
		saving.value = false
	},
})

const deleteResource = createResource({
	url: 'zevar_core.rag.api.knowledge_base.delete_article',
	onSuccess() {
		if (selectedArticle.value?.name === editForm.value.name) {
			selectedArticle.value = null
		}
		loadArticles()
		loadStats()
	},
})

function loadArticles() {
	listResource.fetch({
		category: selectedCategory.value || undefined,
		search: searchQuery.value || undefined,
		start: 0,
		page_length: 50,
	})
}

function loadStats() {
	statsResource.fetch()
}

function debouncedLoad() {
	clearTimeout(debounceTimer)
	debounceTimer = setTimeout(loadArticles, 400)
}

function selectArticle(article) {
	editing.value = false
	getArticleResource.fetch({ name: article.name })
}

function openEditor(article = null) {
	editing.value = true
	if (article) {
		editForm.value = {
			name: article.name,
			title: article.title,
			content: article.content || '',
			category: article.category || 'FAQ',
			visibility: article.visibility || 'Internal',
			tags: article.tags || '',
		}
		// Fetch full content if not loaded
		if (!article.content) {
			getArticleResource.fetch({ name: article.name })
		}
	} else {
		editForm.value = {
			title: '',
			content: '',
			category: 'FAQ',
			visibility: 'Internal',
			tags: '',
			name: '',
		}
	}
}

function cancelEdit() {
	editing.value = false
}

function saveArticle() {
	if (!editForm.value.title?.trim() || !editForm.value.content?.trim()) return

	saving.value = true
	if (editForm.value.name) {
		updateResource.fetch(editForm.value)
	} else {
		createResource2.fetch({
			title: editForm.value.title,
			content: editForm.value.content,
			category: editForm.value.category,
			visibility: editForm.value.visibility,
			tags: editForm.value.tags,
		})
	}
}

function confirmDelete(article) {
	if (confirm(`Delete "${article.title}"? This will also remove it from the AI search index.`)) {
		editForm.value.name = article.name
		deleteResource.fetch({ name: article.name })
	}
}

function formatDate(dateStr) {
	if (!dateStr) return ''
	const d = new Date(dateStr)
	const now = new Date()
	const diff = now - d
	if (diff < 60000) return 'Just now'
	if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
	if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
	return d.toLocaleDateString()
}

onMounted(() => {
	loadArticles()
	loadStats()
})
</script>
