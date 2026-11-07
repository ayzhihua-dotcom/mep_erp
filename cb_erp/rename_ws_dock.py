# -*- coding: utf-8 -*-
OLD = "CB 机电总控"
NEW = "巴西机电ERP系统测试"


def run():
    import frappe
    frappe.set_user("Administrator")
    if frappe.db.exists("Workspace", OLD) and not frappe.db.exists("Workspace", NEW):
        frappe.rename_doc("Workspace", OLD, NEW, force=True)
        frappe.db.commit()
        print("RENAMED_WORKSPACE")
    else:
        print("RENAME_SKIP", frappe.db.exists("Workspace", OLD), frappe.db.exists("Workspace", NEW))
    # try add to erpnext dock
    added = False
    try:
        dock = frappe.get_doc("Dock", "erpnext")
        if not any((i.link_to == NEW) for i in dock.items):
            dock.append("items", {"link_type": "Workspace", "link_to": NEW, "title": NEW,
                                  "icon": "tool-soft", "hidden": 0})
            dock.save(ignore_permissions=True)
            frappe.db.commit()
            print("DOCK_ITEM_ADDED_ERPNEXT")
            added = True
        else:
            print("DOCK_ITEM_EXISTS")
            added = True
    except Exception as e:
        print("DOCK_ERR", repr(e)[:200])
    if not added:
        try:
            if not frappe.db.exists("Dock", "cb_erp"):
                frappe.get_doc({"doctype": "Dock", "app": "cb_erp", "standard": 0, "mount_on": "erpnext",
                                "items": [{"link_type": "Workspace", "link_to": NEW, "title": NEW,
                                           "icon": "tool-soft", "hidden": 0}]}).insert(ignore_permissions=True)
                frappe.db.commit()
                print("CB_DOCK_CREATED_MOUNTED")
        except Exception as e:
            print("CB_DOCK_ERR", repr(e)[:200])
    frappe.clear_cache()
    print("WS_EXISTS:", frappe.db.exists("Workspace", NEW))
    return "DONE"
