# -*- coding: utf-8 -*-
"""用 field_order 属性把「专业与系统」区块精确放到指定位置。

Frappe 的 insert_after 对「自定义字段 -> 自定义字段」的链式插入不稳定，
这里直接为每个 DocType 生成完整字段顺序。
"""
import json
import frappe

BLOCK = ["custom_disc_section", "custom_disc_cb1", "custom_discipline",
         "custom_disc_cb2", "custom_system", "custom_disc_cb3", "custom_responsible"]

ANCHOR = {
    "Material Request": ["company", "transaction_date"],
    "Purchase Order": ["project", "company"],
    "Stock Entry": ["project", "company"],
    "Purchase Receipt": ["project", "company"],
    "Quality Inspection": ["project", "company", "item_code"],
}

# 先于区块摆放的自定义字段（按顺序）
PRE_BLOCK = ["custom_cb_project", "custom_cb_budget"]


def build_order(dt):
    std = [f.fieldname for f in frappe.get_all(
        "DocField", filters={"parent": dt}, fields=["fieldname", "idx"], order_by="idx asc")]
    customs = [r["fieldname"] for r in frappe.get_all(
        "Custom Field", filters={"dt": dt}, fields=["fieldname"], order_by="idx asc, creation asc")]

    anchor = None
    for a in ANCHOR[dt]:
        if a in std:
            anchor = a
            break
    if not anchor:
        return None

    block = [b for b in BLOCK if b in customs]
    pre = [c for c in PRE_BLOCK if c in customs and c not in block]
    others = [c for c in customs if c not in block and c not in pre]

    order = []
    for f in std:
        order.append(f)
        if f == anchor:
            order.extend(pre)
            order.extend(block)
    order.extend(others)
    # 去重保序
    seen, final = set(), []
    for f in order:
        if f in seen:
            continue
        seen.add(f)
        final.append(f)
    return final


def set_field_order(dt):
    order = build_order(dt)
    if not order:
        print("SKIP", dt)
        return
    val = json.dumps(order)
    name = frappe.db.get_value("Property Setter", {
        "doc_type": dt, "property": "field_order", "field_name": ["in", ["", None]]})
    if name:
        frappe.db.set_value("Property Setter", name, "value", val, update_modified=False)
    else:
        frappe.get_doc({
            "doctype": "Property Setter", "doctype_or_field": "DocType",
            "doc_type": dt, "property": "field_order", "property_type": "JSON", "value": val,
        }).insert(ignore_permissions=True)
    print("ORDER_SET", dt, len(order))


def run():
    frappe.set_user("Administrator")
    for dt in ANCHOR:
        set_field_order(dt)
    frappe.db.commit()
    frappe.clear_cache()
    from frappe.model.meta import clear_meta_cache
    for dt in ("Material Request", "Purchase Order", "Stock Entry", "Purchase Receipt", "Quality Inspection"):
        try:
            clear_meta_cache(dt)
        except Exception:
            pass
        seq = [f.fieldname for f in frappe.get_meta(dt, cached=False).fields]
        picked = [n for n in seq if n in BLOCK or n in PRE_BLOCK]
        print(dt, "->", picked)
    return "ORDER_DONE"
