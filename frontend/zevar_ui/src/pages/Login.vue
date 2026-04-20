<template>
	<div class="login-wrapper">
		<div class="login-card">
			<!-- Logo -->
			<div class="login-logo">
				<div class="logo-circle">Z</div>
				<h1 class="login-heading">Zevar Fine Jewelers</h1>
				<p class="login-subheading">Sign in to continue</p>
			</div>

			<form @submit.prevent="login" class="login-form">
				<!-- Username -->
				<div class="field-group">
					<label class="field-label">Employee ID / Username</label>
					<div class="input-wrapper">
						<svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
						<input
							v-model="email"
							type="text"
							id="login-username"
							placeholder="Enter your employee ID"
							autocomplete="username"
							class="login-input"
						/>
					</div>
				</div>

				<!-- Password -->
				<div class="field-group">
					<label class="field-label">PIN / Password</label>
					<div class="input-wrapper">
						<svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0110 0v4"></path></svg>
						<input
							v-model="password"
							:type="showPassword ? 'text' : 'password'"
							id="login-password"
							placeholder="Enter your PIN"
							autocomplete="current-password"
							class="login-input"
						/>
						<button type="button" @click="showPassword = !showPassword" class="toggle-pw" tabindex="-1">
							<svg v-if="!showPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
							<svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
						</button>
					</div>
				</div>

				<!-- Remember me -->
				<label class="remember-row" for="login-remember">
					<input type="checkbox" v-model="rememberMe" id="login-remember" class="remember-check" />
					<span class="remember-text">Remember me</span>
				</label>

				<!-- Submit -->
				<button type="submit" class="login-btn" :disabled="auth.loading" id="login-submit">
					<svg v-if="!auth.loading" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5"><path d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4"></path><polyline points="10,17 15,12 10,7"></polyline><line x1="15" y1="12" x2="3" y2="12"></line></svg>
					<span v-if="auth.loading" class="spinner"></span>
					{{ auth.loading ? 'Signing in...' : 'Login' }}
				</button>

				<!-- Switch User -->
				<button type="button" class="switch-btn" @click="switchUser" id="login-switch">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 00-3-3.87"></path><path d="M16 3.13a4 4 0 010 7.75"></path></svg>
					Switch User
				</button>

				<!-- Error -->
				<p v-if="auth.error" class="login-error">
					{{ auth.error?.message || 'Invalid credentials. Please try again.' }}
				</p>
			</form>

			<div class="login-footer">
				&copy; {{ new Date().getFullYear() }} POS System. All rights reserved.
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref } from 'vue'
import { createResource } from 'frappe-ui'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const rememberMe = ref(false)
const router = useRouter()

const auth = createResource({
	url: 'login',
	makeParams() {
		return {
			usr: email.value,
			pwd: password.value,
		}
	},
	onSuccess() {
		router.push('/')
	},
})

function login() {
	auth.submit()
}

function switchUser() {
	email.value = ''
	password.value = ''
}
</script>

<style scoped>
.login-wrapper {
	min-height: 100vh;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 1rem;
}

.login-card {
	width: 100%;
	max-width: 420px;
	background: white;
	border-radius: 24px;
	padding: 2.5rem 2.25rem 2rem;
	box-shadow: 0 4px 24px rgba(0,0,0,0.06), 0 1px 4px rgba(0,0,0,0.04);
}

/* Logo */
.login-logo { text-align: center; margin-bottom: 2rem; }
.logo-circle {
	width: 56px; height: 56px;
	background: #F97316;
	border-radius: 50%;
	display: inline-flex;
	align-items: center;
	justify-content: center;
	font-size: 1.5rem;
	font-weight: 800;
	color: white;
	margin-bottom: 0.75rem;
	box-shadow: 0 4px 14px rgba(249, 115, 22, 0.3);
}
.login-heading { font-size: 1.5rem; font-weight: 800; color: #1F2937; margin: 0; }
.login-subheading { font-size: 0.85rem; color: #9CA3AF; margin-top: 0.25rem; }

/* Form */
.login-form { display: flex; flex-direction: column; gap: 1.25rem; }

.field-group { display: flex; flex-direction: column; gap: 0.4rem; }
.field-label { font-size: 0.8rem; font-weight: 600; color: #374151; }

.input-wrapper {
	position: relative;
	display: flex;
	align-items: center;
}
.input-icon {
	position: absolute;
	left: 14px;
	width: 18px; height: 18px;
	color: #9CA3AF;
	pointer-events: none;
}
.login-input {
	width: 100%;
	height: 48px;
	padding: 0 14px 0 44px;
	border: 1.5px solid #E5E7EB;
	border-radius: 12px;
	font-size: 0.9rem;
	color: #1F2937;
	background: #FAFAFA;
	transition: all 0.2s;
	outline: none;
	font-family: inherit;
}
.login-input:focus {
	border-color: #F97316;
	box-shadow: 0 0 0 3px rgba(249,115,22,0.1);
	background: white;
}
.login-input::placeholder { color: #D1D5DB; }

.toggle-pw {
	position: absolute;
	right: 12px;
	background: none;
	border: none;
	cursor: pointer;
	color: #9CA3AF;
	padding: 4px;
	display: flex;
}
.toggle-pw:hover { color: #6B7280; }
.toggle-pw svg { width: 18px; height: 18px; }

/* Remember */
.remember-row {
	display: flex;
	align-items: center;
	gap: 0.5rem;
	cursor: pointer;
	margin-top: -0.25rem;
}
.remember-check {
	width: 16px; height: 16px;
	accent-color: #F97316;
	cursor: pointer;
}
.remember-text { font-size: 0.8rem; color: #6B7280; }

/* Buttons */
.login-btn {
	width: 100%;
	height: 48px;
	background: linear-gradient(135deg, #F97316, #EA580C);
	color: white;
	border: none;
	border-radius: 12px;
	font-size: 0.95rem;
	font-weight: 700;
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 0.5rem;
	transition: all 0.2s;
	font-family: inherit;
}
.login-btn:hover:not(:disabled) { background: linear-gradient(135deg, #EA580C, #C2410C); transform: translateY(-1px); box-shadow: 0 4px 16px rgba(249,115,22,0.35); }
.login-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.login-btn svg { width: 20px; height: 20px; }

.switch-btn {
	width: 100%;
	height: 44px;
	background: white;
	border: 1.5px solid #E5E7EB;
	border-radius: 12px;
	font-size: 0.85rem;
	font-weight: 600;
	color: #374151;
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 0.5rem;
	transition: all 0.2s;
	font-family: inherit;
}
.switch-btn:hover { border-color: #D1D5DB; background: #F9FAFB; }
.switch-btn svg { width: 16px; height: 16px; }

/* Error */
.login-error {
	text-align: center;
	font-size: 0.8rem;
	color: #DC2626;
	background: #FEF2F2;
	padding: 0.6rem 1rem;
	border-radius: 10px;
	border: 1px solid #FECACA;
	margin: 0;
}

/* Spinner */
.spinner {
	width: 18px; height: 18px;
	border: 2.5px solid rgba(255,255,255,0.3);
	border-top-color: white;
	border-radius: 50%;
	animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Footer */
.login-footer {
	text-align: center;
	font-size: 0.7rem;
	color: #9CA3AF;
	margin-top: 1.5rem;
	padding-top: 1rem;
	border-top: 1px solid #F3F4F6;
}
</style>
