# -*- coding: utf-8 -*-
"""补齐采购入库 / 质检 的专业/系统字段，并回填全链路历史单据。"""
import frappe

EXTRA_DTS = ["Purchase Receipt", "Quality Inspection"]

L1_TO_DISC = {
    "管道与阀门": "管道",
    "给排水": "给排水",
    "消防": "消防",
    "暖通空调": "暖通",
    "电气与电缆": "电气",
    "弱电与通信": "电气",
    "仪表与自控": "仪表",
    "机电设备与主材": "机械设备",
    "钢结构与建筑": "钢结构",
    "焊接与辅材": "焊接",
    "防腐保温": "防腐保温",
    "安全与临时设施": "安全环保",
    "五金辅材": "其他",
    "其他": "其他",
}

BACKFILL_DTS = ["Material Budget", "Material Commitment", "Design BOM",
                "Design Change Request", "CB Shipment", "CB Import Case",
                "Purchase Receipt", "Quality Inspection"]


def ensure_extra_fields():
    for dt in EXTRA_DTS:
        for fn, label, opts in (("custom_discipline", "专业", "CB Discipline"),
                                ("custom_system", "系统", "CB System")):
            if frappe.db.exists("Custom Field", {"dt": dt, "fieldname": fn}):
                continue
            frappe.get_doc({
                "doctype": "Custom Field", "dt": dt, "fieldname": fn, "label": label,
                "fieldtype": "Link", "options": opts, "in_standard_filter": 1,
                "insert_after": "project",
            }).insert(ignore_permissions=True)
            print("FIELD", dt, fn)
    frappe.db.commit()
    frappe.clear_cache()


def _l1_of(group):
    seen = set()
    g = group
    while g and g not in seen:
        seen.add(g)
        parent = frappe.db.get_value("Item Group", g, "parent_item_group")
        if not parent or parent == "所有物料组":
            return g
        g = parent
    return None


def _system_for(discipline, project):
    if project:
        row = frappe.db.get_value("CB Project System", {"parent": project, "discipline": discipline},
                                  "system", order_by="idx asc")
        if row:
            return row
    return frappe.db.get_value("CB System", {"discipline": discipline, "enabled": 1},
                               "name", order_by="sort_order asc")


def _pair_from_items(doc, project):
    for f in doc.meta.get_table_fields():
        for row in doc.get(f.fieldname) or []:
            code = row.get("item_code")
            if not code:
                continue
            group = frappe.db.get_value("Item", code, "item_group")
            if not group:
                continue
            disc = L1_TO_DISC.get(_l1_of(group))
            if not disc:
                continue
            system = _system_for(disc, project)
            if system:
                return disc, system
    return None


def _pair_from_project(project):
    if not project:
        return None
    row = frappe.db.get_value("CB Project System", {"parent": project},
                              ["discipline", "system"], order_by="idx asc", as_dict=True)
    if row:
        return row["discipline"], row["system"]
    return None


def _pair_from_links(doc):
    for fn in ("design_bom", "bom", "purchase_order", "purchase_receipt",
               "material_request", "cb_import_case", "shipment"):
        if not doc.meta.get_field(fn):
            continue
        target = doc.get(fn)
        if not target:
            continue
        dt = doc.meta.get_field(fn).options
        if not dt or not frappe.db.exists(dt, target):
            continue
        d, s = frappe.db.get_value(dt, target, ["custom_discipline", "custom_system"]) or (None, None)
        if d and s:
            return d, s
        project = frappe.db.get_value(dt, target, "project") or frappe.db.get_value(dt, target, "custom_cb_project")
        pair = _pair_from_project(project)
        if pair:
            return pair
    return None


def backfill_empty():
    updated = 0
    details = {}
    for dt in BACKFILL_DTS:
        if not frappe.db.has_column(dt, "custom_discipline"):
            continue
        names = frappe.get_all(dt, filters={"custom_discipline": ["in", ["", None]]}, pluck="name", limit=0)
        n = 0
        for name in names:
            doc = frappe.get_doc(dt, name)
            project = doc.get("project") or doc.get("custom_cb_project")
            pair = _pair_from_items(doc, project) or _pair_from_project(project) or _pair_from_links(doc)
            if not pair or not pair[0] or not pair[1]:
                continue
            frappe.db.set_value(dt, name, {"custom_discipline": pair[0], "custom_system": pair[1]},
                                update_modified=False)
            n += 1
        details[dt] = n
        updated += n
    frappe.db.commit()
    frappe.clear_cache()
    print("BACKFILLED:", updated)
    for k, v in details.items():
        print("   ", k, v)
    return updated


def run():
    frappe.set_user("Administrator")
    ensure_extra_fields()
    backfill_empty()
    return "DISC_EXTEND_DONE"
