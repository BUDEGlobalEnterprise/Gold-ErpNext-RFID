/**
 * Zevar Custom Desk - Vue 3 Application
 *
 * A modern, accessible desk page with grouped shortcuts,
 * quick stats, and activity feed.
 */

(function () {
	"use strict";

	const deskTemplate = `
<div class="desk-wrapper">
	<header class="desk-header" role="banner">
		<div class="header-content">
			<div class="logo-section">
				<img src="/assets/zevar_core/images/pos_logo.svg" alt="Zevar Logo" class="desk-logo">
				<div class="header-text">
					<h1 class="desk-title">Zevar Desk</h1>
					<p class="desk-subtitle">Jewelry Retail Management</p>
				</div>
			</div>
			<div class="header-actions">
				<button
					v-if="canManageShortcuts"
					class="btn-secondary"
					@click="openShortcutManager"
					aria-label="Manage shortcuts"
					title="Manage shortcuts">
					Manage Shortcuts
				</button>
				<button
					class="btn-refresh"
					@click="refresh"
					aria-label="Refresh dashboard"
					title="Refresh">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>
				</button>
			</div>
		</div>
	</header>

	<section
		v-for="(section, sectionIndex) in shortcutSections"
		:key="section.name"
		class="shortcut-section"
		:aria-labelledby="'shortcut-section-' + sectionIndex">
		<h2 :id="'shortcut-section-' + sectionIndex" class="section-title">
			<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
			{{ section.name }}
		</h2>
		<div class="shortcuts-grid" role="list">
			<button
				v-for="shortcut in section.items"
				:key="shortcut.name"
				class="shortcut-card"
				:style="{ '--accent-color': shortcut.color || '#2563eb' }"
				@click="navigate(shortcut)"
				@keydown.enter="navigate(shortcut)"
				@keydown.space.prevent="navigate(shortcut)"
				:aria-label="getAriaLabel(shortcut)"
				role="listitem"
				tabindex="0">
				<div class="shortcut-icon-wrapper" :style="{ backgroundColor: shortcut.color || '#2563eb' }">
					<svg v-if="getIconPath(shortcut.icon_name)" xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="getIconPath(shortcut.icon_name)"></svg>
					<img v-else-if="shortcut.custom_icon" :src="shortcut.custom_icon" :alt="shortcut.shortcut_name" class="shortcut-custom-icon">
					<span v-else class="shortcut-letter">{{ shortcut.shortcut_name.charAt(0) }}</span>
				</div>
				<span class="shortcut-label">{{ shortcut.shortcut_name }}</span>
				<span v-if="shortcut.keyboard_shortcut" class="shortcut-hint">
					{{ formatShortcut(shortcut.keyboard_shortcut) }}
				</span>
			</button>
		</div>
	</section>

	<section class="stats-section" aria-labelledby="stats-heading">
		<h2 id="stats-heading" class="section-title">
			<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
			Today's Overview
		</h2>
		<div class="stats-grid" role="list">
			<div class="stat-card" role="listitem">
				<div class="stat-icon" style="background-color: #10b981;">
					<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
				</div>
				<div class="stat-content">
					<span class="stat-value">\${{ formatNumber(quickStats.todays_sales) }}</span>
					<span class="stat-label">Today's Sales</span>
				</div>
			</div>
			<div class="stat-card" role="listitem">
				<div class="stat-icon" style="background-color: #f59e0b;">
					<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>
				</div>
				<div class="stat-content">
					<span class="stat-value">{{ quickStats.pending_repairs || 0 }}</span>
					<span class="stat-label">Pending Repairs</span>
				</div>
			</div>
			<div class="stat-card" role="listitem">
				<div class="stat-icon" style="background-color: #8b5cf6;">
					<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect><line x1="1" y1="10" x2="23" y2="10"></line></svg>
				</div>
				<div class="stat-content">
					<span class="stat-value">{{ quickStats.active_layaways || 0 }}</span>
					<span class="stat-label">Active Layaways</span>
				</div>
			</div>
			<div class="stat-card" role="listitem">
				<div class="stat-icon" style="background-color: #ec4899;">
					<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="17 1 21 5 17 9"></polyline><path d="M3 11V9a4 4 0 0 1 4-4h14"></path><polyline points="7 23 3 19 7 15"></polyline><path d="M21 13v2a4 4 0 0 1-4 4H3"></path></svg>
				</div>
				<div class="stat-content">
					<span class="stat-value">{{ quickStats.pending_trade_ins || 0 }}</span>
					<span class="stat-label">Pending Trade-Ins</span>
				</div>
			</div>
			<div class="stat-card" role="listitem">
				<div class="stat-icon" style="background-color: #06b6d4;">
					<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
				</div>
				<div class="stat-content">
					<span class="stat-value">{{ quickStats.todays_customers || 0 }}</span>
					<span class="stat-label">Customers Today</span>
				</div>
			</div>
		</div>
	</section>

	<section class="activity-section" aria-labelledby="activity-heading">
		<h2 id="activity-heading" class="section-title">
			<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
			Recent Activity
		</h2>
		<div class="activity-feed" role="feed" aria-live="polite">
			<div v-if="recentActivity.length === 0" class="no-activity">
				<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"></polyline><path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"></path></svg>
				<p>No recent activity</p>
			</div>
			<a
				v-else
				v-for="(activity, index) in recentActivity"
				:key="index"
				:href="activity.link"
				class="activity-item"
				role="article">
				<div class="activity-icon" :class="'activity-type-' + activity.type">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="getActivityIcon(activity.icon)"></svg>
				</div>
				<div class="activity-content">
					<p class="activity-message">{{ activity.message }}</p>
					<span class="activity-time">{{ formatTimeAgo(activity.time) }}</span>
				</div>
				<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="activity-arrow"><polyline points="9 18 15 12 9 6"></polyline></svg>
			</a>
		</div>
	</section>
</div>
`;

	const icons = {
		"shopping-cart":
			'<circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>',
		user: '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle>',
		"credit-card":
			'<rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect><line x1="1" y1="10" x2="23" y2="10"></line>',
		tools: '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>',
		repeat: '<polyline points="17 1 21 5 17 9"></polyline><path d="M3 11V9a4 4 0 0 1 4-4h14"></path><polyline points="7 23 3 19 7 15"></polyline><path d="M21 13v2a4 4 0 0 1-4 4H3"></path>',
		gift: '<polyline points="20 12 20 22 4 22 4 12"></polyline><rect x="2" y="7" width="20" height="5"></rect><line x1="12" y1="22" x2="12" y2="7"></line><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"></path><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"></path>',
		gem: '<polygon points="12 2 2 7 12 22 22 7 12 2"></polygon><polyline points="2 7 12 12 22 7"></polyline><line x1="12" y1="22" x2="12" y2="12"></line>',
		percentage:
			'<line x1="19" y1="5" x2="5" y2="19"></line><circle cx="6.5" cy="6.5" r="2.5"></circle><circle cx="17.5" cy="17.5" r="2.5"></circle>',
		"file-text":
			'<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline>',
		calendar:
			'<rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line>',
		settings:
			'<circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>',
		home: '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline>',
		store: '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><path d="M9 22V12h6v10"></path>',
		"dollar-sign":
			'<line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>',
		package:
			'<line x1="16.5" y1="9.4" x2="7.5" y2="4.21"></line><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line>',
		"clipboard-list":
			'<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect><line x1="12" y1="11" x2="12" y2="17"></line><line x1="9" y1="14" x2="15" y2="14"></line>',
		users: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path>',
		star: '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>',
		check: '<polyline points="20 6 9 17 4 12"></polyline>',
		"map-pin":
			'<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle>',
		activity: '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>',
		folder: '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>',
		image: '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline>',
		edit: '<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.12 2.12 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>',
		x: '<line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line>',
		plus: '<line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line>',
		download:
			'<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line>',
		upload: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line>',
		"alert-circle":
			'<circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line>',
		"arrow-right":
			'<line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline>',
		bookmark: '<path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>',
		"bar-chart-2":
			'<line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line>',
	};

	const { createApp, ref, computed, onMounted } = Vue;

	const app = createApp({
		template: deskTemplate,
		setup() {
			const shortcutSections = ref([]);
			const quickStats = ref({});
			const recentActivity = ref([]);
			const loading = ref(true);
			const error = ref(null);

			const shortcuts = computed(() =>
				shortcutSections.value.flatMap((section) => section.items || [])
			);

			const canManageShortcuts = computed(() => {
				return (
					frappe.user.has_role("System Manager") ||
					frappe.user.has_role("Desk Customization Manager")
				);
			});

			const getIconPath = (iconName) => icons[iconName] || null;
			const getActivityIcon = (iconName) => icons[iconName] || icons.activity;

			const fetchShortcuts = async () => {
				try {
					const response = await frappe.call({
						method: "zevar_core.api.shortcuts.get_shortcut_sections",
						args: { surface: "desk" },
						freeze: false,
					});
					shortcutSections.value = response.message || [];
				} catch (err) {
					console.error("Failed to fetch shortcut sections:", err);
					shortcutSections.value = [];
				}
			};

			const fetchStats = async () => {
				try {
					const response = await frappe.call({
						method: "zevar_core.api.shortcuts.get_quick_stats",
						freeze: false,
					});
					quickStats.value = response.message || {};
				} catch (err) {
					console.error("Failed to fetch stats:", err);
					quickStats.value = {};
				}
			};

			const fetchActivity = async () => {
				try {
					const response = await frappe.call({
						method: "zevar_core.api.shortcuts.get_recent_activity",
						args: { limit: 10 },
						freeze: false,
					});
					recentActivity.value = response.message || [];
				} catch (err) {
					console.error("Failed to fetch activity:", err);
					recentActivity.value = [];
				}
			};

			const navigate = (shortcut) => {
				const url = shortcut.route || shortcut.link_to;
				if (!url) return;
				if (shortcut.open_in_new_tab) {
					window.open(url, "_blank", "noopener");
				} else {
					window.location.href = url;
				}
			};

			const formatShortcut = (shortcut) => {
				if (!shortcut) return "";
				return shortcut
					.toUpperCase()
					.split("+")
					.map((part) => {
						if (part === "ALT") return "⌥";
						if (part === "CTRL") return "⌃";
						if (part === "SHIFT") return "⇧";
						return part;
					})
					.join(" + ");
			};

			const formatNumber = (num) => {
				if (!num) return "0";
				return parseFloat(num).toLocaleString("en-US", {
					minimumFractionDigits: 0,
					maximumFractionDigits: 0,
				});
			};

			const formatTimeAgo = (date) => (date ? frappe.datetime.comment_when(date) : "");

			const getAriaLabel = (shortcut) => {
				let label = shortcut.shortcut_name;
				if (shortcut.keyboard_shortcut) {
					label += ". Keyboard shortcut: " + shortcut.keyboard_shortcut;
				}
				if (shortcut.description) {
					label += ". " + shortcut.description;
				}
				return label;
			};

			const openShortcutManager = () => {
				window.location.href = "/app/zevar-desk-shortcut";
			};

			const refresh = async () => {
				loading.value = true;
				await Promise.all([fetchShortcuts(), fetchStats(), fetchActivity()]);
				loading.value = false;
			};

			const setupKeyboardShortcuts = () => {
				document.addEventListener("keydown", (e) => {
					if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") {
						return;
					}

					shortcuts.value.forEach((shortcut) => {
						if (!shortcut.keyboard_shortcut) return;
						const parts = shortcut.keyboard_shortcut.toLowerCase().split("+");
						const key = parts.pop();

						let match = true;
						if (parts.includes("alt") && !e.altKey) match = false;
						if (parts.includes("ctrl") && !e.ctrlKey) match = false;
						if (parts.includes("shift") && !e.shiftKey) match = false;
						if (e.key.toLowerCase() !== key) match = false;

						if (match) {
							e.preventDefault();
							navigate(shortcut);
						}
					});

					if (e.altKey && e.key.toLowerCase() === "h") {
						e.preventDefault();
						window.location.href = "/zevar-desk";
					}
				});
			};

			onMounted(async () => {
				try {
					await Promise.all([fetchShortcuts(), fetchStats(), fetchActivity()]);
				} catch (err) {
					error.value = err.message;
				} finally {
					loading.value = false;
					setupKeyboardShortcuts();
				}
			});

			return {
				shortcutSections,
				quickStats,
				recentActivity,
				loading,
				error,
				canManageShortcuts,
				navigate,
				formatShortcut,
				formatNumber,
				formatTimeAgo,
				getAriaLabel,
				getIconPath,
				getActivityIcon,
				openShortcutManager,
				refresh,
			};
		},
	});

	frappe.ready(() => {
		app.mount("#zevar-desk");
	});
})();
