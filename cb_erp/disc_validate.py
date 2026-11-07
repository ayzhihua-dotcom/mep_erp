# -*- coding: utf-8 -*-
"""专业/系统 联动校验 + 项目专业系统配置回填。"""
import frappe

DOC_TYPES = [
    "Material Request", "Purchase Order", "Stock Entry", "Stock Reconciliation",
    "Material Budget", "Material Commitment", "Design BOM", "Design Change Request",
    "CB Shipment", "CB Import Case",
]
PROJECT_FIELD = {"Material Request": "custom_cb_project", "Purchase Order": "custom_cb_project"}


def _project_of(doc):
    for f in ("custom_cb_project", "project"):
        if doc.get(f):
            return doc.get(f)
    if doc.doctype == "Stock Entry":
        ps = {r.get("project") for r in (doc.get("items") or []) if r.get("project")}
        if len(ps) == 1:
            return ps.pop()
    return None


def _item_rows(doc):
    for f in ("items", "bom_items", "budget_items", "change_items", "supplied_items"):
        rows = doc.get(f)
        if rows:
            return rows
    return []


def _all_uncontrolled(rows):
    from cb_erp.cb_erp.linkage import is_controlled
    any_item = False
    for r in rows:
        code = r.get("item_code")
        if not code:
            continue
        any_item = True
        if is_controlled(code):
            return False
    return any_item


def validate_doc(doc, method=None):
    d = (doc.get("custom_discipline") or "").strip()
    s = (doc.get("custom_system") or "").strip()
    project = _project_of(doc)

    # 非受控物料（辅材/耗材/通用备料）：只要求专业，不要求系统
    rows = _item_rows(doc)
    if rows and _all_uncontrolled(rows):
        if not d:
            frappe.throw("请选择「专业」（非受控物料可不选系统）")
        return

    if not d and not s:
        # 历史单据允许保持为空；新建且挂项目时必须先区分专业/系统
        if doc.is_new() and project:
            frappe.throw("请先选择「专业」与「系统」（当前项目：%s）。"
                         "若该项目尚未配置专业系统，请先到项目里建立。" % project)
        return

    if not d or not s:
        frappe.throw("「专业」与「系统」必须同时填写")

    sys_disc = frappe.db.get_value("CB System", s, "discipline")
    if not sys_disc:
        frappe.throw("系统「%s」不存在，请在「系统」主数据中维护" % s)
    if sys_disc != d:
        frappe.throw("系统「%s」属于专业「%s」，与所选专业「%s」不一致" % (s, sys_disc, d))

    if project and frappe.db.exists("Project", project):
        rows = frappe.get_all("CB Project System", filters={"parent": project},
                              fields=["discipline", "system"])
        if rows and not any(r["discipline"] == d and r["system"] == s for r in rows):
            frappe.throw("「%s / %s」不在项目「%s」已配置的专业系统清单内，请先在项目里添加" % (d, s, project))


def project_validate(doc, method=None):
    rows = doc.get("custom_project_systems") or []
    if doc.is_new() and not rows:
        frappe.throw("新建项目请先建立「项目专业与系统」（可点右上角「载入标准专业与系统」一键生成）")

    seen = set()
    for r in rows:
        if not r.get("discipline") or not r.get("system"):
            frappe.throw("项目专业与系统：第 %s 行专业/系统不能为空" % r.idx)
        sys_disc = frappe.db.get_value("CB System", r.get("system"), "discipline")
        if sys_disc != r.get("discipline"):
            frappe.throw("第 %s 行：系统「%s」不属于专业「%s」" % (r.idx, r.get("system"), r.get("discipline")))
        key = (r.get("discipline"), r.get("system"))
        if key in seen:
            frappe.throw("第 %s 行：专业/系统重复" % r.idx)
        seen.add(key)


# ---------------------------------------------------------------- 回填
def _doc_pairs(project):
    pairs = set()
    sources = [
        ("Material Request", "custom_cb_project"),
        ("Purchase Order", "project"),
        ("Purchase Order", "custom_cb_project"),
        ("Stock Entry", "project"),
        ("Material Budget", "project"),
        ("Material Commitment", "project"),
        ("Design BOM", "project"),
        ("Stock Reconciliation", None),
    ]
    for dt, field in sources:
        if not field or not frappe.db.has_column(dt, field):
            continue
        if not frappe.db.has_column(dt, "custom_discipline"):
            continue
        rows = frappe.get_all(dt, filters={field: project},
                              fields=["custom_discipline", "custom_system"], limit=0)
        for r in rows:
            if r.get("custom_discipline") and r.get("custom_system"):
                pairs.add((r["custom_discipline"], r["custom_system"]))
    return pairs


def backfill_projects(fill_all=False):
    """把项目里已发生的专业/系统回填到项目配置；没有单据的项目可选择填充全部标准系统。"""
    frappe.set_user("Administrator")
    all_systems = frappe.get_all("CB System", fields=["name", "discipline"], limit=0)
    projects = frappe.get_all("Project", fields=["name"], limit=0)
    filled = 0
    for p in projects:
        name = p["name"]
        if frappe.db.count("CB Project System", {"parent": name}):
            continue
        pairs = _doc_pairs(name)
        if not pairs and fill_all:
            pairs = {(s["discipline"], s["name"]) for s in all_systems}
        if not pairs:
            continue
        doc = frappe.get_doc("Project", name)
        for d, s in sorted(pairs):
            doc.append("custom_project_systems", {"discipline": d, "system": s})
        doc.flags.ignore_validate = True
        doc.save(ignore_permissions=True)
        filled += 1
    frappe.db.commit()
    frappe.clear_cache()
    print("PROJECTS_FILLED:", filled, "of", len(projects))
    return filled


def value_audit():
    """检查所有单据里的专业/系统值是否都能对上主数据。"""
    bad = []
    for dt in DOC_TYPES:
        if not frappe.db.has_column(dt, "custom_discipline"):
            continue
        rows = frappe.db.sql("""select name, ifnull(custom_discipline,'') d, ifnull(custom_system,'') s
                                from `tab%s`
                                where ifnull(custom_discipline,'')!='' or ifnull(custom_system,'')!=''""" % dt,
                             as_dict=True)
        for r in rows:
            ok = True
            if not r["d"] or not r["s"]:
                ok = False
            else:
                sd = frappe.db.get_value("CB System", r["s"], "discipline")
                ok = bool(sd) and sd == r["d"]
            if not ok:
                bad.append((dt, r["name"], r["d"], r["s"]))
    print("BAD_VALUES:", len(bad))
    for b in bad[:20]:
        print("   ", b)
    return bad


def run():
    frappe.set_user("Administrator")
    value_audit()
    backfill_projects(fill_all=False)
    value_audit()
    return "DISC_ENFORCE_READY"


@frappe.whitelist()
def load_standard_systems():
    """返回全部启用的专业/系统，供项目「载入标准专业与系统」按钮使用。"""
    return frappe.get_all("CB System", filters={"enabled": 1},
                          fields=["name", "discipline", "system_name"],
                          order_by="discipline asc, sort_order asc", limit=0)
