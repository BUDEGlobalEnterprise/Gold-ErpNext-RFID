<template>
	<div class="h-full flex flex-col gap-10 no-scrollbar overflow-y-auto pb-20">
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
			<div class="flex items-center gap-4">
				<button
					class="px-6 py-3 bg-white border border-gray-100 rounded-xl text-[10px] font-black uppercase tracking-widest text-gray-400 hover:text-gray-900 transition-all flex items-center gap-2 shadow-sm hover:shadow-md"
				>
					<span class="material-symbols-outlined text-lg">filter_list</span>
					Filters
				</button>
				<button
					class="px-6 py-3 bg-white border border-gray-100 rounded-xl text-[10px] font-black uppercase tracking-widest text-gray-400 hover:text-gray-900 transition-all flex items-center gap-2 shadow-sm hover:shadow-md"
				>
					<span class="material-symbols-outlined text-lg">sort</span>
					Sort
				</button>
			</div>
		</div>

		<!-- Quick Add Row -->
		<div class="shrink-0">
			<div
				class="premium-card !p-0 flex flex-col md:flex-row items-stretch border-gray-100 overflow-hidden shadow-sm"
			>
				<div class="flex-1 p-6 border-b md:border-b-0 md:border-r border-gray-50">
					<p class="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-2">
						Task Description
					</p>
					<input
						v-model="newTodoText"
						type="text"
						placeholder="Add a new task to your board..."
						class="w-full bg-gray-50 border border-gray-100 rounded-xl py-3 px-4 text-sm font-bold text-gray-900 placeholder:text-gray-300 outline-none focus:bg-white transition-all"
						@keyup.enter="addTodo"
					/>
				</div>
				<div class="w-full md:w-64 p-6 border-b md:border-b-0 md:border-r border-gray-50">
					<p class="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-2">
						Priority
					</p>
					<select
						v-model="newTodoPriority"
						class="w-full bg-gray-50 border border-gray-100 rounded-xl py-3 px-4 text-[11px] font-black uppercase tracking-widest text-gray-900 outline-none appearance-none cursor-pointer focus:bg-white transition-all"
					>
						<option value="Low">Low Priority</option>
						<option value="Medium">Medium Priority</option>
						<option value="High">High Priority</option>
					</select>
				</div>
				<div class="p-6 flex items-center justify-center bg-gray-50/30">
					<button
						@click="addTodo"
						:disabled="!newTodoText.trim() || tasksStore.loading"
						class="h-full px-10 py-4 bg-primary text-white rounded-xl text-[11px] font-black uppercase tracking-[0.2em] shadow-glow-emerald hover:bg-black transition-all flex items-center gap-3 active:scale-[0.98] disabled:opacity-50"
					>
						<span class="material-symbols-outlined text-lg">add</span>
						Add Task
					</button>
				</div>
			</div>
		</div>

		<!-- Kanban Columns -->
		<div class="flex-1 min-h-0">
			<div class="grid grid-cols-1 md:grid-cols-3 gap-10 h-full items-start">
				<!-- ASSIGNED Column -->
				<div
					class="flex flex-col h-full space-y-6"
					@dragover.prevent="onDragOver($event, 'assigned')"
					@dragleave="onDragLeave($event)"
					@drop="onDrop($event, 'assigned')"
				>
					<div class="flex items-center gap-3 px-2">
						<div class="w-1.5 h-1.5 rounded-full bg-gray-400"></div>
						<h3
							class="text-[12px] font-black tracking-[0.25em] text-gray-900 uppercase"
						>
							Assigned
						</h3>
						<span
							class="bg-gray-100 text-gray-500 px-2 py-0.5 rounded text-[10px] font-black"
							>{{ assignedTasks.length }}</span
						>
						<button class="ml-auto text-gray-300 hover:text-gray-600">
							<span class="material-symbols-outlined">more_horiz</span>
						</button>
					</div>

					<div class="space-y-6">
						<div
							v-for="task in assignedTasks"
							:key="task.id"
							:draggable="true"
							@dragstart="onDragStart($event, task, 'task')"
							@dragend="onDragEnd"
							class="premium-card !p-8 hover:shadow-lg cursor-grab active:cursor-grabbing border-gray-100 group transition-all"
							:class="{ 'opacity-50': draggedItem?.id === task.id }"
						>
							<div class="flex items-start justify-between mb-4">
								<span
									class="text-[9px] font-black bg-gray-950 text-white px-2 py-0.5 rounded uppercase tracking-[0.2em]"
									>{{ task.sku || "SKU-9021" }}</span
								>
								<span
									class="text-[9px] font-black text-red-500 flex items-center gap-1"
									v-if="isDueToday(task)"
								>
									<span class="material-symbols-outlined text-[12px]"
										>schedule</span
									>
									TODAY
								</span>
							</div>
							<h4
								class="font-black text-[15px] mb-6 text-gray-900 leading-snug tracking-tight group-hover:text-primary transition-colors"
							>
								{{ task.title }}
							</h4>
							<div
								class="flex items-center justify-between pt-6 border-t border-gray-50"
							>
								<div class="flex items-center -space-x-2">
									<div
										v-for="i in task.assignees || 2"
										:key="i"
										class="w-7 h-7 rounded-full border-2 border-white overflow-hidden bg-gray-100"
									>
										<img
											:src="`https://i.pravatar.cc/50?u=${task.id}${i}`"
											class="w-full h-full object-cover"
										/>
									</div>
								</div>
								<div class="flex items-center gap-1.5 text-gray-400">
									<span class="material-symbols-outlined text-[18px]"
										>chat_bubble_outline</span
									>
									<span class="text-[10px] font-black tracking-widest">{{
										task.comments || 3
									}}</span>
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- IN PROGRESS Column -->
				<div
					class="flex flex-col h-full space-y-6"
					@dragover.prevent="onDragOver($event, 'inProgress')"
					@dragleave="onDragLeave($event)"
					@drop="onDrop($event, 'inProgress')"
				>
					<div class="flex items-center gap-3 px-2">
						<div class="w-1.5 h-1.5 rounded-full bg-amber-500"></div>
						<h3
							class="text-[12px] font-black tracking-[0.25em] text-gray-900 uppercase"
						>
							In Progress
						</h3>
						<span
							class="bg-amber-100 text-amber-900 px-2 py-0.5 rounded text-[10px] font-black"
							>{{ inProgressTasks.length }}</span
						>
						<button class="ml-auto text-gray-300 hover:text-gray-600">
							<span class="material-symbols-outlined">more_horiz</span>
						</button>
					</div>

					<div class="space-y-6">
						<div
							v-for="task in inProgressTasks"
							:key="task.id"
							:draggable="true"
							@dragstart="onDragStart($event, task, 'task')"
							@dragend="onDragEnd"
							class="premium-card !p-0 hover:shadow-lg cursor-grab border-gray-100 group transition-all overflow-hidden"
							:class="{ 'opacity-50': draggedItem?.id === task.id }"
						>
							<!-- Card Image -->
							<div class="h-32 bg-gray-900 relative overflow-hidden">
								<img
									:src="
										task.image ||
										'https://images.unsplash.com/photo-1573408301185-3cbb9820f3e6?auto=format&fit=crop&q=80&w=400'
									"
									class="w-full h-full object-cover opacity-60"
								/>
								<div class="absolute top-4 left-4">
									<span
										class="text-[9px] font-black bg-emerald-400 text-black px-2 py-0.5 rounded uppercase tracking-widest"
										>{{ task.tag || "Production" }}</span
									>
								</div>
							</div>

							<div class="p-8">
								<h4
									class="font-black text-[15px] mb-6 text-gray-900 leading-snug tracking-tight"
								>
									{{ task.title }}
								</h4>

								<!-- Progress Bar -->
								<div class="space-y-2 mb-6">
									<div
										class="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden"
									>
										<div
											class="h-full bg-emerald-600 rounded-full transition-all"
											:style="{ width: `${task.progress || 65}%` }"
										></div>
									</div>
									<div
										class="flex justify-between text-[9px] font-black uppercase tracking-widest text-gray-400"
									>
										<span>{{ task.progress || 65 }}%</span>
									</div>
								</div>

								<div
									class="flex items-center justify-between pt-6 border-t border-gray-50"
								>
									<div class="flex items-center -space-x-2">
										<div
											class="w-6 h-6 rounded-full border-2 border-white overflow-hidden bg-gray-100"
										>
											<img
												:src="`https://i.pravatar.cc/50?u=active${task.id}`"
												class="w-full h-full object-cover"
											/>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- MY TASKS Column -->
				<div
					class="flex flex-col h-full space-y-6"
					@dragover.prevent="onDragOver($event, 'myTasks')"
					@dragleave="onDragLeave($event)"
					@drop="onDrop($event, 'myTasks')"
				>
					<div class="flex items-center gap-3 px-2">
						<div class="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
						<h3
							class="text-[12px] font-black tracking-[0.25em] text-gray-900 uppercase"
						>
							My Tasks
						</h3>
						<span
							class="bg-emerald-100 text-emerald-900 px-2 py-0.5 rounded text-[10px] font-black"
							>{{ sortedOpenTodos.length }}</span
						>
						<button class="ml-auto text-gray-300 hover:text-gray-600">
							<span class="material-symbols-outlined">more_horiz</span>
						</button>
					</div>

					<div class="space-y-6">
						<div
							v-for="todo in sortedOpenTodos"
							:key="todo.id"
							:draggable="true"
							@dragstart="onDragStart($event, todo, 'todo')"
							@dragend="onDragEnd"
							class="premium-card !p-8 hover:shadow-lg cursor-grab border-gray-100 group transition-all"
							:class="{ 'opacity-50': draggedItem?.id === todo.id }"
						>
							<div class="flex items-start justify-between mb-4">
								<div class="flex items-center gap-2">
									<span
										class="material-symbols-outlined text-emerald-500 text-[14px]"
										>check_circle</span
									>
									<span
										class="text-[9px] font-black text-emerald-600 uppercase tracking-widest"
										>Finalized</span
									>
								</div>
							</div>
							<h4
								class="font-black text-[15px] mb-8 text-gray-900 leading-snug tracking-tight line-through text-gray-400"
							>
								{{ todo.description }}
							</h4>
							<div class="flex items-center gap-2 pt-6 border-t border-gray-50">
								<span
									class="text-[10px] font-black text-gray-400 uppercase tracking-widest flex-1"
									>Completed yesterday</span
								>
								<span
									class="material-symbols-outlined text-emerald-500 text-[18px]"
									>verified</span
								>
							</div>
						</div>

						<!-- Drop Zone Placeholder -->
						<div
							class="h-44 border-2 border-dashed border-gray-100 rounded-4xl flex flex-col items-center justify-center text-center p-8 bg-gray-50/30"
						>
							<span
								class="material-symbols-outlined text-gray-300 text-3xl mb-3 font-light"
								>task_alt</span
							>
							<p
								class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] leading-relaxed"
							>
								Drop tasks here to complete
							</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useTasksStore } from "@/stores/tasks";

const tasksStore = useTasksStore();
const newTodoText = ref("");
const newTodoPriority = ref("Medium");

const draggedItem = ref(null);
const draggedType = ref(null);

const assignedTasks = computed(() => {
	return tasksStore.tasks.filter(
		(t) => t.status === "Backlog" || t.status === "Todo" || t.status === "Open"
	);
});

const inProgressTasks = computed(() => {
	return tasksStore.tasks.filter((t) => t.status === "In Progress");
});

const priorityOrder = { High: 1, Medium: 2, Low: 3 };

const sortedOpenTodos = computed(() => {
	return [...tasksStore.openTodos].sort((a, b) => {
		return (priorityOrder[a.priority] || 99) - (priorityOrder[b.priority] || 99);
	});
});

function isDueToday(task) {
	if (!task.due_date) return false;
	const today = new Date();
	const due = new Date(task.due_date);
	return due.toDateString() === today.toDateString();
}

async function addTodo() {
	if (!newTodoText.value.trim()) return;
	await tasksStore.createTodo(newTodoText.value.trim(), null, newTodoPriority.value);
	newTodoText.value = "";
	newTodoPriority.value = "Medium";
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

	if (sourceType === "task") {
		let newStatus = null;
		if (targetZone === "assigned") newStatus = "Todo";
		else if (targetZone === "inProgress") newStatus = "In Progress";
		else if (targetZone === "myTasks") newStatus = "Closed";

		if (newStatus && item.status !== newStatus) {
			await tasksStore.updateTaskStatus(item.id, newStatus);
		}
	}
}

onMounted(() => {
	tasksStore.init();
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
