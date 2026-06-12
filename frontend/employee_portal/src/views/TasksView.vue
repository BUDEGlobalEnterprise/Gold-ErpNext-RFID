<template>
		<!-- Header -->
		<div class="flex flex-col md:flex-row md:items-end justify-between gap-8 shrink-0 px-2">
			<div>
				<h1 class="text-4xl font-black text-gray-900 tracking-tight leading-none mb-3">
					My Tasks
				</h1>
				<p class="text-gray-500 font-medium font-sans">
					Manage the precision workflow for the Spring Collection.
				</p>
			</div>
			<div class="flex items-center justify-end gap-4 mb-2">
				<!-- User Filter Dropdown -->
				<div v-if="metadata.can_assign_to_others" class="flex items-center gap-2">
					<label class="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">User:</label>
					<div class="relative">
						<select
							v-model="selectedUserFilter"
							class="appearance-none pr-8 pl-3 py-2 text-sm cursor-pointer min-w-[200px] border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-1 focus:ring-primary"
						>
							<option value="">All Users</option>
							<option v-for="user in metadata.users" :key="user.name" :value="user.name">
								{{ user.full_name }}
							</option>
						</select>
					</div>
				</div>
				<button
					@click="openAddTaskDialog"
					class="px-5 py-3 rounded-lg text-[11px] font-black uppercase tracking-[0.2em] transition-all flex items-center gap-2 bg-emerald-950 text-white shadow-glow-emerald hover:bg-emerald-900 active:scale-[0.98]"
				>
					<span class="material-symbols-outlined text-lg">add_circle</span>Add Task
				</button>
			</div>
		</div>

		<!-- Kanban Columns -->
		<div class="flex-1 min-h-0">
			<div :class="`grid grid-cols-1 md:grid-cols-${metadata.statuses?.length || 3} gap-10 h-full`">
				<div
					v-for="status in metadata.statuses"
					:key="status"
					class="flex flex-col h-full space-y-6"
					@dragover.prevent="onDragOver($event)"
					@dragleave="onDragLeave($event)"
					@drop="onDrop($event, status)"
				>
					<div class="flex items-center gap-3 px-2">
						<div :class="`w-1.5 h-1.5 rounded-full ${getStatusBulletColor(status)}`"></div>
						<h3
							class="text-[12px] font-black tracking-[0.25em] text-gray-900 dark:text-white uppercase"
						>
							{{ status }}
						</h3>
						<span
							class="px-2 py-0.5 rounded text-[10px] font-black bg-gray-150 text-gray-700 dark:bg-gray-800 dark:text-gray-300"
						>
							{{ getTodosByStatus(status).length }}
						</span>
					</div>

					<div class="space-y-6">
						<div
							v-for="todo in getTodosByStatus(status)"
							:key="todo.id"
							:draggable="true"
							@dragstart="onDragStart($event, todo, 'todo')"
							@dragend="onDragEnd"
							class="premium-card !p-8 !overflow-visible cursor-grab active:cursor-grabbing border-gray-100 dark:border-gray-800 group transition-all"
							:class="[
								draggedItem?.id === todo.id ? 'opacity-50' : '',
								todo.status === 'Closed' || todo.status === 'Cancelled' ? 'bg-gray-50/50 dark:bg-gray-900/30' : ''
							]"
						>
							<div class="flex items-start justify-between mb-4 relative">
								<div class="flex items-center gap-2">
									<span
										:class="`text-[9px] font-black px-2 py-0.5 rounded uppercase tracking-[0.2em] ${getPriorityTagClass(todo.priority)}`"
									>
										{{ todo.priority }} Priority
									</span>
								</div>

								<!-- Action Controls (Status Badge & Menu dropdown) -->
								<div class="flex items-center gap-2">
									<!-- Status Badge (Always Visible) -->
									<span
										:class="`text-[9px] font-black px-2 py-0.5 rounded uppercase tracking-[0.2em] ${getStatusBadgeClass(todo.status)}`"
									>
										{{ todo.status }}
									</span>

									<!-- More Dropdown Button -->
									<div class="relative">
										<button
											@click.stop="toggleTodoMenu(todo.id)"
											class="px-2.5 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-1 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400 border border-gray-200 dark:border-gray-750 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-700 dark:hover:text-white"
										>
											<span>More</span>
											<span class="material-symbols-outlined text-xs">expand_more</span>
										</button>
										
										<!-- Dropdown Popover -->
										<div
											v-if="activeTodoMenuId === todo.id"
											class="absolute right-0 mt-1 w-36 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg shadow-lg py-1 z-30"
										>
											<button
												@click.stop="openEditTaskDialog(todo)"
												class="w-full text-left px-3 py-1.5 text-xs font-semibold text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center gap-2"
											>
												<span class="material-symbols-outlined text-sm">edit</span>Edit
											</button>
											<button
												@click.stop="handleDeleteTodo(todo.id)"
												class="w-full text-left px-3 py-1.5 text-xs font-semibold text-red-650 hover:bg-red-55 dark:hover:bg-red-950/20 flex items-center gap-2"
											>
												<span class="material-symbols-outlined text-sm">delete</span>Delete
											</button>

											<!-- Divider -->
											<div class="border-t border-gray-100 dark:border-gray-800 my-1"></div>

											<!-- Status Update Buttons -->
											<button
												v-for="st in metadata.statuses"
												:key="st"
												v-show="st !== todo.status"
												@click.stop="handleUpdateStatus(todo.id, st)"
												class="w-full text-left px-3 py-1.5 text-xs font-semibold text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center gap-2"
											>
												<span class="material-symbols-outlined text-sm">
													{{ st === 'Open' ? 'play_arrow' : st === 'Closed' ? 'check_circle' : 'cancel' }}
												</span>
												Mark {{ st }}
											</button>
										</div>
									</div>
								</div>
							</div>
							<h4
								class="font-black text-[15px] mb-6 text-gray-900 dark:text-white leading-snug tracking-tight transition-colors"
							>
								{{ todo.description }}
							</h4>
							<div
								class="flex items-center justify-between pt-6 border-t border-gray-50 dark:border-gray-800"
							>
								<div class="flex items-center gap-2">
									<div
										class="w-7 h-7 rounded-full border-2 border-white dark:border-gray-900 overflow-hidden bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-[10px] font-black uppercase text-gray-700 dark:text-gray-300"
										:title="`Allocated to: ${todo.allocated_to_name || todo.allocated_to}`"
									>
										{{ getInitials(todo.allocated_to_name || todo.allocated_to) }}
									</div>
									<span class="text-[10px] font-bold text-gray-500 dark:text-gray-400">
										{{ todo.allocated_to_name || todo.allocated_to }}
									</span>
								</div>
								<div
									v-if="todo.date"
									class="text-[10px] font-black tracking-widest flex items-center gap-1"
									:class="isTodoOverdueOrDueToday(todo) ? 'text-red-500' : 'text-gray-400 dark:text-gray-500'"
								>
									<span>DUE DATE:</span>
									{{ formatTodoDate(todo.date) }}
								</div>
							</div>
						</div>

						<!-- Drop Zone Placeholder -->
						<div
							v-if="getTodosByStatus(status).length === 0"
							class="h-44 border-2 border-dashed border-gray-100 dark:border-gray-850 rounded-4xl flex flex-col items-center justify-center text-center p-8 bg-gray-50/30 dark:bg-gray-900/10"
						>
							<span
								class="material-symbols-outlined text-gray-300 dark:text-gray-700 text-3xl mb-3 font-light"
								>task_alt</span
							>
							<p
								class="text-[10px] font-black text-gray-400 dark:text-gray-505 uppercase tracking-[0.2em] leading-relaxed"
							>
								Drop tasks here to update status
							</p>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Add/Edit Task Dialog -->
		<div v-if="showAddTaskDialog" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
			<div class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 shadow-xl w-full max-w-md mx-4">
				<div class="p-6">
					<div class="flex items-center justify-between mb-6">
						<h3 class="text-lg font-black text-gray-900 dark:text-white">
							{{ isEditing ? 'Edit Task' : 'Add Task' }}
						</h3>
						<button @click="showAddTaskDialog = false" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
							<span class="material-symbols-outlined">close</span>
						</button>
					</div>
					<div class="space-y-4 text-left">
						<!-- Assigned To Field -->
						<div>
							<label class="block text-xs font-black text-gray-500 dark:text-gray-400 uppercase tracking-widest mb-2">Assigned To</label>
							<div v-if="metadata.can_assign_to_others" class="relative">
								<select
									v-model="addTaskAssignedTo"
									class="appearance-none pr-8 pl-3 py-3 text-sm w-full cursor-pointer border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-1 focus:ring-primary"
								>
									<option value="">Select User</option>
									<option v-for="user in metadata.users" :key="user.name" :value="user.name">
										{{ user.full_name }} ({{ user.name }})
									</option>
								</select>
							</div>
							<div v-else class="py-3 px-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-100 dark:border-gray-700 text-sm font-bold text-gray-900 dark:text-gray-100">
								{{ metadata.current_user?.full_name || 'Loading...' }}
							</div>
						</div>

						<!-- Status Field (Only visible when editing) -->
						<div v-if="isEditing">
							<label class="block text-xs font-black text-gray-500 dark:text-gray-400 uppercase tracking-widest mb-2">Status</label>
							<select
								v-model="addTaskStatus"
								class="w-full px-4 py-3 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-1 focus:ring-primary"
							>
								<option v-for="status in metadata.statuses" :key="status" :value="status">
									{{ status }}
								</option>
							</select>
						</div>

						<!-- Priority Field -->
						<div>
							<label class="block text-xs font-black text-gray-500 dark:text-gray-400 uppercase tracking-widest mb-2">Priority</label>
							<select
								v-model="addTaskPriority"
								class="w-full px-4 py-3 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-1 focus:ring-primary"
							>
								<option v-for="prio in metadata.priorities" :key="prio" :value="prio">
									{{ prio }}
								</option>
							</select>
						</div>

						<!-- Allocated Date (Label of Today) -->
						<div>
							<label class="block text-xs font-black text-gray-500 dark:text-gray-400 uppercase tracking-widest mb-2">Allocated Date</label>
							<div class="py-3 px-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-100 dark:border-gray-700 text-sm font-bold text-gray-955 dark:text-gray-50">
								{{ formattedTodayDate }}
							</div>
						</div>

						<!-- Due Date -->
						<div>
							<label class="block text-xs font-black text-gray-500 dark:text-gray-400 uppercase tracking-widest mb-2">Due Date <span class="text-red-500">*</span></label>
							<input
								v-model="addTaskDueDate"
								type="date"
								class="w-full px-4 py-3 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-1 focus:ring-primary"
							/>
						</div>

						<!-- Task Description -->
						<div>
							<label class="block text-xs font-black text-gray-500 dark:text-gray-400 uppercase tracking-widest mb-2">Task Description <span class="text-red-500">*</span></label>
							<textarea
								v-model="addTaskDescription"
								placeholder="Enter task details..."
								rows="3"
								class="w-full px-4 py-3 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder:text-gray-300 dark:placeholder:text-gray-600 focus:outline-none focus:ring-1 focus:ring-primary resize-none"
							></textarea>
						</div>

						<!-- Validation Error message -->
						<div v-if="addTaskError" class="text-sm text-red-650 dark:text-red-400 font-semibold mt-2">
							{{ addTaskError }}
						</div>
					</div>

					<!-- Form Actions -->
					<div class="flex items-center gap-3 mt-6">
						<button
							@click="handleSaveTask"
							:disabled="tasksStore.loading"
							class="flex-1 px-5 py-3 rounded-lg text-[11px] font-black uppercase tracking-[0.2em] transition-all flex items-center justify-center gap-2 bg-emerald-950 text-white hover:bg-emerald-900 disabled:opacity-50 disabled:cursor-not-allowed"
						>
							<span class="material-symbols-outlined text-base">save</span>{{ isEditing ? 'Save Changes' : 'Add Task' }}
						</button>
						<button
							@click="showAddTaskDialog = false"
							class="flex-1 px-5 py-3 rounded-lg text-[11px] font-black uppercase tracking-[0.2em] transition-all flex items-center justify-center gap-2 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-2 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
						>
							<span class="material-symbols-outlined text-base">close</span>Dismiss
						</button>
					</div>
				</div>
			</div>
		</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { createResource } from "frappe-ui";
import { useTasksStore } from "@/stores/tasks";

const tasksStore = useTasksStore();

const draggedItem = ref(null);
const draggedType = ref(null);

// Administrative User Filter
const selectedUserFilter = ref("");

// Add/Edit Task dialog state
const showAddTaskDialog = ref(false);
const isEditing = ref(false);
const editingTodoId = ref(null);
const addTaskAssignedTo = ref("");
const addTaskPriority = ref("Medium");
const addTaskDueDate = ref("");
const addTaskDescription = ref("");
const addTaskStatus = ref("Open");
const addTaskError = ref("");

// Card actions menu state
const activeTodoMenuId = ref(null);

const metadata = ref({
	can_assign_to_others: false,
	priorities: ["Low", "Medium", "High"],
	statuses: ["Open", "Closed", "Cancelled"],
	users: [],
	current_user: null,
	today: new Date().toISOString().split("T")[0]
});

const metadataResource = createResource({
	url: "zevar_core.api.tasks.get_todo_creation_metadata",
	auto: true,
	onSuccess(data) {
		if (data) {
			metadata.value = data;
			if (data.current_user?.name && !addTaskAssignedTo.value) {
				addTaskAssignedTo.value = data.current_user.name;
			}
			if (data.priorities && data.priorities.length > 0 && !addTaskPriority.value) {
				addTaskPriority.value = data.priorities[1] || data.priorities[0];
			}
		}
	}
});

const formattedTodayDate = computed(() => {
	if (metadata.value.today) {
		const d = new Date(metadata.value.today + "T00:00:00");
		return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
	}
	const d = new Date();
	return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
});

function openAddTaskDialog() {
	isEditing.value = false;
	editingTodoId.value = null;
	addTaskDescription.value = "";
	addTaskDueDate.value = "";
	addTaskError.value = "";
	addTaskPriority.value = metadata.value.priorities?.[1] || "Medium";
	addTaskAssignedTo.value = metadata.value.current_user?.name || "";
	addTaskStatus.value = "Open";
	showAddTaskDialog.value = true;
}

function openEditTaskDialog(todo) {
	isEditing.value = true;
	editingTodoId.value = todo.id;
	addTaskDescription.value = todo.description || "";
	addTaskDueDate.value = todo.date || "";
	addTaskPriority.value = todo.priority || "Medium";
	addTaskAssignedTo.value = todo.allocated_to || "";
	addTaskStatus.value = todo.status || "Open";
	addTaskError.value = "";
	activeTodoMenuId.value = null; // Close menu on click edit
	showAddTaskDialog.value = true;
}

function toggleTodoMenu(todoId) {
	if (activeTodoMenuId.value === todoId) {
		activeTodoMenuId.value = null;
	} else {
		activeTodoMenuId.value = todoId;
	}
}

function closeTodoMenu() {
	activeTodoMenuId.value = null;
}

async function handleDeleteTodo(todoId) {
	activeTodoMenuId.value = null;
	if (confirm("Are you sure you want to delete this task?")) {
		try {
			await tasksStore.deleteTodoItem(todoId, selectedUserFilter.value);
		} catch (err) {
			console.error("Failed to delete todo:", err);
		}
	}
}

async function handleUpdateStatus(todoId, status) {
	activeTodoMenuId.value = null;
	try {
		await tasksStore.updateTodoStatus(todoId, status, selectedUserFilter.value);
	} catch (err) {
		console.error("Failed to update todo status:", err);
	}
}

async function handleSaveTask() {
	addTaskError.value = "";

	if (!addTaskDescription.value.trim()) {
		addTaskError.value = "Task Description is required.";
		return;
	}
	if (!addTaskDueDate.value) {
		addTaskError.value = "Due Date is required.";
		return;
	}

	const today = new Date();
	today.setHours(0, 0, 0, 0);
	const selectedDue = new Date(addTaskDueDate.value + "T00:00:00");
	selectedDue.setHours(0, 0, 0, 0);

	if (selectedDue < today) {
		addTaskError.value = "Due Date cannot be before the Allocated Date (Today).";
		return;
	}

	try {
		if (isEditing.value) {
			await tasksStore.updateTodo(
				editingTodoId.value,
				addTaskDescription.value.trim(),
				addTaskDueDate.value,
				addTaskPriority.value,
				addTaskAssignedTo.value || null,
				addTaskStatus.value,
				selectedUserFilter.value
			);
		} else {
			await tasksStore.createTodo(
				addTaskDescription.value.trim(),
				addTaskDueDate.value,
				addTaskPriority.value,
				addTaskAssignedTo.value || null,
				selectedUserFilter.value
			);
		}
		showAddTaskDialog.value = false;
	} catch (err) {
		addTaskError.value = err.message || "Failed to save task.";
	}
}

const priorityOrder = { High: 1, Medium: 2, Low: 3 };

function getTodosByStatus(status) {
	if (!tasksStore.todos) return [];
	return [...tasksStore.todos]
		.filter((t) => t.status === status)
		.sort((a, b) => (priorityOrder[a.priority] || 99) - (priorityOrder[b.priority] || 99));
}

function getStatusBulletColor(status) {
	if (status === "Open") return "bg-emerald-500";
	if (status === "Closed") return "bg-gray-400";
	if (status === "Cancelled") return "bg-red-500";
	return "bg-blue-500";
}

function getPriorityTagClass(priority) {
	if (priority === "High") return "bg-red-100 text-red-750 dark:bg-red-500/10 dark:text-red-400";
	if (priority === "Medium") return "bg-amber-100 text-amber-750 dark:bg-amber-500/10 dark:text-amber-400";
	return "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400";
}

function getStatusBadgeClass(status) {
	if (status === "Open") return "bg-emerald-100 text-emerald-850 dark:bg-emerald-500/10 dark:text-emerald-400";
	if (status === "Closed") return "bg-gray-150 text-gray-750 dark:bg-gray-800 dark:text-gray-300";
	if (status === "Cancelled") return "bg-red-100 text-red-750 dark:bg-red-500/10 dark:text-red-400";
	return "bg-blue-100 text-blue-800 dark:bg-blue-500/10 dark:text-blue-400";
}

function getInitials(name) {
	if (!name) return "?";
	return name.split(" ").map(n => n[0]).join("").toUpperCase().slice(0, 2);
}

function formatTodoDate(dateStr) {
	if (!dateStr) return "";
	const d = new Date(dateStr + "T00:00:00");
	return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function isTodoDueToday(todo) {
	if (!todo.date) return false;
	const today = new Date().toISOString().split("T")[0];
	return todo.date === today;
}

function isTodoOverdueOrDueToday(todo) {
	if (!todo.date) return false;
	const today = new Date();
	today.setHours(0, 0, 0, 0);
	const dueDate = new Date(todo.date + "T00:00:00");
	dueDate.setHours(0, 0, 0, 0);
	return dueDate <= today;
}

function onDragStart(event, item, type) {
	draggedItem.value = item;
	draggedType.value = type;
	event.dataTransfer.effectAllowed = "move";
}

function onDragEnd() {
	draggedItem.value = null;
	draggedType.value = null;
}

function onDragOver(event) {
	event.preventDefault();
}

function onDragLeave(event) {
	if (!event.currentTarget.contains(event.relatedTarget)) {
		// noop
	}
}

async function onDrop(event, targetZone) {
	event.preventDefault();
	const item = draggedItem.value;
	const sourceType = draggedType.value;
	onDragEnd();

	if (!item) return;

	if (sourceType === "todo") {
		if (item.status !== targetZone) {
			await tasksStore.updateTodoStatus(item.id, targetZone, selectedUserFilter.value);
		}
	}
}

watch(selectedUserFilter, (newFilter) => {
	tasksStore.fetchTodos(newFilter);
});

onMounted(() => {
	tasksStore.init(selectedUserFilter.value);
	window.addEventListener("click", closeTodoMenu);
});

onUnmounted(() => {
	window.removeEventListener("click", closeTodoMenu);
});
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
	display: none;
}
.no-scrollbar {
	-ms-overflow-style: none;
	scrollbar-width: none;
}
</style>
