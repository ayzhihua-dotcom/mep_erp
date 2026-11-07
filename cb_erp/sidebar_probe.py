# -*- coding: utf-8 -*-
import json
def run():
    import frappe
    frappe.set_user("Administrator")
    sm = frappe.get_meta("Sidebar Item")
    f = sm.get_field("link_type")
    print("SIDEBAR_LINK_TYPES:", f.options if f else None)
    print("SIDEBAR_FIELDS:", json.dumps([x.fieldname for x in sm.fields], ensure_ascii=True))
    print("SIDEBARS:", json.dumps(frappe.get_all("Sidebar", pluck="name"), ensure_ascii=True))
    # stock sidebar items
    if frappe.db.exists("Sidebar", "Stock"):
        d = frappe.get_doc("Sidebar", "Stock")
        print("STOCK_ITEMS:", json.dumps([(i.link_type, i.link_to, i.label) for i in d.items], ensure_ascii=True))
    return "OK"
