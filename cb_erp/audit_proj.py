# -*- coding: utf-8 -*-
def run():
    import frappe
    frappe.set_user("Administrator")
    for dt in ("Material Request", "Purchase Order", "Stock Entry", "Stock Reconciliation",
               "Material Budget", "Material Commitment", "Design BOM", "Design Change Request",
               "CB Shipment", "CB Import Case"):
        fields = [f.fieldname for f in frappe.get_meta(dt).fields if "project" in (f.fieldname or "").lower()]
        print(dt, "->", fields)
    print("--- Stock Entry Detail project field type:",
          frappe.get_meta("Stock Entry Detail").get_field("project").fieldtype if frappe.get_meta("Stock Entry Detail").get_field("project") else None)
    print("--- Project fields sample:", [f.fieldname for f in frappe.get_meta("Project").fields][:40])
    print("--- Roles:", [r.name for r in frappe.get_all("Role", fields=["name"], limit=0) if r.name.startswith("CB")])
    return "OK"
