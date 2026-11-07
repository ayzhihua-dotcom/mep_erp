# -*- coding: utf-8 -*-
def run():
    import frappe
    frappe.set_user("Administrator")
    specs = [
        ("Item", "custom_spec", "Data", "规格参数"),
        ("Material Request Item", "custom_spec", "Data", "规格参数"),
        ("Material Request Item", "custom_remark", "Data", "备注"),
        ("Stock Entry Detail", "custom_spec", "Data", "规格参数"),
        ("Stock Entry Detail", "custom_remark", "Data", "备注"),
        ("Purchase Order Item", "custom_spec", "Data", "规格参数"),
        ("Purchase Order Item", "custom_remark", "Data", "备注"),
        ("Stock Reconciliation Item", "custom_spec", "Data", "规格参数"),
        ("Stock Reconciliation Item", "custom_remark", "Data", "备注"),
    ]
    made = 0
    for dt, fn, ft, lb in specs:
        if frappe.db.has_column(dt, fn):
            continue
        try:
            frappe.get_doc({"doctype": "Custom Field", "dt": dt, "fieldname": fn,
                            "fieldtype": ft, "label": lb, "in_list_view": 1}).insert(ignore_permissions=True)
            made += 1
        except Exception as e:
            print("CF_ERR", dt, fn, repr(e)[:120])
    frappe.db.commit()
    frappe.clear_cache()
    print("LINE_FIELDS_CREATED", made)
    return "LINE_FIELDS_DONE"
