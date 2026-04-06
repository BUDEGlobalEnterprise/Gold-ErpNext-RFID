"""
Helpdesk API - Issue reporting and ticket management
"""

import frappe
from frappe import _
from frappe.utils import now_datetime


def _ensure_mapping(doctype, value, extra_fields=None):
	if not value or not frappe.db.exists("DocType", doctype):
		return False
	if frappe.db.exists(doctype, value):
		return True
	try:
		doc_fields = {"doctype": doctype, "__newname": value}
		if extra_fields:
			doc_fields.update(extra_fields)
		frappe.get_doc(doc_fields).insert(
			ignore_permissions=True,
			ignore_mandatory=True,
		)
		return True
	except Exception:
		frappe.log_error(
			"Helpdesk Mapping Create: {}={}".format(doctype, value),
			frappe.get_traceback(),
		)
		return False


def _field_exists(doctype, fieldname):
	return frappe.db.exists("DocField", {"parent": doctype, "fieldname": fieldname})


def _link_target_exists(doctype, fieldname, value):
	if not _field_exists(doctype, fieldname):
		return False
	field_meta = frappe.get_meta(doctype).get_field(fieldname)
	if not field_meta or field_meta.fieldtype != "Link":
		return True
	return bool(frappe.db.exists(field_meta.options, value))


def _set_if_link_valid(doc_dict, doctype, fieldname, value):
	if not value:
		return
	if _link_target_exists(doctype, fieldname, value):
		doc_dict[fieldname] = value


def _try_create_hd_ticket(subject, description, raised_by, priority, category, extra_fields=None):
	if not frappe.db.exists("DocType", "HD Ticket"):
		return None

	_ensure_mapping(
		"HD Ticket Status",
		"Open",
		{"label_agent": "Open", "label_customer": "Open", "category": "Open"},
	)
	_ensure_mapping("HD Ticket Priority", priority, {"integer_value": 1})
	_ensure_mapping("HD Ticket Type", category)

	ticket_doc = {
		"doctype": "HD Ticket",
		"subject": subject,
		"description": description,
		"raised_by": raised_by,
	}

	_set_if_link_valid(ticket_doc, "HD Ticket", "status", "Open")
	_set_if_link_valid(ticket_doc, "HD Ticket", "priority", priority)
	_set_if_link_valid(ticket_doc, "HD Ticket", "ticket_type", category)

	if extra_fields:
		for field, val in extra_fields.items():
			if _field_exists("HD Ticket", field):
				ticket_doc[field] = val

	ticket = frappe.get_doc(ticket_doc)
	ticket.flags.ignore_permissions = True
	ticket.insert()
	return ticket


def _try_create_issue(subject, description, raised_by, priority, category):
	if not frappe.db.exists("DocType", "Issue"):
		return None

	_ensure_mapping("Issue Priority", priority)
	_ensure_mapping("Issue Type", category)

	issue_doc = {
		"doctype": "Issue",
		"subject": subject,
		"description": description,
		"raised_by": raised_by,
		"status": "Open",
	}

	_set_if_link_valid(issue_doc, "Issue", "priority", priority)
	_set_if_link_valid(issue_doc, "Issue", "issue_type", category)

	issue = frappe.get_doc(issue_doc)
	issue.flags.ignore_permissions = True
	issue.insert()
	return issue


def _create_todo_fallback(subject, full_description, category, assigned_to):
	allocated_to = assigned_to or "Administrator"
	try:
		hr_user = frappe.db.get_value("Has Role", {"role": "HR Manager", "parenttype": "User"}, "parent")
		if hr_user:
			allocated_to = hr_user
	except Exception:
		pass

	todo = frappe.get_doc(
		{
			"doctype": "ToDo",
			"description": "[{}] {}\n\n{}".format(category, subject, full_description),
			"allocated_to": allocated_to,
			"status": "Open",
			"date": frappe.utils.today(),
		}
	)
	todo.flags.ignore_permissions = True
	todo.insert()
	return todo


@frappe.whitelist()
def create_support_ticket(
	subject: str,
	description: str,
	category: str = "Other",
	sub_category: str | None = None,
	priority: str = "Medium",
	department: str | None = None,
	reference_type: str | None = None,
	reference_name: str | None = None,
):
	if not subject:
		frappe.throw(_("Subject is required"))
	if not description:
		frappe.throw(_("Description is required"))

	employee = frappe.db.get_value(
		"Employee",
		{"user_id": frappe.session.user},
		["name", "employee_name", "department", "designation", "reports_to"],
		as_dict=True,
	)

	manager_user_id = None
	if employee and employee.get("reports_to"):
		manager_user_id = frappe.db.get_value("Employee", {"name": employee.reports_to}, "user_id")

	assigned_to = manager_user_id
	if department:
		dept_user = frappe.db.get_value(
			"Employee",
			{"department": department, "status": "Active"},
			"user_id",
			order_by="creation desc",
		)
		if dept_user:
			assigned_to = dept_user

	reporter = employee.employee_name if employee else frappe.session.user
	emp_id = employee.name if employee else "N/A"
	emp_dept = employee.department if employee else "N/A"
	dt_str = now_datetime().strftime("%Y-%m-%d %H:%M:%S")

	context_info = (
		"**Reported by:** {}\n"
		"**Employee ID:** {}\n"
		"**Employee Department:** {}\n"
		"**Category:** {}\n"
		"**Sub-Category:** {}\n"
		"**Priority:** {}\n"
		"**Responsible Department:** {}\n"
		"**Date/Time:** {}"
	).format(
		reporter,
		emp_id,
		emp_dept,
		category,
		sub_category or "N/A",
		priority,
		department or "N/A",
		dt_str,
	)

	if reference_type and reference_name:
		context_info += "\n**Related {}:** {}".format(reference_type, reference_name)

	full_description = ("{}\n\n---\n\n**Issue Description:**\n\n{}").format(context_info, description)

	ticket = None
	try:
		ticket = _try_create_hd_ticket(
			subject,
			full_description,
			frappe.session.user,
			priority,
			category,
			{
				"custom_category": category,
				"custom_sub_category": sub_category or "",
				"custom_department": department or "",
			},
		)
	except Exception:
		frappe.log_error("HD Ticket Create Failed", frappe.get_traceback())

	if ticket:
		return {
			"success": True,
			"ticket_id": ticket.name,
			"message": _("Ticket {0} created successfully").format(ticket.name),
			"helpdesk_installed": True,
		}

	issue = None
	try:
		issue = _try_create_issue(
			subject,
			full_description,
			frappe.session.user,
			priority,
			category,
		)
	except Exception:
		frappe.log_error("Issue Create Failed", frappe.get_traceback())

	if issue:
		if assigned_to:
			try:
				todo = frappe.get_doc(
					{
						"doctype": "ToDo",
						"reference_type": "Issue",
						"reference_name": issue.name,
						"description": "[{}] {}".format(category, subject),
						"allocated_to": assigned_to,
						"status": "Open",
					}
				)
				todo.flags.ignore_permissions = True
				todo.insert()
			except Exception:
				pass
		return {
			"success": True,
			"ticket_id": issue.name,
			"message": _("Issue {0} created successfully").format(issue.name),
			"helpdesk_installed": False,
		}

	todo = _create_todo_fallback(subject, full_description, category, assigned_to)
	return {
		"success": True,
		"ticket_id": todo.name,
		"message": _("Your issue has been reported. A ToDo has been created."),
		"helpdesk_installed": False,
	}


@frappe.whitelist()
def get_support_categories():
	return [
		{
			"value": "Customer Issue",
			"label": "Customer Issue",
			"department": "Customer Service",
			"sub_categories": [
				{"value": "Return Request", "label": "Return Request"},
				{"value": "Exchange Request", "label": "Exchange Request"},
				{"value": "Complaint", "label": "Complaint"},
				{"value": "Billing Dispute", "label": "Billing Dispute"},
				{"value": "Layaway Issue", "label": "Layaway Issue"},
				{"value": "Gift Card Issue", "label": "Gift Card Issue"},
			],
		},
		{
			"value": "Jewelry Issue",
			"label": "Jewelry Issue",
			"department": "Quality Control",
			"sub_categories": [
				{"value": "Quality Defect", "label": "Quality Defect"},
				{"value": "Sizing Issue", "label": "Sizing Issue"},
				{"value": "Damage", "label": "Damage"},
				{"value": "Missing Stones", "label": "Missing Stones"},
				{"value": "Hallmark Issue", "label": "Hallmark Issue"},
			],
		},
		{
			"value": "Vendor Issue",
			"label": "Vendor Issue",
			"department": "Procurement",
			"sub_categories": [
				{"value": "Late Delivery", "label": "Late Delivery"},
				{"value": "Quality Problem", "label": "Quality Problem"},
				{"value": "Wrong Item", "label": "Wrong Item"},
				{"value": "Pricing Dispute", "label": "Pricing Dispute"},
			],
		},
		{
			"value": "Employee Issue",
			"label": "Employee Issue",
			"department": "Human Resources",
			"sub_categories": [
				{"value": "Attendance", "label": "Attendance"},
				{"value": "Payroll", "label": "Payroll"},
				{"value": "Leave", "label": "Leave"},
				{"value": "Manager", "label": "Manager"},
			],
		},
		{
			"value": "Store Issue",
			"label": "Store Issue",
			"department": "Operations",
			"sub_categories": [
				{"value": "Equipment", "label": "Equipment"},
				{"value": "Security", "label": "Security"},
				{"value": "Inventory", "label": "Inventory"},
				{"value": "POS System", "label": "POS System"},
			],
		},
		{
			"value": "Technical",
			"label": "Technical / IT",
			"department": "IT Support",
			"sub_categories": [],
		},
		{
			"value": "Other",
			"label": "Other",
			"department": "General",
			"sub_categories": [],
		},
	]


@frappe.whitelist()
def get_responsible_departments():
	departments = frappe.get_all(
		"Department",
		filters={"is_group": 0},
		fields=["name", "department_name"],
		order_by="name",
	)

	result = []
	for dept in departments:
		manager = frappe.db.get_value(
			"Employee",
			{"department": dept.name, "designation": "Manager"},
			["user_id", "employee_name"],
			as_dict=True,
		)
		result.append(
			{
				"value": dept.name,
				"label": dept.department_name or dept.name,
				"manager": manager.employee_name if manager else None,
				"manager_email": manager.user_id if manager else None,
			}
		)

	return result


@frappe.whitelist()
def create_attendance_issue(
	subject: str,
	description: str,
	issue_type: str = "Attendance",
	priority: str = "Medium",
):
	if not subject:
		frappe.throw(_("Subject is required"))
	if not description:
		frappe.throw(_("Description is required"))

	employee = frappe.db.get_value(
		"Employee",
		{"user_id": frappe.session.user},
		["name", "employee_name", "department", "designation", "reports_to"],
		as_dict=True,
	)

	manager_user_id = None
	if employee and employee.get("reports_to"):
		manager_user_id = frappe.db.get_value("Employee", {"name": employee.reports_to}, "user_id")

	reporter = employee.employee_name if employee else frappe.session.user
	emp_id = employee.name if employee else "N/A"
	emp_dept = employee.department if employee else "N/A"
	emp_desig = employee.designation if employee else "N/A"
	dt_str = now_datetime().strftime("%Y-%m-%d %H:%M:%S")

	full_description = (
		"**Reported by Employee:** {}\n"
		"**Employee ID:** {}\n"
		"**Department:** {}\n"
		"**Designation:** {}\n"
		"**Date/Time:** {}\n\n---\n\n"
		"**Issue Description:**\n\n{}"
	).format(reporter, emp_id, emp_dept, emp_desig, dt_str, description)

	ticket = None
	try:
		ticket = _try_create_hd_ticket(
			subject,
			full_description,
			frappe.session.user,
			priority,
			issue_type,
		)
	except Exception:
		frappe.log_error("HD Ticket Create Failed (attendance)", frappe.get_traceback())

	if ticket:
		return {
			"success": True,
			"ticket_id": ticket.name,
			"message": _("Ticket {0} created successfully").format(ticket.name),
			"helpdesk_installed": True,
		}

	issue = None
	try:
		issue = _try_create_issue(
			subject,
			full_description,
			frappe.session.user,
			priority,
			issue_type,
		)
	except Exception:
		frappe.log_error("Issue Create Failed (attendance)", frappe.get_traceback())

	if issue:
		if manager_user_id:
			try:
				todo = frappe.get_doc(
					{
						"doctype": "ToDo",
						"reference_type": "Issue",
						"reference_name": issue.name,
						"description": "New issue assigned: {}".format(subject),
						"allocated_to": manager_user_id,
						"status": "Open",
					}
				)
				todo.flags.ignore_permissions = True
				todo.insert()
			except Exception:
				pass
		return {
			"success": True,
			"ticket_id": issue.name,
			"message": _("Issue {0} created successfully").format(issue.name),
			"helpdesk_installed": False,
		}

	todo = _create_todo_fallback(subject, full_description, issue_type, manager_user_id)
	return {
		"success": True,
		"ticket_id": todo.name,
		"message": _("Your issue has been reported. A ToDo has been created for HR."),
		"helpdesk_installed": False,
	}


@frappe.whitelist()
def get_employee_tickets(status: str | None = None, limit: int = 50):
	tickets = []
	user = frappe.session.user

	if frappe.db.exists("DocType", "HD Ticket"):
		filters = {"raised_by": user}
		if status:
			filters["status"] = status

		hd_tickets = frappe.get_all(
			"HD Ticket",
			filters=filters,
			fields=[
				"name",
				"subject",
				"status",
				"priority",
				"ticket_type",
				"creation",
				"modified",
				"resolution_details",
			],
			order_by="creation desc",
			limit=limit,
		)

		for t in hd_tickets:
			tickets.append(
				{
					"name": t.name,
					"subject": t.subject,
					"status": t.status,
					"priority": t.priority,
					"issue_type": t.ticket_type,
					"category": t.ticket_type,
					"creation": str(t.creation),
					"modified": str(t.modified),
					"resolution": t.resolution_details,
					"source": "helpdesk",
				}
			)

	if frappe.db.exists("DocType", "Issue"):
		filters = {"raised_by": user}
		if status:
			filters["status"] = status

		issues = frappe.get_all(
			"Issue",
			filters=filters,
			fields=[
				"name",
				"subject",
				"status",
				"priority",
				"issue_type",
				"creation",
				"modified",
				"resolution_details",
			],
			order_by="creation desc",
			limit=limit,
		)

		for i in issues:
			tickets.append(
				{
					"name": i.name,
					"subject": i.subject,
					"status": i.status,
					"priority": i.priority,
					"issue_type": i.issue_type,
					"category": i.issue_type,
					"creation": str(i.creation),
					"modified": str(i.modified),
					"resolution": i.resolution_details,
					"source": "issue",
				}
			)

	tickets.sort(key=lambda x: x["creation"], reverse=True)
	return tickets[:limit]


@frappe.whitelist()
def get_ticket_details(ticket_id: str):
	if frappe.db.exists("DocType", "HD Ticket") and frappe.db.exists("HD Ticket", ticket_id):
		ticket = frappe.get_doc("HD Ticket", ticket_id)
		if ticket.raised_by != frappe.session.user:
			frappe.throw(_("You can only view your own tickets"))
		return {
			"name": ticket.name,
			"subject": ticket.subject,
			"description": ticket.description,
			"status": ticket.status,
			"priority": ticket.priority,
			"issue_type": ticket.ticket_type,
			"creation": str(ticket.creation),
			"modified": str(ticket.modified),
			"resolution": ticket.resolution_details,
			"source": "helpdesk",
		}

	if frappe.db.exists("Issue", ticket_id):
		issue = frappe.get_doc("Issue", ticket_id)
		if issue.raised_by != frappe.session.user:
			frappe.throw(_("You can only view your own tickets"))
		return {
			"name": issue.name,
			"subject": issue.subject,
			"description": issue.description,
			"status": issue.status,
			"priority": issue.priority,
			"issue_type": issue.issue_type,
			"creation": str(issue.creation),
			"modified": str(issue.modified),
			"resolution": issue.resolution_details,
			"source": "issue",
		}

	frappe.throw(_("Ticket not found"))


@frappe.whitelist()
def add_ticket_reply(ticket_id: str, message: str):
	if not message:
		frappe.throw(_("Message is required"))

	if frappe.db.exists("DocType", "HD Ticket") and frappe.db.exists("HD Ticket", ticket_id):
		ticket = frappe.get_doc("HD Ticket", ticket_id)
		if ticket.raised_by != frappe.session.user:
			frappe.throw(_("You can only reply to your own tickets"))
		frappe.get_doc(
			{
				"doctype": "Comment",
				"comment_type": "Comment",
				"reference_doctype": "HD Ticket",
				"reference_name": ticket_id,
				"content": message,
				"comment_email": frappe.session.user,
			}
		).insert(ignore_permissions=True)
		return {"success": True, "message": _("Reply added successfully")}

	if frappe.db.exists("Issue", ticket_id):
		issue = frappe.get_doc("Issue", ticket_id)
		if issue.raised_by != frappe.session.user:
			frappe.throw(_("You can only reply to your own tickets"))
		frappe.get_doc(
			{
				"doctype": "Comment",
				"comment_type": "Comment",
				"reference_doctype": "Issue",
				"reference_name": ticket_id,
				"content": message,
				"comment_email": frappe.session.user,
			}
		).insert(ignore_permissions=True)
		return {"success": True, "message": _("Reply added successfully")}

	frappe.throw(_("Ticket not found"))


@frappe.whitelist()
def get_issue_types():
	return [
		{"value": "Attendance", "label": "Attendance Issue"},
		{"value": "Manager", "label": "Manager/Escalation"},
		{"value": "Payroll", "label": "Payroll/Salary"},
		{"value": "Leave", "label": "Leave Request Issue"},
		{"value": "Other", "label": "Other"},
	]


@frappe.whitelist()
def get_ticket_stats():
	stats = {"total": 0, "open": 0, "closed": 0, "pending": 0}
	user = frappe.session.user

	if frappe.db.exists("DocType", "HD Ticket"):
		hd_stats = frappe.db.sql(
			"""
            SELECT status, COUNT(*) as count
            FROM `tabHD Ticket`
            WHERE raised_by = %s
            GROUP BY status
        """,
			(user,),
			as_dict=True,
		)
		for s in hd_stats:
			stats["total"] += s.count
			if s.status in ["Open", "Replied"]:
				stats["open"] += s.count
			elif s.status in ["Resolved", "Closed"]:
				stats["closed"] += s.count
			else:
				stats["pending"] += s.count

	if frappe.db.exists("DocType", "Issue"):
		issue_stats = frappe.db.sql(
			"""
            SELECT status, COUNT(*) as count
            FROM `tabIssue`
            WHERE raised_by = %s
            GROUP BY status
        """,
			(user,),
			as_dict=True,
		)
		for s in issue_stats:
			stats["total"] += s.count
			if s.status in ["Open"]:
				stats["open"] += s.count
			elif s.status in ["Closed", "Resolved"]:
				stats["closed"] += s.count
			else:
				stats["pending"] += s.count

	return stats
