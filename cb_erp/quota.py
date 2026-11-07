import frappe
from frappe.utils import flt


def _po_total(doc):
    total = flt(doc.get("total"))
    if total <= 0:
        total = sum(flt(r.get("amount")) for r in (doc.get("items") or []))
    return total


def validate_po_quota(doc, method=None):
    """采购下单额度校验：无预算不提交；已用 + 本单 不得超过预算总额。"""
    budget = doc.get("custom_cb_budget")
    if not budget:
        frappe.throw("采购订单未关联材料预算，无额度不可提交（严格额度校验）")

    if not frappe.db.exists("Material Budget", budget):
        frappe.throw("关联的材料预算不存在，无额度不可提交")

    budget_total = flt(frappe.db.get_value("Material Budget", budget, "total_amount"))
    if budget_total <= 0:
        frappe.throw("材料预算「%s」额度为 0，禁止下单" % budget)

    used = flt(frappe.db.sql(
        """select sum(total) from `tabPurchase Order`
           where docstatus=1 and custom_cb_budget=%s and name<>%s""",
        (budget, doc.name or ""))[0][0])

    this_total = _po_total(doc)
    if used + this_total > budget_total + 0.005:
        frappe.throw(
            "超出材料预算额度：已用 {0} + 本单 {1} = {2}，超出预算 {3}（严格额度校验）".format(
                used, this_total, used + this_total, budget_total))


def default_po_name(doc, method=None):
    """采购订单未填自定义名称时，用 项目名 / 供应商名 兜底，保证标题可读。"""
    if doc.get("custom_order_name"):
        return
    parts = []
    if doc.get("custom_cb_project"):
        parts.append(frappe.db.get_value("Project", doc.custom_cb_project, "project_name") or doc.custom_cb_project)
    if doc.get("supplier"):
        parts.append(frappe.db.get_value("Supplier", doc.supplier, "supplier_name") or doc.supplier)
    doc.custom_order_name = " / ".join(parts)


def validate_receipt_project(doc, method=None):
    """采购入库（收货）必须指定项目与专业，保证到货量能按项目/专业归集。"""
    if doc.get("purpose") != "Material Receipt":
        return
    if not doc.get("project"):
        frappe.throw("采购入库（收货）必须指定项目，否则到货量无法归集（严格归集校验）")
    if not doc.get("custom_discipline"):
        frappe.throw("采购入库（收货）必须指定专业（辅材也要求专业），否则无法归集（严格归集校验）")


def _is_controlled(item_code):
    v = frappe.db.get_value("Item", item_code, "custom_controlled")
    return True if v is None else bool(v)


def _design_qty(project, discipline, system, item_code):
    # 取该项目/专业/系统的「当前有效版本」BOM，避免多版本重复累加
    return flt(frappe.db.sql(
        """select sum(i.qty * (1 + ifnull(i.loss_rate,0)/100))
           from `tabDesign BOM Item` i
           join `tabDesign BOM` b on b.name = i.parent
           join (select project, custom_discipline, custom_system, max(name) cur_bom
                 from `tabDesign BOM` where docstatus=1
                 group by project, custom_discipline, custom_system) cb on cb.cur_bom = b.name
           where b.project=%s
             and ifnull(b.custom_discipline,'')=%s
             and ifnull(b.custom_system,'')=%s
             and i.item_code=%s""",
        (project, discipline or "", system or "", item_code))[0][0])


def _issued_qty(project, discipline, system, item_code, exclude_name):
    return flt(frappe.db.sql(
        """select sum(d.qty) from `tabStock Entry Detail` d
           join `tabStock Entry` s on s.name = d.parent
           where s.docstatus=1 and s.purpose='Material Issue' and s.name<>%s
             and ifnull(s.project,'')=%s
             and ifnull(s.custom_discipline,'')=%s
             and ifnull(s.custom_system,'')=%s
             and d.item_code=%s""",
        (exclude_name or "", project, discipline or "", system or "", item_code))[0][0])


def validate_issue_quota(doc, method=None):
    """领用额度校验：必须有项目+专业；受控物料（或全管控项目）不得超过设计量。"""
    if doc.get("purpose") != "Material Issue":
        return

    project = doc.get("project")
    if not project:
        frappe.throw("领用必须指定项目，无项目即无设计额度，禁止提交（严格额度校验）")
    if not doc.get("custom_discipline"):
        frappe.throw("领用必须指定专业（辅材也要求专业），否则无法归集（严格归集校验）")

    disc = doc.get("custom_discipline")
    system = doc.get("custom_system")

    from cb_erp.cb_erp.linkage import is_enforced

    for row in (doc.get("items") or []):
        item = row.get("item_code")
        if not item:
            continue
        if not is_enforced(project, item):
            continue
        qty = flt(row.get("qty"))
        design = _design_qty(project, disc, system, item)
        if design <= 0:
            frappe.throw("物料「%s」在项目「%s」无设计额度，禁止领用（严格额度校验）" % (item, project))
        issued = _issued_qty(project, disc, system, item, doc.name)
        if issued + qty > design + 0.005:
            frappe.throw(
                "物料「{0}」超出设计额度：已领 {1} + 本次 {2} = {3} > 设计额度 {4}（严格额度校验）".format(
                    item, issued, qty, issued + qty, design))


@frappe.whitelist()
def check_issue_quota(project, discipline=None, system=None, item_code=None, qty=0, name=None):
    """前端/接口预检查：返回是否还有额度（不抛错）。"""
    design = _design_qty(project, discipline, system, item_code)
    issued = _issued_qty(project, discipline, system, item_code, name)
    remaining = design - issued
    ok = design > 0 and (issued + flt(qty) <= design + 0.005)
    return {"design": design, "issued": issued, "remaining": remaining, "ok": ok}
