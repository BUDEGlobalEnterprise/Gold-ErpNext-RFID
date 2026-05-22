<template>
	<div class="dashboard-wrapper">
		<!-- Header -->
		<header class="dashboard-header">
			<div class="header-left">
				<div class="logo-block">
					<div class="logo-icon" style="font-weight: 900; font-size: 24px">Z</div>
					<div>
						<h1 class="premium-title !text-[1.35rem] !leading-[1.2]">
							Zevar Fine Jewelers
						</h1>
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
					<svg
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
						class="w-4 h-4"
					>
						<path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"></path>
						<polyline points="16,17 21,12 16,7"></polyline>
						<line x1="21" y1="12" x2="9" y2="12"></line>
					</svg>
					Logout
				</button>
			</div>
		</header>

		<div class="dashboard-container" style="padding-top: 0">
			<div
				v-if="session.user"
				class="welcome-text"
				style="width: 100%; margin-bottom: 1.25rem"
			>
				Welcome back,
				<strong>{{ session.user?.full_name?.split(' ')[0] || 'User' }}</strong>
			</div>

			<div class="dashboard-layout">
				<!-- Main Content -->
				<main class="dashboard-main">
					<!-- Hero: POS Tile -->
					<router-link to="/terminal" class="tile-hero" id="tile-pos">
						<div class="tile-hero-icon" style="background: #f97316">
							<svg
								viewBox="0 0 24 24"
								fill="none"
								stroke="white"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
								class="w-8 h-8"
							>
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
					<br />

					<!-- Section: Employee Portal (for Employee/ESS/Sales Associate roles) -->
					<div
						class="admin-section"
						v-if="
							session.hasAnyRole([
								'Employee',
								'Employee Self Service',
								'Sales Associate',
							]) && !session.isAdmin
						"
					>
						<h4 class="section-label">Employee Portal</h4>
						<div class="tile-row-4">
							<router-link to="/portal" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #0ea5e9">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"></path>
										<circle cx="12" cy="7" r="4"></circle>
									</svg>
								</div>
								<h3 class="tile-title-sm">My Portal</h3>
							</router-link>
							<router-link to="/time-clock" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #f43f5e">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<circle cx="12" cy="12" r="10"></circle>
										<polyline points="12 6 12 12 16 14"></polyline>
									</svg>
								</div>
								<h3 class="tile-title-sm">Time Clock</h3>
							</router-link>
							<router-link to="/time-clock" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #10b981">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<rect
											x="3"
											y="4"
											width="18"
											height="18"
											rx="2"
											ry="2"
										></rect>
										<line x1="16" y1="2" x2="16" y2="6"></line>
										<line x1="8" y1="2" x2="8" y2="6"></line>
										<line x1="3" y1="10" x2="21" y2="10"></line>
									</svg>
								</div>
								<h3 class="tile-title-sm">Attendance</h3>
							</router-link>
							<router-link to="/leave" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #8b5cf6">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<circle cx="12" cy="12" r="10"></circle>
										<polyline points="12 6 12 12 16 14"></polyline>
									</svg>
								</div>
								<h3 class="tile-title-sm">Leave</h3>
							</router-link>
						</div>
					</div>

					<!-- Section: Primary Operations (Legacy Mapping) -->
					<div class="admin-section">
						<h4 class="section-label">Primary Operations</h4>
						<div class="tile-row-4">
							<!-- End Of Day Reports -->
							<router-link
								v-if="visibility.reportsTile"
								to="/reports"
								class="tile-secondary"
							>
								<div class="tile-icon-sm" style="background: #3b82f6">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path
											d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"
										></path>
										<polyline points="14,2 14,8 20,8"></polyline>
										<line x1="16" y1="13" x2="8" y2="13"></line>
										<line x1="16" y1="17" x2="8" y2="17"></line>
									</svg>
								</div>
								<h3 class="tile-title-sm">End Of Day Reports</h3>
							</router-link>
							<!-- Customer List -->
							<router-link to="/customers" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #10b981">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"></path>
										<circle cx="9" cy="7" r="4"></circle>
										<path d="M23 21v-2a4 4 0 00-3-3.87"></path>
										<path d="M16 3.13a4 4 0 010 7.75"></path>
									</svg>
								</div>
								<h3 class="tile-title-sm">Customer List</h3>
							</router-link>
							<!-- Source Management -->
							<router-link to="/catalogues" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #8b5cf6">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path
											d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"
										></path>
										<line x1="7" y1="7" x2="7.01" y2="7"></line>
									</svg>
								</div>
								<h3 class="tile-title-sm">Source Management</h3>
							</router-link>
							<!-- Reports -->
							<router-link
								v-if="visibility.reportsTile"
								to="/reports"
								class="tile-secondary"
							>
								<div class="tile-icon-sm" style="background: #ec4899">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<line x1="18" y1="20" x2="18" y2="10"></line>
										<line x1="12" y1="20" x2="12" y2="4"></line>
										<line x1="6" y1="20" x2="6" y2="14"></line>
									</svg>
								</div>
								<h3 class="tile-title-sm">Reports</h3>
							</router-link>
							<!-- Inventory -->
							<router-link to="/inventory" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #64748b">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path
											d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"
										></path>
										<polyline
											points="3.27,6.96 12,12.01 20.73,6.96"
										></polyline>
										<line x1="12" y1="22.08" x2="12" y2="12"></line>
									</svg>
								</div>
								<h3 class="tile-title-sm">Inventory</h3>
							</router-link>
							<!-- Time Clock -->
							<router-link to="/time-clock" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #f43f5e">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<circle cx="12" cy="12" r="10"></circle>
										<polyline points="12 6 12 12 16 14"></polyline>
									</svg>
								</div>
								<h3 class="tile-title-sm">Time Clock</h3>
							</router-link>
							<!-- Back Up -->
							<router-link to="/support" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #6b7280">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"></path>
										<polyline points="7 10 12 15 17 10"></polyline>
										<line x1="12" y1="15" x2="12" y2="3"></line>
									</svg>
								</div>
								<h3 class="tile-title-sm">Back Up</h3>
							</router-link>
							<!-- Repairs -->
							<router-link to="/repairs" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #6366f1">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path
											d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"
										></path>
									</svg>
								</div>
								<h3 class="tile-title-sm">Repairs</h3>
							</router-link>
						</div>
					</div>

					<!-- Section: Core Operations -->
					<div class="admin-section">
						<h4 class="section-label">Core Operations</h4>
						<div class="tile-row-4">
							<!-- Sales -->
							<router-link to="/transactions" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #3b82f6">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path
											d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"
										></path>
										<polyline points="14,2 14,8 20,8"></polyline>
										<line x1="16" y1="13" x2="8" y2="13"></line>
										<line x1="16" y1="17" x2="8" y2="17"></line>
									</svg>
								</div>
								<h3 class="tile-title-sm">Sales</h3>
							</router-link>
							<!-- Quotes -->
							<router-link to="/quotes" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #0ea5e9">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path
											d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"
										></path>
										<polyline points="14,2 14,8 20,8"></polyline>
										<line x1="16" y1="13" x2="8" y2="13"></line>
										<line x1="16" y1="17" x2="8" y2="17"></line>
									</svg>
								</div>
								<h3 class="tile-title-sm">Quotes</h3>
							</router-link>
							<router-link
								to="/layaway"
								class="tile-secondary"
								v-if="
									session.hasAnyRole([
										'Sales User',
										'Store Manager',
										'System Manager',
										'Administrator',
										'Employee',
										'Employee Self Service',
									])
								"
							>
								<div class="tile-icon-sm" style="background: #f59e0b">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<line x1="12" y1="1" x2="12" y2="23"></line>
										<path
											d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"
										></path>
									</svg>
								</div>
								<h3 class="tile-title-sm">Layaways</h3>
							</router-link>
							<!-- Repairs -->
							<router-link
								to="/repairs"
								class="tile-secondary"
								v-if="
									session.hasAnyRole([
										'Sales User',
										'Technician',
										'Store Manager',
										'System Manager',
										'Administrator',
										'Employee',
										'Employee Self Service',
									])
								"
							>
								<div class="tile-icon-sm" style="background: #6366f1">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path
											d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"
										></path>
									</svg>
								</div>
								<h3 class="tile-title-sm">Repairs</h3>
							</router-link>
							<!-- Suppliers -->
							<router-link to="/contacts" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #10b981">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"></path>
										<circle cx="9" cy="7" r="4"></circle>
										<path d="M23 21v-2a4 4 0 00-3-3.87"></path>
										<path d="M16 3.13a4 4 0 010 7.75"></path>
									</svg>
								</div>
								<h3 class="tile-title-sm">Suppliers</h3>
							</router-link>
							<!-- Products -->
							<router-link to="/catalogues" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #8b5cf6">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path
											d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"
										></path>
										<line x1="7" y1="7" x2="7.01" y2="7"></line>
									</svg>
								</div>
								<h3 class="tile-title-sm">Products</h3>
							</router-link>
							<!-- Tasks -->
							<router-link to="/tasks" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #f43f5e">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<polyline points="9 11 12 14 22 4"></polyline>
										<path
											d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"
										></path>
									</svg>
								</div>
								<h3 class="tile-title-sm">Tasks</h3>
							</router-link>
						</div>
					</div>

					<!-- Section: Inventory Management -->
					<div
						class="admin-section"
						v-if="
							session.hasAnyRole([
								'Store Manager',
								'System Manager',
								'Administrator',
							])
						"
					>
						<h4 class="section-label">Stock</h4>
						<div class="tile-row-4">
							<router-link to="/stock/supplier-orders" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #64748b">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path
											d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"
										></path>
									</svg>
								</div>
								<h3 class="tile-title-sm">Supplier Orders</h3>
							</router-link>
							<router-link to="/stock/incoming-memos" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #64748b">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path
											d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"
										></path>
									</svg>
								</div>
								<h3 class="tile-title-sm">Incoming Memos</h3>
							</router-link>
							<router-link to="/inventory" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #64748b">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path
											d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"
										></path>
										<polyline
											points="3.27,6.96 12,12.01 20.73,6.96"
										></polyline>
										<line x1="12" y1="22.08" x2="12" y2="12"></line>
									</svg>
								</div>
								<h3 class="tile-title-sm">Stock In</h3>
							</router-link>
							<router-link to="/stock/assemblies" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #64748b">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path
											d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"
										></path>
									</svg>
								</div>
								<h3 class="tile-title-sm">Assemblies</h3>
							</router-link>
							<router-link to="/stock/metals" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #64748b">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
										<polyline points="2 17 12 22 22 17"></polyline>
										<polyline points="2 12 12 17 22 12"></polyline>
									</svg>
								</div>
								<h3 class="tile-title-sm">Metals</h3>
							</router-link>
							<router-link to="/stock/gems" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #64748b">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
									</svg>
								</div>
								<h3 class="tile-title-sm">Gems</h3>
							</router-link>
							<router-link to="/inventory-counts" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #64748b">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<rect
											x="3"
											y="4"
											width="18"
											height="18"
											rx="2"
											ry="2"
										></rect>
										<line x1="16" y1="2" x2="16" y2="6"></line>
										<line x1="8" y1="2" x2="8" y2="6"></line>
										<line x1="3" y1="10" x2="21" y2="10"></line>
									</svg>
								</div>
								<h3 class="tile-title-sm">Inventory Counts</h3>
							</router-link>
							<router-link to="/stock/storages" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #64748b">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path
											d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"
										></path>
									</svg>
								</div>
								<h3 class="tile-title-sm">Storages</h3>
							</router-link>
							<router-link to="/stock/categories" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #64748b">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<line x1="8" y1="6" x2="21" y2="6"></line>
										<line x1="8" y1="12" x2="21" y2="12"></line>
										<line x1="8" y1="18" x2="21" y2="18"></line>
										<line x1="3" y1="6" x2="3.01" y2="6"></line>
										<line x1="3" y1="12" x2="3.01" y2="12"></line>
										<line x1="3" y1="18" x2="3.01" y2="18"></line>
									</svg>
								</div>
								<h3 class="tile-title-sm">Categories</h3>
							</router-link>
							<router-link to="/stock/brands" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #64748b">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<circle cx="12" cy="12" r="10"></circle>
										<polygon
											points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"
										></polygon>
									</svg>
								</div>
								<h3 class="tile-title-sm">Brands</h3>
							</router-link>
							<router-link to="/stock/collections" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #64748b">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<rect x="3" y="3" width="7" height="7"></rect>
										<rect x="14" y="3" width="7" height="7"></rect>
										<rect x="14" y="14" width="7" height="7"></rect>
										<rect x="3" y="14" width="7" height="7"></rect>
									</svg>
								</div>
								<h3 class="tile-title-sm">Collections</h3>
							</router-link>
							<router-link to="/stock/catalogs" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #64748b">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path d="M4 19.5A2.5 2.5 0 016.5 17H20"></path>
										<path
											d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"
										></path>
									</svg>
								</div>
								<h3 class="tile-title-sm">Catalogs</h3>
							</router-link>
						</div>
					</div>

					<!-- Section: Accounting & Financials -->
					<div
						class="admin-section"
						v-if="
							session.hasAnyRole([
								'Store Manager',
								'System Manager',
								'Administrator',
								'Accounts Manager',
							])
						"
					>
						<h4 class="section-label">Accounting</h4>
						<div class="tile-row-4">
							<router-link to="/accounting/transactions" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #14b8a6">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<line x1="12" y1="1" x2="12" y2="23"></line>
										<path
											d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"
										></path>
									</svg>
								</div>
								<h3 class="tile-title-sm">Transactions</h3>
							</router-link>
							<router-link to="/closing" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #14b8a6">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path
											d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z"
										></path>
									</svg>
								</div>
								<h3 class="tile-title-sm">End-of-day Closing</h3>
							</router-link>
							<router-link
								v-if="visibility.accountingSection"
								to="/reports"
								class="tile-secondary"
							>
								<div class="tile-icon-sm" style="background: #ec4899">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<line x1="18" y1="20" x2="18" y2="10"></line>
										<line x1="12" y1="20" x2="12" y2="4"></line>
										<line x1="6" y1="20" x2="6" y2="14"></line>
									</svg>
								</div>
								<h3 class="tile-title-sm">Reports</h3>
							</router-link>
							<router-link to="/accounting/terminals" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #14b8a6">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<rect
											x="2"
											y="3"
											width="20"
											height="14"
											rx="2"
											ry="2"
										></rect>
										<line x1="8" y1="21" x2="16" y2="21"></line>
										<line x1="12" y1="17" x2="12" y2="21"></line>
									</svg>
								</div>
								<h3 class="tile-title-sm">Terminals</h3>
							</router-link>
							<router-link to="/accounting/invoices" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #14b8a6">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path
											d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"
										></path>
										<polyline points="14 2 14 8 20 8"></polyline>
										<line x1="16" y1="13" x2="8" y2="13"></line>
										<line x1="16" y1="17" x2="8" y2="17"></line>
									</svg>
								</div>
								<h3 class="tile-title-sm">Invoices to be Processed</h3>
							</router-link>
							<router-link
								to="/accounting/invoices?tab=purchase"
								class="tile-secondary"
							>
								<div class="tile-icon-sm" style="background: #14b8a6">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path
											d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"
										></path>
										<polyline points="14 2 14 8 20 8"></polyline>
										<line x1="16" y1="13" x2="8" y2="13"></line>
										<line x1="16" y1="17" x2="8" y2="17"></line>
									</svg>
								</div>
								<h3 class="tile-title-sm">Incoming Invoices</h3>
							</router-link>
							<router-link
								to="/accounting/invoices?tab=sales"
								class="tile-secondary"
							>
								<div class="tile-icon-sm" style="background: #14b8a6">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path
											d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"
										></path>
										<polyline points="14 2 14 8 20 8"></polyline>
										<line x1="16" y1="13" x2="8" y2="13"></line>
										<line x1="16" y1="17" x2="8" y2="17"></line>
									</svg>
								</div>
								<h3 class="tile-title-sm">Outgoing Invoices</h3>
							</router-link>
							<router-link
								to="/accounting/credit-notes?tab=incoming"
								class="tile-secondary"
							>
								<div class="tile-icon-sm" style="background: #14b8a6">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path
											d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"
										></path>
										<polyline points="14 2 14 8 20 8"></polyline>
										<line x1="16" y1="13" x2="8" y2="13"></line>
										<line x1="16" y1="17" x2="8" y2="17"></line>
									</svg>
								</div>
								<h3 class="tile-title-sm">Incoming Credit Notes</h3>
							</router-link>
							<router-link
								to="/accounting/credit-notes?tab=outgoing"
								class="tile-secondary"
							>
								<div class="tile-icon-sm" style="background: #14b8a6">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path
											d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"
										></path>
										<polyline points="14 2 14 8 20 8"></polyline>
										<line x1="16" y1="13" x2="8" y2="13"></line>
										<line x1="16" y1="17" x2="8" y2="17"></line>
									</svg>
								</div>
								<h3 class="tile-title-sm">Outgoing Credit Notes</h3>
							</router-link>
							<router-link to="/accounting/export-ubl" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #14b8a6">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"></path>
										<polyline points="7 10 12 15 17 10"></polyline>
										<line x1="12" y1="15" x2="12" y2="3"></line>
									</svg>
								</div>
								<h3 class="tile-title-sm">Export UBL</h3>
							</router-link>
						</div>
					</div>

					<!-- Admin Section: Settings & Portal -->
					<div v-if="session.isAdmin" class="admin-section">
						<h4 class="section-label">System Administration</h4>
						<div class="tile-row-4">
							<router-link to="/portal" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #0ea5e9">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"></path>
										<circle cx="12" cy="7" r="4"></circle>
									</svg>
								</div>
								<h3 class="tile-title-sm">Employee Portal</h3>
							</router-link>
							<router-link to="/settings" class="tile-secondary">
								<div class="tile-icon-sm" style="background: #6b7280">
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="white"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<circle cx="12" cy="12" r="3"></circle>
										<path
											d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"
										></path>
									</svg>
								</div>
								<h3 class="tile-title-sm">Settings</h3>
							</router-link>
						</div>
					</div>
				</main>

				<!-- Sidebar -->
				<aside class="dashboard-sidebar">
					<!-- Quick Actions -->
					<div
						class="sidebar-section"
						v-if="
							session.hasAnyRole([
								'Store Manager',
								'System Manager',
								'Administrator',
								'Inventory Manager',
							])
						"
					>
						<h4 class="sidebar-label">Quick Actions</h4>
						<router-link to="/inventory/add" class="quick-action-btn">
							<div class="quick-action-icon">
								<svg
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
									stroke-linecap="round"
									stroke-linejoin="round"
								>
									<line x1="12" y1="5" x2="12" y2="19"></line>
									<line x1="5" y1="12" x2="19" y2="12"></line>
								</svg>
							</div>
							<div class="quick-action-text">
								<h5>Add to Inventory</h5>
								<p>Item with Vendor & SKU</p>
							</div>
						</router-link>
					</div>

					<!-- Market Prices -->
					<div class="sidebar-section market-prices" v-if="sortedRates.length > 0">
						<h4
							class="sidebar-label"
							style="display: flex; align-items: center; gap: 0.5rem"
						>
							<svg
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								style="width: 14px; height: 14px"
							>
								<polyline points="22,7 13.5,15.5 8.5,10.5 2,17"></polyline>
								<polyline points="16,7 22,7 22,13"></polyline>
							</svg>
							Market Prices
						</h4>
							<div class="market-grid">
								<div
									v-for="[key, rate, changePct, trend, changeAmt] in sortedRates"
									:key="key"
									class="market-card cursor-pointer hover:bg-gray-50 dark:hover:bg-warm-dark-700 rounded-lg px-2 transition"
									role="button"
									tabindex="0"
									title="Refresh prices"
									@click="refreshMarketRates"
									@keydown.enter.prevent="refreshMarketRates"
									@keydown.space.prevent="refreshMarketRates"
								>
									<div class="market-name">
									{{ formatPurityLabel(key).toUpperCase() }}
								</div>
								<div class="flex items-end justify-between mt-1">
									<div class="market-price">${{ rate }}</div>
									<div
										v-if="changePct != null"
										class="flex items-center gap-1 text-[11px] font-bold pb-0.5"
										:style="{
											color:
												trend === 'up'
													? '#10b981'
													: trend === 'down'
													? '#ef4444'
													: '#9ca3af',
										}"
									>
										<span
											>{{ trend === 'up' ? '+' : trend === 'down' ? '-' : ''
											}}{{
												changeAmt !== '0.00' ? Math.abs(changeAmt) : '0.00'
											}}</span
										>
										<span class="text-[9px]">{{
											trend === 'up' ? '▲' : trend === 'down' ? '▼' : '●'
										}}</span>
										<span>{{ Math.abs(changePct).toFixed(2) }}%</span>
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
import { useSessionStore } from '@/stores/session.js'
import { useGoldStore } from '@/stores/gold.js'
import { getDashboardVisibility } from '@/utils/permissions.js'

const session = useSessionStore()
const goldStore = useGoldStore()

// Role-based dashboard visibility
const visibility = getDashboardVisibility()

// Clock
const currentTime = ref('')
const currentDate = ref('')
let clockInterval = null

function updateClock() {
	const now = new Date()
	currentTime.value = now.toLocaleTimeString('en-US', {
		hour: '2-digit',
		minute: '2-digit',
		second: '2-digit',
	})
	currentDate.value = now.toLocaleDateString('en-US', {
		weekday: 'long',
		year: 'numeric',
		month: 'long',
		day: 'numeric',
	})
}

function refreshMarketRates() {
	goldStore.refreshRates()
}

const TROY_OZ_GRAMS = 31.1035

const DASHBOARD_RATE_PRIORITIES = [
	'Yellow Gold-22Kt',
	'Yellow Gold-18Kt',
	'Yellow Gold-14Kt',
	'Yellow Gold-10Kt',
	'Silver-925 Sterling',
	'Silver-999 Fine',
]

const sortedRates = computed(() => {
	if (!goldStore.rates) return []
	return Object.entries(goldStore.rates)
		.filter(([key, data]) => {
			if (!key || key === 'null' || !data.rate_per_gram) return false
			if (key.includes('Platinum')) return false
			if (key.includes('24Kt') || key.includes('24K') || key.includes('24kt')) return false
			return true
		})
		.map(([key, data]) => [
			key,
			(data.rate_per_gram * TROY_OZ_GRAMS).toFixed(2),
			data.change_pct,
			data.trend,
			(data.change_amount * TROY_OZ_GRAMS).toFixed(2),
		])
		.sort((a, b) => {
			const iA = DASHBOARD_RATE_PRIORITIES.findIndex((p) => a[0].includes(p))
			const iB = DASHBOARD_RATE_PRIORITIES.findIndex((p) => b[0].includes(p))
			return (iA === -1 ? 99 : iA) - (iB === -1 ? 99 : iB)
		})
})

function formatPurityLabel(key) {
	if (key.startsWith('Silver-')) {
		const purity = key.split('-').slice(1).join(' ')
		return purity.replace('Sterling', '').replace('Fine', '').trim() + ' Silver'
	}
	const parts = key.split('-')
	if (parts.length >= 2) return parts[1] + ' Gold'
	return key
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
/* ===== CSS Custom Properties — Light (default) ===== */
.dashboard-wrapper {
	min-height: 100vh;
	display: flex;
	flex-direction: column;
	background: transparent;
}

/* Header */
.dashboard-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 1.25rem 2rem;
	flex-shrink: 0;
	background: transparent;
	border-bottom: none;
}

.header-left {
	display: flex;
	align-items: center;
}
.header-right {
	display: flex;
	align-items: center;
	gap: 1.5rem;
}

.logo-block {
	display: flex;
	align-items: center;
	gap: 0.75rem;
}
.logo-icon {
	width: 48px;
	height: 48px;
	background: #f97316;
	border-radius: 14px;
	display: flex;
	align-items: center;
	justify-content: center;
	color: white;
	box-shadow: 0 4px 14px rgba(249, 115, 22, 0.35);
}
.logo-icon svg {
	width: 26px;
	height: 26px;
}
.logo-title {
	font-size: 1.35rem;
	font-weight: 800;
	color: #111827;
	line-height: 1.2;
}
.logo-subtitle {
	font-size: 0.75rem;
	color: #9ca3af;
	font-weight: 500;
}

.clock-block {
	text-align: right;
}
.clock-time {
	font-size: 1.25rem;
	font-weight: 700;
	color: #111827;
	font-variant-numeric: tabular-nums;
}
.clock-date {
	font-size: 0.7rem;
	color: #9ca3af;
	font-weight: 500;
}

.logout-btn {
	display: flex;
	align-items: center;
	gap: 0.5rem;
	padding: 0.6rem 1.25rem;
	border: 1.5px solid #e5e7eb;
	border-radius: 12px;
	background: white;
	color: #374151;
	font-size: 0.8rem;
	font-weight: 600;
	cursor: pointer;
	transition: all 0.2s;
}
.logout-btn:hover {
	border-color: #f97316;
	color: #f97316;
	box-shadow: 0 2px 8px rgba(249, 115, 22, 0.15);
}
.logout-btn svg {
	width: 16px;
	height: 16px;
}

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
	color: #6b7280;
	margin-bottom: 1.25rem;
}
.welcome-text strong {
	color: #111827;
}

/* Tiles */
.tile-hero {
	display: flex;
	align-items: center;
	gap: 1.25rem;
	background: white;
	border-radius: 20px;
	padding: 2rem 2.5rem;
	margin-bottom: 1rem;
	box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 4px 16px rgba(0, 0, 0, 0.04);
	text-decoration: none;
	transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
	border: 1.5px solid #f3f4f6;
}
.tile-hero:hover {
	transform: translateY(-2px);
	box-shadow: 0 8px 30px rgba(212, 175, 55, 0.15);
	border-color: #d4af37;
}
.tile-hero-icon {
	width: 64px;
	height: 64px;
	border-radius: 18px;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
}
.tile-hero-icon svg {
	width: 32px;
	height: 32px;
}
.tile-hero-title {
	font-size: 1.75rem;
	font-weight: 800;
	color: #111827;
}
.tile-hero-sub {
	font-size: 0.85rem;
	color: #9ca3af;
	font-weight: 500;
}

.tile-row-2 {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 1rem;
	margin-bottom: 1rem;
}
.tile-row-3 {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 1rem;
	margin-bottom: 1rem;
}
.tile-row-4 {
	display: grid;
	grid-template-columns: repeat(4, 1fr);
	gap: 1rem;
	margin-bottom: 1rem;
}

.tile-primary {
	display: flex;
	align-items: center;
	gap: 1rem;
	background: white;
	border-radius: 18px;
	padding: 1.5rem 1.75rem;
	text-decoration: none;
	box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 4px 16px rgba(0, 0, 0, 0.04);
	transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
	border: 1.5px solid #f3f4f6;
}
.tile-primary:hover {
	transform: translateY(-2px);
	box-shadow: 0 8px 24px rgba(212, 175, 55, 0.12);
	border-color: #d4af37;
}

.tile-icon {
	width: 48px;
	height: 48px;
	border-radius: 14px;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
}
.tile-icon svg {
	width: 24px;
	height: 24px;
}
.tile-title {
	font-size: 1.1rem;
	font-weight: 700;
	color: #111827;
}
.tile-sub {
	font-size: 0.75rem;
	color: #9ca3af;
	font-weight: 500;
}

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
	box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 4px 16px rgba(0, 0, 0, 0.04);
	transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
	border: 1.5px solid #f3f4f6;
}
.tile-secondary:hover {
	transform: translateY(-2px);
	box-shadow: 0 8px 24px rgba(212, 175, 55, 0.12);
	border-color: #d4af37;
}

.tile-icon-sm {
	width: 40px;
	height: 40px;
	border-radius: 12px;
	display: flex;
	align-items: center;
	justify-content: center;
}
.tile-icon-sm svg {
	width: 20px;
	height: 20px;
}
.tile-title-sm {
	font-size: 0.85rem;
	font-weight: 700;
	color: #111827;
}
.tile-sub-sm {
	font-size: 0.65rem;
	color: #9ca3af;
	font-weight: 500;
}

/* Admin Section */
.admin-section {
	margin-top: 0.5rem;
}
.section-label {
	font-size: 0.7rem;
	font-weight: 700;
	text-transform: uppercase;
	letter-spacing: 0.08em;
	color: #9ca3af;
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
	box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
	border: 1px solid #f3f4f6;
}
.sidebar-label {
	font-size: 0.7rem;
	font-weight: 700;
	text-transform: uppercase;
	letter-spacing: 0.08em;
	color: #9ca3af;
	margin: 0 0 0.75rem 0;
}

/* Quick Actions */
.quick-action-btn {
	display: flex;
	align-items: center;
	gap: 1rem;
	padding: 1rem;
	border-radius: 12px;
	background: #f9fafb;
	border: 1.5px solid transparent;
	text-decoration: none;
	transition: all 0.2s;
}
.quick-action-btn:hover {
	background: #fff7ed;
	border-color: #fdba74;
	transform: translateY(-1px);
}
.quick-action-icon {
	width: 40px;
	height: 40px;
	border-radius: 10px;
	background: #f97316;
	color: white;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
}
.quick-action-icon svg {
	width: 20px;
	height: 20px;
}
.quick-action-text h5 {
	font-size: 0.9rem;
	font-weight: 700;
	color: #111827;
	margin: 0 0 0.15rem 0;
}
.quick-action-text p {
	font-size: 0.7rem;
	color: #6b7280;
	margin: 0;
}

/* Market Prices */
.market-prices {
	margin-top: 0.5rem;
}
.market-grid {
	display: flex;
	flex-direction: column;
	gap: 0.5rem;
}
.market-card {
	padding: 0.75rem 0.25rem;
	border-bottom: 1px solid #f3f4f6;
	background: transparent;
	transition: background 0.2s;
}
.market-card:last-child {
	border-bottom: none;
}
.market-name {
	font-size: 0.65rem;
	font-weight: 700;
	color: #9ca3af;
	text-transform: uppercase;
	letter-spacing: 0.05em;
	margin-bottom: 0.25rem;
}
.market-price {
	font-size: 1.25rem;
	font-weight: 800;
	color: #111827;
	font-variant-numeric: tabular-nums;
	line-height: 1;
}

/* Responsive */
@media (max-width: 1024px) {
	.dashboard-layout {
		flex-direction: column;
	}
	.dashboard-sidebar {
		width: 100%;
		flex-direction: row;
		flex-wrap: wrap;
	}
	.dashboard-sidebar > div {
		flex: 1;
		min-width: 300px;
	}
}

@media (max-width: 768px) {
	.dashboard-header {
		padding: 1rem;
		flex-wrap: wrap;
		gap: 0.75rem;
	}
	.dashboard-container {
		padding: 0 1rem 1.5rem;
	}
	.tile-row-2 {
		grid-template-columns: 1fr;
	}
	.tile-row-3 {
		grid-template-columns: 1fr 1fr;
	}
	.tile-row-4 {
		grid-template-columns: 1fr 1fr;
	}
	.tile-hero {
		padding: 1.5rem;
	}
}

@media (max-width: 480px) {
	.tile-row-3 {
		grid-template-columns: 1fr;
	}
	.market-grid {
		grid-template-columns: 1fr;
	}
	.clock-block {
		display: none;
	}
}

/* ===== DARK MODE (orange/gold themed) ===== */
</style>

<style>
/* Dark mode — uses higher specificity to win over scoped light styles */
html.dark .dashboard-wrapper {
	background: #0a0a0c !important;
}
html.dark .dashboard-header {
	background: #0a0a0c !important;
	border-bottom: 1px solid rgba(212, 175, 55, 0.12) !important;
}
html.dark .logo-title {
	color: #f5f0e8 !important;
}
html.dark .logo-subtitle {
	color: #a09484 !important;
}
html.dark .clock-time {
	color: #f5f0e8 !important;
}
html.dark .clock-date {
	color: #a09484 !important;
}
html.dark .logout-btn {
	border-color: rgba(212, 175, 55, 0.25) !important;
	background: #141312 !important;
	color: #d4c4a8 !important;
}
html.dark .logout-btn:hover {
	border-color: #d4af37 !important;
	color: #d4af37 !important;
	box-shadow: 0 2px 8px rgba(212, 175, 55, 0.2) !important;
}
html.dark .welcome-text {
	color: #a09484 !important;
}
html.dark .welcome-text strong {
	color: #f5f0e8 !important;
}
html.dark .tile-hero {
	background: #181614 !important;
	border-color: rgba(212, 175, 55, 0.15) !important;
}
html.dark .tile-hero:hover {
	box-shadow: 0 8px 30px rgba(212, 175, 55, 0.18) !important;
	border-color: #d4af37 !important;
}
html.dark .tile-hero-title {
	color: #f5f0e8 !important;
}
html.dark .tile-hero-sub {
	color: #a09484 !important;
}
html.dark .tile-primary {
	background: #181614 !important;
	border-color: rgba(212, 175, 55, 0.1) !important;
}
html.dark .tile-primary:hover {
	box-shadow: 0 8px 24px rgba(212, 175, 55, 0.15) !important;
	border-color: rgba(212, 175, 55, 0.35) !important;
}
html.dark .tile-title {
	color: #f5f0e8 !important;
}
html.dark .tile-sub {
	color: #a09484 !important;
}
html.dark .tile-secondary {
	background: #181614 !important;
	border-color: rgba(212, 175, 55, 0.1) !important;
}
html.dark .tile-secondary:hover {
	box-shadow: 0 8px 24px rgba(212, 175, 55, 0.15) !important;
	border-color: rgba(212, 175, 55, 0.35) !important;
}
html.dark .tile-title-sm {
	color: #f5f0e8 !important;
}
html.dark .tile-sub-sm {
	color: #a09484 !important;
}
html.dark .section-label {
	color: #a09484 !important;
}
html.dark .sidebar-section {
	background: #181614 !important;
	border-color: rgba(212, 175, 55, 0.1) !important;
}
html.dark .sidebar-label {
	color: #a09484 !important;
}
html.dark .quick-action-btn {
	background: rgba(212, 175, 55, 0.06) !important;
	border-color: rgba(212, 175, 55, 0.15) !important;
}
html.dark .quick-action-btn:hover {
	background: rgba(212, 175, 55, 0.12) !important;
	border-color: #d4af37 !important;
}
html.dark .quick-action-text h5 {
	color: #f5f0e8 !important;
}
html.dark .quick-action-text p {
	color: #a09484 !important;
}
html.dark .market-card {
	border-bottom-color: rgba(212, 175, 55, 0.08) !important;
}
html.dark .market-name {
	color: #8a7d6c !important;
}
html.dark .market-price {
	color: #f5f0e8 !important;
}
</style>
