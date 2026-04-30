frappe.provide("zevar.layaway");

(() => {
	if (zevar.layaway._bootstrapped) {
		return;
	}

	const ns = zevar.layaway;
	ns._bootstrapped = true;

	ns.getBody = (page) => $(page.body);

	ns.goToHub = () => {
		frappe.set_route("layaway");
	};

	ns.call = (method, args = {}) => {
		return frappe
			.call({ method, args })
			.then((response) => {
				if (response && response.exc) {
					throw new Error(response.exc);
				}
				return response.message;
			})
			.catch((err) => {
				console.error(`zevar.layaway.call failed: ${method}`, err);
				throw err;
			});
	};

	ns.makeControl = (parent, df, value) => {
		try {
			const control = frappe.ui.form.make_control({
				parent,
				df,
				render_input: true,
			});
			control.refresh();
			if (value !== undefined) {
				control.set_value(value);
			}
			return control;
		} catch (err) {
			console.error("zevar.layaway.makeControl failed:", err);
			parent.innerHTML = `<div class="zevar-la-empty">Field "${
				df.label || df.fieldname
			}" failed to render.</div>`;
			return null;
		}
	};

	ns.toCurrency = (value) => {
		try {
			return format_currency(Number(value || 0));
		} catch {
			return Number(value || 0).toFixed(2);
		}
	};

	ns.escapeHtml = (value) => {
		return String(value == null ? "" : value)
			.replace(/&/g, "&amp;")
			.replace(/</g, "&lt;")
			.replace(/>/g, "&gt;")
			.replace(/"/g, "&quot;")
			.replace(/'/g, "&#39;");
	};

	ns.toUserDate = (value) => {
		if (!value) {
			return "-";
		}
		try {
			return frappe.datetime.str_to_user(value);
		} catch {
			return value;
		}
	};

	ns.statusLabel = (status, isOverdue) => {
		if (isOverdue && !["Cancelled", "Completed"].includes(status)) {
			return __("Overdue");
		}
		return __(status || "Unknown");
	};

	ns.statusTone = (status, isOverdue) => {
		if (isOverdue && !["Cancelled", "Completed"].includes(status)) {
			return "warning";
		}
		if (status === "Completed") {
			return "success";
		}
		if (status === "Cancelled") {
			return "danger";
		}
		return "neutral";
	};

	ns.statusBadge = (status, isOverdue) => {
		const tone = ns.statusTone(status, isOverdue);
		return `<span class="zevar-la-status is-${tone}">${ns.escapeHtml(
			ns.statusLabel(status, isOverdue)
		)}</span>`;
	};

	ns.renderItemsTable = (items = []) => {
		if (!items || !items.length) {
			return '<div class="zevar-la-empty">No items on this contract.</div>';
		}

		const rows = items
			.map(
				(item) => `
				<tr>
					<td>${ns.escapeHtml(item.item_name || item.item_code)}</td>
					<td>${ns.escapeHtml(item.item_code)}</td>
					<td>${ns.escapeHtml(item.qty)}</td>
					<td>${ns.toCurrency(item.rate)}</td>
					<td>${ns.toCurrency(item.amount)}</td>
				</tr>`
			)
			.join("");

		return `
			<table class="table table-bordered zevar-la-table">
				<thead>
					<tr>
						<th>Item</th>
						<th>Code</th>
						<th>Qty</th>
						<th>Rate</th>
						<th>Amount</th>
					</tr>
				</thead>
				<tbody>${rows}</tbody>
			</table>`;
	};

	ns.renderScheduleTable = (schedule = []) => {
		if (!schedule || !schedule.length) {
			return '<div class="zevar-la-empty">No payment schedule available.</div>';
		}

		const rows = schedule
			.map(
				(row) => `
				<tr>
					<td>${ns.toUserDate(row.payment_date)}</td>
					<td>${ns.toCurrency(row.expected_amount)}</td>
					<td>${ns.toCurrency(row.paid_amount)}</td>
					<td>${ns.escapeHtml(row.mode_of_payment || "-")}</td>
					<td>${ns.escapeHtml(row.reference_number || "-")}</td>
					<td>${ns.escapeHtml(row.status)}</td>
				</tr>`
			)
			.join("");

		return `
			<table class="table table-bordered zevar-la-table">
				<thead>
					<tr>
						<th>Due Date</th>
						<th>Expected</th>
						<th>Paid</th>
						<th>Mode</th>
						<th>Reference</th>
						<th>Status</th>
					</tr>
				</thead>
				<tbody>${rows}</tbody>
			</table>`;
	};

	ns.renderSummary = (detail) => {
		if (!detail) {
			return '<div class="zevar-la-empty">No contract details available.</div>';
		}

		return `
			<div class="zevar-la-summary-grid">
				<div class="zevar-la-panel">
					<div class="zevar-la-eyebrow">Customer</div>
					<h3>${ns.escapeHtml(detail.customer_name || detail.customer || "-")}</h3>
					<p>${ns.escapeHtml(detail.customer_contact || "No phone on file")}</p>
					<p>${ns.escapeHtml(detail.customer_id_number || "No ID number")}</p>
				</div>
				<div class="zevar-la-panel">
					<div class="zevar-la-eyebrow">Contract</div>
					<h3>${ns.escapeHtml(detail.layaway_id || "-")}</h3>
					<p>${ns.statusBadge(detail.status, detail.is_overdue)}</p>
					<p>Duration: ${ns.escapeHtml(detail.duration_months || "-")} months</p>
				</div>
				<div class="zevar-la-panel">
					<div class="zevar-la-eyebrow">Financials</div>
					<h3>${ns.toCurrency(detail.balance_amount)}</h3>
					<p>Total: ${ns.toCurrency(detail.total_amount)}</p>
					<p>Paid: ${ns.toCurrency(detail.total_paid || detail.deposit_amount)}</p>
				</div>
			</div>
			<div class="zevar-la-panel zevar-la-stack-gap">
				<div class="zevar-la-eyebrow">Items</div>
				${ns.renderItemsTable(detail.items)}
			</div>
			<div class="zevar-la-panel zevar-la-stack-gap">
				<div class="zevar-la-eyebrow">Payment Schedule</div>
				${ns.renderScheduleTable(detail.payment_schedule)}
			</div>`;
	};

	ns.renderSearchResults = (container, contracts, onSelect) => {
		if (!contracts || !contracts.length) {
			container.innerHTML = '<div class="zevar-la-empty">No matching layaways found.</div>';
			return;
		}

		container.innerHTML = contracts
			.map(
				(contract) => `
				<button type="button" class="zevar-la-result" data-name="${ns.escapeHtml(contract.name)}">
					<div>
						<strong>${ns.escapeHtml(contract.name)}</strong>
						<span>${ns.escapeHtml(contract.customer_name || contract.customer)}</span>
					</div>
					<div>
						${ns.statusBadge(contract.status, contract.is_overdue)}
						<span>${ns.toCurrency(contract.balance_amount)}</span>
					</div>
				</button>`
			)
			.join("");

		Array.from(container.querySelectorAll(".zevar-la-result")).forEach((button) => {
			button.addEventListener("click", () => onSelect(button.dataset.name));
		});
	};

	ns.showLoading = (container, message) => {
		container.innerHTML = `
			<div class="zevar-la-loading">
				<div class="zevar-la-loading-spinner"></div>
				<p>${ns.escapeHtml(message || __("Loading..."))}</p>
			</div>`;
	};

	ns.showError = (container, message) => {
		container.innerHTML = `
			<div class="zevar-la-error">
				<p>${ns.escapeHtml(message || __("An error occurred."))}</p>
			</div>`;
	};
})();
