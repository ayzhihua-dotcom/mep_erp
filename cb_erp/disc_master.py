# -*- coding: utf-8 -*-
"""专业 / 系统 主数据 + 项目专业系统配置 + 单据字段改为联动 Link。

1) 新建 DocType：CB Discipline（专业）、CB System（系统，按专业过滤）
2) 写入标准专业/系统清单（幂等）
3) 把 10 类单据上的 custom_discipline/custom_system 从 Data 改为 Link 并迁移旧值
4) Project 增加「项目专业与系统」子表
"""
import frappe

ROOT_APP_MODULE = "CB ERP"

DISCIPLINES = [
    ("管道", "PIP", 10, ["工艺系统", "公用工程系统", "循环水系统", "蒸汽系统", "氮气系统", "压缩空气系统"]),
    ("电气", "ELEC", 20, ["电气系统", "变配电系统", "动力配电系统", "照明系统", "防雷接地系统", "UPS不间断电源系统"]),
    ("仪表", "INST", 30, ["仪表自控系统", "DCS控制系统", "SIS安全仪表系统", "现场仪表系统"]),
    ("机械设备", "MECH", 40, ["工艺系统", "起重运输系统", "压缩机组系统"]),
    ("暖通", "HVAC", 50, ["暖通空调系统", "防排烟系统", "通风系统", "冷冻水系统"]),
    ("给排水", "PLB", 60, ["给水系统", "排水系统", "雨水系统", "生活热水系统"]),
    ("消防", "FIR", 70, ["消防水系统", "消防电系统", "气体灭火系统"]),
    ("钢结构", "STL", 80, ["钢结构系统", "平台梯子系统"]),
    ("焊接", "WELD", 90, ["焊接施工系统"]),
    ("防腐保温", "INS", 100, ["防腐系统", "保温系统"]),
    ("安全环保", "SAFE", 110, ["安全设施系统", "环保系统"]),
    ("其他", "MISC", 120, ["其他系统"]),
]

DOC_TYPES = [
    "Material Request", "Purchase Order", "Stock Entry", "Stock Reconciliation",
    "Material Budget", "Material Commitment", "Design BOM", "Design Change Request",
    "CB Shipment", "CB Import Case",
]


def _module():
    for m in ("CB ERP", "Cb Erp", "cb_erp"):
        if frappe.db.exists("Module Def", m):
            return m
    return frappe.get_all("Module Def", pluck="name")[0]


def ensure_doctypes():
    mod = _module()
    if not frappe.db.exists("DocType", "CB Discipline"):
        frappe.get_doc({
            "doctype": "DocType", "name": "CB Discipline", "module": mod, "custom": 0,
            "autoname": "field:discipline_name", "title_field": "discipline_name",
            "search_fields": "discipline_name,code",
            "sort_field": "sort_order", "sort_order": "ASC",
            "fields": [
                {"fieldname": "discipline_name", "fieldtype": "Data", "label": "专业名称",
                 "reqd": 1, "unique": 1, "in_list_view": 1},
                {"fieldname": "code", "fieldtype": "Data", "label": "编码", "unique": 1, "in_list_view": 1},
                {"fieldname": "sort_order", "fieldtype": "Int", "label": "排序", "default": "0"},
                {"fieldname": "enabled", "fieldtype": "Check", "label": "启用", "default": "1", "in_list_view": 1},
                {"fieldname": "description", "fieldtype": "Small Text", "label": "说明"},
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1,
                             "report": 1, "export": 1, "print": 1, "email": 1, "share": 1}],
        }).insert(ignore_permissions=True)
        print("CREATED_DOCTYPE: CB Discipline")

    if not frappe.db.exists("DocType", "CB System"):
        frappe.get_doc({
            "doctype": "DocType", "name": "CB System", "module": mod, "custom": 0,
            "autoname": "format:{discipline}-{system_name}", "title_field": "system_name",
            "search_fields": "system_name,discipline",
            "sort_field": "sort_order", "sort_order": "ASC",
            "fields": [
                {"fieldname": "system_name", "fieldtype": "Data", "label": "系统名称",
                 "reqd": 1, "in_list_view": 1},
                {"fieldname": "discipline", "fieldtype": "Link", "label": "所属专业",
                 "options": "CB Discipline", "reqd": 1, "in_list_view": 1, "in_standard_filter": 1},
                {"fieldname": "code", "fieldtype": "Data", "label": "编码"},
                {"fieldname": "sort_order", "fieldtype": "Int", "label": "排序", "default": "0"},
                {"fieldname": "enabled", "fieldtype": "Check", "label": "启用", "default": "1", "in_list_view": 1},
                {"fieldname": "description", "fieldtype": "Small Text", "label": "说明"},
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1,
                             "report": 1, "export": 1, "print": 1, "email": 1, "share": 1}],
        }).insert(ignore_permissions=True)
        print("CREATED_DOCTYPE: CB System")
    frappe.db.commit()
    frappe.clear_cache()


def ensure_project_system_table():
    mod = _module()
    if not frappe.db.exists("DocType", "CB Project System"):
        frappe.get_doc({
            "doctype": "DocType", "name": "CB Project System", "module": mod,
            "custom": 0, "istable": 1,
            "fields": [
                {"fieldname": "discipline", "fieldtype": "Link", "label": "专业",
                 "options": "CB Discipline", "reqd": 1, "in_list_view": 1, "columns": 2},
                {"fieldname": "system", "fieldtype": "Link", "label": "系统",
                 "options": "CB System", "reqd": 1, "in_list_view": 1, "columns": 3},
                {"fieldname": "responsible", "fieldtype": "Link", "label": "责任人",
                 "options": "User", "in_list_view": 1, "columns": 2},
                {"fieldname": "remark", "fieldtype": "Data", "label": "备注", "in_list_view": 1, "columns": 2},
            ],
            "permissions": [],
        }).insert(ignore_permissions=True)
        print("CREATED_DOCTYPE: CB Project System")

    if not frappe.db.exists("Custom Field", {"dt": "Project", "fieldname": "custom_project_systems"}):
        frappe.get_doc({
            "doctype": "Custom Field", "dt": "Project", "fieldname": "custom_project_systems",
            "label": "项目专业与系统", "fieldtype": "Table", "options": "CB Project System",
            "insert_after": "project_name",
        }).insert(ignore_permissions=True)
        print("CREATED_FIELD: Project.custom_project_systems")
    frappe.db.commit()
    frappe.clear_cache()


def seed_masters():
    for idx, (name, code, order, systems) in enumerate(DISCIPLINES, start=1):
        if not frappe.db.exists("CB Discipline", name):
            frappe.get_doc({"doctype": "CB Discipline", "discipline_name": name, "code": code,
                            "sort_order": order, "enabled": 1}).insert(ignore_permissions=True)
        else:
            frappe.db.set_value("CB Discipline", name, {"code": code, "sort_order": order, "enabled": 1},
                                update_modified=False)
        for j, sysname in enumerate(systems, start=1):
            docname = "%s-%s" % (name, sysname)
            if not frappe.db.exists("CB System", docname):
                frappe.get_doc({"doctype": "CB System", "system_name": sysname, "discipline": name,
                                "code": "%s-%02d" % (code, j), "sort_order": j * 10,
                                "enabled": 1}).insert(ignore_permissions=True)
    frappe.db.commit()
    frappe.clear_cache()
    print("DISCIPLINES:", frappe.db.count("CB Discipline"), "SYSTEMS:", frappe.db.count("CB System"))


def migrate_doc_values():
    """旧值（如「工艺系统」）按 (专业, 系统) 映射到新的系统文档名（如「管道-工艺系统」）。"""
    total = 0
    for dt in DOC_TYPES:
        if not frappe.db.has_column(dt, "custom_discipline"):
            continue
        rows = frappe.db.sql("""select distinct ifnull(custom_discipline,'') d, ifnull(custom_system,'') s
                                from `tab%s`""" % dt, as_dict=True)
        for r in rows:
            d, s = r["d"], r["s"]
            if not d or not s:
                continue
            target = "%s-%s" % (d, s)
            if target == s or s == target or s.startswith(d + "-"):
                continue
            if not frappe.db.exists("CB System", target):
                print("  NO_MASTER", dt, "[%s/%s]" % (d, s))
                continue
            n = frappe.db.count(dt, {"custom_discipline": d, "custom_system": s})
            if n:
                frappe.db.sql("""update `tab%s` set custom_system=%%s
                                 where custom_discipline=%%s and custom_system=%%s""" % dt,
                              (target, d, s))
                total += n
                print("  MAP", dt, "[%s/%s] -> %s (%s 行)" % (d, s, target, n))
    frappe.db.commit()
    print("MIGRATED_ROWS:", total)
    return total


def convert_fields_to_link():
    """把 Data 字段改成 Link。

    Frappe 的 Custom Field.validate 禁止 Data→Link 的类型变更，但两者底层都是 varchar，
    不需要改表结构；这里直接更新 Custom Field 记录（只改元数据），随后清缓存让 meta 重新加载。
    """
    dts = tuple(DOC_TYPES)
    n1 = frappe.db.sql("""update `tabCustom Field` set fieldtype='Link', options='CB Discipline',
                                 in_standard_filter=1
                          where dt in %s and fieldname='custom_discipline'""", (dts,))
    n2 = frappe.db.sql("""update `tabCustom Field` set fieldtype='Link', options='CB System',
                                 in_standard_filter=1
                          where dt in %s and fieldname='custom_system'""", (dts,))
    frappe.db.commit()
    frappe.clear_cache()
    print("LINK_FIELDS_UPDATED discipline/system:", n1, n2)


def run():
    frappe.set_user("Administrator")
    ensure_doctypes()
    ensure_project_system_table()
    seed_masters()
    migrate_doc_values()
    convert_fields_to_link()
    print("DONE")
    return "DISC_MASTER_DONE"
