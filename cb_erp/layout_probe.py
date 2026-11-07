# -*- coding: utf-8 -*-
import json
def run():
    import frappe
    frappe.set_user("Administrator")
    # Bulk Entry 字段顺序
    m = frappe.get_meta("Bulk Entry")
    print("BULK_FIELDS:", json.dumps([(f.idx, f.fieldname, f.fieldtype, f.label) for f in m.fields], ensure_ascii=True))
    # 关键单据的锚点字段
    for dt in ("Material Request", "Purchase Order", "Stock Entry", "Purchase Receipt"):
        mm = frappe.get_meta(dt)
        names = [f.fieldname for f in mm.fields]
        print(dt, "ANCHORS:", [n for n in ("company", "project", "custom_cb_project", "custom_discipline", "custom_system", "custom_responsible", "posting_date", "transaction_date", "schedule_date", "stock_entry_type", "material_request_type") if n in names])
    # workspace link 支持的 link_type
    wm = frappe.get_meta("Workspace Link")
    f = wm.get_field("link_type")
    print("WS_LINK_TYPE_OPTIONS:", f.options if f else None)
    print("WS_LINK_FIELDS:", json.dumps([x.fieldname for x in wm.fields], ensure_ascii=True))
    return "OK"
