import frappe
from frappe import _
from frappe.utils import cint, cstr, flt, today, getdate, add_days


@frappe.whitelist(allow_guest=False)
def get_employee_profile():
    employee = frappe.db.get_value(
        "Employee",
        {"user_id": frappe.session.user, "status": "Active"},
        ["name", "employee_name", "employment_type", "department",
         "designation", "company", "date_of_joining", "cell_number",
         "personal_email", "image", "gender"],
        as_dict=True,
    )
    if not employee:
        return {"success": False, "employee": None}

    return {"success": True, "employee": employee}


@frappe.whitelist(allow_guest=False)
def get_leave_applications(status=None, from_date=None, to_date=None, page=1, page_size=20):
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        return {"success": True, "applications": [], "total": 0}

    filters = {"employee": employee, "docstatus": ["!=", 2]}
    if status:
        filters["status"] = status
    if from_date:
        filters["from_date"] = [">=", from_date]
    if to_date:
        filters.setdefault("to_date", ["<=", to_date])

    page = max(1, cint(page))
    page_size = min(100, max(1, cint(page_size)))
    limit_start = (page - 1) * page_size

    applications = frappe.get_all(
        "Leave Application",
        filters=filters,
        fields=[
            "name", "leave_type", "from_date", "to_date",
            "total_leave_days", "half_day", "status",
            "leave_approver", "description", "docstatus",
        ],
        order_by="creation desc",
        limit_start=limit_start,
        limit=page_size,
    )
    total = frappe.db.count("Leave Application", filters)

    return {"success": True, "applications": applications, "total": total, "page": page, "page_size": page_size}


@frappe.whitelist(allow_guest=False)
def get_leave_balance():
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        return {"success": True, "balances": []}

    today_date = getdate()
    year_start = getdate(f"{today_date.year}-01-01")

    allocations = frappe.get_all(
        "Leave Allocation",
        filters={"employee": employee, "docstatus": 1, "from_date": [">=", year_start]},
        fields=["leave_type", "total_leaves_allocated", "new_leaves_allocated"],
    )

    balances = []
    for alloc in allocations:
        taken = flt(frappe.db.get_value(
            "Leave Application",
            {"employee": employee, "leave_type": alloc.leave_type, "status": "Approved", "docstatus": 1},
            "SUM(total_leave_days)",
        ) or 0)
        pending = flt(frappe.db.get_value(
            "Leave Application",
            {"employee": employee, "leave_type": alloc.leave_type, "status": "Open", "docstatus": 0},
            "SUM(total_leave_days)",
        ) or 0)

        balances.append({
            "leave_type": alloc.leave_type,
            "allocated": flt(alloc.total_leaves_allocated),
            "taken": taken,
            "pending": pending,
            "remaining": flt(alloc.total_leaves_allocated) - taken,
        })

    return {"success": True, "balances": balances}


@frappe.whitelist(allow_guest=False)
def apply_leave(leave_type, from_date, to_date, half_day=0, description=None):
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        frappe.throw(_("No employee record found"))

    leave_type = cstr(leave_type).strip()
    if not leave_type:
        frappe.throw(_("Leave type is required"))

    la = frappe.new_doc("Leave Application")
    la.employee = employee
    la.leave_type = leave_type
    la.from_date = from_date
    la.to_date = to_date
    la.half_day = cint(half_day)
    if description:
        la.description = cstr(description).strip()

    la.insert(ignore_permissions=True)

    return {"success": True, "name": la.name, "status": la.status}


@frappe.whitelist(allow_guest=False)
def cancel_leave(name):
    name = cstr(name).strip()
    if not frappe.db.exists("Leave Application", name):
        frappe.throw(_("Leave application not found"))

    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    doc = frappe.get_doc("Leave Application", name)
    if doc.employee != employee:
        frappe.throw(_("You can only cancel your own leave applications"))

    if doc.docstatus == 0:
        doc.delete(ignore_permissions=True)
    elif doc.docstatus == 1:
        doc.cancel()
    else:
        frappe.throw(_("Cannot cancel this leave application"))

    return {"success": True, "name": name}


@frappe.whitelist(allow_guest=False)
def get_leave_types():
    types = frappe.get_all(
        "Leave Type",
        filters={"disabled": 0},
        fields=["name", "is_lwp", "is_carry_forward", "is_compensatory"],
        order_by="name asc",
    )
    return {"success": True, "leave_types": types}


@frappe.whitelist(allow_guest=False)
def get_attendance_calendar(month=None, year=None):
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        return {"success": True, "days": []}

    today_date = getdate()
    month = cint(month) or today_date.month
    year = cint(year) or today_date.year

    import calendar
    _, days_in_month = calendar.monthrange(year, month)
    start = getdate(f"{year}-{month:02d}-01")
    end = getdate(f"{year}-{month:02d}-{days_in_month}")

    attendance = frappe.get_all(
        "Attendance",
        filters={"employee": employee, "attendance_date": ["between", [start, end]], "docstatus": 1},
        fields=["attendance_date", "status", "working_hours", "late_entry", "early_exit"],
    )

    leave_days = frappe.get_all(
        "Leave Application",
        filters={
            "employee": employee,
            "status": "Approved",
            "docstatus": 1,
            "from_date": ["<=", end],
            "to_date": [">=", start],
        },
        fields=["from_date", "to_date", "leave_type", "total_leave_days"],
    )

    days = []
    for d in range(1, days_in_month + 1):
        date = getdate(f"{year}-{month:02d}-{d}")
        day_data = {"date": str(date), "day": d, "status": "unmarked"}

        for att in attendance:
            if str(att.attendance_date) == str(date):
                day_data["status"] = att.status.lower()
                day_data["hours"] = flt(att.working_hours)
                break

        for leave in leave_days:
            ld_start = getdate(leave.from_date)
            ld_end = getdate(leave.to_date)
            if ld_start <= date <= ld_end:
                day_data["status"] = "on_leave"
                day_data["leave_type"] = leave.leave_type
                break

        days.append(day_data)

    return {"success": True, "days": days, "month": month, "year": year, "days_in_month": days_in_month}
