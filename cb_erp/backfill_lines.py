# -*- coding: utf-8 -*-
def run():
    import frappe
    frappe.set_user("Administrator")
    sqls = [
        ("Material Request Item", """
        update `tabMaterial Request Item` i
        join `tabMaterial Request` m on m.name = i.parent
        join `tabItem` it on it.name = i.item_code
        set i.custom_seq = i.idx, i.custom_uom = it.stock_uom,
            i.custom_use_project = m.custom_cb_project, i.custom_responsible = m.custom_responsible
        """),
        ("Stock Entry Detail", """
        update `tabStock Entry Detail` i
        join `tabStock Entry` s on s.name = i.parent
        join `tabItem` it on it.name = i.item_code
        set i.custom_seq = i.idx, i.custom_uom = it.stock_uom,
            i.custom_use_project = ifnull(s.project, i.custom_use_project),
            i.custom_responsible = ifnull(i.custom_responsible, s.custom_responsible)
        """),
        ("Purchase Order Item", """
        update `tabPurchase Order Item` i
        join `tabPurchase Order` p on p.name = i.parent
        join `tabItem` it on it.name = i.item_code
        set i.custom_seq = i.idx, i.custom_uom = it.stock_uom,
            i.custom_use_project = p.custom_cb_project, i.custom_responsible = p.custom_responsible
        """),
        ("Stock Reconciliation Item", """
        update `tabStock Reconciliation Item` i
        join `tabStock Reconciliation` s on s.name = i.parent
        join `tabItem` it on it.name = i.item_code
        set i.custom_seq = i.idx, i.custom_uom = it.stock_uom,
            i.custom_use_project = ifnull(s.project, i.custom_use_project)
        """),
    ]
    for label, sql in sqls:
        try:
            frappe.db.sql(sql)
            frappe.db.commit()
            print("BACKFILLED", label)
        except Exception as e:
            frappe.db.rollback()
            print("BACKFILL_ERR", label, repr(e)[:150])
    frappe.clear_cache()
    from frappe.desk.query_report import run as qrun
    res = qrun("物料明细（九列）", filters={})
    rows = res.get("result") or []
    print("REPORT_ROWS", len(rows))
    filled = [r for r in rows if r.get("单位")]
    print("ROWS_WITH_UOM", len(filled))
    for r in filled[:4]:
        print("SAMPLE", r)
    return "BACKFILL_LINES_DONE"
