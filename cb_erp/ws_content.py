# -*- coding: utf-8 -*-
import json
def run():
    import frappe
    frappe.set_user("Administrator")
    ws = frappe.get_doc("Workspace", "巴西机电ERP系统测试")
    content = json.loads(ws.content or "[]")
    print("BLOCKS:", len(content))
    for b in content[:12]:
        print(json.dumps(b, ensure_ascii=True)[:220])
    print("...")
    for b in content[-6:]:
        print(json.dumps(b, ensure_ascii=True)[:220])
    return "OK"
