const TROY_OZ_GRAMS = 31.1035;
const metalPriority = { "Yellow Gold": 1, Gold: 1, Silver: 2 };
const purityPriority = {
	"22Kt": 100,
	"18Kt": 90,
	"14Kt": 80,
	"10Kt": 70,
	"999 Fine": 60,
	"925 Sterling": 50,
};

const rates = {
	"Silver-925 Sterling": 2.19,
	"Silver-999 Fine": 2.37,
	"Yellow Gold-10Kt": 62.05,
	"Yellow Gold-14Kt": 87.04,
	"Yellow Gold-18Kt": 111.59,
	"Yellow Gold-22Kt": 136.29,
	"Yellow Gold-24Kt": 148.64,
};

function formatShortLabel(key) {
	if (!key || key === "null") return "";
	if (key.startsWith("Silver-")) {
		const purity = key.split("-")[1] || "";
		return `SILVER ${purity.toUpperCase()}`;
	}
	const parts = key.split("-");
	if (parts.length >= 2) return `GOLD ${parts[1].toUpperCase().replace("KT", "K")}`;
	return key.toUpperCase();
}

const sortedRates = Object.entries(rates)
	.filter(
		([key, rate]) =>
			key &&
			key !== "null" &&
			rate &&
			!key.includes("Platinum") &&
			!key.toLowerCase().includes("24k")
	)
	.sort((a, b) => {
		const [metalA, purityA] = a[0].split("-");
		const [metalB, purityB] = b[0].split("-");
		const mPA = metalPriority[metalA] || 99;
		const mPB = metalPriority[metalB] || 99;
		if (mPA !== mPB) return mPA - mPB;
		const pPA = purityPriority[purityA] || 0;
		const pPB = purityPriority[purityB] || 0;
		return pPB - pPA;
	})
	.map(([key, ratePerGram]) => {
		const perOz = (ratePerGram * TROY_OZ_GRAMS).toFixed(2);
		return [
			key,
			Number(perOz).toLocaleString("en-US", {
				minimumFractionDigits: 2,
				maximumFractionDigits: 2,
			}),
		];
	});

console.log("Sorted Rates:");
console.log(JSON.stringify(sortedRates, null, 2));

sortedRates.forEach(([key, rate]) => {
	console.log(`${formatShortLabel(key)}: ${rate}`);
});
