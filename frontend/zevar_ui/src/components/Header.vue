<template>
	<header class="relative z-50">
		<!-- Top Bar -->
		<div
			:class="isDark ? 'bg-[#1a1a1a] border-white/5' : 'bg-[#faf5f0] border-gray-200'"
			class="border-b"
		>
			<div class="max-w-7xl mx-auto px-8 h-9 flex items-center justify-between text-xs">
				<div
					class="flex items-center gap-4"
					:class="isDark ? 'text-gray-400' : 'text-gray-600'"
				>
					<div class="flex items-center gap-1.5">
						<span
							class="w-4 h-4 rounded-full flex items-center justify-center"
							style="background: linear-gradient(135deg, #c9a962, #8b7355)"
						>
							<span class="text-[7px] text-white font-bold">Au</span>
						</span>
						<span>Gold</span>
						<span
							class="font-semibold"
							:class="isDark ? 'text-white' : 'text-gray-900'"
							>${{ goldPrice }}/oz</span
						>
						<span :class="priceChange >= 0 ? 'text-emerald-500' : 'text-red-500'">
							{{ priceChange >= 0 ? '▲' : '▼' }}
							{{ Math.abs(priceChange).toFixed(2) }}%
						</span>
					</div>
				</div>
				<div
					class="flex items-center gap-4"
					:class="isDark ? 'text-gray-400' : 'text-gray-600'"
				>
					<button class="hover:text-[#C9A962] transition flex items-center gap-1">
						<svg
							class="w-3.5 h-3.5"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							aria-hidden="true"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="1.5"
								d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
							/>
						</svg>
						Find Stores
					</button>
				</div>
			</div>
		</div>

		<!-- Main Header -->
		<div
			:class="isDark ? 'bg-[#15161A] border-white/5' : 'bg-white border-gray-200'"
			class="border-b"
		>
			<div class="max-w-7xl mx-auto px-8 h-16 flex items-center justify-between gap-8">
				<!-- Logo - Fixed alignment -->
				<router-link to="/catalogues" class="flex items-center gap-3 flex-shrink-0">
					<img src="/logo.svg" alt="Zevar POS" class="w-9 h-9 rounded-lg" />
					<div class="flex flex-col justify-center leading-none">
						<span
							class="font-serif font-bold text-xl tracking-tight"
							:class="isDark ? 'text-white' : 'text-gray-900'"
							>ZEVAR</span
						>
						<span
							class="text-[9px] uppercase tracking-[0.2em] mt-0.5"
							:class="isDark ? 'text-gray-500' : 'text-gray-400'"
							>Fine Jewelers</span
						>
					</div>
				</router-link>

				<!-- Search -->
				<div class="flex-1 max-w-xl hidden md:block">
					<div class="relative">
						<input
							v-model="searchQuery"
							type="text"
							placeholder="Search rings, necklaces, earrings..."
							aria-label="Search products"
							class="w-full h-10 pl-10 pr-4 rounded-lg border text-sm transition-all"
							:class="
								isDark
									? 'bg-[#1a1a1a] border-white/10 text-white placeholder-gray-500 focus:border-[#C9A962] focus:ring-1 focus:ring-[#C9A962]/20'
									: 'bg-gray-50 border-gray-200 text-gray-900 placeholder-gray-400 focus:border-[#C9A962] focus:ring-1 focus:ring-[#C9A962]/20'
							"
							@keyup.enter="$emit('search', searchQuery)"
						/>
						<svg
							class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4"
							:class="isDark ? 'text-gray-500' : 'text-gray-400'"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
							/>
						</svg>
					</div>
				</div>

				<!-- Icons -->
				<div
					class="flex items-center gap-1"
					:class="isDark ? 'text-gray-400' : 'text-gray-600'"
				>
					<!-- Dark Mode Toggle -->
					<button
						@click="$emit('toggleTheme')"
						class="w-9 h-9 rounded-lg flex items-center justify-center transition"
						:class="
							isDark
								? 'hover:bg-white/10 hover:text-[#C9A962]'
								: 'hover:bg-gray-100 hover:text-[#8B6914]'
						"
						title="Toggle Theme"
						aria-label="Toggle theme"
					>
						<svg
							v-if="isDark"
							class="w-5 h-5"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="1.5"
								d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
							/>
						</svg>
						<svg
							v-else
							class="w-5 h-5"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="1.5"
								d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
							/>
						</svg>
					</button>
					<button
						class="w-9 h-9 rounded-lg flex items-center justify-center transition"
						:class="
							isDark
								? 'hover:bg-white/10 hover:text-[#C9A962]'
								: 'hover:bg-gray-100 hover:text-[#8B6914]'
						"
						aria-label="Favorites"
						title="Favorites"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="1.5"
								d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
							/>
						</svg>
					</button>
					<button
						class="w-9 h-9 rounded-lg flex items-center justify-center transition"
						:class="
							isDark
								? 'hover:bg-white/10 hover:text-[#C9A962]'
								: 'hover:bg-gray-100 hover:text-[#8B6914]'
						"
						aria-label="Account"
						title="Account"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="1.5"
								d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
							/>
						</svg>
					</button>
				</div>
			</div>
		</div>

		<!-- Navigation -->
		<nav
			:class="isDark ? 'bg-[#15161A] border-white/5' : 'bg-white border-gray-100'"
			class="border-b relative"
		>
			<div class="max-w-7xl mx-auto px-8">
				<div class="flex items-center justify-center">
					<div
						v-for="cat in navCategories"
						:key="cat.id"
						class="relative"
						@mouseenter="openDropdown = cat.id"
						@mouseleave="openDropdown = null"
						@focusin="openDropdown = cat.id"
						@focusout="openDropdown = null"
					>
						<a
							:href="router.resolve({ path: `/catalogues/${cat.id}` }).href"
							@click.prevent="navigateTo(cat.id)"
							:aria-haspopup="!!cat.subcategories"
							:aria-expanded="openDropdown === cat.id"
							class="px-4 py-3.5 text-sm font-medium whitespace-nowrap transition-all relative flex items-center gap-1.5"
							:class="[
								activeCategory === cat.id
									? 'text-[#C9A962]'
									: isDark
									? 'text-gray-300 hover:text-[#C9A962]'
									: 'text-gray-700 hover:text-[#8B6914]',
							]"
						>
							<span>{{ cat.name }}</span>
							<svg
								v-if="cat.subcategories"
								class="w-3 h-3 opacity-50"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M19 9l-7 7-7-7"
								/>
							</svg>
							<span
								v-if="activeCategory === cat.id"
								class="absolute bottom-0 left-4 right-4 h-0.5 bg-[#C9A962]"
							></span>
						</a>

						<!-- Dropdown -->
						<Transition name="dropdown">
							<div
								v-if="cat.subcategories && openDropdown === cat.id"
								class="absolute top-full left-1/2 -translate-x-1/2 rounded-b-xl shadow-xl border border-t-0 py-4 px-2 min-w-[200px] z-50"
								:class="
									isDark
										? 'bg-[#1a1a1a] border-white/10'
										: 'bg-white border-gray-100'
								"
							>
								<!-- Subcategory items navigate to parent category filtered by subcategory name -->
								<a
									v-for="sub in cat.subcategories"
									:key="sub.name"
									:href="
										router.resolve({
											path: `/catalogues/${cat.id}`,
											query: { sub: sub.name },
										}).href
									"
									@click.prevent="navigateTo(cat.id, sub.name)"
									class="block px-4 py-2.5 text-sm rounded-lg transition-all"
									:class="
										isDark
											? 'text-gray-400 hover:text-[#C9A962] hover:bg-white/5'
											: 'text-gray-600 hover:text-[#8B6914] hover:bg-[#faf5f0]'
									"
								>
									{{ sub.name }}
								</a>
							</div>
						</Transition>
					</div>
				</div>
			</div>
		</nav>
	</header>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGoldStore } from '@/stores/gold.js'

defineProps({
	isDark: { type: Boolean, default: false },
	activeCategory: { type: String, default: 'all' },
})

defineEmits(['toggleTheme', 'search'])

const router = useRouter()
const searchQuery = ref('')
const goldStore = useGoldStore()
const openDropdown = ref(null)

const goldPrice = computed(() => {
	const rate22kt = goldStore.rates['Yellow Gold-22Kt']
	if (!rate22kt) return '---'
	const perOz = (rate22kt * 31.1035).toFixed(2)
	return Number(perOz).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
})

const priceChange = ref(0.0)

const navCategories = [
	{ id: 'all', name: 'All Jewellery' },
	{
		id: 'gold',
		name: 'Gold',
		subcategories: [
			{ name: 'Gold Rings' },
			{ name: 'Gold Chains' },
			{ name: 'Gold Earrings' },
			{ name: 'Gold Bangles' },
			{ name: 'Gold Necklace Sets' },
		],
	},
	{
		id: 'diamond',
		name: 'Diamond',
		subcategories: [
			{ name: 'Diamond Rings' },
			{ name: 'Diamond Earrings' },
			{ name: 'Diamond Pendants' },
			{ name: 'Diamond Bracelets' },
			{ name: 'Solitaires' },
		],
	},
	{
		id: 'earrings',
		name: 'Earrings',
		subcategories: [
			{ name: 'Stud Earrings' },
			{ name: 'Hoop Earrings' },
			{ name: 'Drop Earrings' },
			{ name: 'Chandelier Earrings' },
			{ name: 'Pearl Earrings' },
		],
	},
	{
		id: 'rings',
		name: 'Rings',
		subcategories: [
			{ name: 'Engagement Rings' },
			{ name: 'Wedding Bands' },
			{ name: 'Eternity Rings' },
			{ name: 'Statement Rings' },
			{ name: 'Stackable Rings' },
		],
	},
	{
		id: 'necklaces',
		name: 'Necklaces',
		subcategories: [
			{ name: 'Chain Necklaces' },
			{ name: 'Pendant Necklaces' },
			{ name: 'Layered Necklaces' },
			{ name: 'Chokers' },
			{ name: 'Pearl Necklaces' },
		],
	},
	{
		id: 'bracelets',
		name: 'Bracelets',
		subcategories: [
			{ name: 'Tennis Bracelets' },
			{ name: 'Bangles' },
			{ name: 'Cuff Bracelets' },
			{ name: 'Charm Bracelets' },
			{ name: 'Link Bracelets' },
		],
	},
	{
		id: 'pendants',
		name: 'Pendants',
		subcategories: [
			{ name: 'Diamond Pendants' },
			{ name: 'Gold Pendants' },
			{ name: 'Heart Pendants' },
			{ name: 'Cross Pendants' },
			{ name: 'Initial Pendants' },
		],
	},
	{
		id: 'wedding',
		name: 'Wedding',
		subcategories: [
			{ name: 'Bridal Sets' },
			{ name: 'Engagement Rings' },
			{ name: 'Wedding Bands' },
			{ name: 'Bridesmaid Gifts' },
		],
	},
	{
		id: 'gifting',
		name: 'Gifting',
		subcategories: [
			{ name: 'Under $500' },
			{ name: 'Under $1,000' },
			{ name: 'Under $2,500' },
			{ name: 'Luxury Gifts' },
			{ name: 'Gift Cards' },
		],
	},
	{ id: 'collections', name: 'Collections' },
]

function navigateTo(category, subcategory = null) {
	if (category === 'all') router.push('/catalogues')
	else if (subcategory)
		router.push({ path: `/catalogues/${category}`, query: { sub: subcategory } })
	else router.push(`/catalogues/${category}`)
}

onMounted(async () => {
	goldStore.startPolling()
})
</script>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
	transition: opacity 0.15s ease, transform 0.15s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
	opacity: 0;
	transform: translateY(-4px);
}
</style>
