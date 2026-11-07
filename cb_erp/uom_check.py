# -*- coding: utf-8 -*-
def run():
    import frappe
    frappe.set_user("Administrator")
    print("UOMS:", frappe.get_all("UOM", pluck="name"))
    rows = frappe.db.sql("""select stock_uom, count(*) c from `tabItem` group by stock_uom order by c desc""", as_dict=True)
    for r in rows:
        print("  ", r["stock_uom"], r["c"])
    return "OK"
