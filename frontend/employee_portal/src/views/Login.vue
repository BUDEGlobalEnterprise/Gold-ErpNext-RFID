<template>
	<div class="h-screen w-screen flex items-center justify-center bg-[#f9fafb] relative overflow-hidden font-display">
		<!-- Decorative Background Elements -->
		<div class="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-50 rounded-full blur-[120px] opacity-60"></div>
		<div class="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-50 rounded-full blur-[120px] opacity-60"></div>
		
		<div class="w-full max-w-lg p-8 relative z-10">
			<!-- Logo Section -->
			<div class="flex flex-col items-center text-center mb-12">
				<div class="w-20 h-20 rounded-3xl bg-primary flex items-center justify-center text-white shadow-glow-emerald mb-6 transition-transform hover:scale-105 duration-500">
					<span class="material-symbols-outlined text-4xl">diamond</span>
				</div>
				<h1 class="text-4xl font-black text-gray-900 tracking-tighter mb-2 uppercase">Zevar</h1>
				<p class="text-[10px] font-black text-gray-400 uppercase tracking-[0.4em]">The Curated Atelier • Portal</p>
			</div>

			<!-- Login Card -->
			<div class="premium-card !p-12 shadow-2xl border-white/50 backdrop-blur-sm bg-white/80">
				<div class="mb-12 text-center sm:text-left">
					<h2 class="text-3xl font-black text-gray-900 tracking-tight mb-2">Secure Entrance</h2>
					<p class="text-[10px] font-black text-gray-400 uppercase tracking-[0.3em]">Identify yourself to proceed</p>
				</div>

				<form @submit.prevent="handleLogin" class="space-y-10">
					<div class="space-y-8">
						<div class="group">
							<label class="status-label !mb-3 block transition-colors group-focus-within:text-primary">Atelier Email</label>
							<div class="relative">
								<span class="material-symbols-outlined absolute left-6 top-1/2 -translate-y-1/2 text-gray-400 text-lg group-focus-within:text-primary transition-colors">alternate_email</span>
								<input
									v-model="email"
									type="text"
									required
									placeholder="artisan@zevar.com"
									class="w-full bg-gray-50/50 border border-gray-100 rounded-2xl py-5 pl-16 pr-8 text-sm font-bold text-gray-900 placeholder:text-gray-300 focus:ring-8 focus:ring-primary/5 focus:border-primary/20 focus:bg-white outline-none transition-all"
								/>
							</div>
						</div>
						
						<div class="group">
							<div class="flex justify-between items-end mb-3">
								<label class="status-label !mb-0 transition-colors group-focus-within:text-primary">Cipher Key</label>
								<a href="#" class="text-[10px] font-black text-gray-400 uppercase tracking-[0.3em] hover:text-primary transition-colors">Security Reset</a>
							</div>
							<div class="relative">
								<span class="material-symbols-outlined absolute left-6 top-1/2 -translate-y-1/2 text-gray-400 text-lg group-focus-within:text-primary transition-colors">lock</span>
								<input
									v-model="password"
									type="password"
									required
									placeholder="••••••••"
									class="w-full bg-gray-50/50 border border-gray-100 rounded-2xl py-5 pl-16 pr-8 text-sm font-bold text-gray-900 placeholder:text-gray-300 focus:ring-8 focus:ring-primary/5 focus:border-primary/20 focus:bg-white outline-none transition-all"
								/>
							</div>
						</div>
					</div>

					<div v-if="errorMsg" class="p-5 rounded-2xl bg-red-50 border border-red-100 flex items-center gap-4">
						<span class="material-symbols-outlined text-red-500 text-lg">error</span>
						<p class="text-[10px] font-black text-red-600 uppercase tracking-widest leading-relaxed">{{ errorMsg }}</p>
					</div>

					<button
						type="submit"
						:disabled="loading"
						class="w-full py-6 bg-emerald-950 text-white font-black rounded-2xl text-[11px] uppercase tracking-[0.3em] shadow-glow-emerald hover:bg-black hover:shadow-2xl active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-4"
					>
						<span v-if="loading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
						<span>{{ loading ? 'Verifying Identity...' : 'Initiate Access' }}</span>
					</button>
				</form>
			</div>

			<!-- Footer info -->
			<div class="mt-12 text-center">
				<p class="text-[9px] font-black text-gray-400 uppercase tracking-[0.3em]">Authorized Access Only • System Version 4.2.0</p>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref } from "vue";
import { createResource } from "frappe-ui";

const email = ref("");
const password = ref("");
const loading = ref(false);
const errorMsg = ref("");

const loginResource = createResource({
	url: "login",
	makeParams() {
		return { usr: email.value, pwd: password.value };
	},
	onSuccess() {
		window.location.reload();
	},
	onError(err) {
		loading.value = false;
		errorMsg.value = err?.messages?.[0] || "Invalid credentials";
	},
});

function handleLogin() {
	errorMsg.value = "";
	loading.value = true;
	loginResource.submit();
}
</script>

<style scoped>
.font-display {
	font-family: 'Plus Jakarta Sans', sans-serif;
}
</style>
