# -*- coding: utf-8 -*-
import json

DTS = ["Material Request", "Purchase Order", "Stock Entry", "Purchase Receipt", "Quality Inspection",
       "Material Budget", "Material Commitment", "Design BOM", "Design Change Request",
       "CB Shipment", "CB Import Case"]


def run():
    import frappe
    frappe.set_user("Administrator")
    for dt in DTS:
        frappe.db.sql("""update `tabCustom Field` set idx=0
                         where dt=%s and fieldname in
                         ('custom_disc_section','custom_disc_cb1','custom_discipline',
                          'custom_disc_cb2','custom_system','custom_disc_cb3','custom_responsible')""", (dt,))
    frappe.db.commit()
    frappe.clear_cache()
    for dt in DTS[:3]:
        m = frappe.get_meta(dt)
        seq = [f.fieldname for f in m.fields]
        idx = [i for i, n in enumerate(seq) if n in
               ("custom_disc_section", "custom_disc_cb1", "custom_discipline",
                "custom_disc_cb2", "custom_system", "custom_disc_cb3", "custom_responsible")]
        print(dt, "->", [seq[i] for i in idx])
    return "OK"
