# -*- coding: utf-8 -*-
import json


def run():
    import frappe
    frappe.set_user("Administrator")
    ws = frappe.get_doc("Workspace", "巴西机电ERP系统测试")
    rows = [{"label": l.label, "icon": l.icon, "type": l.type, "link_type": l.link_type} for l in ws.links]
    print("LINKS:", json.dumps(rows[:14], ensure_ascii=True))
    print("WITH_ICON:", sum(1 for r in rows if r["icon"]))
    return "OK"
