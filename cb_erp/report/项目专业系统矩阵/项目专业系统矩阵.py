# -*- coding: utf-8 -*-
"""项目专业系统矩阵：行=系统，列=项目，值=该项目的执行数量。"""

import frappe


METRICS = ("已领用数量", "采购订单数量", "采购申请数量")


def _issued(filters):
    cond = ["se.docstatus = 1", "se.stock_entry_type = 'Material Issue'"]
    params = {}
    if filters.get("discipline"):
        cond.append("se.custom_discipline = %(discipline)s")
        params["discipline"] = filters["discipline"]
    if filters.get("project"):
        cond.append("sed.project = %(project)s")
        params["project"] = filters["project"]
    rows = frappe.db.sql("""
        select se.custom_system as system, sed.project as project, sum(sed.qty) as qty
        from `tabStock Entry` se
        join `tabStock Entry Detail` sed on sed.parent = se.name
        where {cond} and ifnull(sed.project,'') != '' and ifnull(se.custom_system,'') != ''
        group by se.custom_system, sed.project
    """.format(cond=" and ".join(cond)), params, as_dict=True)
    return rows


def _purchase_orders(filters):
    cond = ["po.docstatus = 1"]
    params = {}
    if filters.get("discipline"):
        cond.append("po.custom_discipline = %(discipline)s")
        params["discipline"] = filters["discipline"]
    if filters.get("project"):
        cond.append("ifnull(po.project, po.custom_cb_project) = %(project)s")
        params["project"] = filters["project"]
    rows = frappe.db.sql("""
        select po.custom_system as system,
               ifnull(nullif(po.project,''), po.custom_cb_project) as project,
               sum(poi.qty) as qty
        from `tabPurchase Order` po
        join `tabPurchase Order Item` poi on poi.parent = po.name
        where {cond} and ifnull(po.custom_system,'') != ''
          and (ifnull(po.project,'') != '' or ifnull(po.custom_cb_project,'') != '')
        group by po.custom_system, project
    """.format(cond=" and ".join(cond)), params, as_dict=True)
    return rows


def _material_requests(filters):
    cond = ["mr.docstatus = 1"]
    params = {}
    if filters.get("discipline"):
        cond.append("mr.custom_discipline = %(discipline)s")
        params["discipline"] = filters["discipline"]
    if filters.get("project"):
        cond.append("mr.custom_cb_project = %(project)s")
        params["project"] = filters["project"]
    rows = frappe.db.sql("""
        select mr.custom_system as system, mr.custom_cb_project as project, sum(mri.qty) as qty
        from `tabMaterial Request` mr
        join `tabMaterial Request Item` mri on mri.parent = mr.name
        where {cond} and ifnull(mr.custom_system,'') != '' and ifnull(mr.custom_cb_project,'') != ''
        group by mr.custom_system, mr.custom_cb_project
    """.format(cond=" and ".join(cond)), params, as_dict=True)
    return rows


def execute(filters=None):
    filters = filters or {}
    metric = filters.get("metric") or "已领用数量"

    if metric == "采购订单数量":
        rows = _purchase_orders(filters)
    elif metric == "采购申请数量":
        rows = _material_requests(filters)
    else:
        rows = _issued(filters)

    project_names = {}
    for p in frappe.get_all("Project", fields=["name", "project_name"], limit=0):
        project_names[p["name"]] = p["project_name"] or p["name"]

    data_map = {}
    projects = {}
    for r in rows:
        system = r["system"]
        project = r["project"]
        try:
            qty = float(r["qty"] or 0)
        except Exception:
            qty = 0.0
        projects[project] = project_names.get(project, project)
        key = (system, project)
        data_map[key] = data_map.get(key, 0.0) + qty

    if filters.get("project"):
        proj_list = [filters["project"]]
    else:
        ranked = sorted(
            {p for (_s, p) in data_map},
            key=lambda x: -sum(v for (_s, p), v in data_map.items() if p == x),
        )
        top_n = int(filters.get("top_projects") or 12)
        proj_list = ranked[:top_n]
        if len(ranked) > top_n:
            filters["_truncated"] = "显示前 %s 个项目（共 %s 个）" % (top_n, len(ranked))

    systems = frappe.get_all(
        "CB System",
        filters={"enabled": 1, **({"discipline": filters["discipline"]} if filters.get("discipline") else {})},
        fields=["name", "discipline", "system_name"],
        order_by="discipline asc, sort_order asc",
        limit=0,
    )

    columns = [
        {"label": "专业", "fieldname": "discipline", "fieldtype": "Link", "options": "CB Discipline", "width": 90},
        {"label": "系统", "fieldname": "system", "fieldtype": "Link", "options": "CB System", "width": 190},
    ]
    for p in proj_list:
        columns.append({
            "label": projects.get(p, project_names.get(p, p))[:24],
            "fieldname": "p_" + p.replace("-", "_"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 110,
        })
    columns.append({"label": "合计", "fieldname": "total", "fieldtype": "Float", "precision": 2, "width": 110})

    data = []
    for s in systems:
        row = {"discipline": s["discipline"], "system": s["name"], "total": 0.0}
        has_value = False
        for p in proj_list:
            qty = data_map.get((s["name"], p), 0.0)
            if qty:
                has_value = True
            row["p_" + p.replace("-", "_")] = qty
            row["total"] += qty
        if has_value or not filters.get("only_with_data", 1):
            data.append(row)

    data.sort(key=lambda r: (-r["total"], r["discipline"], r["system"]))
    message = "指标：%s；显示项目：%s；系统数：%s" % (metric, len(proj_list), len(data))
    if filters.get("_truncated"):
        message += "；" + filters["_truncated"]
    return columns, data, message
