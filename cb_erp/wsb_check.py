# -*- coding: utf-8 -*-
import json


def run():
    import frappe
    frappe.set_user("Administrator")
    print("HAS_WORKSPACE_SIDEBAR:", frappe.db.exists("DocType", "Workspace Sidebar"))
    if frappe.db.exists("DocType", "Workspace Sidebar"):
        rows = frappe.get_all("Workspace Sidebar", fields=["name", "title", "app"], limit=0)
        print("ROWS:", json.dumps(rows[:10], ensure_ascii=True))
        for r in rows:
            if r["title"] and "巴西" in (r["title"] or "") or r["title"] == "巴西机电ERP系统测试":
                d = frappe.get_doc("Workspace Sidebar", r["name"])
                print("ITEMS:", json.dumps([(i.label, i.icon, i.type) for i in d.items][:12], ensure_ascii=True))
    return "OK"
