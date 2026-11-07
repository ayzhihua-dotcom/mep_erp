# -*- coding: utf-8 -*-
# S5 / TP-CST-004 进口费用分摊（IMP-009）
# 承载形态：custom DocType "CB Import Allocation"，控制器逻辑经 hooks.doc_events 挂接
# （全应用现有 CB DocType 为 custom 形态，无 .py 控制器类，统一走 doc_events）。
# 行为对齐《S5_开发任务书_TP-CST-004_进口费用分摊.md》§2.3：
#   1) 费用总额=分摊合计（逐费用行内平衡，舍入差额定向归末行）
#   2) 回写 CB Import Cost.allocated_amount + 收货单（Stock Entry 草稿）行 basic_rate
#   3) 分摊过程留痕 CB Cost Audit Log；重复分摊拦截（UC-AL04）
# 分摊基础默认映射（S5-AL2，E5-3 决策见台账，草案待追认）：
#   关税/增值税/保险费/其他 → 金额占比；清关费/内陆运输费 → 数量；毛重/体积缺基础数据 → 数量回退并登记。

import frappe
from frappe import _
from frappe.utils import flt

# 站点 BRL 报价精度按 2 位小数（分摊平衡即声称到分摊合计位，逐行单价做 2 位舍入）
PREC = 2

BASIS_DEFAULT = {
    "关税": "金额占比",
    "增值税": "金额占比",
    "保险费": "金额占比",
    "其他": "金额占比",
    "清关费": "数量",
    "内陆运输费": "数量",
}
_BASIS_FALLBACK_BASES = ("毛重", "体积")


def validate_allocation(doc, method=None):
    """每次保存重算：装载案件费用 → 校验收货单草稿 → 重构建费用行/分摊明细 → 合计与重复分摊校验。"""
    _recompute(doc)
    _check_duplicate(doc)


def before_submit_allocation(doc, method=None):
    """提交前复核：收货单须仍为草稿、重算后的费用总额=分摊合计。"""
    _recompute(doc)
    _check_duplicate(doc)
    se = frappe.get_doc("Stock Entry", doc.target_entry)
    if se.docstatus != 0:
        frappe.throw(_("目标收货单 {0} 已不是草稿（docstatus={1}），分摊须在提交收货单之前完成").format(
            se.name, se.docstatus))
    if flt(doc.total_costs, PREC) != flt(doc.total_allocated, PREC):
        frappe.throw(_("费用总额（{0}）与分摊合计（{1}）不一致，禁止提交").format(
            frappe.utils.fmt_money(doc.total_costs), frappe.utils.fmt_money(doc.total_allocated)))


def on_submit_allocation(doc, method=None):
    """提交：回写 CB Import Cost.allocated_amount / SE 行 basic_rate（含费单价）→ 审计留痕。"""
    se = frappe.get_doc("Stock Entry", doc.target_entry)
    if se.docstatus != 0:
        frappe.throw(_("目标收货单 {0} 已提交/已取消，分摊单不允许在此状态下提交").format(se.name))
    _writeback_se(doc, submit=True)
    _writeback_import_cost(doc, submit=True)
    _audit(doc, "提交分摊",
           "费用总额 {0} 已分摊至收货单 {1}：{2}".format(
               flt(doc.total_costs, PREC), se.name,
               "; ".join("{0}:{1}({2})".format(r.item_code, r.se_row, flt(r.add_amount, PREC))
                         for r in doc.allocation_items)))


def on_cancel_allocation(doc, method=None):
    """取消：恢复 SE 行原 basic_rate（仅收货单仍处草稿时）/ Import Cost 回写清零 → 审计留痕。
    三态：SE 草稿 → 恢复行值并清回写；SE 已取消（含联动取消/已被删除）→ 仅清回写；SE 已提交 → 拒绝。"""
    try:
        se = frappe.get_doc("Stock Entry", doc.target_entry)
    except Exception:
        se = None
    if se and se.docstatus == 1:
        frappe.throw(_("收货单 {0} 已提交，须先取消收货单再取消分摊").format(se.name))
    restore_rows = bool(se) and se.docstatus == 0
    if restore_rows:
        _writeback_se(doc, submit=False)
    _writeback_import_cost(doc, submit=False)
    _audit(doc, "取消分摊",
           "分摊 {0} 已取消{1}".format(
               doc.name,
               "，收货单 {0} 行单价恢复原值".format(se.name) if restore_rows
               else "；收货单 {0} 已取消或已删除（行值无会计意义，仅清费用回写）".format(se.name if se else doc.target_entry)))


# ------------------------------------------------------------------ 内部实现

def _recompute(doc):
    if not doc.import_case:
        frappe.throw(_("请选择进口案件"))
    if not doc.target_entry:
        frappe.throw(_("请选择目标收货单"))
    case = frappe.get_doc("CB Import Case", doc.import_case)
    if not case.costs:
        frappe.throw(_("进口案件 {0} 没有费用行，无法分摊").format(case.name))
    se = frappe.get_doc("Stock Entry", doc.target_entry)
    if se.docstatus != 0 and doc.docstatus == 0:
        frappe.throw(_("目标收货单 {0} 已不是草稿（docstatus={1}），已提交收货单不可再分摊").format(
            se.name, se.docstatus))
    company_currency = frappe.get_cached_value("Company", doc.company, "default_currency") if doc.company else None
    if company_currency and any((r.currency or company_currency) != company_currency for r in case.costs):
        frappe.throw(_("案件费用存在非公司本位币（{0}）行，暂不支持跨币种分摊").format(company_currency))

    # 收货行基数据（qty>0；货值 = qty × 行 basic_rate 原值）
    rows = []
    for row in se.items:
        if flt(row.qty, 6) <= 0:
            continue
        rate = flt(row.basic_rate, PREC + 4)
        rows.append({
            "name": row.name,
            "item_code": row.item_code,
            "project": row.get("project"),
            "qty": flt(row.qty, 6),
            "orig_rate": rate,
            "goods": flt(row.qty * rate, PREC),
        })
    if not rows:
        frappe.throw(_("收货单 {0} 没有数量大于 0 的明细行").format(se.name))

    # 保留用户已选分摊基础；未选择者按费用类型默认映射（S5-AL2 代拟草案）
    old_basis = {r.cost_row: r.alloc_basis for r in doc.costs_allocated or []}
    doc.set("costs_allocated", [])
    doc.set("allocation_items", [])

    add_by_row = {r["name"]: 0.0 for r in rows}
    goods_by_row = {r["name"]: r["goods"] for r in rows}
    total_costs = 0.0
    total_allocated = 0.0

    for crow in case.costs:
        amount = flt(crow.amount, PREC)
        basis, fallback = _resolve_basis(crow, old_basis)
        mags = []
        total_mag = 0.0
        for r in rows:
            mag = _row_basis(r, basis)
            mags.append(mag)
            total_mag += mag
        if flt(total_mag, PREC + 4) <= 0:
            frappe.throw(_("费用「{0}」的分摊基础（{1}）合计为零，无法分摊").format(crow.cost_type, basis))
        # 逐行占比分配（2 位舍入），舍入差额定向归末行（任务书 §2.3）
        allocs = [flt(amount * m / total_mag, PREC) for m in mags]
        rounding = flt(amount - sum(allocs), PREC)
        allocs[-1] = flt(allocs[-1] + rounding, PREC)
        for r, a in zip(rows, allocs):
            add_by_row[r["name"]] = flt(add_by_row[r["name"]] + a, PREC)
        total_costs = flt(total_costs + amount, PREC)
        total_allocated = flt(total_allocated + crow.amount, PREC)
        doc.append("costs_allocated", {
            "cost_row": crow.name if crow.name else "{0}-{1:03d}".format(case.name, crow.idx),
            "cost_type": crow.cost_type,
            "currency": crow.currency or company_currency or "BRL",
            "amount": amount,
            "alloc_basis": basis,
            "fallback_note": _basis_note(fallback, crow),
            "base_magnitude": flt(total_mag, PREC),
            "allocated_amount": crow.amount,
        })

    item_diff = 0.0
    for r in rows:
        add = add_by_row[r["name"]]
        new_rate = flt(r["orig_rate"] + add / r["qty"], PREC)
        new_amount = flt(r["qty"] * new_rate, PREC)
        item_diff = flt(item_diff + new_amount - (r["goods"] + add), PREC)
        doc.append("allocation_items", {
            "se_row": r["name"],
            "item_code": r["item_code"],
            "project": r.get("project"),
            "qty": r["qty"],
            "goods_amount": r["goods"],
            "add_amount": add,
            "new_basic_rate": new_rate,
            "new_basic_amount": new_amount,
        })

    doc.total_costs = total_costs
    doc.total_allocated = total_allocated
    doc.rounding_diff = item_diff  # 单价 2 位舍入在明细金额上的残差（信息值，费用行内已精确平衡）


def _resolve_basis(crow, old_basis):
    """返回（生效分摊基础, 基础回退说明）；毛重/体积为本站无基础数据的选项 → 按数量回退并登记（S5-AL2 代拟）。"""
    chosen = old_basis.get(crow.name) or BASIS_DEFAULT.get(crow.cost_type) or "金额占比"
    if chosen in _BASIS_FALLBACK_BASES:
        return "数量", "「{0}」基础数据缺失，按数量回退".format(chosen)
    return chosen, ""


def _basis_note(fallback, crow):
    return fallback or ""


def _row_basis(r, basis):
    if basis == "金额占比":
        return r["goods"]
    return r["qty"]  # 数量（毛重/体积缺基础数据时同按数量回退）


def _check_duplicate(doc):
    # UC-AL04：a) 同一收货单已有已提交分摊单 → 拦截；b) 同一案件的费用行已被另一张
    # 已提交分摊单占用（allocated_amount>0 且 allocation 为已提交单）→ 拦截，防同笔费用重复入成本。
    dup = frappe.db.sql(
        """select name from `tabCB Import Allocation`
           where target_entry = %(t)s and docstatus = 1 and name != %(me)s
           limit 1""",
        {"t": doc.target_entry, "me": doc.name}, as_dict=1)
    if dup:
        frappe.throw(_("重复分摊（UC-AL04）：收货单 {0} 已存在已提交的分摊单 {1}，禁止再次分摊").format(
            doc.target_entry, dup[0].name))
    if doc.import_case:
        taken = frappe.get_all(
            "CB Import Cost",
            filters={"parenttype": "CB Import Case", "parent": doc.import_case,
                     "allocated_amount": [">", 0]},
            fields=["name", "allocation"], limit=5)
        cost_rows = {c.name for c in frappe.get_all(
            "CB Import Cost", filters={"parenttype": "CB Import Case", "parent": doc.import_case},
            fields=["name"]) or []}
    for row in taken:
        if row.name not in cost_rows:
            continue
        other = row.allocation
        if not other or other == doc.name:
            continue
        if frappe.db.get_value("CB Import Allocation", other, "docstatus") == 1:
            frappe.throw(_("重复分摊（UC-AL04）：费用行 {0} 已由已提交分摊单 {1} 占用，禁止再次分摊").format(
                row.name, other))


def _writeback_se(doc, submit=True):
    for item in doc.allocation_items:
        if not item.se_row:
            continue
        if submit:
            rate = item.new_basic_rate
            amount = item.new_basic_amount
        else:
            rate = flt(item.goods_amount / item.qty, PREC + 4) if item.qty else 0
            amount = flt(item.qty * rate, PREC)
        vals = {"basic_rate": rate}
        if frappe.get_meta("Stock Entry Detail").get_field("basic_amount"):
            vals["basic_amount"] = amount
        frappe.db.set_value("Stock Entry Detail", item.se_row, vals, update_modified=False)


def _writeback_import_cost(doc, submit=True):
    resp = {}
    for item in doc.costs_allocated:
        if item.cost_row and frappe.db.exists("CB Import Cost", {"name": item.cost_row}):
            resp[item.cost_row] = item.allocated_amount if submit else 0
    for row_name, amt in resp.items():
        frappe.db.set_value("CB Import Cost", row_name, {
            "allocated_amount": amt,
            "allocation": doc.name if submit else None,
        }, update_modified=False)


def on_se_cancel(doc, method=None):
    """收货单取消时兜底：把指向本单的（可能已被联动取消的）已提交分摊单的 Import Cost
    回写清零。实证：联动取消不派发 CB Import Allocation 的 on_cancel doc_event，
    故必须在收货单取消侧完成一致性收口（台账 S5-A 批登记）。"""
    names = frappe.get_all("CB Import Allocation", filters={"target_entry": doc.name}, pluck="name")
    for n in names:
        try:
            alc = frappe.get_doc("CB Import Allocation", n)
        except Exception:
            continue
        _writeback_import_cost(alc, submit=False)
        if frappe.db.exists("CB Cost Audit Log", {"allocation": n, "event": "取消分摊"}) is None:
            _audit(alc, "取消分摊", "收货单 {0} 取消，分摊 {1} 终结，费用回写清零（收货单取消兜底）".format(doc.name, n))


def _audit(doc, event, detail):
    frappe.get_doc({
        "doctype": "CB Cost Audit Log",
        "allocation": doc.name,
        "import_case": doc.import_case,
        "target_entry": doc.target_entry,
        "event": event,
        "allocated_total": doc.total_costs,
        "detail": detail,
    }).insert(ignore_permissions=True)
