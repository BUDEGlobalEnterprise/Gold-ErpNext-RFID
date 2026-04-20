<template>
	<div class="dashboard-wrapper">
		<!-- Header -->
		<header class="dashboard-header">
			<div class="header-left">
				<div class="logo-block">
					<div class="logo-icon" style="font-weight: 900; font-size: 24px;">
						Z
					</div>
					<div>
						<h1 class="logo-title">Zevar Fine Jewelers</h1>
						<p class="logo-subtitle">Point of Sale Management</p>
					</div>
				</div>
			</div>
			<div class="header-right">
				<div class="clock-block">
					<div class="clock-time">{{ currentTime }}</div>
					<div class="clock-date">{{ currentDate }}</div>
				</div>
				<button @click="handleLogout" class="logout-btn">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4">
						<path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"></path>
						<polyline points="16,17 21,12 16,7"></polyline>
						<line x1="21" y1="12" x2="9" y2="12"></line>
					</svg>
					Logout
				</button>
			</div>
		</header>

		<div class="dashboard-container" style="padding-top: 0;">
			<div v-if="session.user" class="welcome-text" style="width: 100%; margin-bottom: 1.25rem;">
				Welcome back, <strong>{{ session.user?.full_name?.split(' ')[0] || 'User' }}</strong>
			</div>
			
			<div class="dashboard-layout">
				<!-- Main Content -->
				<main class="dashboard-main">
					<!-- Hero: POS Tile -->
			<router-link to="/terminal" class="tile-hero" id="tile-pos">
				<div class="tile-hero-icon" style="background: #F97316">
					<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-8 h-8">
						<path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"></path>
						<line x1="3" y1="6" x2="21" y2="6"></line>
						<path d="M16 10a4 4 0 01-8 0"></path>
					</svg>
				</div>
				<div>
					<h2 class="tile-hero-title">POS</h2>
					<p class="tile-hero-sub">Point of Sale Terminal</p>
				</div>
			</router-link>

			<!-- Section: Core Operations -->
			<div class="admin-section">
				<h4 class="section-label">Core Operations</h4>
				<div class="tile-row-4">
					<!-- Sales -->
					<router-link to="/transactions" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #3B82F6">
							<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"></path><polyline points="14,2 14,8 20,8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
						</div>
						<h3 class="tile-title-sm">Sales</h3>
					</router-link>
					<!-- Quotes -->
					<router-link to="#" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #0EA5E9">
							<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"></path><polyline points="14,2 14,8 20,8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
						</div>
						<h3 class="tile-title-sm">Quotes</h3>
					</router-link>
					<!-- Cash Drawer -->
					<router-link to="/layaway" class="tile-secondary" v-if="session.hasAnyRole(['Sales User','Store Manager','System Manager','Administrator', 'Employee', 'Employee Self Service'])">
						<div class="tile-icon-sm" style="background: #F59E0B">
							<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"></path></svg>
						</div>
						<h3 class="tile-title-sm">Cash Drawer</h3>
					</router-link>
					<!-- Repairs -->
					<router-link to="/repairs" class="tile-secondary" v-if="session.hasAnyRole(['Sales User','Technician','Store Manager','System Manager','Administrator', 'Employee', 'Employee Self Service'])">
						<div class="tile-icon-sm" style="background: #6366F1">
							<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"></path></svg>
						</div>
						<h3 class="tile-title-sm">Repairs</h3>
					</router-link>
					<!-- Contacts -->
					<router-link to="/customers" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #10B981">
							<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 00-3-3.87"></path><path d="M16 3.13a4 4 0 010 7.75"></path></svg>
						</div>
						<h3 class="tile-title-sm">Contacts</h3>
					</router-link>
					<!-- Products -->
					<router-link to="/catalogues" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #8B5CF6">
							<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>
						</div>
						<h3 class="tile-title-sm">Products</h3>
					</router-link>
					<!-- Tasks -->
					<a href="/employee-portal/tasks" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #F43F5E">
							<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 11 12 14 22 4"></polyline><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"></path></svg>
						</div>
						<h3 class="tile-title-sm">Tasks</h3>
					</a>
				</div>
			</div>

			<!-- Section: Inventory Management -->
			<div class="admin-section" v-if="session.hasAnyRole(['Store Manager', 'System Manager', 'Administrator'])">
				<h4 class="section-label">Inventory Management</h4>
				<div class="tile-row-4">
					<router-link to="#" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #64748B"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"></path></svg></div>
						<h3 class="tile-title-sm">Vendor Orders</h3>
					</router-link>
					<router-link to="#" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #64748B"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"></path></svg></div>
						<h3 class="tile-title-sm">Incoming Memos</h3>
					</router-link>
					<router-link to="/inventory" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #64748B"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"></path><polyline points="3.27,6.96 12,12.01 20.73,6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg></div>
						<h3 class="tile-title-sm">Receiving</h3>
					</router-link>
					<router-link to="#" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #64748B"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"></path></svg></div>
						<h3 class="tile-title-sm">Custom Jobs</h3>
					</router-link>
					<router-link to="#" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #64748B"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg></div>
						<h3 class="tile-title-sm">Metals</h3>
					</router-link>
					<router-link to="#" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #64748B"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon></svg></div>
						<h3 class="tile-title-sm">Diamonds & Gems</h3>
					</router-link>
					<router-link to="#" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #64748B"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg></div>
						<h3 class="tile-title-sm">Physical Inventory</h3>
					</router-link>
					<router-link to="#" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #64748B"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"></path></svg></div>
						<h3 class="tile-title-sm">Vaults & Safes</h3>
					</router-link>
					<router-link to="#" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #64748B"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg></div>
						<h3 class="tile-title-sm">Categories</h3>
					</router-link>
					<router-link to="#" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #64748B"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg></div>
						<h3 class="tile-title-sm">Brands</h3>
					</router-link>
					<router-link to="#" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #64748B"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg></div>
						<h3 class="tile-title-sm">Collections</h3>
					</router-link>
					<router-link to="#" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #64748B"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"></path></svg></div>
						<h3 class="tile-title-sm">Catalogs</h3>
					</router-link>
				</div>
			</div>

			<!-- Section: Accounting & Financials -->
			<div class="admin-section" v-if="session.hasAnyRole(['Store Manager', 'System Manager', 'Administrator', 'Accounts Manager'])">
				<h4 class="section-label">Accounting & Financials</h4>
				<div class="tile-row-4">
					<router-link to="#" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #14B8A6"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"></path></svg></div>
						<h3 class="tile-title-sm">Transactions</h3>
					</router-link>
					<router-link to="#" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #14B8A6"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z"></path></svg></div>
						<h3 class="tile-title-sm">End of Day Close</h3>
					</router-link>
					<router-link to="/reports" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #EC4899"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg></div>
						<h3 class="tile-title-sm">Reports</h3>
					</router-link>
					<router-link to="#" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #14B8A6"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg></div>
						<h3 class="tile-title-sm">Registers</h3>
					</router-link>
					<router-link to="#" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #14B8A6"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg></div>
						<h3 class="tile-title-sm">Pending Invoices</h3>
					</router-link>
					<router-link to="#" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #14B8A6"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg></div>
						<h3 class="tile-title-sm">Vendor Bills</h3>
					</router-link>
					<router-link to="#" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #14B8A6"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg></div>
						<h3 class="tile-title-sm">Customer Invoices</h3>
					</router-link>
					<router-link to="#" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #14B8A6"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg></div>
						<h3 class="tile-title-sm">Vendor Credits</h3>
					</router-link>
					<router-link to="#" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #14B8A6"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg></div>
						<h3 class="tile-title-sm">Customer Credits</h3>
					</router-link>
					<router-link to="#" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #14B8A6"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg></div>
						<h3 class="tile-title-sm">Accounting Export</h3>
					</router-link>
				</div>
			</div>

			<!-- Admin Section: Settings & Portal -->
			<div v-if="session.isAdmin" class="admin-section">
				<h4 class="section-label">System Administration</h4>
				<div class="tile-row-4">
					<a href="/employee-portal" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #0EA5E9">
							<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
						</div>
						<h3 class="tile-title-sm">Employee Portal</h3>
					</a>
					<router-link to="/support" class="tile-secondary">
						<div class="tile-icon-sm" style="background: #6B7280">
							<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"></path></svg>
						</div>
						<h3 class="tile-title-sm">Settings</h3>
					</router-link>
				</div>
			</div>

				</main>

				<!-- Sidebar -->
				<aside class="dashboard-sidebar">
					<!-- Quick Actions -->
					<div class="sidebar-section" v-if="session.hasAnyRole(['Store Manager', 'System Manager', 'Administrator', 'Inventory Manager'])">
						<h4 class="sidebar-label">Quick Actions</h4>
						<router-link to="/inventory/add" class="quick-action-btn">
							<div class="quick-action-icon">
								<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
							</div>
							<div class="quick-action-text">
								<h5>Add to Inventory</h5>
								<p>Item with Vendor & SKU</p>
							</div>
						</router-link>
					</div>

					<!-- Market Prices -->
					<div class="sidebar-section market-prices" v-if="sortedRates.length > 0">
						<h4 class="sidebar-label" style="display: flex; align-items: center; gap: 0.5rem;">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><polyline points="22,7 13.5,15.5 8.5,10.5 2,17"></polyline><polyline points="16,7 22,7 22,13"></polyline></svg>
							Market Prices
						</h4>
						<div class="market-grid">
							<div v-for="[key, rate, change] in sortedRates" :key="key" class="market-card">
								<div class="market-name">{{ formatMetalName(key) }}</div>
								<div style="display: flex; justify-content: space-between; align-items: baseline;">
									<div class="market-price">${{ rate }}</div>
									<div class="market-change" :class="change >= 0 ? 'up' : 'down'">
										<span>{{ change >= 0 ? '+' : '' }}{{ change.toFixed(2) }}</span>
										<span class="market-pct">{{ change >= 0 ? '▲' : '▼' }} {{ Math.abs(change / parseFloat(rate) * 100).toFixed(2) }}%</span>
									</div>
								</div>
							</div>
						</div>
					</div>
				</aside>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useSessionStore } from '@/stores/session'
import { useGoldStore } from '@/stores/gold.js'

const session = useSessionStore()
const goldStore = useGoldStore()

// Clock
const currentTime = ref('')
const currentDate = ref('')
let clockInterval = null

function updateClock() {
	const now = new Date()
	currentTime.value = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
	currentDate.value = now.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
}

const TROY_OZ_GRAMS = 31.1035

const sortedRates = computed(() => {
	if (!goldStore.rates) return []
	const priority = ['Yellow Gold-24K', 'Silver-925 Sterling', 'Platinum-950', 'Diamond-Natural']
	return Object.entries(goldStore.rates)
		.slice(0, 4)
		.map(([key, ratePerGram]) => {
			const price = (ratePerGram * TROY_OZ_GRAMS).toFixed(2)
			const change = (Math.random() - 0.4) * 20 // Simulated change
			return [key, price, change]
		})
		.sort((a, b) => {
			const iA = priority.indexOf(a[0])
			const iB = priority.indexOf(b[0])
			if (iA !== -1 && iB !== -1) return iA - iB
			if (iA !== -1) return -1
			if (iB !== -1) return 1
			return 0
		})
})

function formatMetalName(key) {
	const parts = key.split('-')
	return parts[0]
}

function handleLogout() {
	session.logoutResource.submit()
}

onMounted(() => {
	updateClock()
	clockInterval = setInterval(updateClock, 1000)
	goldStore.startPolling()
})

onUnmounted(() => {
	if (clockInterval) clearInterval(clockInterval)
})
</script>

<style scoped>
.dashboard-wrapper {
	min-height: 100vh;
	background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 30%, #FED7AA 70%, #FDBA74 100%);
	font-family: 'Inter', -apple-system, sans-serif;
	display: flex;
	flex-direction: column;
}

/* Header */
.dashboard-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 1.25rem 2rem;
	flex-shrink: 0;
}

.header-left { display: flex; align-items: center; }
.header-right { display: flex; align-items: center; gap: 1.5rem; }

.logo-block { display: flex; align-items: center; gap: 0.75rem; }
.logo-icon {
	width: 48px; height: 48px;
	background: #F97316;
	border-radius: 14px;
	display: flex; align-items: center; justify-content: center;
	color: white;
	box-shadow: 0 4px 14px rgba(249, 115, 22, 0.35);
}
.logo-icon svg { width: 26px; height: 26px; }
.logo-title { font-size: 1.35rem; font-weight: 800; color: #1F2937; line-height: 1.2; }
.logo-subtitle { font-size: 0.75rem; color: #9CA3AF; font-weight: 500; }

.clock-block { text-align: right; }
.clock-time { font-size: 1.25rem; font-weight: 700; color: #1F2937; font-variant-numeric: tabular-nums; }
.clock-date { font-size: 0.7rem; color: #9CA3AF; font-weight: 500; }

.logout-btn {
	display: flex; align-items: center; gap: 0.5rem;
	padding: 0.6rem 1.25rem;
	border: 1.5px solid #E5E7EB;
	border-radius: 12px;
	background: white;
	color: #374151;
	font-size: 0.8rem;
	font-weight: 600;
	cursor: pointer;
	transition: all 0.2s;
}
.logout-btn:hover { border-color: #F97316; color: #F97316; box-shadow: 0 2px 8px rgba(249,115,22,0.15); }
.logout-btn svg { width: 16px; height: 16px; }

/* Layout Container */
.dashboard-container {
	max-width: 1200px;
	width: 100%;
	margin: 0 auto;
	padding: 0 2rem 2rem;
}
.dashboard-layout {
	display: flex;
	gap: 2rem;
	align-items: flex-start;
}

/* Main */
.dashboard-main {
	flex: 1;
	min-width: 0;
}

.welcome-text {
	font-size: 0.9rem;
	color: #6B7280;
	margin-bottom: 1.25rem;
}
.welcome-text strong { color: #1F2937; }

/* Tiles */
.tile-hero {
	display: flex;
	align-items: center;
	gap: 1.25rem;
	background: white;
	border-radius: 20px;
	padding: 2rem 2.5rem;
	margin-bottom: 1rem;
	box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.04);
	text-decoration: none;
	transition: all 0.25s cubic-bezier(.4,0,.2,1);
	border: 1.5px solid transparent;
}
.tile-hero:hover {
	transform: translateY(-2px);
	box-shadow: 0 8px 30px rgba(249,115,22,0.12);
	border-color: #FDBA74;
}
.tile-hero-icon {
	width: 64px; height: 64px;
	border-radius: 18px;
	display: flex; align-items: center; justify-content: center;
	flex-shrink: 0;
}
.tile-hero-icon svg { width: 32px; height: 32px; }
.tile-hero-title { font-size: 1.75rem; font-weight: 800; color: #1F2937; }
.tile-hero-sub { font-size: 0.85rem; color: #9CA3AF; font-weight: 500; }

.tile-row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.tile-row-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1rem; }
.tile-row-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1rem; }

.tile-primary {
	display: flex;
	align-items: center;
	gap: 1rem;
	background: white;
	border-radius: 18px;
	padding: 1.5rem 1.75rem;
	text-decoration: none;
	box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.04);
	transition: all 0.25s cubic-bezier(.4,0,.2,1);
	border: 1.5px solid transparent;
}
.tile-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.08); border-color: #E5E7EB; }

.tile-icon {
	width: 48px; height: 48px;
	border-radius: 14px;
	display: flex; align-items: center; justify-content: center;
	flex-shrink: 0;
}
.tile-icon svg { width: 24px; height: 24px; }
.tile-title { font-size: 1.1rem; font-weight: 700; color: #1F2937; }
.tile-sub { font-size: 0.75rem; color: #9CA3AF; font-weight: 500; }

.tile-secondary {
	display: flex;
	flex-direction: column;
	align-items: center;
	text-align: center;
	gap: 0.5rem;
	background: white;
	border-radius: 18px;
	padding: 1.5rem 1rem;
	text-decoration: none;
	box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.04);
	transition: all 0.25s cubic-bezier(.4,0,.2,1);
	border: 1.5px solid transparent;
}
.tile-secondary:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.08); border-color: #E5E7EB; }

.tile-icon-sm {
	width: 40px; height: 40px;
	border-radius: 12px;
	display: flex; align-items: center; justify-content: center;
}
.tile-icon-sm svg { width: 20px; height: 20px; }
.tile-title-sm { font-size: 0.85rem; font-weight: 700; color: #1F2937; }
.tile-sub-sm { font-size: 0.65rem; color: #9CA3AF; font-weight: 500; }

/* Admin Section */
.admin-section { margin-top: 0.5rem; }
.section-label {
	font-size: 0.7rem;
	font-weight: 700;
	text-transform: uppercase;
	letter-spacing: 0.08em;
	color: #9CA3AF;
	margin-bottom: 0.75rem;
	padding-left: 0.25rem;
}

/* Sidebar */
.dashboard-sidebar {
	width: 320px;
	flex-shrink: 0;
	display: flex;
	flex-direction: column;
	gap: 1.5rem;
}
.sidebar-section {
	background: white;
	border-radius: 18px;
	padding: 1.25rem;
	box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.sidebar-label {
	font-size: 0.7rem;
	font-weight: 700;
	text-transform: uppercase;
	letter-spacing: 0.08em;
	color: #9CA3AF;
	margin: 0 0 0.75rem 0;
}

/* Quick Actions */
.quick-action-btn {
	display: flex;
	align-items: center;
	gap: 1rem;
	padding: 1rem;
	border-radius: 12px;
	background: #F9FAFB;
	border: 1.5px solid transparent;
	text-decoration: none;
	transition: all 0.2s;
}
.quick-action-btn:hover {
	background: #FFF7ED;
	border-color: #FDBA74;
	transform: translateY(-1px);
}
.quick-action-icon {
	width: 40px; height: 40px;
	border-radius: 10px;
	background: #F97316;
	color: white;
	display: flex; align-items: center; justify-content: center;
	flex-shrink: 0;
}
.quick-action-icon svg { width: 20px; height: 20px; }
.quick-action-text h5 { font-size: 0.9rem; font-weight: 700; color: #1F2937; margin: 0 0 0.15rem 0; }
.quick-action-text p { font-size: 0.7rem; color: #6B7280; margin: 0; }

/* Market Prices */
.market-prices {
	margin-top: 0;
}
.market-grid {
	display: grid;
	grid-template-columns: 1fr;
	gap: 0;
}
.market-card {
	padding: 0.85rem 0;
	border-bottom: 1px solid #F3F4F6;
	background: transparent;
}
.market-card:last-child { border-bottom: none; padding-bottom: 0; }
.market-card:first-child { padding-top: 0; }
.market-name { font-size: 0.65rem; font-weight: 600; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.05em; }
.market-price { font-size: 1.1rem; font-weight: 800; color: #1F2937; margin: 0.15rem 0; }
.market-change { font-size: 0.65rem; font-weight: 600; display: flex; align-items: center; gap: 0.35rem; }
.market-change.up { color: #16A34A; }
.market-change.down { color: #DC2626; }
.market-pct { font-size: 0.6rem; }

/* Responsive */
@media (max-width: 1024px) {
	.dashboard-layout { flex-direction: column; }
	.dashboard-sidebar { width: 100%; flex-direction: row; flex-wrap: wrap; }
	.dashboard-sidebar > div { flex: 1; min-width: 300px; }
}

@media (max-width: 768px) {
	.dashboard-header { padding: 1rem; flex-wrap: wrap; gap: 0.75rem; }
	.dashboard-container { padding: 0 1rem 1.5rem; }
	.tile-row-2 { grid-template-columns: 1fr; }
	.tile-row-3 { grid-template-columns: 1fr 1fr; }
	.tile-row-4 { grid-template-columns: 1fr 1fr; }
	.market-grid { grid-template-columns: 1fr 1fr; gap: 1rem; }
	.market-card { border-bottom: none; }
	.tile-hero { padding: 1.5rem; }
}

@media (max-width: 480px) {
	.tile-row-3 { grid-template-columns: 1fr; }
	.market-grid { grid-template-columns: 1fr 1fr; }
	.clock-block { display: none; }
}
</style>
