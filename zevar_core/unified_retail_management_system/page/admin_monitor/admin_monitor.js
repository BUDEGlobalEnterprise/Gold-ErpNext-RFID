frappe.pages['admin_monitor'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Live Monitor'),
		single_column: true,
	});

	// Embed the Vue SPA admin monitor page in an iframe
	const base_url = frappe.boot.sitename
		? '/' + frappe.boot.sitename
		: '';

	const iframe = document.createElement('iframe');
	iframe.src = base_url + '/pos/reports/dashboards/admin';
	iframe.style.width = '100%';
	iframe.style.height = 'calc(100vh - 120px)';
	iframe.style.border = 'none';
	iframe.style.marginTop = '-10px';
	iframe.setAttribute('frameborder', '0');

	$(wrapper).find('.layout-main-section').html(iframe);
};
