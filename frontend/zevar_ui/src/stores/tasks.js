import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { ref, computed } from 'vue'

export const useTasksStore = defineStore('tasks', () => {
	const tasks = ref([])
	const taskStats = ref(null)
	const todos = ref([])
	const currentTask = ref(null)
	const recentActivities = ref([])

	const tasksResource = createResource({
		url: 'zevar_core.api.tasks.get_employee_tasks',
		onSuccess(data) {
			tasks.value = data.tasks || []
		},
	})

	const taskStatsResource = createResource({
		url: 'zevar_core.api.tasks.get_task_stats',
		onSuccess(data) {
			taskStats.value = data
		},
	})

	const todosResource = createResource({
		url: 'zevar_core.api.tasks.get_personal_todos',
		onSuccess(data) {
			todos.value = data || []
		},
	})

	const taskDetailResource = createResource({
		url: 'zevar_core.api.tasks.get_task_detail',
		onSuccess(data) {
			currentTask.value = data.task || null
		},
	})

	const createTodoResource = createResource({
		url: 'zevar_core.api.tasks.create_personal_todo',
	})

	const updateTodoResource = createResource({
		url: 'zevar_core.api.tasks.update_todo_status',
	})

	const deleteTodoResource = createResource({
		url: 'zevar_core.api.tasks.delete_todo',
	})

	const updateTaskStatusResource = createResource({
		url: 'zevar_core.api.tasks.update_task_status',
	})

	const activitiesResource = createResource({
		url: 'zevar_core.api.tasks.get_recent_activities',
		onSuccess(data) {
			recentActivities.value = data || []
		},
	})

	const todoCount = computed(() => todos.value.filter((t) => t.status === 'Open').length)
	const overdueCount = computed(() => taskStats.value?.overdue || 0)

	function loadTasks(status) {
		return tasksResource.submit({ status })
	}

	function loadTaskStats() {
		return taskStatsResource.submit()
	}

	function loadTodos(status = 'Open') {
		return todosResource.submit({ status })
	}

	function loadTaskDetail(task_id) {
		return taskDetailResource.submit({ task_id })
	}

	function createTodo(description, date, priority) {
		return createTodoResource.submit({ description, date, priority })
	}

	function updateTodo(todo_id, status) {
		return updateTodoResource.submit({ todo_id, status })
	}

	function deleteTodo(todo_id) {
		return deleteTodoResource.submit({ todo_id })
	}

	function updateTaskStatus(task_id, status) {
		return updateTaskStatusResource.submit({ task_id, status })
	}

	function loadActivities(limit = 20) {
		return activitiesResource.submit({ limit })
	}

	return {
		tasks,
		taskStats,
		todos,
		currentTask,
		recentActivities,
		todoCount,
		overdueCount,
		tasksResource,
		taskStatsResource,
		todosResource,
		taskDetailResource,
		createTodoResource,
		updateTodoResource,
		deleteTodoResource,
		updateTaskStatusResource,
		activitiesResource,
		loadTasks,
		loadTaskStats,
		loadTodos,
		loadTaskDetail,
		createTodo,
		updateTodo,
		deleteTodo,
		updateTaskStatus,
		loadActivities,
	}
})
