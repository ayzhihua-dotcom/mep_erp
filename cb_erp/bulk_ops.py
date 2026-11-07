# -*- coding: utf-8 -*-
# 批量业务后端：把多行数据合并成尽量少的单据（MR / 入库 / 领料 / 退料 / 盘点）
# 供：批量录入页（粘贴/Excel）与 CSV 导入共用。
import csv
import io
import json
import base64
import frappe
from frappe.utils import today, add_days, flt

DEFAULT_COMPANY = "中巴机电（巴西）项目有限公司"


def _rows(rows):
    if isinstance(rows, str):
        rows = frappe.parse_json(rows)
    return rows or []


def _rate(item_code, rate=None):
    if rate not in (None, ""):
        return flt(rate)
    return flt(frappe.db.get_value("Item", item_code, "valuation_rate")) or 100.0


def _uom(item_code):
    return frappe.db.get_value("Item", item_code, "stock_uom") or "Nos"


def _group(rows, key):
    g = {}
    for r in rows:
        g.setdefault((r.get(key) or "").strip(), []).append(r)
    return g


def _mk_line(child_dt, r, seq=None, use_project=None, responsible=None, **extra):
    d = {"item_code": r["item_code"], "qty": flt(r["qty"])}
    d.update(extra)
    meta = frappe.get_meta(child_dt)
    nm = r.get("item_name") or frappe.db.get_value("Item", r["item_code"], "item_name")
    if meta.has_field("item_name") and nm:
        d["item_name"] = nm
    if meta.has_field("custom_item_name") and nm:
        d["custom_item_name"] = nm
    if meta.has_field("custom_seq") and seq is not None:
        d["custom_seq"] = seq
    if meta.has_field("custom_uom"):
        d["custom_uom"] = r.get("unit") or frappe.db.get_value("Item", r["item_code"], "stock_uom")
    if meta.has_field("custom_use_project"):
        d["custom_use_project"] = use_project or r.get("project")
    if meta.has_field("custom_responsible") and responsible:
        d["custom_responsible"] = responsible
    if meta.has_field("custom_spec") and r.get("spec"):
        d["custom_spec"] = r["spec"]
    if meta.has_field("custom_remark") and r.get("remark"):
        d["custom_remark"] = r["remark"]
    return d


def _submit(doc, discipline=None, system=None, responsible=None):
    if discipline and doc.meta.has_field("custom_discipline"):
        doc.custom_discipline = discipline
    if system and doc.meta.has_field("custom_system"):
        doc.custom_system = system
    if responsible and doc.meta.has_field("custom_responsible"):
        doc.custom_responsible = responsible
    doc.insert(ignore_permissions=True)
    doc.submit()
    frappe.db.commit()
    return doc.name


@frappe.whitelist()
def api_create(kind, rows, project=None, warehouse=None, company=None, posting_date=None,
               discipline=None, system=None, responsible=None,
               supplier=None, budget=None, order_name=None):
    """kind: material_request | material_receipt | material_issue | material_return | stock_reconciliation | purchase_order"""
    rows = _rows(rows)
    if not rows:
        return {"created": [], "errors": ["no rows"], "count": 0}
    company = company or DEFAULT_COMPANY
    posting_date = posting_date or today()
    created, errors = [], []

    if kind == "material_request":
        groups = _group(rows, "project")
        for proj, rws in groups.items():
            try:
                items = [_mk_line("Material Request Item", r, seq=i + 1, use_project=proj or project,
                                  responsible=responsible,
                                  schedule_date=r.get("schedule_date") or add_days(today(), 7)) for i, r in enumerate(rws)]
                d = frappe.get_doc({"doctype": "Material Request", "material_request_type": "Purchase",
                                    "company": company, "custom_cb_project": proj or project,
                                    "schedule_date": add_days(today(), 7), "items": items})
                created.append({"kind": kind, "name": _submit(d, discipline, system, responsible), "rows": len(items), "group": proj or project})
            except Exception as e:
                frappe.db.rollback(); errors.append("%s: %s" % (proj, repr(e)[:200]))

    elif kind == "material_receipt":
        groups = _group(rows, "warehouse")
        for wh, rws in groups.items():
            wh = wh or warehouse
            try:
                items = [_mk_line("Stock Entry Detail", r, seq=i + 1, use_project=project, responsible=responsible,
                                  t_warehouse=wh, uom=_uom(r["item_code"]),
                                  basic_rate=_rate(r["item_code"], r.get("rate")),
                                  project=r.get("project")) for i, r in enumerate(rws)]
                d = frappe.get_doc({"doctype": "Stock Entry", "stock_entry_type": "Material Receipt",
                                    "company": company, "posting_date": posting_date, "items": items})
                created.append({"kind": kind, "name": _submit(d, discipline, system, responsible), "rows": len(items), "group": wh})
            except Exception as e:
                frappe.db.rollback(); errors.append("%s: %s" % (wh, repr(e)[:200]))

    elif kind == "material_issue":
        groups = _group(rows, "project")
        for proj, rws in groups.items():
            proj = proj or project
            try:
                items = [_mk_line("Stock Entry Detail", r, seq=i + 1, use_project=proj, responsible=responsible,
                                  s_warehouse=r.get("warehouse") or warehouse, uom=_uom(r["item_code"]),
                                  basic_rate=_rate(r["item_code"], r.get("rate")),
                                  project=proj) for i, r in enumerate(rws)]
                d = frappe.get_doc({"doctype": "Stock Entry", "stock_entry_type": "Material Issue",
                                    "company": company, "posting_date": posting_date, "project": proj, "items": items})
                created.append({"kind": kind, "name": _submit(d, discipline, system, responsible), "rows": len(items), "group": proj})
            except Exception as e:
                frappe.db.rollback(); errors.append("%s: %s" % (proj, repr(e)[:200]))

    elif kind == "material_return":
        groups = _group(rows, "project")
        for proj, rws in groups.items():
            proj = proj or project
            try:
                items = [_mk_line("Stock Entry Detail", r, seq=i + 1, use_project=proj, responsible=responsible,
                                  t_warehouse=r.get("warehouse") or warehouse, uom=_uom(r["item_code"]),
                                  basic_rate=_rate(r["item_code"], r.get("rate")),
                                  project=proj, against_stock_entry=r.get("against_stock_entry")) for i, r in enumerate(rws)]
                d = frappe.get_doc({"doctype": "Stock Entry", "stock_entry_type": "Material Receipt",
                                    "company": company, "posting_date": posting_date, "is_return": 1,
                                    "project": proj, "remarks": "批量退料入库", "items": items})
                created.append({"kind": kind, "name": _submit(d, discipline, system, responsible), "rows": len(items), "group": proj})
            except Exception as e:
                frappe.db.rollback(); errors.append("%s: %s" % (proj, repr(e)[:200]))

    elif kind == "stock_reconciliation":
        groups = _group(rows, "warehouse")
        for wh, rws in groups.items():
            wh = wh or warehouse
            try:
                items = [_mk_line("Stock Reconciliation Item", r, seq=i + 1, use_project=project, responsible=responsible,
                                  warehouse=wh, valuation_rate=_rate(r["item_code"], r.get("rate"))) for i, r in enumerate(rws)]
                hdr = {"doctype": "Stock Reconciliation", "company": company, "purpose": "Stock Reconciliation",
                       "posting_date": posting_date, "set_warehouse": wh, "project": project, "items": items}
                exp = frappe.db.get_value("Company", company, "stock_adjustment_account")
                if exp:
                    hdr["expense_account"] = exp
                d = frappe.get_doc(hdr)
                created.append({"kind": kind, "name": _submit(d, discipline, system, responsible), "rows": len(items), "group": wh})
            except Exception as e:
                frappe.db.rollback(); errors.append("%s: %s" % (wh, repr(e)[:200]))
    elif kind == "purchase_order":
        if not supplier:
            return {"created": [], "errors": ["请选择供应商"], "count": 0}
        groups = _group(rows, "project")
        for proj, rws in groups.items():
            proj = proj or project
            try:
                items = []
                for r in rws:
                    items.append({
                        "item_code": r["item_code"],
                        "item_name": r.get("item_name") or frappe.db.get_value("Item", r["item_code"], "item_name"),
                        "qty": flt(r.get("qty")),
                        "uom": r.get("unit") or _uom(r["item_code"]),
                        "rate": _rate(r["item_code"], r.get("rate")),
                        "schedule_date": r.get("schedule_date") or add_days(today(), 7),
                        "warehouse": r.get("warehouse") or warehouse,
                    })
                d = frappe.get_doc({
                    "doctype": "Purchase Order", "company": company, "supplier": supplier,
                    "transaction_date": posting_date,
                    "custom_cb_project": proj, "custom_discipline": discipline,
                    "custom_system": system, "custom_cb_budget": budget,
                    "custom_order_name": order_name or ("批量下单 " + str(posting_date or today())),
                    "items": items,
                })
                d.insert(ignore_permissions=True)
                frappe.db.commit()
                created.append({"kind": kind, "name": d.name, "rows": len(items), "group": proj})
            except Exception as e:
                frappe.db.rollback(); errors.append("%s: %s" % (proj, repr(e)[:200]))
    else:
        return {"created": [], "errors": ["unknown kind: %s" % kind], "count": 0}

    return {"created": created, "errors": errors, "count": len(created),
            "total_rows": sum(c["rows"] for c in created)}


def _parse_file(content, filename):
    name = (filename or "").lower()
    rows = []
    if name.endswith(".xlsx") or name.endswith(".xlsm"):
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        ws = wb.active
        it = ws.iter_rows(values_only=True)
        header = [str(c).strip() if c is not None else "" for c in next(it)]
        for vals in it:
            if not any(v not in (None, "") for v in vals):
                continue
            rows.append({header[i]: vals[i] for i in range(len(header)) if i < len(vals) and header[i]})
    elif name.endswith(".xls"):
        try:
            import xlrd
        except Exception:
            frappe.throw("暂不支持旧版 .xls，请在 Excel 中另存为 .xlsx 或 .csv 后再导入")
        wb = xlrd.open_workbook(file_contents=content)
        ws = wb.sheet_by_index(0)
        header = [str(ws.cell_value(0, c)).strip() for c in range(ws.ncols)]
        for r in range(1, ws.nrows):
            vals = [ws.cell_value(r, c) for c in range(ws.ncols)]
            if not any(v not in (None, "") for v in vals):
                continue
            rows.append({header[i]: vals[i] for i in range(len(header)) if header[i]})
    else:
        text = content.decode("utf-8-sig", errors="replace")
        rdr = csv.DictReader(io.StringIO(text))
        for r in rdr:
            rows.append({(k or "").strip(): v for k, v in r.items()})
    return rows


@frappe.whitelist()
def api_import_file(kind, project=None, warehouse=None, company=None, posting_date=None,
                    discipline=None, system=None, responsible=None,
                    supplier=None, budget=None, order_name=None):
    f = frappe.request.files.get("file")
    if not f:
        frappe.throw("未收到文件")
    content = f.read()
    rows = _parse_file(content, getattr(f, "filename", ""))
    return api_create(kind, rows, project=project, warehouse=warehouse, company=company,
                      posting_date=posting_date, discipline=discipline, system=system, responsible=responsible,
                      supplier=supplier, budget=budget, order_name=order_name)


@frappe.whitelist()
def api_preview(rows):
    rows = _rows(rows)
    return {"rows": rows[:50], "total": len(rows)}


@frappe.whitelist()
def api_bulk_submit(doctype, names):
    """列表多选批量提交：仅提交选中的草稿单据。"""
    names = _rows(names) if isinstance(names, str) else (names or [])
    ok, err = [], []
    for n in names:
        try:
            d = frappe.get_doc(doctype, n)
            if d.docstatus == 0:
                d.submit()
                frappe.db.commit()
                ok.append(n)
            else:
                err.append("%s: 非草稿(docstatus=%s)" % (n, d.docstatus))
        except Exception as e:
            frappe.db.rollback()
            err.append("%s: %s" % (n, repr(e)[:150]))
    return {"ok": ok, "err": err, "count": len(ok)}


@frappe.whitelist()
def api_bulk_cancel(doctype, names):
    names = _rows(names) if isinstance(names, str) else (names or [])
    ok, err = [], []
    for n in names:
        try:
            d = frappe.get_doc(doctype, n)
            if d.docstatus == 1:
                d.cancel()
                frappe.db.commit()
                ok.append(n)
            else:
                err.append("%s: 非已提交(docstatus=%s)" % (n, d.docstatus))
        except Exception as e:
            frappe.db.rollback()
            err.append("%s: %s" % (n, repr(e)[:150]))
    return {"ok": ok, "err": err, "count": len(ok)}


@frappe.whitelist()
def api_bulk_delete(doctype, names):
    names = _rows(names) if isinstance(names, str) else (names or [])
    ok, err = [], []
    for n in names:
        try:
            if not frappe.db.exists(doctype, n):
                err.append(n + ": 不存在")
                continue
            d = frappe.get_doc(doctype, n)
            if d.docstatus == 1:
                d.cancel()
                frappe.db.commit()
            frappe.delete_doc(doctype, n, force=True)
            frappe.db.commit()
            if doctype in ("Stock Entry", "Stock Reconciliation"):
                for s in frappe.get_all("Stock Ledger Entry", filters={"voucher_no": n}, pluck="name"):
                    try:
                        frappe.delete_doc("Stock Ledger Entry", s, force=True)
                    except Exception:
                        pass
                for g in frappe.get_all("GL Entry", filters={"voucher_no": n}, pluck="name"):
                    try:
                        frappe.delete_doc("GL Entry", g, force=True)
                    except Exception:
                        pass
                frappe.db.commit()
            ok.append(n)
        except Exception as e:
            frappe.db.rollback()
            err.append("%s: %s" % (n, repr(e)[:150]))
    return {"ok": ok, "err": err, "count": len(ok)}


@frappe.whitelist()
def api_bulk_set_project(doctype, names, project):
    names = _rows(names) if isinstance(names, str) else (names or [])
    meta = frappe.get_meta(doctype)
    field = "project" if meta.get_field("project") else ("custom_cb_project" if meta.get_field("custom_cb_project") else None)
    if not field:
        return {"ok": [], "err": ["该单据无项目字段"], "count": 0}
    ok, err = [], []
    for n in names:
        try:
            d = frappe.get_doc(doctype, n)
            if d.docstatus != 0:
                err.append("%s: 非草稿，禁止改项目" % n)
                continue
            d.set(field, project)
            for row in d.get("items") or []:
                if row.meta.get_field("project"):
                    row.project = project
            d.save(ignore_permissions=True)
            frappe.db.commit()
            ok.append(n)
        except Exception as e:
            frappe.db.rollback()
            err.append("%s: %s" % (n, repr(e)[:150]))
    return {"ok": ok, "err": err, "count": len(ok)}


@frappe.whitelist()
def api_template(kind=None):
    return "item_code,qty,warehouse,project,rate\nSIM-PV-0001,2,巴西现场总仓 - 巴项,PROJ-0001,100\n"


# ---- 通用「物料批量行」解析（设计BOM / 设计变更 / 材料预算 共用） ----
HEADER_ALIASES = {
    "item_code": "item_code", "code": "item_code", "物料编码": "item_code", "编码": "item_code", "物料": "item_code",
    "item_name": "item_name", "name": "item_name", "名称": "item_name", "物料名称": "item_name",
    "spec": "spec", "specification": "spec", "规格": "spec", "型号": "spec", "规格型号": "spec",
    "uom": "uom", "unit": "uom", "单位": "uom",
    "qty": "qty", "quantity": "qty", "数量": "qty",
    "rate": "rate", "price": "rate", "单价": "rate", "价格": "rate",
    "loss_rate": "loss_rate", "损耗率": "loss_rate", "损耗": "loss_rate",
    "remark": "remark", "remarks": "remark", "备注": "remark",
    "design_basis": "design_basis", "设计依据": "design_basis",
    "category": "category", "分类": "category", "类别": "category",
    "new_qty": "new_qty", "新数量": "new_qty", "变更后数量": "new_qty",
    "old_qty": "old_qty", "原数量": "old_qty",
}


def _norm_row(r):
    n = {}
    for k, v in (r or {}).items():
        key = HEADER_ALIASES.get(str(k).strip().lower())
        if key:
            n[key] = v
    # 设计变更可用"新数量"作为 qty
    if not n.get("qty") and n.get("new_qty"):
        n["qty"] = n["new_qty"]
    return n


@frappe.whitelist()
def api_parse_rows():
    """上传 Excel/CSV，解析为标准化物料行（不建单）。"""
    f = frappe.request.files.get("file")
    if not f:
        frappe.throw("未收到文件")
    raw = _parse_file(f.read(), getattr(f, "filename", ""))
    rows = []
    for r in raw:
        n = _norm_row(r)
        if n.get("item_code"):
            rows.append(n)
    return {"rows": rows, "total": len(rows)}


@frappe.whitelist()
def api_batch_template():
    cols = "item_code,item_name,spec,uom,qty,loss_rate,rate,remark,design_basis,category"
    sample = "SIM-PV-0001,示例物料,DN100,个,10,2,100,备注,图纸A-01,消防水"
    return cols + "\n" + sample + "\n"


@frappe.whitelist()
def api_set_group_controlled(group, controlled=1):
    """按物料分类（含子级）批量设置"是否受控"。"""
    controlled = 1 if str(controlled) in ("1", "true", "True") else 0
    if frappe.db.get_value("Item Group", group, "is_group"):
        groups = _leaf_groups(group) or [group]
    else:
        groups = [group]
    items = frappe.get_all("Item", filters={"item_group": ["in", groups]}, pluck="name", limit=0)
    for it in items:
        frappe.db.set_value("Item", it, "custom_controlled", controlled, update_modified=False)
    frappe.db.commit()
    return {"group": group, "groups": len(groups), "items": len(items), "controlled": controlled}


def _l1_of(group):
    g = group
    while g:
        p = frappe.db.get_value("Item Group", g, "parent_item_group")
        if not p or p == "所有物料组":
            return g
        g = p
    return "其他"


def _leaf_groups(group):
    out = []
    for c in frappe.get_all("Item Group", filters={"parent_item_group": group}, pluck="name"):
        if frappe.db.get_value("Item Group", c, "is_group"):
            out.extend(_leaf_groups(c))
        else:
            out.append(c)
    return out


@frappe.whitelist()
def api_list_categories():
    return frappe.get_all("Item Group", filters={"parent_item_group": "所有物料组"},
                          pluck="name", order_by="name")


@frappe.whitelist()
def api_list_subgroups(parent=None):
    """返回某个分类的直接下级分组（用于二级筛选，如 消防 → 消防水/消防电）。"""
    if not parent:
        return []
    return frappe.get_all("Item Group", filters={"parent_item_group": parent},
                          fields=["name", "is_group"], order_by="name")


@frappe.whitelist()
def api_search_items(keyword=None, category=None, limit=50):
    limit = int(limit or 50)
    filters = {}
    if category:
        if frappe.db.get_value("Item Group", category, "is_group"):
            leaves = _leaf_groups(category)
            if leaves:
                filters["item_group"] = ["in", leaves]
        else:
            filters["item_group"] = category
    or_filters = None
    if keyword:
        kw = "%" + keyword + "%"
        or_filters = [["item_code", "like", kw], ["item_name", "like", kw], ["custom_spec", "like", kw]]
    fields = ["item_code", "item_name", "custom_spec", "stock_uom", "item_group"]
    items = frappe.get_all("Item", filters=filters or None, or_filters=or_filters,
                           fields=fields, limit=limit, order_by="item_code")
    for it in items:
        it["category"] = _l1_of(it["item_group"])
    return items


# ---------------- v2：树 / 分页搜索 / 导入预览 / Excel 模板 / 从BOM生成 ----------------

@frappe.whitelist()
def api_item_tree(parent=None):
    """返回某分类的直接下级（含叶子组），带累计物料数。"""
    parent = parent or "所有物料组"
    groups = frappe.get_all("Item Group", filters={"parent_item_group": parent},
                            fields=["name", "is_group"], order_by="name")
    for g in groups:
        if g.get("is_group"):
            leaves = _leaf_groups(g["name"])
            g["count"] = frappe.db.count("Item", {"item_group": ["in", leaves]}) if leaves else frappe.db.count("Item", {"item_group": g["name"]})
        else:
            g["count"] = frappe.db.count("Item", {"item_group": g["name"]})
    return groups


@frappe.whitelist()
def api_item_search(keyword=None, group=None, start=0, page_length=50):
    """分页搜索：编码/名称/规格/英文名/葡语名。返回 {items,total}。"""
    start = max(int(start or 0), 0)
    plen = min(max(int(page_length or 50), 1), 200)
    conds, params = ["1=1"], {}
    if group:
        if frappe.db.get_value("Item Group", group, "is_group"):
            leaves = _leaf_groups(group) or [group]
            if len(leaves) == 1:
                conds.append("item_group = %(group)s")
                params["group"] = leaves[0]
            else:
                conds.append("item_group in %(groups)s")
                params["groups"] = tuple(leaves)
        else:
            conds.append("item_group = %(group)s")
            params["group"] = group
    if keyword:
        conds.append(
            "(item_code like %(kw)s or item_name like %(kw)s or ifnull(custom_spec,'') like %(kw)s"
            " or ifnull(custom_item_name_en,'') like %(kw)s or ifnull(custom_item_name_pt,'') like %(kw)s)"
        )
        params["kw"] = "%" + keyword + "%"
    where = " and ".join(conds)
    params.update({"start": start, "plen": plen})
    total = frappe.db.sql("select count(*) from `tabItem` where " + where, params)[0][0]
    items = frappe.db.sql(
        "select item_code, item_name, custom_spec, stock_uom, item_group,"
        " ifnull(custom_controlled,1) as custom_controlled"
        " from `tabItem` where " + where + " order by item_code limit %(start)s, %(plen)s",
        params, as_dict=True)
    return {"items": items, "total": int(total or 0)}


@frappe.whitelist()
def api_group_items(group=None, limit=1000):
    """按分类（含子组）返回物料，用于整类添加。"""
    if not group:
        return []
    limit = min(max(int(limit or 1000), 1), 5000)
    filters = {}
    if frappe.db.get_value("Item Group", group, "is_group"):
        leaves = _leaf_groups(group) or [group]
        filters["item_group"] = ["in", leaves]
    else:
        filters["item_group"] = group
    return frappe.get_all("Item", filters=filters,
                          fields=["item_code", "item_name", "custom_spec", "stock_uom", "item_group", "custom_controlled"],
                          limit=limit, order_by="item_code")


@frappe.whitelist()
def api_parse_preview():
    """上传 Excel/CSV，返回逐行校验结果（不建单、不入库）。"""
    f = frappe.request.files.get("file")
    if not f:
        frappe.throw("未收到文件")
    raw = _parse_file(f.read(), getattr(f, "filename", ""))
    out = []
    for idx, r in enumerate(raw, start=1):
        n = _norm_row(r)
        code = (n.get("item_code") or "").strip() if n.get("item_code") else ""
        if not code:
            continue
        row = {
            "row_no": idx,
            "item_code": code,
            "qty": flt(n.get("qty")) or 0,
            "uom": (n.get("uom") or "").strip(),
            "rate": flt(n.get("rate")) or 0,
            "loss_rate": flt(n.get("loss_rate")) or 0,
            "remark": (n.get("remark") or "").strip(),
            "valid": True,
            "reason": "",
        }
        item = frappe.db.get_value("Item", code, ["item_name", "stock_uom", "valuation_rate", "custom_controlled"], as_dict=True)
        if not item:
            row.update({"valid": False, "reason": "物料编码不存在"})
        else:
            row["item_name"] = item.item_name
            row["controlled"] = 1 if item.custom_controlled is None else int(bool(item.custom_controlled))
            row["spec"] = frappe.db.get_value("Item", code, "custom_spec")
            if not row["uom"]:
                row["uom"] = item.stock_uom
            elif not frappe.db.exists("UOM", row["uom"]):
                row.update({"valid": False, "reason": "单位不存在：" + row["uom"]})
            if row["qty"] <= 0:
                row.update({"valid": False, "reason": "数量必须大于 0"})
            if not row["rate"]:
                row["rate"] = flt(item.valuation_rate)
        out.append(row)
    return {
        "rows": out,
        "total": len(out),
        "valid_count": len([x for x in out if x["valid"]]),
        "invalid_count": len([x for x in out if not x["valid"]]),
    }


@frappe.whitelist()
def api_batch_template_xlsx():
    """下载 Excel 模板（含说明页 + 示例行）。"""
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill
    except Exception:
        return {"filename": "物料批量录入模板.csv", "content": api_batch_template()}

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "物料明细"
    headers = ["item_code", "qty", "uom", "loss_rate", "rate", "remark", "design_basis"]
    ws.append(headers)
    ws.append(["CB-EL-001", 10, "米", 2, 100, "示例行（可删除）", "图纸A-01"])
    for c in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=c)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="2563EB")
    widths = [22, 10, 10, 12, 12, 30, 20]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

    info = wb.create_sheet("填写说明")
    lines = [
        ["列名", "是否必填", "说明"],
        ["item_code", "必填", "物料编码，必须已存在"],
        ["qty", "必填", "数量，大于 0"],
        ["uom", "选填", "单位，留空取物料默认单位"],
        ["loss_rate", "选填", "损耗率（%），如 2 表示 2%"],
        ["rate", "选填", "单价，留空取物料估值单价"],
        ["remark", "选填", "备注"],
        ["design_basis", "选填", "设计依据（图纸号/规范）"],
        [],
        ["提示", "", "首行必须是列名；支持 xlsx / csv；导入后系统会先预览校验，再写入单据。"],
    ]
    for r in lines:
        info.append(r)
    for c in range(1, 4):
        info.cell(row=1, column=c).font = Font(bold=True)
    info.column_dimensions["A"].width = 18
    info.column_dimensions["B"].width = 12
    info.column_dimensions["C"].width = 70

    buf = io.BytesIO()
    wb.save(buf)
    return {"filename": "物料批量录入模板.xlsx", "content_b64": base64.b64encode(buf.getvalue()).decode()}


@frappe.whitelist()
def api_bom_rows(project=None, discipline=None, system=None):
    """当前有效设计BOM明细（用于设计变更/材料预算一键生成）。"""
    if not project:
        return []
    rows = frappe.db.sql(
        """select i.item_code, i.item_name, i.spec, i.qty, i.uom, i.loss_rate, i.remark,
                  i.custom_tag_no, i.custom_install_location,
                  ifnull(it.valuation_rate,0) as rate,
                  ifnull(it.custom_controlled,1) as custom_controlled
           from `tabDesign BOM Item` i
           join `tabDesign BOM` b on b.name = i.parent
           join (select project, custom_discipline, custom_system, max(name) cur_bom
                 from `tabDesign BOM` where docstatus=1
                 group by project, custom_discipline, custom_system) cb on cb.cur_bom = b.name
           left join `tabItem` it on it.name = i.item_code
           where b.project=%s and ifnull(b.custom_discipline,'')=%s and ifnull(b.custom_system,'')=%s
           order by i.idx""",
        (project, discipline or "", system or ""), as_dict=True)
    for r in rows:
        r["old_qty"] = r.get("qty") or 0
        r["new_qty"] = r.get("qty") or 0
        r["delta"] = 0
    return rows


@frappe.whitelist()
def api_bom_gap(project=None, discipline=None, system=None, kind="mr"):
    """按BOM计算缺口：kind=mr 用 设计-已请购；kind=po 用 请购-已下单。"""
    if not project:
        return []
    from cb_erp.cb_erp import linkage
    rows = api_bom_rows(project, discipline, system)
    out = []
    for r in rows:
        it = r["item_code"]
        design = linkage.design_qty(project, discipline, system, it)
        requested = linkage.sum_source("mr", project, discipline, system, it)
        ordered = linkage.sum_source("po", project, discipline, system, it)
        received = linkage.sum_source("recv", project, discipline, system, it)
        issued = linkage.sum_source("issue", project, discipline, system, it)
        gap = (design - requested) if kind == "mr" else (requested - ordered)
        if gap <= 0.005:
            continue
        out.append({
            "item_code": it, "item_name": r.get("item_name"), "uom": r.get("uom"),
            "qty": flt(gap), "rate": r.get("rate") or 0,
            "design": design, "requested": requested, "ordered": ordered,
            "received": received, "issued": issued,
        })
    return out


@frappe.whitelist()
def api_set_group_controlled2(group, controlled=1, include_children=1):
    """按分类批量设置受控；include_children=0 时仅直属物料。"""
    controlled = 1 if str(controlled) in ("1", "true", "True") else 0
    include_children = 1 if str(include_children) in ("1", "true", "True") else 0
    if include_children and frappe.db.get_value("Item Group", group, "is_group"):
        groups = _leaf_groups(group) or [group]
    else:
        groups = [group]
    items = frappe.get_all("Item", filters={"item_group": ["in", groups]}, pluck="name", limit=0)
    for it in items:
        frappe.db.set_value("Item", it, "custom_controlled", controlled, update_modified=False)
    frappe.db.commit()
    return {"group": group, "groups": len(groups), "items": len(items), "controlled": controlled}


@frappe.whitelist()
def api_set_groups_controlled(groups=None, controlled=1):
    """多选分类（可含父子）批量设置受控，自动去重。"""
    groups = _rows(groups) if isinstance(groups, str) else (groups or [])
    controlled = 1 if str(controlled) in ("1", "true", "True") else 0
    codes = set()
    for g in groups:
        if not g:
            continue
        if frappe.db.get_value("Item Group", g, "is_group"):
            codes.update(_leaf_groups(g) or [g])
        else:
            codes.add(g)
    items = frappe.get_all("Item", filters={"item_group": ["in", list(codes)]}, pluck="name", limit=0) if codes else []
    for it in items:
        frappe.db.set_value("Item", it, "custom_controlled", controlled, update_modified=False)
    frappe.db.commit()
    return {"groups": len(codes), "items": len(items), "controlled": controlled}

