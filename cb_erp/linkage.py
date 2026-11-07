import frappe
from frappe.utils import flt

# 单体材料全链条：设计量 → 请购量 → 下单量 → 到货量 → 领用量 → 安装量
# 每一环不得超过上一环（同 项目×专业×系统×物料 汇总）
# 受控物料走全链条；非受控物料（辅材/耗材）仍受项目+预算，但从项目库存放行、不卡设计量/系统。


def is_controlled(item_code):
    """物料是否受控：默认受控（字段为空按受控处理）。"""
    v = frappe.db.get_value("Item", item_code, "custom_controlled")
    return True if v is None else bool(v)


MODE_UNCONTROLLED = "不管控"
MODE_CONTROLLED_ONLY = "只管控受控物料"
MODE_ALL = "全管控"


def project_control_mode(project):
    """项目材料管控模式：不管控 / 只管控受控物料（默认） / 全管控。"""
    if not project:
        return MODE_CONTROLLED_ONLY
    try:
        v = frappe.db.get_value("Project", project, "custom_material_control_mode")
    except Exception:
        v = None
    return v or MODE_CONTROLLED_ONLY


def is_enforced(project, item_code):
    """本次是否执行全链条强控（设计量/请购/下单/到货/领用/安装）。"""
    mode = project_control_mode(project)
    if mode == MODE_UNCONTROLLED:
        return False
    if mode == MODE_ALL:
        return True
    return is_controlled(item_code)


def design_qty(project, discipline, system, item_code):
    return flt(frappe.db.sql(
        """select sum(i.qty * (1 + ifnull(i.loss_rate,0)/100))
           from `tabDesign BOM Item` i
           join `tabDesign BOM` b on b.name = i.parent
           join (select project, custom_discipline, custom_system, max(name) cur_bom
                 from `tabDesign BOM` where docstatus=1
                 group by project, custom_discipline, custom_system) cb on cb.cur_bom = b.name
           where b.project=%s and ifnull(b.custom_discipline,'')=%s
             and ifnull(b.custom_system,'')=%s and i.item_code=%s""",
        (project, discipline or "", system or "", item_code))[0][0])


def sum_source(src, project, discipline, system, item_code, exclude=None):
    p, d, s, it = project, discipline or "", system or "", item_code
    ex = exclude or ""
    if src == "mr":
        return flt(frappe.db.sql(
            """select sum(i.qty) from `tabMaterial Request Item` i
               join `tabMaterial Request` m on m.name=i.parent
               where m.docstatus=1 and ifnull(m.custom_cb_project,'')=%s
                 and ifnull(m.custom_discipline,'')=%s and ifnull(m.custom_system,'')=%s and i.item_code=%s""",
            (p, d, s, it))[0][0])
    if src == "po":
        return flt(frappe.db.sql(
            """select sum(i.qty) from `tabPurchase Order Item` i
               join `tabPurchase Order` m on m.name=i.parent
               where m.docstatus=1 and ifnull(m.custom_cb_project,'')=%s
                 and ifnull(m.custom_discipline,'')=%s and ifnull(m.custom_system,'')=%s and i.item_code=%s""",
            (p, d, s, it))[0][0])
    if src == "recv":
        return flt(frappe.db.sql(
            """select sum(d.qty) from `tabStock Entry Detail` d
               join `tabStock Entry` m on m.name=d.parent
               where m.docstatus=1 and m.purpose='Material Receipt'
                 and ifnull(m.project,'')=%s and ifnull(m.custom_discipline,'')=%s
                 and ifnull(m.custom_system,'')=%s and d.item_code=%s""",
            (p, d, s, it))[0][0])
    if src == "issue":
        return flt(frappe.db.sql(
            """select sum(d.qty) from `tabStock Entry Detail` d
               join `tabStock Entry` m on m.name=d.parent
               where m.docstatus=1 and m.purpose='Material Issue'
                 and ifnull(m.project,'')=%s and ifnull(m.custom_discipline,'')=%s
                 and ifnull(m.custom_system,'')=%s and d.item_code=%s""",
            (p, d, s, it))[0][0])
    if src == "installed":
        return flt(frappe.db.sql(
            """select sum(qty) from `tabCB Installation Record`
               where ifnull(project,'')=%s and ifnull(custom_discipline,'')=%s
                 and ifnull(custom_system,'')=%s and item_code=%s and name<>%s""",
            (p, d, s, it, ex))[0][0])
    return 0.0


def _pds(doc):
    return (doc.get("custom_cb_project") or doc.get("project"),
            doc.get("custom_discipline"), doc.get("custom_system"))


def on_mr_submit(doc, method=None):
    """请购量不得超过设计量。"""
    p, d, s = _pds(doc)
    if not p:
        return
    for row in doc.get("items") or []:
        it = row.get("item_code")
        if not it:
            continue
        if not is_enforced(p, it):
            continue
        design = design_qty(p, d, s, it)
        if design <= 0:
            frappe.throw("物料「%s」在项目「%s」无设计额度，禁止请购（全链条校验）" % (it, p))
        used = sum_source("mr", p, d, s, it)
        if used + flt(row.get("qty")) > design + 0.005:
            frappe.throw("物料「%s」请购超出设计量：已请购 %s + 本次 %s > 设计 %s（全链条校验）"
                         % (it, used, row.get("qty"), design))


def on_po_submit(doc, method=None):
    """下单量不得超过请购量（无请购依据不可下单）。"""
    p, d, s = _pds(doc)
    if not p:
        return
    for row in doc.get("items") or []:
        it = row.get("item_code")
        if not it:
            continue
        if not is_enforced(p, it):
            continue
        requested = sum_source("mr", p, d, s, it)
        if requested <= 0:
            frappe.throw("物料「%s」无已提交的请购额度，禁止下单（全链条校验）" % it)
        ordered = sum_source("po", p, d, s, it)
        if ordered + flt(row.get("qty")) > requested + 0.005:
            frappe.throw("物料「%s」下单超出请购量：已下单 %s + 本次 %s > 请购 %s（全链条校验）"
                         % (it, ordered, row.get("qty"), requested))


def on_se_submit(doc, method=None):
    """收货不超下单量；领用不超到货量、不超设计量。"""
    p = doc.get("project")
    if not p:
        return
    d, s = doc.get("custom_discipline"), doc.get("custom_system")
    purpose = doc.get("purpose")

    if purpose == "Material Receipt":
        for row in doc.get("items") or []:
            it = row.get("item_code")
            if not it:
                continue
            if not is_enforced(p, it):
                continue
            ordered = sum_source("po", p, d, s, it)
            received = sum_source("recv", p, d, s, it)
            if received + flt(row.get("qty")) > ordered + 0.005:
                frappe.throw("物料「%s」收货超出下单量：已收货 %s + 本次 %s > 下单 %s（全链条校验）"
                             % (it, received, row.get("qty"), ordered))
    elif purpose == "Material Issue":
        for row in doc.get("items") or []:
            it = row.get("item_code")
            if not it:
                continue
            if not is_enforced(p, it):
                continue
            received = sum_source("recv", p, d, s, it)
            issued = sum_source("issue", p, d, s, it)
            if issued + flt(row.get("qty")) > received + 0.005:
                frappe.throw("物料「%s」领用超出到货量：已领 %s + 本次 %s > 到货 %s（全链条校验）"
                             % (it, issued, row.get("qty"), received))
            design = design_qty(p, d, s, it)
            if issued + flt(row.get("qty")) > design + 0.005:
                frappe.throw("物料「%s」领用超出设计量：已领 %s + 本次 %s > 设计 %s（全链条校验）"
                             % (it, issued, row.get("qty"), design))


def on_install_validate(doc, method=None):
    """安装量不得超过领用量。"""
    p = doc.get("project")
    if not p:
        return
    d, s = doc.get("custom_discipline"), doc.get("custom_system")
    it = doc.get("item_code")
    if not it:
        return
    if not is_enforced(p, it):
        return
    issued = sum_source("issue", p, d, s, it)
    installed = sum_source("installed", p, d, s, it, exclude=doc.name)
    if installed + flt(doc.get("qty")) > issued + 0.005:
        frappe.throw("物料「%s」安装量超出领用量：已安装 %s + 本次 %s > 已领 %s（全链条校验）"
                     % (it, installed, doc.get("qty"), issued))
