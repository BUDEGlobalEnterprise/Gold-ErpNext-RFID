<template>
	<div class="min-h-screen" :class="isDark ? 'bg-[#1e1e24]' : 'bg-white'">
		<!-- Header - only shown when not inside AppLayout -->
		<Header
			v-if="!isEmbedded"
			:isDark="isDark"
			:activeCategory="activeCategory"
			@toggleTheme="ui.toggleTheme"
			@search="performSearch"
			@selectCategory="handleCategorySelect"
		/>

		<!-- ======== 1. HERO CAROUSEL ======== -->
		<section class="relative overflow-hidden bg-[#faf5f0]" style="height: 520px">
			<TransitionGroup name="hero-slide" tag="div" class="relative w-full h-full">
				<div
					v-for="(slide, i) in heroSlides"
					:key="slide.id"
					v-show="currentSlide === i"
					class="absolute inset-0"
				>
					<img
						:src="slide.image"
						:alt="slide.title"
						class="w-full h-full object-cover"
					/>
					<div class="absolute inset-0" :style="{ background: slide.overlay }">
						<div
							class="max-w-7xl mx-auto px-6 h-full flex items-center"
							:class="slide.align === 'center' ? 'justify-center text-center' : ''"
						>
							<div class="max-w-lg" :class="slide.align === 'center' ? '' : ''">
								<p
									v-if="slide.subtitle"
									class="text-[#8B6914] text-sm tracking-[0.25em] uppercase mb-3 font-semibold"
								>
									{{ slide.subtitle }}
								</p>
								<h2
									class="text-4xl md:text-5xl font-serif font-bold text-gray-900 mb-4 leading-tight"
									v-html="slide.title"
								></h2>
								<p
									v-if="slide.description"
									class="text-gray-700 text-lg mb-6 font-light"
								>
									{{ slide.description }}
								</p>
								<button
									@click="scrollTo('shop-categories')"
									class="px-8 py-3.5 bg-[#8B6914] text-white font-bold tracking-wider uppercase text-sm rounded hover:bg-[#7a5c11] transition-all shadow-lg"
								>
									{{ slide.cta || 'Explore Now' }}
								</button>
							</div>
						</div>
					</div>
				</div>
			</TransitionGroup>
			<!-- Dots -->
			<div class="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-2 z-10">
				<button
					v-for="(_, i) in heroSlides"
					:key="i"
					@click="currentSlide = i"
					class="w-2.5 h-2.5 rounded-full transition-all"
					:class="
						currentSlide === i
							? 'bg-[#8B6914] w-6'
							: 'bg-gray-400/50 hover:bg-gray-400'
					"
				></button>
			</div>
			<!-- Arrows -->
			<button
				@click="prevSlide"
				class="absolute left-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/80 rounded-full flex items-center justify-center shadow hover:bg-white transition z-10"
			>
				<svg
					class="w-5 h-5 text-gray-700"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M15 19l-7-7 7-7"
					/>
				</svg>
			</button>
			<button
				@click="nextSlide"
				class="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/80 rounded-full flex items-center justify-center shadow hover:bg-white transition z-10"
			>
				<svg
					class="w-5 h-5 text-gray-700"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M9 5l7 7-7 7"
					/>
				</svg>
			</button>
		</section>

		<!-- ======== 2. SIGNATURE COLLECTIONS (4 lifestyle cards) ======== -->
		<section class="py-16 bg-white">
			<div class="max-w-6xl mx-auto px-6">
				<div class="text-center mb-10">
					<h2 class="text-3xl font-serif font-bold text-gray-900">
						Signature Diamond Collection
					</h2>
					<p class="text-gray-600 mt-2 font-light">Curated for the Modern Woman</p>
				</div>
				<div class="grid grid-cols-2 md:grid-cols-4 gap-5">
					<div
						v-for="col in signatureCollections"
						:key="col.name"
						class="group cursor-pointer"
						@click="handleCategorySelect(col.link)"
					>
						<div class="relative overflow-hidden rounded-2xl aspect-[3/4]">
							<img
								:src="col.image"
								:alt="col.name"
								class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
							/>
							<div
								class="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent"
							></div>
							<p
								class="absolute bottom-5 left-0 right-0 text-center text-white font-semibold text-sm tracking-wide"
							>
								{{ col.name }}
							</p>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- ======== 3. ZEVAR COLLECTIONS ======== -->
		<section class="py-16" :class="isDark ? 'bg-[#111]' : 'bg-[#faf5f0]'">
			<div class="max-w-6xl mx-auto px-8">
				<div class="text-center mb-12">
					<h2 class="text-3xl font-serif font-bold tracking-wide">Zevar Collections</h2>
					<p
						class="mt-3 font-light tracking-wide"
						:class="isDark ? 'text-gray-400' : 'text-gray-500'"
					>
						Explore our newly launched collections
					</p>
				</div>
				<div class="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-5xl mx-auto">
					<div
						class="relative overflow-hidden rounded-2xl cursor-pointer group shadow-sm aspect-[3/4]"
						@click="handleCategorySelect('rings')"
					>
						<img
							src="https://images.unsplash.com/photo-1599643477877-530eb83abc8e?w=600&q=80"
							class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
						/>
						<div
							class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent flex items-end p-6"
						>
							<p class="text-white font-serif text-xl tracking-wide">
								Valentine's Special
							</p>
						</div>
					</div>
					<div
						class="relative overflow-hidden rounded-2xl cursor-pointer group shadow-sm aspect-[3/4]"
						@click="handleCategorySelect('earrings')"
					>
						<img
							src="https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=600&q=80"
							class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
						/>
						<div
							class="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent flex items-end p-6"
						>
							<p class="text-white font-serif text-xl tracking-wide">
								Stunning Every Ear
							</p>
						</div>
					</div>
					<div
						class="relative overflow-hidden rounded-2xl cursor-pointer group shadow-sm aspect-[3/4]"
						@click="handleCategorySelect('rings')"
					>
						<img
							src="https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=600&q=80"
							class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
						/>
						<div
							class="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent flex items-end p-6"
						>
							<p class="text-white font-serif text-xl tracking-wide">
								Wedding Gifts
							</p>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- ======== 4. SHOP BY CATEGORIES (circle grid) ======== -->
		<section id="shop-categories" class="py-16 bg-white">
			<div class="max-w-6xl mx-auto px-6">
				<div class="text-center mb-10">
					<h2 class="text-3xl font-serif font-bold text-gray-900">
						Find Your Perfect Match
					</h2>
					<p class="text-[#8B6914] mt-2 font-semibold tracking-wide">
						Shop by Categories
					</p>
				</div>
				<div class="grid grid-cols-4 gap-x-6 gap-y-8 max-w-3xl mx-auto">
					<div
						v-for="cat in shopCategories"
						:key="cat.name"
						class="flex flex-col items-center group cursor-pointer"
						@click="handleCategorySelect(cat.link)"
					>
						<div
							class="w-28 h-28 md:w-36 md:h-36 rounded-2xl overflow-hidden border-2 border-transparent group-hover:border-[#C9A962] transition-all duration-300 shadow-sm group-hover:shadow-lg"
						>
							<img
								:src="cat.image"
								:alt="cat.name"
								class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
							/>
						</div>
						<p
							class="mt-3 text-sm font-bold text-gray-700 uppercase tracking-wider group-hover:text-[#8B6914] transition-colors"
						>
							{{ cat.name }}
						</p>
					</div>
				</div>
			</div>
		</section>

		<!-- ======== 5. TRENDING NOW ======== -->
		<section class="py-16 bg-white">
			<div class="max-w-6xl mx-auto px-6">
				<div class="text-center mb-10">
					<h2 class="text-3xl font-serif font-bold text-gray-900">Trending Now</h2>
					<p class="text-gray-600 mt-2 font-light">
						Jewelry pieces everyone's eyeing right now
					</p>
				</div>
				<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
					<div
						v-for="item in trendingItems"
						:key="item.name"
						class="group cursor-pointer"
						@click="openProduct(item)"
					>
						<div class="relative overflow-hidden rounded-2xl aspect-[4/3]">
							<img
								:src="item.image"
								:alt="item.name"
								class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
							/>
						</div>
						<p class="text-center mt-4 text-gray-800 font-medium tracking-wide">
							{{ item.name }}
						</p>
					</div>
				</div>
			</div>
		</section>

		<!-- ======== 6. ZEVAR WORLD (2x2 grid) ======== -->
		<section class="py-16 bg-[#faf5f0]">
			<div class="max-w-6xl mx-auto px-6">
				<div class="text-center mb-10">
					<h2 class="text-3xl font-serif font-bold text-gray-900">Zevar World</h2>
					<p class="text-gray-600 mt-2 font-light">A companion for every occasion</p>
				</div>
				<div class="grid grid-cols-2 gap-5 max-w-4xl mx-auto">
					<div
						v-for="world in zevarWorld"
						:key="world.name"
						class="relative overflow-hidden rounded-2xl aspect-[4/3] cursor-pointer group"
						@click="handleCategorySelect(world.link)"
					>
						<img
							:src="world.image"
							:alt="world.name"
							class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
						/>
						<div
							class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex items-end justify-center pb-6"
						>
							<p
								class="text-white font-serif text-2xl font-light tracking-wide italic"
							>
								{{ world.name }}
							</p>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- ======== 7. NEW ARRIVALS ======== -->
		<section class="py-16 bg-[#e8ddd0] relative overflow-hidden">
			<img
				src="https://images.unsplash.com/photo-1601121141461-9d6647bca1ed?w=1920&q=60"
				class="absolute inset-0 w-full h-full object-cover opacity-30"
			/>
			<div class="relative max-w-6xl mx-auto px-6">
				<div class="mb-8">
					<h2 class="text-3xl font-serif font-bold text-gray-900">New Arrivals</h2>
					<span
						class="inline-block ml-3 px-3 py-1 bg-[#8B6914] text-white text-xs font-bold rounded-full"
						>100+ New Items</span
					>
					<p class="text-gray-700 mt-2 font-light">
						Fresh designs dropping daily. Explore the latest launches.
					</p>
				</div>
				<div class="grid grid-cols-2 md:grid-cols-4 gap-5">
					<div
						v-for="item in newArrivals"
						:key="item.name"
						class="group cursor-pointer"
						@click="openProduct(item)"
					>
						<div
							class="relative overflow-hidden rounded-2xl aspect-square bg-white shadow-md"
						>
							<img
								:src="item.image"
								:alt="item.name"
								class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
							/>
							<div
								class="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/50 to-transparent p-4"
							>
								<p class="text-white font-semibold text-sm">{{ item.name }}</p>
							</div>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- ======== 8. TRUST BADGES ======== -->
		<section class="py-14 bg-white border-t border-gray-100">
			<div class="max-w-5xl mx-auto px-6">
				<div class="grid grid-cols-2 md:grid-cols-4 gap-8">
					<div
						v-for="badge in trustBadges"
						:key="badge.title"
						class="flex flex-col items-center text-center gap-3"
					>
						<div
							class="w-16 h-16 rounded-full bg-[#faf5f0] flex items-center justify-center"
						>
							<svg
								class="w-7 h-7 text-[#8B6914]"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="1.5"
									:d="badge.icon"
								/>
							</svg>
						</div>
						<div>
							<p class="font-bold text-gray-900 text-sm">{{ badge.title }}</p>
							<p class="text-gray-500 text-xs mt-0.5 font-light">{{ badge.sub }}</p>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- ======== 9. CURATED FOR YOU (Gender) ======== -->
		<section class="py-16 bg-white">
			<div class="max-w-6xl mx-auto px-6">
				<div class="text-center mb-10">
					<h2 class="text-3xl font-serif font-bold text-gray-900">Curated For You</h2>
					<p class="text-[#8B6914] mt-2 font-semibold tracking-wide">Shop By Style</p>
				</div>
				<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
					<div
						v-for="g in genderShop"
						:key="g.name"
						class="group cursor-pointer"
						@click="handleCategorySelect(g.link)"
					>
						<div class="relative overflow-hidden rounded-2xl aspect-[3/4]">
							<img
								:src="g.image"
								:alt="g.name"
								class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
							/>
							<div
								class="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent flex items-end justify-center pb-6"
							>
								<p class="text-white font-serif text-2xl font-light tracking-wide">
									{{ g.name }}
								</p>
							</div>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- ======== 10. ZEVAR EXPERIENCE ======== -->
		<section class="py-16 bg-[#faf5f0]">
			<div class="max-w-6xl mx-auto px-6">
				<div class="text-center mb-10">
					<h2 class="text-3xl font-serif font-bold text-gray-900">
						The Zevar Experience
					</h2>
					<p class="text-gray-600 mt-2 font-light">
						Find a Boutique or Book a Consultation
					</p>
				</div>
				<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
					<div v-for="exp in experiences" :key="exp.title" class="group cursor-pointer">
						<div class="relative overflow-hidden rounded-2xl aspect-[4/3]">
							<img
								:src="exp.image"
								:alt="exp.title"
								class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
							/>
						</div>
						<p
							class="text-center mt-4 text-gray-800 font-bold uppercase tracking-wider text-sm"
						>
							{{ exp.title }}
						</p>
					</div>
				</div>
			</div>
		</section>

		<!-- ======== 11. PARTNER COLLECTIONS (with toggle) ======== -->
		<section
			class="py-16 border-t"
			:class="isDark ? 'bg-[#1e1e24] border-white/5' : 'bg-white border-gray-100'"
		>
			<div class="max-w-6xl mx-auto px-8">
				<div class="flex items-center justify-between mb-10">
					<div>
						<h2 class="text-3xl font-serif font-bold tracking-wide">
							Partner Collections
						</h2>
						<p
							class="mt-2 font-light tracking-wide"
							:class="isDark ? 'text-gray-400' : 'text-gray-500'"
						>
							Curated from our trusted partners
						</p>
					</div>
					<button
						@click="showPartners = !showPartners"
						class="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-bold transition-all"
						:class="
							showPartners
								? 'bg-[#8B6914] text-white shadow-lg'
								: isDark
								? 'bg-white/10 text-gray-300 hover:bg-white/15'
								: 'bg-gray-100 text-gray-600 hover:bg-gray-200'
						"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
							/>
						</svg>
						{{ showPartners ? 'Hide Partners' : 'Show Partners' }}
					</button>
				</div>

				<Transition name="partner-fade">
					<div v-if="showPartners">
						<div class="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
							<div
								v-for="partner in partnerBrands"
								:key="partner.name"
								class="flex flex-col items-center gap-3 p-6 rounded-2xl border transition-all cursor-pointer group"
								:class="
									isDark
										? 'border-white/5 hover:border-[#C9A962]/40 bg-[#111]'
										: 'border-gray-100 hover:border-[#C9A962] bg-gray-50 hover:bg-[#faf5f0]'
								"
								@click="openPartner(partner)"
							>
								<div
									class="w-16 h-16 rounded-xl flex items-center justify-center text-2xl font-serif font-bold"
									:class="
										isDark
											? 'bg-white/5 text-[#C9A962]'
											: 'bg-white text-[#8B6914] shadow-sm'
									"
								>
									{{ partner.initial }}
								</div>
								<p class="font-bold text-sm tracking-wide">{{ partner.name }}</p>
								<p
									class="text-xs font-light text-center"
									:class="isDark ? 'text-gray-500' : 'text-gray-400'"
								>
									{{ partner.desc }}
								</p>
							</div>
						</div>
						<div class="text-center">
							<p
								class="text-xs font-light"
								:class="isDark ? 'text-gray-600' : 'text-gray-400'"
							>
								Partner items are sourced from verified suppliers. Pricing and
								availability may vary.
							</p>
						</div>
					</div>
				</Transition>
			</div>
		</section>

		<!-- ======== 12. FOOTER ======== -->
		<footer
			v-if="!isEmbedded"
			class="pt-16 pb-8"
			:class="isDark ? 'bg-black' : 'bg-[#1a0f08]'"
			style="color: white"
		>
			<div class="max-w-6xl mx-auto px-6">
				<div class="grid grid-cols-1 md:grid-cols-4 gap-10 mb-12">
					<!-- Brand -->
					<div>
						<div class="flex items-center gap-3 mb-4">
							<div
								class="w-10 h-10 rounded-lg flex items-center justify-center"
								style="background: linear-gradient(135deg, #c9a962, #8b7355)"
							>
								<span class="text-white font-serif font-bold text-lg">Z</span>
							</div>
							<span class="font-serif font-bold text-2xl tracking-tight">ZEVAR</span>
						</div>
						<p class="text-gray-400 text-sm leading-relaxed font-light">
							Crafting timeless elegance since 1980. Your trusted jeweler for life's
							precious moments.
						</p>
					</div>
					<!-- Quick Links -->
					<div>
						<h4 class="font-bold mb-4 text-[#C9A962]">Quick Links</h4>
						<ul class="space-y-2.5 text-sm text-gray-400 font-light">
							<li>
								<a href="#" class="hover:text-[#C9A962] transition"
									>Delivery Information</a
								>
							</li>
							<li>
								<a href="#" class="hover:text-[#C9A962] transition"
									>Shipping Policy</a
								>
							</li>
							<li>
								<a href="#" class="hover:text-[#C9A962] transition"
									>Payment Options</a
								>
							</li>
							<li>
								<a href="#" class="hover:text-[#C9A962] transition"
									>Track your Order</a
								>
							</li>
							<li>
								<a href="#" class="hover:text-[#C9A962] transition">Returns</a>
							</li>
						</ul>
					</div>
					<!-- Information -->
					<div>
						<h4 class="font-bold mb-4 text-[#C9A962]">Information</h4>
						<ul class="space-y-2.5 text-sm text-gray-400 font-light">
							<li>
								<a href="#" class="hover:text-[#C9A962] transition">Our Story</a>
							</li>
							<li>
								<a href="#" class="hover:text-[#C9A962] transition"
									>Store Locations</a
								>
							</li>
							<li>
								<a href="#" class="hover:text-[#C9A962] transition">Help & FAQs</a>
							</li>
							<li>
								<a href="#" class="hover:text-[#C9A962] transition"
									>Jewelry Care Guide</a
								>
							</li>
							<li>
								<a href="#" class="hover:text-[#C9A962] transition">Size Guide</a>
							</li>
						</ul>
					</div>
					<!-- Contact -->
					<div>
						<h4 class="font-bold mb-4 text-[#C9A962]">Contact Us</h4>
						<p class="text-gray-400 text-sm mb-2 font-light">1-800-ZEVAR-00</p>
						<p class="text-gray-400 text-sm mb-4 font-light">
							hello@zevarjewelers.com
						</p>
						<h4 class="font-bold mb-3 text-[#C9A962]">Follow Us</h4>
						<div class="flex gap-3">
							<a
								v-for="s in ['Instagram', 'Facebook', 'Pinterest']"
								:key="s"
								href="#"
								class="w-9 h-9 rounded-full bg-white/10 flex items-center justify-center hover:bg-[#C9A962] transition text-sm font-bold"
								>{{ s[0] }}</a
							>
						</div>
					</div>
				</div>
				<div
					class="border-t border-white/10 pt-6 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-gray-500 font-light"
				>
					<p>
						&copy; {{ new Date().getFullYear() }} ZEVAR Jewelers. All rights reserved.
					</p>
					<div class="flex gap-6">
						<a href="#" class="hover:text-[#C9A962] transition">Privacy Policy</a>
						<a href="#" class="hover:text-[#C9A962] transition">Terms & Conditions</a>
					</div>
				</div>
			</div>
		</footer>

		<!-- Product Modal -->
		<ProductModal
			:show="showProductModal"
			:item-code="selectedItemCode"
			@close="closeProductModal"
		/>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUIStore } from '@/stores/ui'
import Header from '@/components/Header.vue'
import ProductModal from '@/components/ProductModal.vue'

const props = defineProps({
	isEmbedded: {
		type: Boolean,
		default: false,
	},
})

const router = useRouter()
const route = useRoute()
const ui = useUIStore()
const isDark = computed(() => ui.isDark)
const activeCategory = ref('all')
const showProductModal = ref(false)
const selectedItemCode = ref(null)
const currentSlide = ref(0)
let slideTimer = null

function closeProductModal() {
	showProductModal.value = false
	selectedItemCode.value = null
}

// ---- HERO SLIDES ----
const heroSlides = [
	{
		id: 1,
		image: 'https://images.unsplash.com/photo-1610375461246-83df859d849d?w=1920&q=80',
		overlay:
			'linear-gradient(135deg, rgba(250,245,240,0.92) 0%, rgba(250,245,240,0.6) 50%, transparent 100%)',
		subtitle: 'New Season',
		title: 'Season of<br/><em class="not-italic font-light">Brilliance</em>',
		description: 'Timeless designs that captured hearts — a tribute to elegance and joy.',
		cta: 'Explore Now',
		align: 'left',
	},
	{
		id: 2,
		image: 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=1920&q=80',
		overlay: 'linear-gradient(to right, rgba(0,0,0,0.5), transparent)',
		subtitle: 'Exclusive',
		title: 'Diamonds That<br/><em class="not-italic font-light">Define You</em>',
		description: 'Discover our premium diamond collection crafted for the modern you.',
		cta: 'Shop Diamonds',
		align: 'left',
	},
	{
		id: 3,
		image: 'https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=1920&q=80',
		overlay:
			'linear-gradient(135deg, rgba(250,245,240,0.9) 0%, rgba(250,245,240,0.5) 50%, transparent 100%)',
		subtitle: "Valentine's Edit",
		title: 'Gifts of<br/><em class="not-italic font-light">Love</em>',
		description: 'Celebrate love with handpicked pieces that speak from the heart.',
		cta: 'Shop Gifts',
		align: 'left',
	},
]

// ---- SIGNATURE COLLECTIONS ----
const signatureCollections = [
	{
		name: 'Everyday Diamonds',
		image: 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=500&q=80',
		link: 'diamond',
	},
	{
		name: 'Statement Elegance',
		image: 'https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?w=500&q=80',
		link: 'necklaces',
	},
	{
		name: 'Modern Minimal',
		image: 'https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=500&q=80',
		link: 'pendants',
	},
	{
		name: 'The Gifting Edit',
		image: 'https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=500&q=80',
		link: 'rings',
	},
]

// ---- SHOP CATEGORIES ----
const shopCategories = [
	{
		name: 'Earrings',
		image: 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=400&q=80',
		link: 'earrings',
	},
	{
		name: 'Rings',
		image: 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=400&q=80',
		link: 'rings',
	},
	{
		name: 'Pendants',
		image: 'https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=400&q=80',
		link: 'pendants',
	},
	{
		name: 'Necklaces',
		image: 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=400&q=80',
		link: 'necklaces',
	},
	{
		name: 'Bracelets',
		image: 'https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=400&q=80',
		link: 'bracelets',
	},
	{
		name: 'Bangles',
		image: 'https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=400&q=80',
		link: 'bracelets',
	},
	{
		name: 'Chains',
		image: 'https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?w=400&q=80',
		link: 'chains',
	},
	{
		name: 'View All',
		image: 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=400&q=80',
		link: 'all',
	},
]

// ---- TRENDING ITEMS ----
const trendingItems = [
	{
		name: 'Timeless Classics',
		image: 'https://images.unsplash.com/photo-1601121141461-9d6647bca1ed?w=700&q=80',
		item_code: 'DEMO-T1',
	},
	{
		name: 'Gifting Jewelry',
		image: 'https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=700&q=80',
		item_code: 'DEMO-T2',
	},
	{
		name: 'Drops of Radiance',
		image: 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=700&q=80',
		item_code: 'DEMO-T3',
	},
]

// ---- ZEVAR WORLD ----
const zevarWorld = [
	{
		name: 'Wedding',
		image: 'https://images.unsplash.com/photo-1519741497674-611481863552?w=700&q=80',
		link: 'rings',
	},
	{
		name: 'Diamond',
		image: 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=700&q=80',
		link: 'diamond',
	},
	{
		name: 'Gold',
		image: 'https://images.unsplash.com/photo-1610375461246-83df859d849d?w=700&q=80',
		link: 'gold',
	},
	{
		name: 'Everyday',
		image: 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=700&q=80',
		link: 'all',
	},
]

// ---- NEW ARRIVALS ----
const newArrivals = [
	{
		name: 'Diamond Studs',
		image: 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=500&q=80',
		item_code: 'DEMO-N1',
	},
	{
		name: 'Gold Hoops',
		image: 'https://images.unsplash.com/photo-1617038260897-41a1f14a8ca0?w=500&q=80',
		item_code: 'DEMO-N2',
	},
	{
		name: 'Pearl Collection',
		image: 'https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=500&q=80',
		item_code: 'DEMO-N3',
	},
	{
		name: 'Rose Gold Set',
		image: 'https://images.unsplash.com/photo-1603561596112-0a132b757442?w=500&q=80',
		item_code: 'DEMO-N4',
	},
]

// ---- TRUST BADGES ----
const trustBadges = [
	{
		title: 'Zevar Exchange',
		sub: 'Easy gold exchange policy',
		icon: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15',
	},
	{
		title: 'Purity Guarantee',
		sub: 'BIS hallmarked jewelry',
		icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
	},
	{
		title: 'Transparency',
		sub: 'Complete pricing clarity',
		icon: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z',
	},
	{
		title: 'Lifetime Care',
		sub: 'Free cleaning & maintenance',
		icon: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z',
	},
]

// ---- GENDER SHOP ----
const genderShop = [
	{
		name: 'For Her',
		image: 'https://images.unsplash.com/photo-1617038260897-41a1f14a8ca0?w=600&q=80',
		link: 'all',
	},
	{
		name: 'For Him',
		image: 'https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=600&q=80',
		link: 'chains',
	},
	{
		name: 'Gifts & Sets',
		image: 'https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=600&q=80',
		link: 'all',
	},
]

// ---- ZEVAR EXPERIENCE ----
const experiences = [
	{
		title: 'Visit Our Store',
		image: 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=600&q=80',
	},
	{
		title: 'Book an Appointment',
		image: 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=600&q=80',
	},
	{
		title: 'Talk to an Expert',
		image: 'https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=600&q=80',
	},
]

// ---- PARTNER BRANDS ----
const showPartners = ref(true)
const partnerBrands = [
	{ name: 'QGold', initial: 'Q', desc: 'Premium Gold Collections', url: 'https://qgold.com' },
	{
		name: 'Stuller',
		initial: 'S',
		desc: 'Fine Jewelry & Diamonds',
		url: 'https://www.stuller.com',
	},
	{
		name: 'Blue Nile',
		initial: 'B',
		desc: 'Diamond Specialists',
		url: 'https://www.bluenile.com',
	},
	{ name: 'Zevar In-House', initial: 'Z', desc: 'Our Exclusive Collection', url: '/catalogues' },
]

// ---- CAROUSEL LOGIC ----
function nextSlide() {
	currentSlide.value = (currentSlide.value + 1) % heroSlides.length
}
function prevSlide() {
	currentSlide.value = (currentSlide.value - 1 + heroSlides.length) % heroSlides.length
}
function startAutoSlide() {
	slideTimer = setInterval(nextSlide, 5000)
}
function stopAutoSlide() {
	if (slideTimer) {
		clearInterval(slideTimer)
		slideTimer = null
	}
}

// ---- ACTIONS ----
function handleCategorySelect(id) {
	if (id === 'all') {
		router.push('/catalogues')
	} else {
		router.push(`/catalogues/${id}`)
	}
}

function openProduct(item) {
	selectedItemCode.value = item.item_code
	showProductModal.value = true
}

function scrollTo(id) {
	document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}

function openPartner(partner) {
	if (partner.url.startsWith('http')) {
		window.open(partner.url, '_blank')
	} else {
		router.push(partner.url)
	}
}

function performSearch(q) {
	// Add search logic if needed
}

onMounted(() => {
	startAutoSlide()
})
onUnmounted(() => {
	stopAutoSlide()
})
</script>

<style scoped>
.hero-slide-enter-active,
.hero-slide-leave-active {
	transition: opacity 0.8s ease;
}
.hero-slide-enter-from,
.hero-slide-leave-to {
	opacity: 0;
}

.partner-fade-enter-active,
.partner-fade-leave-active {
	transition: all 0.3s ease;
}
.partner-fade-enter-from,
.partner-fade-leave-to {
	opacity: 0;
	transform: translateY(-10px);
}

.partner-fade-enter-active,
.partner-fade-leave-active {
	transition: all 0.3s ease;
}
.partner-fade-enter-from,
.partner-fade-leave-to {
	opacity: 0;
	transform: translateY(-10px);
}
</style>
