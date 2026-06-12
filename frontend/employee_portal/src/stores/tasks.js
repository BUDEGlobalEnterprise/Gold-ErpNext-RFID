import { defineStore } from "pinia";
import { createResource } from "frappe-ui";
import { ref, computed } from "vue";

export const useTasksStore = defineStore("tasks", () => {
	const tasks = ref([]);
	const todos = ref([]);
	const taskStats = ref({ total: 0, overdue: 0, by_status: {} });
	const gameplanInstalled = ref(false);
	const loading = ref(false);

	// Get employee tasks from Gameplan
	const tasksResource = createResource({
		url: "zevar_core.api.tasks.get_employee_tasks",
		auto: false,
		onSuccess(data) {
			tasks.value = data?.tasks || [];
			gameplanInstalled.value = data?.gameplan_installed || false;
		},
	});

	// Get task stats
	const taskStatsResource = createResource({
		url: "zevar_core.api.tasks.get_task_stats",
		auto: false,
		onSuccess(data) {
			if (data) {
				taskStats.value = {
					total: data.total || 0,
					overdue: data.overdue || 0,
					by_status: data.by_status || {},
				};
				gameplanInstalled.value = data.gameplan_installed || false;
			}
		},
	});

	// Get personal todos
	const todosResource = createResource({
		url: "zevar_core.api.tasks.get_personal_todos",
		auto: false,
		onSuccess(data) {
			todos.value = data || [];
		},
	});

	// Create todo
	const createTodoResource = createResource({
		url: "zevar_core.api.tasks.create_personal_todo",
		auto: false,
	});

	// Update todo status
	const updateTodoResource = createResource({
		url: "zevar_core.api.tasks.update_todo_status",
		auto: false,
	});

	// Delete todo
	const deleteTodoResource = createResource({
		url: "zevar_core.api.tasks.delete_todo",
		auto: false,
	});

	// Update todo details
	const updateTodoDetailResource = createResource({
		url: "zevar_core.api.tasks.update_personal_todo",
		auto: false,
	});

	// Update Gameplan task status
	const updateTaskStatusResource = createResource({
		url: "zevar_core.api.tasks.update_task_status",
		auto: false,
	});

	// Computed
	const pendingTasks = computed(() => {
		return tasks.value.filter((t) => t.status !== "Done" && t.status !== "Canceled");
	});

	const overdueTasks = computed(() => {
		return tasks.value.filter((t) => t.is_overdue);
	});

	const openTodos = computed(() => {
		return todos.value.filter((t) => t.status === "Open");
	});

	const completedTodos = computed(() => {
		return todos.value.filter((t) => t.status === "Closed");
	});

	// Actions
	async function fetchTasks() {
		await tasksResource.fetch();
	}

	async function fetchTaskStats() {
		await taskStatsResource.fetch();
	}

	async function fetchTodos(userFilter = null) {
		await todosResource.fetch({ user_filter: userFilter });
	}

	async function createTodo(description, date = null, priority = "Medium", allocated_to = null, userFilter = null) {
		loading.value = true;
		try {
			const result = await createTodoResource.fetch({
				description,
				date,
				priority,
				allocated_to,
			});
			await fetchTodos(userFilter);
			return result;
		} finally {
			loading.value = false;
		}
	}

	async function updateTodo(todoId, description, date = null, priority = "Medium", allocated_to = null, status = "Open", userFilter = null) {
		loading.value = true;
		try {
			const result = await updateTodoDetailResource.fetch({
				todo_id: todoId,
				description,
				date,
				priority,
				allocated_to,
				status,
			});
			await fetchTodos(userFilter);
			return result;
		} finally {
			loading.value = false;
		}
	}

	async function toggleTodo(todoId, currentStatus, userFilter = null) {
		const newStatus = currentStatus === "Closed" ? "Open" : "Closed";
		await updateTodoResource.fetch({ todo_id: todoId, status: newStatus });
		await fetchTodos(userFilter);
	}

	async function updateTodoStatus(todoId, status, userFilter = null) {
		await updateTodoResource.fetch({ todo_id: todoId, status: status });
		await fetchTodos(userFilter);
	}

	// Optimistic delete - removes from UI immediately
	async function deleteTodoItem(todoId, userFilter = null) {
		const previousTodos = [...todos.value];
		todos.value = todos.value.filter((t) => t.id !== todoId);

		try {
			await deleteTodoResource.fetch({ todo_id: todoId });
			await fetchTodos(userFilter);
		} catch (error) {
			todos.value = previousTodos;
			throw error;
		}
	}

	// Optimistic task status update for drag and drop
	async function updateTaskStatus(taskId, newStatus) {
		const previousTasks = [...tasks.value];
		const taskIndex = tasks.value.findIndex((t) => t.id === taskId);
		if (taskIndex !== -1) {
			tasks.value[taskIndex] = { ...tasks.value[taskIndex], status: newStatus };
		}

		try {
			await updateTaskStatusResource.fetch({ task_id: taskId, status: newStatus });
			// Refresh tasks from server to ensure sync
			await fetchTasks();
		} catch (error) {
			tasks.value = previousTasks;
			throw error;
		}
	}

	function init(userFilter = null) {
		fetchTasks();
		fetchTaskStats();
		fetchTodos(userFilter);
	}

	return {
		tasks,
		todos,
		taskStats,
		gameplanInstalled,
		loading,
		pendingTasks,
		overdueTasks,
		openTodos,
		completedTodos,
		fetchTasks,
		fetchTaskStats,
		fetchTodos,
		createTodo,
		updateTodo,
		toggleTodo,
		updateTodoStatus,
		deleteTodoItem,
		updateTaskStatus,
		init,
	};
});
