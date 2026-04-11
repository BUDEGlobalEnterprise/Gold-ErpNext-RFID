<template>
	<div class="h-full flex flex-col gap-10 no-scrollbar overflow-y-auto pb-20">
		<!-- Header Redesigned -->
		<div class="shrink-0 px-2">
			<div class="flex flex-col md:flex-row md:items-end justify-between gap-8">
				<div>
					<h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight leading-none mb-3">Artisan Directory</h1>
					<p class="text-gray-500 font-medium font-sans">Connect with the brilliant minds behind our jewelry atelier.</p>
				</div>
                <div class="flex items-center gap-4">
                    <div class="relative w-80 group">
                        <span class="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 text-lg group-focus-within:text-primary transition-colors">search</span>
                        <input 
                            type="search" 
                            placeholder="Find resonance..." 
                            class="w-full bg-white border border-gray-100 rounded-xl py-3 pl-12 pr-6 text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all shadow-sm placeholder-gray-400"
                        />
                    </div>
                    <button class="px-8 py-3 bg-primary text-white rounded-xl text-[11px] font-black uppercase tracking-[0.2em] shadow-glow-emerald hover:bg-black transition-all">
                        Onboard Member
                    </button>
                </div>
			</div>
		</div>

		<div class="space-y-10">
			<!-- Metrics Row Redesigned -->
			<div class="grid grid-cols-2 lg:grid-cols-4 gap-8">
				<div class="premium-card !p-10 flex flex-col items-center justify-center group hover:bg-emerald-50/30 transition-all">
					<p class="text-[10px] font-black uppercase tracking-[0.3em] text-gray-400 mb-4">Synchronized</p>
					<p class="text-[40px] font-black text-emerald-600 tracking-tighter tabular-nums leading-none">94</p>
				</div>
				<div class="premium-card !p-10 flex flex-col items-center justify-center group hover:bg-blue-50/30 transition-all">
					<p class="text-[10px] font-black uppercase tracking-[0.3em] text-gray-400 mb-4">Collaboration</p>
					<p class="text-[40px] font-black text-blue-600 tracking-tighter tabular-nums leading-none">12</p>
				</div>
				<div class="premium-card !p-10 flex flex-col items-center justify-center group hover:bg-amber-50/30 transition-all">
					<p class="text-[10px] font-black uppercase tracking-[0.3em] text-gray-400 mb-4">Restorative</p>
					<p class="text-[40px] font-black text-amber-600 tracking-tighter tabular-nums leading-none">08</p>
				</div>
				<div class="premium-card !p-10 flex flex-col items-center justify-center group hover:bg-gray-50/30 transition-all">
					<p class="text-[10px] font-black uppercase tracking-[0.3em] text-gray-400 mb-4">Offline</p>
					<p class="text-[40px] font-black text-gray-300 tracking-tighter tabular-nums leading-none">14</p>
				</div>
			</div>

            <!-- Directory Grid Redesigned -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
                <!-- Member Card -->
                <div v-for="member in team" :key="member.id" class="premium-card !p-0 flex flex-col items-center text-center relative overflow-hidden bg-white border-gray-100 shadow-sm hover:shadow-md transition-all group cursor-default">
                    <div class="absolute top-4 right-4">
                        <div class="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-50 border border-emerald-100" v-if="member.status === 'Available'">
                            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                            <span class="text-[8px] font-black uppercase tracking-widest text-emerald-700">Live</span>
                        </div>
                        <div class="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-amber-50 border border-amber-100" v-else>
                            <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                            <span class="text-[8px] font-black uppercase tracking-widest text-amber-700">Busy</span>
                        </div>
                    </div>

                    <div class="p-8 pb-6">
                        <div class="w-24 h-24 rounded-3xl border-4 border-gray-50 p-1 mb-6 mx-auto relative group-hover:scale-105 transition-transform">
                            <div class="w-full h-full rounded-2xl bg-gray-50 flex items-center justify-center text-2xl font-black text-gray-300 group-hover:bg-emerald-50 group-hover:text-primary transition-colors">
                                {{ member.initials }}
                            </div>
                        </div>

                        <h3 class="text-lg font-black text-gray-900 tracking-tight leading-none mb-2">{{ member.name }}</h3>
                        <p class="text-[10px] font-black text-primary uppercase tracking-[0.2em] mb-8">{{ member.role }}</p>

                        <div class="grid grid-cols-2 gap-6 pt-6 border-t border-gray-50">
                            <div class="text-left">
                                <p class="text-[8px] font-black text-gray-400 uppercase tracking-widest mb-1">Guild</p>
                                <p class="text-[11px] font-bold text-gray-900">{{ member.dept }}</p>
                            </div>
                            <div class="text-left">
                                <p class="text-[8px] font-black text-gray-400 uppercase tracking-widest mb-1">Tenure</p>
                                <p class="text-[11px] font-bold text-gray-900">{{ member.joined }}</p>
                            </div>
                        </div>
                    </div>

                    <div class="w-full grid grid-cols-2 border-t border-gray-50">
                        <button class="py-4 text-[10px] font-black uppercase tracking-widest text-gray-400 hover:text-gray-900 hover:bg-gray-50 transition-all border-r border-gray-50">Portfolio</button>
                        <button class="py-4 text-[10px] font-black uppercase tracking-widest text-emerald-600 hover:bg-emerald-50 transition-all">Message</button>
                    </div>
                </div>

                <!-- Expansion Card -->
                <div class="premium-card !p-8 bg-gray-50/50 border-2 border-dashed border-gray-100 flex flex-col items-center justify-center text-center hover:bg-emerald-50 hover:border-primary transition-all group cursor-pointer">
                    <div class="w-16 h-16 rounded-2xl bg-white border border-gray-100 flex items-center justify-center text-gray-300 font-light text-4xl mb-6 group-hover:text-primary transition-colors animate-pulse">
                        <span class="material-symbols-outlined">add</span>
                    </div>
                    <h3 class="text-sm font-black text-gray-900 tracking-widest uppercase mb-2">Expansion</h3>
                    <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest leading-relaxed">Onboard a new artisan</p>
                </div>
            </div>
		</div>
	</div>
</template>

<script setup>
const team = [
	{ id: 1, name: "Alex Rivera", initials: "AR", role: "Sr. Gemologist", dept: "Appraisal", joined: "2022", status: "Available" },
	{ id: 2, name: "Elena Thorne", initials: "ET", role: "Master Craftsman", dept: "Production", joined: "2021", status: "Meeting" },
	{ id: 3, name: "Marcus Vane", initials: "MV", role: "Design Lead", dept: "Creative", joined: "2023", status: "Available" },
    { id: 4, name: "Sofia Chen", initials: "SC", role: "Visualizer", dept: "Creative", joined: "2022", status: "Meeting" },
    { id: 5, name: "Julian Voss", initials: "JV", role: "Store Manager", dept: "Operations", joined: "2020", status: "Available" },
    { id: 6, name: "Lara Croft", initials: "LC", role: "Floor Staff", dept: "Sales", joined: "2024", status: "Available" },
];
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
