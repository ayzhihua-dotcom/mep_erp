import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    print("PROJECT_COUNT:", frappe.db.count("Project"))
    for p in frappe.get_all("Project", fields=["name", "project_name", "status", "company", "percent_complete", "expected_start_date", "expected_end_date"]):
        print("PROJECT:", p.name, "|", p.project_name, "|", p.status, "|", p.company, "| pct:", p.percent_complete, "|", p.expected_start_date, "->", p.expected_end_date)
    print("TASK_COUNT:", frappe.db.count("Task"))
    for t in frappe.get_all("Task", fields=["name", "subject", "project", "status"], limit=15):
        print("TASK:", t.name, "|", t.subject, "| proj:", t.project, "|", t.status)
    doctypes = ["Material Budget", "Material Commitment", "Design BOM", "Design Change Request",
                "CB Shipment", "CB Shipment Line", "CB Import Case", "CB Import Checklist",
                "CB Import Cost", "Quality Inspection", "Stock Entry", "Purchase Order", "Material Request"]
    for dt in doctypes:
        try:
            meta = frappe.get_meta(dt)
            proj_fields = [f.fieldname for f in meta.fields if f.fieldtype == "Link" and f.options == "Project"]
            cnt = frappe.db.count(dt)
            nonnull = {}
            for pf in proj_fields:
                try:
                    nonnull[pf] = frappe.db.count(dt, {pf: ["is", "set"]})
                except Exception:
                    nonnull[pf] = "?"
            print("LINKPROJ:", dt, "| total:", cnt, "| project_fields:", proj_fields, "| nonnull:", nonnull)
        except Exception as e:
            print("META_ERR:", dt, repr(e))
    for dt in ["Dashboard", "Dashboard Chart", "Number Card", "Report"]:
        try:
            print("COUNT", dt, ":", frappe.db.count(dt))
        except Exception as e:
            print("COUNT_ERR", dt, repr(e))
    sys.exit(0)
main()
