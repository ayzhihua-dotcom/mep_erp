# -*- coding: utf-8 -*-
import json
def run():
    import frappe
    frappe.set_user("Administrator")
    ws = frappe.get_doc("Workspace", "巴西机电ERP系统测试")
    print("LINKS:", len(ws.links))
    print(json.dumps([(l.type, l.label, l.link_type, l.link_to) for l in ws.links], ensure_ascii=True, indent=0)[:2000])
    from frappe.desk.desktop import get_workspaces
    pages = get_workspaces()["pages"]
    names = [p.name for p in pages]
    print("IN_PAGES:", "巴西机电ERP系统测试" in names, "count:", len(names))
    return "OK"
