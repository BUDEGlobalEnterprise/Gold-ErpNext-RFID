frappe.provide("zevar_core.pages.eod_calendar");

zevar_core.pages.eod_calendar = class EODCalendar {
	constructor(wrapper) {
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: "EOD Analytics Calendar",
			single_column: true,
		});

		this.wrapper = $(wrapper);
		this.make();
	}

	make() {
		this.current_year = frappe.datetime.now_date().split("-")[0];
		this.current_month = frappe.datetime.now_date().split("-")[1];
		this.stream = "Jewelry Sale";

		this.page.set_title(`EOD Calendar - ${this.current_year}`);

		this.setup_header();
		this.setup_layout();
		this.fetch_and_render_heatmap();
	}

	setup_header() {
		let me = this;

		this.page.add_field({
			fieldname: "year",
			label: "Year",
			fieldtype: "Select",
			options: [this.current_year, this.current_year - 1, this.current_year - 2],
			default: this.current_year,
			change: function () {
				me.current_year = this.get_value();
				me.page.set_title(`EOD Calendar - ${me.current_year}`);
				me.fetch_and_render_heatmap();
			},
		});

		this.page.add_field({
			fieldname: "month",
			label: "Month",
			fieldtype: "Select",
			options: [
				{ label: "January", value: "01" },
				{ label: "February", value: "02" },
				{ label: "March", value: "03" },
				{ label: "April", value: "04" },
				{ label: "May", value: "05" },
				{ label: "June", value: "06" },
				{ label: "July", value: "07" },
				{ label: "August", value: "08" },
				{ label: "September", value: "09" },
				{ label: "October", value: "10" },
				{ label: "November", value: "11" },
				{ label: "December", value: "12" },
			],
			default: this.current_month,
			change: function () {
				me.current_month = this.get_value();
				me.fetch_and_render_heatmap();
			},
		});

		this.page.add_field({
			fieldname: "stream",
			label: "Stream",
			fieldtype: "Select",
			options: ["Jewelry Sale", "Repair"],
			default: "Jewelry Sale",
			change: function () {
				me.stream = this.get_value();
				me.fetch_and_render_heatmap();
			},
		});
	}

	setup_layout() {
		let template = `
			<div class="row">
				<div class="col-sm-7">
					<div class="panel panel-default">
						<div class="panel-heading">
							<h3 class="panel-title">Sales Heatmap</h3>
						</div>
						<div class="panel-body">
							<div id="heatmap-container" style="min-height: 250px;"></div>
						</div>
					</div>
				</div>
				<div class="col-sm-5">
					<div class="panel panel-info">
						<div class="panel-heading">
							<h3 class="panel-title" id="drilldown-title">Day Drill-down</h3>
						</div>
						<div class="panel-body" id="drilldown-body">
							<p class="text-muted text-center mt-4">Click a day on the calendar to see details.</p>
						</div>
					</div>
				</div>
			</div>
		`;

		$(this.page.body).html(template);
	}

	fetch_and_render_heatmap() {
		let me = this;
		frappe.call({
			method: "zevar_core.api.sales_history.get_daily_sales_heatmap",
			args: {
				year: this.current_year,
				month: this.current_month,
				stream: this.stream,
			},
			callback: function (r) {
				if (r.message) {
					me.render_heatmap(r.message);
				}
			},
		});
	}

	render_heatmap(data) {
		let me = this;
		let container = this.page.body.find("#heatmap-container")[0];
		$(container).empty();

		let datapoints = {};
		data.forEach((d) => {
			// frappe charts heatmap needs unix timestamps in seconds as keys
			let ts = Math.floor(new Date(d.date).getTime() / 1000);
			datapoints[ts] = d.net;
		});

		// Build a start date for the chart (beginning of the selected year/month)
		let startDate = new Date(this.current_year, parseInt(this.current_month) - 1, 1);

		this.chart = new frappe.Chart(container, {
			data: {
				dataPoints: datapoints,
				start: startDate,
				end: new Date(this.current_year, parseInt(this.current_month), 0),
			},
			type: "heatmap",
			colors: ["#ebedf0", "#c6e48b", "#7bc96f", "#239a3b", "#196127"],
			discreteDomains: 0,
			radius: 3,
		});

		// Listen to chart click
		setTimeout(() => {
			$(container)
				.find(".day")
				.on("click", function () {
					let dateStr = $(this).attr("data-date");
					if (dateStr) {
						me.load_day_drilldown(dateStr);
					}
				});
		}, 500);
	}

	load_day_drilldown(date) {
		let me = this;
		this.page.body.find("#drilldown-title").text(`Metrics for ${date}`);
		this.page.body
			.find("#drilldown-body")
			.html('<p class="text-center"><i class="fa fa-spinner fa-spin"></i> Loading...</p>');

		frappe.call({
			method: "zevar_core.api.sales_history.get_day_drilldown",
			args: { date: date },
			callback: function (r) {
				if (r.message) {
					frappe.call({
						method: "zevar_core.api.sales_history.get_yoy_delta",
						args: { date: date },
						callback: function (yoy_res) {
							me.render_drilldown(date, r.message, yoy_res.message);
						},
					});
				}
			},
		});
	}

	render_drilldown(date, data, yoy) {
		let container = this.page.body.find("#drilldown-body");
		container.empty();

		let yoy_color = yoy.delta_pct >= 0 ? "text-success" : "text-danger";
		let yoy_icon = yoy.delta_pct >= 0 ? "fa-arrow-up" : "fa-arrow-down";

		let html = `
			<div class="row text-center mb-4">
				<div class="col-xs-6">
					<h5 class="text-muted mb-1">Net Sales</h5>
					<h3 class="mt-0">${format_currency(data.net_sales)}</h3>
				</div>
				<div class="col-xs-6">
					<h5 class="text-muted mb-1">YoY Delta</h5>
					<h3 class="mt-0 ${yoy_color}">
						<i class="fa ${yoy_icon}"></i> ${Math.abs(yoy.delta_pct).toFixed(1)}%
					</h3>
					<small class="text-muted">vs ${format_currency(yoy.last_year)}</small>
				</div>
			</div>

			<div class="row text-center mb-4 border-top pt-3" style="border-top: 1px solid #eee; padding-top: 15px;">
				<div class="col-xs-6">
					<h5 class="text-muted mb-1">Repairs</h5>
					<h4 class="mt-0">${format_currency(data.repairs)}</h4>
				</div>
				<div class="col-xs-6">
					<h5 class="text-muted mb-1">Layaway Deposits</h5>
					<h4 class="mt-0">${format_currency(data.layaway_deposits)}</h4>
				</div>
			</div>

			<hr>

			<h5>Tender Breakdown</h5>
			<div id="tender-donut-chart" style="height: 200px;"></div>
		`;

		container.html(html);

		// Render donut
		let labels = [];
		let values = [];
		data.tender_breakdown.forEach((t) => {
			labels.push(t.name);
			values.push(flt(t.value));
		});

		if (values.length > 0) {
			new frappe.Chart(container.find("#tender-donut-chart")[0], {
				data: {
					labels: labels,
					datasets: [{ values: values }],
				},
				type: "donut",
				colors: ["#28a745", "#17a2b8", "#ffc107", "#fd7e14", "#6f42c1", "#007bff"],
			});
		} else {
			container
				.find("#tender-donut-chart")
				.html('<p class="text-muted text-center mt-4">No payments recorded</p>');
		}
	}
};

frappe.pages["eod-calendar"].on_page_load = function (wrapper) {
	new zevar_core.pages.eod_calendar(wrapper);
};
