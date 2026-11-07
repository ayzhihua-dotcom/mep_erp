# -*- coding: utf-8 -*-
WS = "巴西机电ERP系统测试"


def run():
    import frappe
    frappe.set_user("Administrator")
    from frappe.desk.doctype.dock.dock import save_site_dock, resolve_app_dock, get_app_entry_set

    items = [
        {"link_type": "Sidebar", "link_to": "Users", "icon": "users-soft", "title": "用户"},
        {"link_type": "Sidebar", "link_to": "System", "icon": "system-monitor-soft", "title": "系统"},
        {"link_type": "Workspace", "link_to": WS, "icon": "factory-soft", "title": WS},
    ]
    rail = save_site_dock("frappe", items)
    frappe.db.commit()
    frappe.clear_cache()
    print("SAVED_RAIL:", [(e.get("link_type"), e.get("link_to"), e.get("title")) for e in rail])
    print("RESOLVED_FRAPPE:", [(e.get("link_type"), e.get("link_to"), e.get("title"), e.get("hidden"))
                               for e in resolve_app_dock("frappe")])
    print("ENTRY_SET_FRAPPE:", [(e.get("link_type"), e.get("link_to")) for e in get_app_entry_set("frappe")])
    print("RESOLVED_ERPNEXT:", [(e.get("link_type"), e.get("link_to"), e.get("title"), e.get("hidden"))
                                for e in resolve_app_dock("erpnext")])
    return "DONE"
