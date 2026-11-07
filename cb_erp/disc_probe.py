# -*- coding: utf-8 -*-
import json
def run():
    import frappe
    frappe.set_user("Administrator")
    for dt in ("Material Budget", "Material Commitment", "Design BOM", "Design Change Request",
               "CB Shipment", "CB Import Case"):
        m = frappe.get_meta(dt)
        tables = [f.fieldname for f in m.fields if f.fieldtype == "Table"]
        has_item = []
        for t in tables:
            cm = frappe.get_meta(m.get_field(t).options)
            if cm.get_field("item_code"):
                has_item.append(t)
        links = [f.fieldname for f in m.fields if f.fieldtype == "Link" and "project" in (f.fieldname or "").lower()]
        print(json.dumps({"dt": dt, "tables": tables, "item_tables": has_item,
                          "rows": frappe.db.count(dt), "project_links": links}, ensure_ascii=True))
    return "OK"
