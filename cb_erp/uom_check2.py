# -*- coding: utf-8 -*-
import json
def run():
    import frappe
    frappe.set_user("Administrator")
    print(json.dumps(frappe.get_all("UOM", pluck="name"), ensure_ascii=True))
    rows = frappe.db.sql("""select stock_uom u, count(*) c from `tabItem` group by stock_uom order by c desc""", as_dict=True)
    print(json.dumps([[r["u"], r["c"]] for r in rows], ensure_ascii=True))
    return "OK"
