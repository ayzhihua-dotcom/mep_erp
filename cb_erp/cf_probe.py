# -*- coding: utf-8 -*-
import json
def run():
    import frappe
    frappe.set_user("Administrator")
    cols = [c[0] for c in frappe.db.sql("desc `tabCustom Field`", as_dict=False)]
    print("CF_COLUMNS:", json.dumps(cols, ensure_ascii=True))
    rows = frappe.get_all("Custom Field", filters={"dt": "Material Request", "fieldname": ["like", "custom_disc%"]},
                          fields=["fieldname", "fieldtype", "insert_after", "idx", "creation"], order_by="idx asc")
    print("MR_CF:", json.dumps([[r.fieldname, r.fieldtype, r.insert_after, r.idx, str(r.creation)] for r in rows], ensure_ascii=True))
    for r in frappe.get_all("Custom Field", filters={"dt": "Material Request", "fieldname": ["in", ["custom_discipline", "custom_system", "custom_responsible"]]},
                            fields=["fieldname", "insert_after", "idx"], order_by="idx asc"):
        print("  ", r.fieldname, "| after:", r.insert_after, "| idx:", r.idx)
    return "OK"
