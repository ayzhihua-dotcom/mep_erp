# -*- coding: utf-8 -*-
WS = "巴西机电ERP系统测试"


def run():
    import frappe
    frappe.set_user("Administrator")
    results = {}
    for dock_name in ("frappe", "erpnext"):
        try:
            dock = frappe.get_doc("Dock", dock_name)
        except Exception as e:
            results[dock_name] = "NO_DOCK:" + repr(e)[:100]
            continue
        if any(getattr(i, "link_to", None) == WS for i in dock.items):
            results[dock_name] = "EXISTS"
            continue
        dock.append("items", {
            "link_type": "Workspace",
            "link_to": WS,
            "title": WS,
            "icon": "factory-soft",
            "hidden": 0,
        })
        try:
            dock.save(ignore_permissions=True)
            frappe.db.commit()
            results[dock_name] = "ADDED"
        except Exception as e:
            results[dock_name] = "ERR:" + repr(e)[:150]
    frappe.clear_cache()
    print("RESULTS:", results)
    for dock_name in ("frappe", "erpnext"):
        if frappe.db.exists("Dock", dock_name):
            d = frappe.get_doc("Dock", dock_name)
            print(dock_name, "ITEMS:", [(i.link_type, i.link_to) for i in d.items])
    return "DONE"
