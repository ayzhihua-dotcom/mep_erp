# -*- coding: utf-8 -*-
WS = "巴西机电ERP系统测试"


def run():
    import frappe
    frappe.set_user("Administrator")
    from frappe.desk.doctype.dock.dock import resolve_app_dock, get_site_dock

    for app in ("frappe", "erpnext"):
        rail = resolve_app_dock(app)
        print("==", app, "site_rows:", len(get_site_dock(app)))
        for e in rail:
            print("   ", e.get("link_type"), e.get("link_to") or e.get("url"), "|", e.get("title"), "| hidden", e.get("hidden"))
    return "DONE"
