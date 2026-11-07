# -*- coding: utf-8 -*-
CHILDREN = ["Material Request Item", "Stock Entry Detail", "Purchase Order Item", "Stock Reconciliation Item"]
NEW_FIELDS = [
    ("custom_seq", "Int", "序号", None),
    ("custom_uom", "Link", "单位", "UOM"),
    ("custom_use_project", "Link", "使用项目", "Project"),
    ("custom_responsible", "Link", "责任人", "User"),
]
DESIRED = ["custom_seq", "item_code", "item_name", "custom_spec", "custom_uom",
           "qty", "custom_use_project", "custom_responsible", "custom_remark"]
DESIRED_SR = ["custom_seq", "item_code", "custom_item_name", "custom_spec", "custom_uom",
              "qty", "custom_use_project", "custom_responsible", "custom_remark"]


def run():
    import frappe
    frappe.set_user("Administrator")
    for dt in CHILDREN:
        for fn, ft, lb, opt in NEW_FIELDS:
            if frappe.db.has_column(dt, fn):
                continue
            d = {"doctype": "Custom Field", "dt": dt, "fieldname": fn, "fieldtype": ft,
                 "label": lb, "in_list_view": 1}
            if opt:
                d["options"] = opt
            frappe.get_doc(d).insert(ignore_permissions=True)
        if dt == "Stock Reconciliation Item" and not frappe.db.has_column(dt, "custom_item_name"):
            frappe.get_doc({"doctype": "Custom Field", "dt": dt, "fieldname": "custom_item_name",
                            "fieldtype": "Data", "label": "物料名称", "in_list_view": 1}).insert(ignore_permissions=True)
        frappe.db.commit()
        d = frappe.get_doc("DocType", dt)
        existing = {f.fieldname for f in d.fields}
        desired = DESIRED_SR if dt == "Stock Reconciliation Item" else DESIRED
        desired = [x for x in desired if x in existing]
        order = {fn: i for i, fn in enumerate(desired)}
        for f in d.fields:
            f.in_list_view = 1 if f.fieldname in desired else 0
        d.fields.sort(key=lambda f: (0, order[f.fieldname]) if f.fieldname in order else (1, f.idx or 0))
        for i, f in enumerate(d.fields):
            f.idx = i + 1
        d.save(ignore_permissions=True)
        frappe.db.commit()
        print("REORDERED", dt, desired)
    frappe.clear_cache()
    print("LINE_V2_DONE")
    return "LINE_V2_DONE"
