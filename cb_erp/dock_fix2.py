# -*- coding: utf-8 -*-
WS = "巴西机电ERP系统测试"


def run():
    import frappe
    frappe.set_user("Administrator")
    from frappe.desk.doctype.dock.dock import save_site_dock, resolve_app_dock

    print("HOME_WS:", frappe.db.get_value("Workspace", "Home", ["label", "is_hidden", "public"], as_dict=True))
    items = [
        {"link_type": "Sidebar", "link_to": "Users", "icon": "users-soft", "title": "用户"},
        {"link_type": "Sidebar", "link_to": "System", "icon": "system-monitor-soft", "title": "系统"},
        {"link_type": "URL", "url": "/desk/home", "icon": "home-soft", "title": "ERPNext 主页"},
        {"link_type": "Workspace", "link_to": WS, "icon": "factory-soft", "title": WS},
    ]
    rail = save_site_dock("frappe", items)
    frappe.db.commit()
    frappe.clear_cache()
    print("RAIL:", [(e.get("link_type"), e.get("link_to"), e.get("title")) for e in rail])
    print("RESOLVED:", [(e.get("link_type"), e.get("link_to"), e.get("title"), e.get("hidden"))
                        for e in resolve_app_dock("frappe")])
    return "DONE"
