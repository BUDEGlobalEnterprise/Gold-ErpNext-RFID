import { createRouter, createWebHashHistory } from "vue-router";
import { useAuthStore } from "./stores/auth";

const router = createRouter({
	history: createWebHashHistory(),
	routes: [
		{
			path: "/login",
			name: "login",
			component: () => import("./views/Login.vue"),
			meta: { guest: true },
		},
		{
			path: "/",
			name: "dashboard",
			component: () => import("./views/DashboardView.vue"),
			meta: { requiresAuth: true },
		},
		{
			path: "/tasks",
			name: "tasks",
			component: () => import("./views/TasksView.vue"),
			meta: { requiresAuth: true },
		},
		{
			path: "/attendance",
			name: "attendance",
			component: () => import("./views/AttendanceView.vue"),
			meta: { requiresAuth: true },
		},
		{
			path: "/roster",
			name: "roster",
			component: () => import("./views/RosterView.vue"),
			meta: { requiresAuth: true },
		},
		{
			path: "/leave",
			name: "leave",
			component: () => import("./views/LeaveView.vue"),
			meta: { requiresAuth: true },
		},
		{
			path: "/payroll",
			name: "payroll",
			component: () => import("./views/PayrollView.vue"),
			meta: { requiresAuth: true },
		},
		{
			path: "/expense",
			name: "expense",
			component: () => import("./views/ExpenseView.vue"),
			meta: { requiresAuth: true },
		},
		{
			path: "/issues",
			name: "issues",
			component: () => import("./views/IssuesView.vue"),
			meta: { requiresAuth: true },
		},
		{
			path: "/team",
			name: "team",
			component: () => import("./views/TeamView.vue"),
			meta: { requiresAuth: true },
		},
		{
			path: "/reports",
			name: "reports",
			component: () => import("./views/ReportsView.vue"),
			meta: { requiresAuth: true },
		},
		{
			path: "/open-desk",
			name: "open-desk",
			component: () => import("./views/DashboardView.vue"), // Placeholder
			meta: { requiresAuth: true },
		},
		// Catch-all → dashboard
		{
			path: "/:pathMatch(.*)*",
			redirect: "/",
		},
	],
});

router.beforeEach(async (to, _from, next) => {
	const auth = useAuthStore();

	if (!auth.ready) {
		await auth.init();
	}

	if (to.meta.requiresAuth && !auth.isLoggedIn) {
		next({ name: "login" });
	} else if (to.name === "login" && auth.isLoggedIn) {
		next({ name: "dashboard" });
	} else {
		next();
	}
});

export default router;
