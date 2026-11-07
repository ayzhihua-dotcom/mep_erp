# -*- coding: utf-8 -*-
def run():
    import frappe
    frappe.set_user("Administrator")
    NEW = "巴西机电ERP系统测试"
    dock = frappe.get_doc("Dock", "erpnext")
    if any(i.link_to == NEW for i in dock.items):
        print("DOCK_ITEM_EXISTS")
        return "OK"
    dock.append("items", {"link_type": "Workspace", "link_to": NEW, "title": NEW,
                          "icon": "tool-soft", "hidden": 0})
    dock.save(ignore_permissions=True)
    frappe.db.commit()
    frappe.clear_cache()
    print("DOCK_ITEM_ADDED")
    return "OK"
