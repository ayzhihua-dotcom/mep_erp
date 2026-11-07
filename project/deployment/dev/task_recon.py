import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    meta = frappe.get_meta("Task")
    want = ["subject", "project", "status", "priority", "progress", "exp_start_date", "exp_end_date",
            "expected_time", "is_milestone", "parent_task", "task_weight", "description", "type"]
    present = {}
    for w in want:
        f = meta.get_field(w)
        present[w] = (f.fieldtype if f else None, (f.options[:60] if f and f.options and f.fieldtype == "Select" else None))
    print("TASK_FIELDS:", present)
    print("TASK_STATUS_OPTIONS:", (meta.get_field("status").options if meta.get_field("status") else None))
    print("TASK_COUNT:", frappe.db.count("Task"))
    print("KANBAN_BOARDS:", frappe.get_all("Kanban Board", fields=["name", "reference_doctype", "field_name"]))
    print("PROJECTS:", frappe.get_all("Project", fields=["name", "project_name", "expected_start_date", "expected_end_date", "status"]))
    ws = frappe.get_doc("Workspace", "CB 机电总控")
    print("WS_LINKS:", [(l.type, l.label, l.link_to, l.link_type) for l in ws.links])
    sys.exit(0)
main()
