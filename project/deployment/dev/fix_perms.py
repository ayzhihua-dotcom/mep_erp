import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    parents = sorted({c.parent for c in frappe.get_all("Custom DocPerm", fields=["parent"], limit=0)})
    print("PARENTS:", parents)
    FULL = dict(read=1, write=1, create=1, delete=1, report=1, export=1, print=1,
                email=1, share=1, submit=1, cancel=1, amend=1)
    for dt in parents:
        rows = frappe.get_all("Custom DocPerm", filters={"parent": dt},
                              fields=["name", "role", "read", "report", "write"])
        for r in rows:
            if r.read and not r.report:
                frappe.db.set_value("Custom DocPerm", r.name, "report", 1, update_modified=False)
        if not any(r.role == "System Manager" for r in rows):
            frappe.get_doc({"doctype": "Custom DocPerm", "parent": dt, "parenttype": "DocType",
                            "parentfield": "permissions", "role": "System Manager", **FULL}).insert(ignore_permissions=True)
            print("ADDED_SM:", dt)
        else:
            print("HAS_SM:", dt)
    frappe.db.commit()
    frappe.clear_cache()
    frappe.set_user("chenzhihua@cb.local")
    gaps = []
    for dt in parents:
        r = frappe.has_permission(dt, "read")
        rp = frappe.has_permission(dt, "report")
        if r is not True or rp is not True:
            gaps.append((dt, r, rp))
    print("REMAINING_GAPS:", gaps)
    from frappe.desk.query_report import run
    try:
        res = run("项目总览", filters={})
        print("REPORT_RUN_OK rows:", len(res.get("result") or []))
    except Exception as e:
        print("REPORT_RUN_ERR:", repr(e))
    sys.exit(0)
main()
