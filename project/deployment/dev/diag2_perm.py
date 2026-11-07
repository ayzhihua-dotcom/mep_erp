import sys
def main():
    import frappe
    frappe.set_user("chenzhihua@cb.local")
    print("SESSION_USER:", frappe.session.user)
    print("Project report:", frappe.has_permission("Project", "report"))
    print("Report read (type):", frappe.has_permission("Report", "read"))
    try:
        print("Report doc read (项目总览):", frappe.has_permission("Report", "read", "项目总览"))
    except Exception as e:
        print("doc_perm_err", repr(e))
    from frappe.desk.query_report import run
    try:
        res = run("项目总览", filters={})
        print("RUN_OK rows:", len(res.get("result") or []))
    except Exception as e:
        print("RUN_ERR:", repr(e))
    cdps = frappe.get_all("Custom DocPerm", fields=["parent", "role", "read", "report", "write"], limit=0)
    parents = sorted({c.parent for c in cdps})
    print("CUSTOM_DOCPERM_PARENT_COUNT:", len(parents))
    gaps = []
    for dt in parents:
        try:
            r = frappe.has_permission(dt, "read")
            rp = frappe.has_permission(dt, "report")
        except Exception as e:
            r = rp = "ERR:" + repr(e)[:50]
        if r is not True or rp is not True:
            gaps.append((dt, r, rp))
    print("PERM_GAPS:", gaps)
    sys.exit(0)
main()
