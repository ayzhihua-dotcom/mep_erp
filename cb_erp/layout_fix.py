# -*- coding: utf-8 -*-
"""表单横向布局：3 列一行。

1) 批量录入：业务类型|项目|仓库 / 单据日期|专业|系统 / 责任人
2) 采购申请/采购订单/库存移动/采购入库/质检：加「专业与系统」区块，专业|系统|责任人 三列
"""
import frappe

BULK = "Bulk Entry"

ANCHORS = {
    "Material Request": "custom_cb_project",
    "Purchase Order": "custom_cb_project",
    "Stock Entry": "project",
    "Purchase Receipt": "project",
    "Quality Inspection": "project",
}


def _field_exists(dt, fn):
    return bool(frappe.db.exists("DocField", {"parent": dt, "fieldname": fn}))


def _set_docfield_idx(dt, order):
    """按给定顺序重排 DocField.idx。"""
    for i, fn in enumerate(order, start=1):
        frappe.db.sql("""update `tabDocField` set idx=%s where parent=%s and fieldname=%s""",
                      (i, dt, fn))


def setup_bulk_layout():
    fields = {f.fieldname: f for f in frappe.get_meta(BULK).fields}
    need = ["kind", "project", "warehouse", "posting_date", "discipline", "system", "responsible", "rows_text"]
    for fn in need:
        if fn not in fields:
            print("BULK_MISSING", fn)
            return

    # 先删除旧的布局字段（可重复执行）
    frappe.db.sql("""delete from `tabDocField` where parent=%s and fieldname in
                     ('cb_l1','cb_l2','sb_line2','cb_l3','cb_l4','sb_line3')""", (BULK,))

    rows = [
        # (fieldname, fieldtype, label, insert_after)
        ("cb_l1", "Column Break", "", "kind"),
        ("cb_l2", "Column Break", "", "project"),
        ("sb_line2", "Section Break", "单据信息", "warehouse"),
        ("cb_l3", "Column Break", "", "posting_date"),
        ("cb_l4", "Column Break", "", "discipline"),
        ("sb_line3", "Section Break", "专业与责任人", "system"),
    ]
    for fn, ft, label, after in rows:
        nxt = frappe.db.get_value("DocField", {"parent": BULK, "fieldname": after}, "idx")
        if not nxt:
            continue
        frappe.db.sql("""update `tabDocField` set idx=idx+1 where parent=%s and idx>%s""", (BULK, nxt))
        frappe.db.sql("""insert into `tabDocField`
                         (name, parent, parenttype, parentfield, idx, fieldname, fieldtype, label)
                         values (%s,%s,'DocType','fields',%s,%s,%s,%s)""",
                      ("%s-%s" % (BULK, fn), BULK, nxt + 1, fn, ft, label))

    order = ["kind", "cb_l1", "project", "cb_l2", "warehouse", "sb_line2",
             "posting_date", "cb_l3", "discipline", "cb_l4", "system",
             "sb_line3", "responsible", "rows_text"]
    _set_docfield_idx(BULK, order)
    frappe.db.commit()
    frappe.clear_cache()
    print("BULK_LAYOUT_OK")


def setup_section(dt):
    anchor = ANCHORS.get(dt)
    if not anchor:
        return
    if not frappe.db.exists("Custom Field", {"dt": dt, "fieldname": "custom_discipline"}):
        return

    sb = dt + "-custom_disc_section"
    cb1 = dt + "-custom_disc_cb1"
    cb2 = dt + "-custom_disc_cb2"
    cb3 = dt + "-custom_disc_cb3"

    def ensure_cf(fieldname, fieldtype, label, insert_after):
        name = frappe.db.exists("Custom Field", {"dt": dt, "fieldname": fieldname})
        if name:
            frappe.db.set_value("Custom Field", name, {"insert_after": insert_after, "label": label,
                                                       "fieldtype": fieldtype}, update_modified=False)
            return
        frappe.get_doc({
            "doctype": "Custom Field", "dt": dt, "fieldname": fieldname, "label": label,
            "fieldtype": fieldtype, "insert_after": insert_after,
        }).insert(ignore_permissions=True)

    ensure_cf("custom_disc_section", "Section Break", "专业与系统", anchor)
    ensure_cf("custom_disc_cb1", "Column Break", "", "custom_disc_section")
    frappe.db.set_value("Custom Field", {"dt": dt, "fieldname": "custom_discipline"},
                        "insert_after", "custom_disc_cb1", update_modified=False)
    ensure_cf("custom_disc_cb2", "Column Break", "", "custom_discipline")
    frappe.db.set_value("Custom Field", {"dt": dt, "fieldname": "custom_system"},
                        "insert_after", "custom_disc_cb2", update_modified=False)

    has_resp = frappe.db.exists("Custom Field", {"dt": dt, "fieldname": "custom_responsible"})
    if has_resp:
        ensure_cf("custom_disc_cb3", "Column Break", "", "custom_system")
        frappe.db.set_value("Custom Field", {"dt": dt, "fieldname": "custom_responsible"},
                            "insert_after", "custom_disc_cb3", update_modified=False)
    frappe.db.commit()
    frappe.clear_cache()
    print("SECTION_OK", dt)


def run():
    frappe.set_user("Administrator")
    setup_bulk_layout()
    for dt in ANCHORS:
        try:
            setup_section(dt)
        except Exception as e:
            print("FAIL", dt, repr(e)[:160])
    return "LAYOUT_DONE"
