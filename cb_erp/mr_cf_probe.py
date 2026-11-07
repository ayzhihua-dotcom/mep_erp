# -*- coding: utf-8 -*-
import json
def run():
    import frappe
    frappe.set_user("Administrator")
    rows = frappe.get_all("Custom Field", filters={"dt": "Material Request"},
                          fields=["fieldname", "fieldtype", "insert_after", "idx", "creation"],
                          order_by="idx asc, creation asc")
    for r in rows:
        print(json.dumps([r.fieldname, r.fieldtype, r.insert_after, r.idx, str(r.creation)], ensure_ascii=True))
    print("COUNT:", len(rows))
    m = frappe.get_meta("Material Request")
    print("META_ORDER:", json.dumps([f.fieldname for f in m.fields if f.fieldname.startswith("custom_")], ensure_ascii=True))
    return "OK"
