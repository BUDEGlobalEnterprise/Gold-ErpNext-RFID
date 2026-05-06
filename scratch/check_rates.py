import frappe

frappe.init(site="zevar.localhost")
frappe.connect()

count = frappe.db.count("Gold Rate Log")
print(f"Total records: {count}")

latest = frappe.get_all(
	"Gold Rate Log",
	filters={"metal": "Yellow Gold", "purity": "18Kt"},
	fields=["name", "rate_per_gram", "timestamp"],
	order_by="timestamp desc",
	limit=2,
)
for l in latest:
	print(f"Entry: {l.name}, Rate: {l.rate_per_gram}, TS: {l.timestamp}")
