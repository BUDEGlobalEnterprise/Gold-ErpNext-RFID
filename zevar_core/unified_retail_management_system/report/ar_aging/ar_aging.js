// AR Aging Report - Filter setup
frappe.query_fields = [
  {fieldtype: "Date", label: "As of Date", fieldname: "as_of_date"},
  {fieldtype: "Link", options: "Customer", label: "Customer", fieldname: "customer"},
  {fieldtype: "Select", options: "\nActive\nSuspended\nClosed\nCollections", label: "Account Status", fieldname: "status"},
  {fieldtype: "Check", label: "Show Zero Balance", fieldname: "show_zero"},
];
