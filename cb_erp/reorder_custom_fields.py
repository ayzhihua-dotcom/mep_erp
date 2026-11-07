# -*- coding: utf-8 -*-
def run():
    import frappe
    frappe.set_user("Administrator")
    mapping = {
        "custom_spec": "item_name",
        "custom_uom": "custom_spec",
        "custom_use_project": "qty",
        "custom_responsible": "custom_use_project",
        "custom_remark": "custom_responsible",
    }
    for dt in ["Material Request Item", "Stock Entry Detail", "Purchase Order Item", "Stock Reconciliation Item"]:
        for fn, after in mapping.items():
            nm = frappe.db.get_value("Custom Field", {"dt": dt, "fieldname": fn}, "name")
            if nm:
                frappe.db.set_value("Custom Field", nm, "insert_after", after, update_modified=False)
    frappe.db.commit()
    frappe.clear_cache()
    for dt in ["Stock Entry Detail", "Material Request Item", "Purchase Order Item", "Stock Reconciliation Item"]:
        m = frappe.get_meta(dt)
        cols = [f.fieldname for f in m.fields if f.in_list_view]
        print("GRID_COLS", dt, "->", cols)
    return "REORDER_DONE"
