"""
Tasks API - Gameplan integration and personal todos
"""

import frappe
from frappe import _
from frappe.utils import getdate, today


@frappe.whitelist()
def get_employee_tasks(status: str | None = None, limit: int = 50):
	"""
	Get Gameplan tasks assigned to current user.

	Args:
	    status: Filter by status (optional: 'Backlog', 'Todo', 'In Progress', 'Done', 'Canceled')
	    limit: Maximum number of tasks to return

	Returns:
	    List of tasks with details
	"""
	# Check if Gameplan is installed
	if not frappe.db.exists("DocType", "GP Task"):
		return {"tasks": [], "gameplan_installed": False, "message": "Gameplan not installed"}

	user = frappe.session.user

	filters = {"assigned_to": user}
	if status:
		filters["status"] = status

	tasks = frappe.get_all(
		"GP Task",
		filters=filters,
		fields=[
			"name",
			"title",
			"description",
			"status",
			"priority",
			"due_date",
			"project",
			"team",
			"creation",
			"modified",
		],
		order_by="due_date asc, priority desc, creation desc",
		limit=limit,
	)

	if not tasks:
		return {"tasks": [], "gameplan_installed": True, "total": 0}

	# Batch fetch project titles to avoid N+1 queries
	project_ids = list(set(t.project for t in tasks if t.project))
	project_map = {}
	if project_ids:
		projects = frappe.get_all(
			"GP Project", filters={"name": ["in", project_ids]}, fields=["name", "title"]
		)
		project_map = {p.name: p.title for p in projects}

	result = []
	for task in tasks:
		project_name = project_map.get(task.project) if task.project else None

		result.append(
			{
				"id": task.name,
				"title": task.title,
				"description": task.description,
				"status": task.status,
				"priority": task.priority,
				"due_date": str(task.due_date) if task.due_date else None,
				"is_overdue": getdate(task.due_date) < getdate() if task.due_date else False,
				"project_id": task.project,
				"project_name": project_name,
				"team": task.team,
				"url": f"/g/tasks/{task.name}",
				"created": str(task.creation),
				"modified": str(task.modified),
			}
		)

	return {"tasks": result, "gameplan_installed": True, "total": len(result)}


@frappe.whitelist()
def get_task_stats():
	"""
	Get task statistics for current user.

	Returns:
	    Dict with task counts by status
	"""
	if not frappe.db.exists("DocType", "GP Task"):
		return {"gameplan_installed": False}

	user = frappe.session.user

	stats = frappe.db.sql(  # nosemgrep
		"""
        SELECT status, COUNT(*) as count
        FROM `tabGP Task`
        WHERE assigned_to = %s
        GROUP BY status
    """,
		(user,),
		as_dict=True,
	)

	# Get overdue count
	overdue = frappe.db.count(
		"GP Task",
		filters={"assigned_to": user, "due_date": ("<", today()), "status": ("not in", ["Done", "Canceled"])},
	)

	result = {"gameplan_installed": True, "by_status": {}, "total": 0, "overdue": overdue}

	for stat in stats:
		result["by_status"][stat.status] = stat.count
		result["total"] += stat.count

	return result


@frappe.whitelist()
def get_personal_todos(status: str = "Open"):
	"""
	Get personal TODO items for current user.

	Args:
	    status: Filter by status ('Open' or 'Closed')

	Returns:
	    List of TODO items
	"""
	todos = frappe.get_all(
		"ToDo",
		filters={"allocated_to": frappe.session.user, "status": status},
		fields=["name", "description", "date", "priority", "status", "reference_type", "reference_name"],
		order_by="date asc, priority desc",
		limit=50,
		ignore_permissions=True,
	)

	return [
		{
			"id": todo.name,
			"description": todo.description,
			"date": str(todo.date) if todo.date else None,
			"priority": todo.priority,
			"status": todo.status,
			"reference_type": todo.reference_type,
			"reference_name": todo.reference_name,
		}
		for todo in todos
	]


@frappe.whitelist()
def create_personal_todo(description: str, date: str | None = None, priority: str = "Medium"):
	"""
	Create a personal TODO item.

	Args:
	    description: TODO description (required)
	    date: Due date (optional, defaults to today)
	    priority: Priority ('Low', 'Medium', 'High')

	Returns:
	    Dict with success status and TODO id
	"""
	if not description:
		frappe.throw(_("Description is required"))

	todo = frappe.get_doc(
		{
			"doctype": "ToDo",
			"description": description,
			"allocated_to": frappe.session.user,
			"date": date or today(),
			"priority": priority,
			"status": "Open",
		}
	)
	todo.insert(ignore_permissions=True)

	return {"success": True, "todo_id": todo.name, "message": _("TODO created successfully")}


@frappe.whitelist()
def update_todo_status(todo_id: str, status: str = "Closed"):
	"""
	Update TODO status.

	Args:
	    todo_id: TODO document name
	    status: New status ('Open' or 'Closed')

	Returns:
	    Dict with success status
	"""
	todo = frappe.get_doc("ToDo", todo_id)

	# Verify ownership
	if todo.allocated_to != frappe.session.user:
		frappe.throw(_("You can only modify your own TODOs"))

	todo.status = status
	todo.save(ignore_permissions=True)

	return {"success": True, "message": _("TODO updated successfully")}


@frappe.whitelist()
def delete_todo(todo_id: str):
	"""
	Delete a personal TODO item.

	Args:
	    todo_id: TODO document name

	Returns:
	    Dict with success status
	"""
	todo = frappe.get_doc("ToDo", todo_id)

	# Verify ownership
	if todo.allocated_to != frappe.session.user:
		frappe.throw(_("You can only delete your own TODOs"))

	todo.delete(ignore_permissions=True)

	return {"success": True, "message": _("TODO deleted successfully")}


@frappe.whitelist()
def get_recent_activities(limit: int = 20):
	"""
	Get recent task and TODO activities for current user.

	Args:
	    limit: Maximum number of activities to return

	Returns:
	    List of recent activities
	"""
	activities = []

	# Get recent Gameplan tasks
	if frappe.db.exists("DocType", "GP Task"):
		tasks = frappe.get_all(
			"GP Task",
			filters={"assigned_to": frappe.session.user},
			fields=["name", "title", "status", "modified"],
			order_by="modified desc",
			limit=limit // 2,
		)

		for task in tasks:
			activities.append(
				{
					"type": "task",
					"id": task.name,
					"title": task.title,
					"status": task.status,
					"date": str(task.modified),
					"url": f"/g/tasks/{task.name}",
				}
			)

	# Get recent TODOs
	todos = frappe.get_all(
		"TODO",
		filters={"allocated_to": frappe.session.user},
		fields=["name", "description", "status", "modified"],
		order_by="modified desc",
		limit=limit // 2,
	)

	for todo in todos:
		activities.append(
			{
				"type": "todo",
				"id": todo.name,
				"title": todo.description,
				"status": todo.status,
				"date": str(todo.modified),
				"url": None,
			}
		)

	# Sort by date
	activities.sort(key=lambda x: x["date"], reverse=True)

	return activities[:limit]


# =============================================================================
# Gameplan Task Management APIs
# =============================================================================


@frappe.whitelist()
def get_task_detail(task_id: str):
	"""
	Get detailed information about a specific Gameplan task including comments.

	Args:
	    task_id: The GP Task document name

	Returns:
	    Dict with task details and comments
	"""
	if not frappe.db.exists("DocType", "GP Task"):
		return {"gameplan_installed": False, "message": "Gameplan not installed"}

	if not frappe.db.exists("GP Task", task_id):
		frappe.throw(_("Task not found"))

	task = frappe.get_doc("GP Task", task_id)
	user = frappe.session.user

	# Verify access - user must be assigned or owner
	if task.assigned_to != user and task.owner != user:
		# Check if user has Gameplan access
		if not frappe.db.exists("Has Role", {"parent": user, "role": "Gameplan Member"}):
			frappe.throw(_("You don't have permission to view this task"))

	# Get project info
	project_name = None
	if task.project:
		project_name = frappe.db.get_value("GP Project", task.project, "title")

	# Get team info
	team_name = None
	if task.team:
		team_name = frappe.db.get_value("GP Team", task.team, "title")

	# Get comments
	comments = frappe.get_all(
		"GP Comment",
		filters={"reference_doctype": "GP Task", "reference_name": task_id},
		fields=["name", "content", "owner", "creation", "modified"],
		order_by="creation asc",
	)

	# Batch fetch comment authors' info
	if comments:
		owner_ids = list({c.owner for c in comments if c.owner})
		user_info_map = {}
		if owner_ids:
			users = frappe.get_all(
				"User", filters={"name": ("in", owner_ids)}, fields=["name", "full_name", "user_image"]
			)
			user_info_map = {u.name: u for u in users}

		for comment in comments:
			u_info = user_info_map.get(comment.owner) or {}
			comment["author_name"] = u_info.get("full_name") or comment.owner
			comment["author_image"] = u_info.get("user_image")
			comment["created"] = str(comment.creation)
			comment["modified"] = str(comment.modified)

	return {
		"gameplan_installed": True,
		"task": {
			"id": task.name,
			"title": task.title,
			"description": task.description,
			"status": task.status,
			"priority": task.priority,
			"due_date": str(task.due_date) if task.due_date else None,
			"is_overdue": getdate(task.due_date) < getdate() if task.due_date else False,
			"project_id": task.project,
			"project_name": project_name,
			"team_id": task.team,
			"team_name": team_name,
			"assigned_to": task.assigned_to,
			"owner": task.owner,
			"is_completed": task.is_completed,
			"completed_by": task.completed_by,
			"completion_date": str(task.completion_date) if task.completion_date else None,
			"comments_count": task.comments_count or 0,
			"created": str(task.creation),
			"modified": str(task.modified),
		},
		"comments": comments,
	}


@frappe.whitelist()
def update_task_status(task_id: str, status: str):
	"""
	Update the status of a Gameplan task.

	Args:
	    task_id: The GP Task document name
	    status: New status ('Backlog', 'Todo', 'In Progress', 'Done', 'Canceled')

	Returns:
	    Dict with success status and updated task info
	"""
	if not frappe.db.exists("DocType", "GP Task"):
		return {"success": False, "message": "Gameplan not installed"}

	valid_statuses = ["Backlog", "Todo", "In Progress", "Done", "Canceled"]
	if status not in valid_statuses:
		frappe.throw(_("Invalid status. Must be one of: {0}").format(", ".join(valid_statuses)))

	task = frappe.get_doc("GP Task", task_id)
	user = frappe.session.user

	# Verify access
	if task.assigned_to != user and task.owner != user:
		frappe.throw(_("You can only update tasks assigned to you or created by you"))

	task.status = status

	if status == "Done":
		task.is_completed = 1
		task.completed_by = user
		task.completion_date = frappe.utils.now()
	elif task.status == "Done" and status != "Done":
		# Reopening a completed task
		task.is_completed = 0
		task.completed_by = None
		task.completion_date = None

	task.save()

	return {
		"success": True,
		"task_id": task.name,
		"status": task.status,
		"message": _("Task status updated successfully"),
	}


@frappe.whitelist()
def add_task_comment(task_id: str, content: str):
	"""
	Add a comment to a Gameplan task.

	Args:
	    task_id: The GP Task document name
	    content: Comment content (HTML supported)

	Returns:
	    Dict with success status and comment info
	"""
	if not frappe.db.exists("DocType", "GP Task"):
		return {"success": False, "message": "Gameplan not installed"}

	if not frappe.db.exists("GP Task", task_id):
		frappe.throw(_("Task not found"))

	if not content or not content.strip():
		frappe.throw(_("Comment content is required"))

	task = frappe.get_doc("GP Task", task_id)
	user = frappe.session.user

	# Verify access
	if task.assigned_to != user and task.owner != user:
		if not frappe.db.exists("Has Role", {"parent": user, "role": "Gameplan Member"}):
			frappe.throw(_("You don't have permission to comment on this task"))

	comment = frappe.get_doc(
		{
			"doctype": "GP Comment",
			"reference_doctype": "GP Task",
			"reference_name": task_id,
			"content": content,
		}
	)
	comment.insert()

	return {
		"success": True,
		"comment_id": comment.name,
		"author": user,
		"author_name": frappe.db.get_value("User", user, "full_name") or user,
		"created": str(comment.creation),
		"message": _("Comment added successfully"),
	}


@frappe.whitelist()
def get_tasks_by_project(project_id: str | None = None, limit: int = 50):
	"""
	Get tasks grouped by project for the current user.

	Args:
	    project_id: Filter by specific project (optional)
	    limit: Maximum number of tasks per project

	Returns:
	    Dict with projects and their tasks
	"""
	if not frappe.db.exists("DocType", "GP Task"):
		return {"gameplan_installed": False, "projects": []}

	user = frappe.session.user

	# Base filters for user's tasks
	base_filters = {"assigned_to": user}
	if project_id:
		base_filters["project"] = project_id

	# Get all tasks
	tasks = frappe.get_all(
		"GP Task",
		filters=base_filters,
		fields=["name", "title", "status", "priority", "due_date", "project", "team"],
		order_by="project asc, due_date asc",
		limit=limit * 10,  # Get more to group properly
	)

	# Get unique projects
	project_ids = list(set(t.project for t in tasks if t.project))

	# Batch fetch project details to avoid N+1 queries
	projects = {}
	if project_ids:
		project_data = frappe.get_all(
			"GP Project", filters={"name": ["in", project_ids]}, fields=["name", "title"]
		)
		for p in project_data:
			projects[p.name] = {"id": p.name, "title": p.title, "tasks": []}

	# Add "No Project" bucket
	projects[None] = {"id": None, "title": "No Project", "tasks": []}

	# Group tasks by project
	for task in tasks:
		project_key = task.project
		projects[project_key]["tasks"].append(
			{
				"id": task.name,
				"title": task.title,
				"status": task.status,
				"priority": task.priority,
				"due_date": str(task.due_date) if task.due_date else None,
				"is_overdue": getdate(task.due_date) < getdate() if task.due_date else False,
			}
		)

	# Filter out empty projects and convert to list
	result = [p for p in projects.values() if p["tasks"]]

	# Sort by project title
	result.sort(key=lambda x: x["title"] or "zzz")

	return {"gameplan_installed": True, "projects": result[:10]}  # Limit to 10 projects


@frappe.whitelist()
def get_tasks_by_department(limit: int = 50):
	"""
	Get tasks grouped by employee department.

	This maps employees to their departments and shows tasks organized by department.

	Args:
	    limit: Maximum number of tasks to return

	Returns:
	    Dict with departments and their tasks
	"""
	if not frappe.db.exists("DocType", "GP Task"):
		return {"gameplan_installed": False, "departments": []}

	user = frappe.session.user

	# Get current user's employee record
	employee = frappe.db.get_value(
		"Employee", {"user_id": user}, ["name", "department", "employee_name"], as_dict=True
	)

	if not employee:
		return {"gameplan_installed": True, "departments": [], "message": "No employee record found"}

	user_department = employee.department

	# Get all employees in the same department with their user IDs
	dept_employees = frappe.get_all(
		"Employee",
		filters={"department": user_department},
		fields=["user_id", "employee_name"],
	)

	if not dept_employees:
		return {"gameplan_installed": True, "departments": []}

	# Get user IDs
	user_ids = [e.user_id for e in dept_employees if e.user_id]

	# Get tasks for all department members
	tasks = frappe.get_all(
		"GP Task",
		filters={"assigned_to": ["in", user_ids]},
		fields=["name", "title", "status", "priority", "due_date", "project", "assigned_to"],
		order_by="due_date asc",
		limit=limit,
	)

	# Group tasks by assignee
	by_user = {}
	employee_map = {e.user_id: e.employee_name for e in dept_employees}

	for task in tasks:
		assignee = task.assigned_to
		if assignee not in by_user:
			by_user[assignee] = {
				"user_id": assignee,
				"employee_name": employee_map.get(assignee, assignee),
				"tasks": [],
			}

		by_user[assignee]["tasks"].append(
			{
				"id": task.name,
				"title": task.title,
				"status": task.status,
				"priority": task.priority,
				"due_date": str(task.due_date) if task.due_date else None,
				"is_overdue": getdate(task.due_date) < getdate() if task.due_date else False,
				"project": task.project,
			}
		)

	# Sort by employee name
	departments = list(by_user.values())
	departments.sort(key=lambda x: x["employee_name"])

	return {
		"gameplan_installed": True,
		"department_name": user_department,
		"departments": departments,
	}


@frappe.whitelist()
def get_available_projects():
	"""
	Get list of available Gameplan projects for task creation.

	Returns:
	    List of projects
	"""
	if not frappe.db.exists("DocType", "GP Project"):
		return {"gameplan_installed": False, "projects": []}

	projects = frappe.get_all(
		"GP Project",
		filters={},
		fields=["name", "title", "team"],
		order_by="title asc",
	)

	# Batch fetch team titles to avoid N+1 queries
	team_ids = list(set(p.team for p in projects if p.team))
	team_map = {}
	if team_ids:
		teams = frappe.get_all("GP Team", filters={"name": ["in", team_ids]}, fields=["name", "title"])
		team_map = {t.name: t.title for t in teams}

	result = []
	for project in projects:
		team_name = team_map.get(project.team) if project.team else None
		result.append(
			{"id": project.name, "title": project.title, "team_id": project.team, "team_name": team_name}
		)

	return {"gameplan_installed": True, "projects": result}


@frappe.whitelist()
def create_gameplan_task(
	title: str,
	description: str = "",
	project: str | None = None,
	assigned_to: str | None = None,
	due_date: str | None = None,
	priority: str = "Medium",
):
	"""
	Create a new Gameplan task.

	Args:
	    title: Task title (required)
	    description: Task description (optional)
	    project: Project ID (optional)
	    assigned_to: User to assign task to (defaults to current user)
	    due_date: Due date (optional)
	    priority: Priority ('Low', 'Medium', 'High', 'Urgent')

	Returns:
	    Dict with success status and task ID
	"""
	if not frappe.db.exists("DocType", "GP Task"):
		return {"success": False, "message": "Gameplan not installed"}

	if not title:
		frappe.throw(_("Task title is required"))

	valid_priorities = ["Low", "Medium", "High", "Urgent"]
	if priority not in valid_priorities:
		priority = "Medium"

	task = frappe.get_doc(
		{
			"doctype": "GP Task",
			"title": title,
			"description": description,
			"project": project,
			"assigned_to": assigned_to or frappe.session.user,
			"due_date": due_date,
			"priority": priority,
			"status": "Todo",
		}
	)
	task.insert()

	return {"success": True, "task_id": task.name, "message": _("Task created successfully")}
