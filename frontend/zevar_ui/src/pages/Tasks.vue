<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Tasks</h2>
					<span v-if="store.overdueCount" class="text-[9px] font-bold px-2 py-0.5 rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">{{ store.overdueCount }} overdue</span>
				</div>
				<div class="flex items-center gap-2">
					<div class="flex bg-gray-100 dark:bg-warm-dark-700 rounded-lg p-0.5">
						<button @click="viewMode = 'kanban'" class="px-2.5 py-1 rounded text-[10px] font-bold transition" :class="viewMode === 'kanban' ? 'bg-white dark:bg-warm-dark-600 text-gray-900 dark:text-white shadow-sm' : 'text-gray-500'">Kanban</button>
						<button @click="viewMode = 'list'" class="px-2.5 py-1 rounded text-[10px] font-bold transition" :class="viewMode === 'list' ? 'bg-white dark:bg-warm-dark-600 text-gray-900 dark:text-white shadow-sm' : 'text-gray-500'">List</button>
						<button @click="viewMode = 'todos'" class="px-2.5 py-1 rounded text-[10px] font-bold transition" :class="viewMode === 'todos' ? 'bg-white dark:bg-warm-dark-600 text-gray-900 dark:text-white shadow-sm' : 'text-gray-500'">My Todos</button>
					</div>
					<button @click="showCreate = true" class="flex items-center gap-1.5 px-3 py-2 bg-[#D4AF37] text-white rounded-lg text-xs font-bold hover:bg-[#C4A030] transition">
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" /></svg>
						Add
					</button>
				</div>
			</div>

			<!-- KPI Cards -->
			<div v-if="store.taskStats" class="grid grid-cols-2 lg:grid-cols-5 gap-3 mb-4 flex-shrink-0">
				<div class="premium-card !p-3"><div class="text-[10px] font-bold text-gray-500 uppercase">Total</div><div class="text-xl font-bold text-gray-900 dark:text-white">{{ store.taskStats.total || 0 }}</div></div>
				<div class="premium-card !p-3"><div class="text-[10px] font-bold text-gray-500 uppercase">To Do</div><div class="text-xl font-bold text-blue-500">{{ store.taskStats.by_status?.Todo || 0 }}</div></div>
				<div class="premium-card !p-3"><div class="text-[10px] font-bold text-gray-500 uppercase">In Progress</div><div class="text-xl font-bold text-amber-500">{{ store.taskStats.by_status?.['In Progress'] || 0 }}</div></div>
				<div class="premium-card !p-3"><div class="text-[10px] font-bold text-gray-500 uppercase">Done</div><div class="text-xl font-bold text-emerald-500">{{ store.taskStats.by_status?.Done || 0 }}</div></div>
				<div class="premium-card !p-3"><div class="text-[10px] font-bold text-gray-500 uppercase">Overdue</div><div class="text-xl font-bold text-red-500">{{ store.taskStats.overdue || 0 }}</div></div>
			</div>

			<!-- Kanban View -->
			<div v-if="viewMode === 'kanban'" class="flex-1 overflow-x-auto min-h-0">
				<div class="flex gap-3 h-full min-w-[700px]">
					<div v-for="col in kanbanColumns" :key="col.status" class="flex-1 min-w-[200px] flex flex-col">
						<div class="flex items-center gap-2 mb-3 px-1">
							<div class="w-2 h-2 rounded-full" :style="{ background: col.color }"></div>
							<span class="text-xs font-bold text-gray-700 dark:text-gray-300">{{ col.label }}</span>
							<span class="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-gray-100 dark:bg-warm-dark-700 text-gray-500">{{ col.tasks.length }}</span>
						</div>
						<div class="flex-1 overflow-y-auto space-y-2 pr-1">
							<div v-for="task in col.tasks" :key="task.id" class="premium-card !p-3 cursor-pointer hover:border-[#D4AF37]/50" @click="viewTask(task)">
								<div class="text-xs font-bold text-gray-900 dark:text-white mb-1">{{ task.title }}</div>
								<div v-if="task.project_name" class="text-[10px] text-gray-500 mb-1.5">{{ task.project_name }}</div>
								<div class="flex items-center justify-between">
									<span v-if="task.priority" class="text-[9px] font-bold px-1.5 py-0.5 rounded" :class="priorityClass(task.priority)">{{ task.priority }}</span>
									<span v-if="task.due_date" class="text-[9px] font-mono" :class="task.is_overdue ? 'text-red-500 font-bold' : 'text-gray-400'">{{ task.due_date }}</span>
								</div>
							</div>
							<div v-if="!col.tasks.length" class="text-center py-8 text-gray-300 dark:text-gray-600 text-xs">No tasks</div>
						</div>
					</div>
				</div>
			</div>

			<!-- List View -->
			<div v-if="viewMode === 'list'" class="flex-1 overflow-y-auto min-h-0">
				<div v-if="store.tasksResource.loading && !store.tasks.length" class="flex items-center justify-center py-20"><div class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"></div></div>
				<div v-else-if="!store.tasks.length" class="text-center py-20 text-gray-400 text-sm">No tasks assigned</div>
				<div v-else class="premium-card !p-0 overflow-hidden">
					<table class="w-full text-sm">
						<thead><tr class="bg-gray-50 dark:bg-warm-dark-700 border-b border-gray-200 dark:border-warm-border/50">
							<th class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase">Task</th>
							<th class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase hidden sm:table-cell">Project</th>
							<th class="text-center px-4 py-3 text-[10px] font-bold text-gray-500 uppercase hidden md:table-cell">Priority</th>
							<th class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase hidden md:table-cell">Due</th>
							<th class="text-center px-4 py-3 text-[10px] font-bold text-gray-500 uppercase">Status</th>
						</tr></thead>
						<tbody>
							<tr v-for="t in store.tasks" :key="t.id" class="border-b border-gray-100 dark:border-warm-border/50 hover:bg-gray-50/50 dark:hover:bg-white/[0.02] transition-colors cursor-pointer" @click="viewTask(t)">
								<td class="px-4 py-3"><div class="text-xs font-bold text-gray-900 dark:text-white">{{ t.title }}</div></td>
								<td class="px-4 py-3 text-xs text-gray-500 hidden sm:table-cell">{{ t.project_name || '-' }}</td>
								<td class="px-4 py-3 text-center hidden md:table-cell"><span class="text-[9px] font-bold px-1.5 py-0.5 rounded" :class="priorityClass(t.priority)">{{ t.priority }}</span></td>
								<td class="px-4 py-3 text-xs hidden md:table-cell" :class="t.is_overdue ? 'text-red-500 font-bold' : 'text-gray-500'">{{ t.due_date || '-' }}</td>
								<td class="px-4 py-3 text-center"><span class="text-[9px] font-bold px-2 py-1 rounded-full" :class="taskStatusClass(t.status)">{{ t.status }}</span></td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>

			<!-- Todos View -->
			<div v-if="viewMode === 'todos'" class="flex-1 overflow-y-auto min-h-0">
				<div class="flex items-center gap-2 mb-3">
					<button @click="todoFilter = 'Open'; store.loadTodos('Open')" class="px-3 py-1.5 rounded-full text-xs font-bold transition" :class="todoFilter === 'Open' ? 'bg-[#D4AF37] text-white' : 'bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300'">Open ({{ store.todoCount }})</button>
					<button @click="todoFilter = 'Closed'; store.loadTodos('Closed')" class="px-3 py-1.5 rounded-full text-xs font-bold transition" :class="todoFilter === 'Closed' ? 'bg-[#D4AF37] text-white' : 'bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300'">Closed</button>
				</div>
				<div v-if="store.todosResource.loading && !store.todos.length" class="flex items-center justify-center py-20"><div class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"></div></div>
				<div v-else-if="!store.todos.length" class="text-center py-20 text-gray-400 text-sm">No todos</div>
				<div v-else class="space-y-2">
					<div v-for="todo in store.todos" :key="todo.id" class="premium-card !p-3 flex items-start gap-3">
						<button @click="toggleTodo(todo)" class="mt-0.5 w-5 h-5 rounded-md border-2 flex items-center justify-center transition shrink-0" :class="todo.status === 'Closed' ? 'bg-emerald-500 border-emerald-500' : 'border-gray-300 dark:border-gray-600 hover:border-[#D4AF37]'">
							<svg v-if="todo.status === 'Closed'" class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
						</button>
						<div class="flex-1 min-w-0">
							<div class="text-xs text-gray-900 dark:text-white" :class="{ 'line-through opacity-50': todo.status === 'Closed' }">{{ todo.description }}</div>
							<div class="flex items-center gap-3 mt-1">
								<span v-if="todo.date" class="text-[10px] text-gray-500">{{ todo.date }}</span>
								<span v-if="todo.priority" class="text-[9px] font-bold px-1.5 py-0.5 rounded" :class="priorityClass(todo.priority)">{{ todo.priority }}</span>
							</div>
						</div>
						<button @click="handleDeleteTodo(todo.id)" class="p-1 text-gray-400 hover:text-red-500 shrink-0"><svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg></button>
					</div>
				</div>
			</div>

			<!-- Create Modal -->
			<div v-if="showCreate" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" @click.self="showCreate = false">
				<div class="premium-card !rounded-2xl w-full max-w-md max-h-[80vh] overflow-y-auto m-4">
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-bold text-gray-900 dark:text-white">New Todo</h3>
						<button @click="showCreate = false" class="p-1 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded-lg"><svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg></button>
					</div>
					<div class="space-y-3">
						<div><label class="text-[10px] font-bold text-gray-500 uppercase">Description</label><textarea v-model="todoForm.description" rows="3" placeholder="What needs to be done?" class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white outline-none focus:ring-2 focus:ring-[#D4AF37] resize-none"></textarea></div>
						<div class="grid grid-cols-2 gap-3">
							<div><label class="text-[10px] font-bold text-gray-500 uppercase">Due Date</label><input v-model="todoForm.date" type="date" class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white outline-none focus:ring-2 focus:ring-[#D4AF37]" /></div>
							<div><label class="text-[10px] font-bold text-gray-500 uppercase">Priority</label><select v-model="todoForm.priority" class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white outline-none focus:ring-2 focus:ring-[#D4AF37]"><option>Low</option><option>Medium</option><option>High</option></select></div>
						</div>
					</div>
					<button @click="handleCreateTodo" :disabled="store.createTodoResource.loading" class="w-full mt-4 py-2.5 bg-[#D4AF37] text-white rounded-lg text-sm font-bold hover:bg-[#C4A030] transition disabled:opacity-50">
						{{ store.createTodoResource.loading ? 'Creating...' : 'Create Todo' }}
					</button>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { toast } from 'frappe-ui'
import AppLayout from '@/components/AppLayout.vue'
import { useTasksStore } from '@/stores/tasks.js'

const store = useTasksStore()
const viewMode = ref('kanban')
const todoFilter = ref('Open')
const showCreate = ref(false)
const todoForm = ref({ description: '', date: '', priority: 'Medium' })

const kanbanColumns = computed(() => {
	const cols = [
		{ status: 'Backlog', label: 'Backlog', color: '#94a3b8', tasks: [] },
		{ status: 'Todo', label: 'To Do', color: '#3b82f6', tasks: [] },
		{ status: 'In Progress', label: 'In Progress', color: '#f59e0b', tasks: [] },
		{ status: 'Done', label: 'Done', color: '#22c55e', tasks: [] },
	]
	for (const task of store.tasks) {
		const col = cols.find((c) => c.status === task.status)
		if (col) col.tasks.push(task)
		else cols[0].tasks.push(task)
	}
	return cols
})

function loadAll() {
	store.loadTasks()
	store.loadTaskStats()
	store.loadTodos('Open')
}

function viewTask(task) {
	// For now, just toggle status inline
	const nextMap = { Backlog: 'Todo', Todo: 'In Progress', 'In Progress': 'Done', Done: 'Backlog' }
	const next = nextMap[task.status] || 'Todo'
	store.updateTaskStatus(task.id, next).then(() => {
		toast({ title: `Moved to ${next}`, icon: 'check', intent: 'success' })
		store.loadTasks()
		store.loadTaskStats()
	})
}

async function toggleTodo(todo) {
	const newStatus = todo.status === 'Open' ? 'Closed' : 'Open'
	await store.updateTodo(todo.id, newStatus)
	store.loadTodos(todoFilter.value)
}

async function handleDeleteTodo(id) {
	await store.deleteTodo(id)
	toast({ title: 'Todo deleted', icon: 'check', intent: 'success' })
	store.loadTodos(todoFilter.value)
}

async function handleCreateTodo() {
	if (!todoForm.value.description) { toast({ title: 'Description required', icon: 'alert-circle', intent: 'warning' }); return }
	await store.createTodo(todoForm.value.description, todoForm.value.date, todoForm.value.priority)
	toast({ title: 'Todo created', icon: 'check', intent: 'success' })
	showCreate.value = false
	todoForm.value = { description: '', date: '', priority: 'Medium' }
	store.loadTodos('Open')
}

function priorityClass(p) {
	const map = {
		Low: 'bg-gray-100 dark:bg-gray-800 text-gray-500',
		Medium: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400',
		High: 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400',
		Urgent: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400',
	}
	return map[p] || 'bg-gray-100 text-gray-500'
}

function taskStatusClass(s) {
	const map = {
		Backlog: 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300',
		Todo: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400',
		'In Progress': 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400',
		Done: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400',
		Canceled: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400',
	}
	return map[s] || 'bg-gray-100 text-gray-600'
}

onMounted(loadAll)
</script>
