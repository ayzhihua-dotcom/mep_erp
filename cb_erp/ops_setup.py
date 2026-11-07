# -*- coding: utf-8 -*-
"""业务操作入口：工作台「业务操作」卡片 + 库存侧栏 4 个操作入口 + 矩阵看板报表。"""
import frappe

WS = "巴西机电ERP系统测试"
REPORT = "项目专业系统矩阵"

OPS_LINKS = [
    ("批量录入", "DocType", "Bulk Entry"),
    ("采购申请", "DocType", "Material Request"),
    ("采购订单", "DocType", "Purchase Order"),
    ("采购入库", "DocType", "Purchase Receipt"),
    ("物料领用/退料", "DocType", "Stock Entry"),
    ("库存盘点", "DocType", "Stock Reconciliation"),
    ("专业系统矩阵", "Report", REPORT),
]

SIDEBAR_ADD = [
    ("物料领用（出库）", "Stock Entry", '{"stock_entry_type": "Material Issue"}'),
    ("物料入库", "Stock Entry", '{"stock_entry_type": "Material Receipt"}'),
    ("物料退料（批量）", "Bulk Entry", '{"kind": "\\u9000\\u6599"}'),
    ("库存盘点（新建）", "Stock Reconciliation", None),
]
OLD_URL_PREFIX = "/desk/stock-entry/new"


def ensure_report():
    if frappe.db.exists("Report", REPORT):
        return
    frappe.get_doc({
        "doctype": "Report", "report_name": REPORT, "ref_doctype": "Stock Entry",
        "report_type": "Script Report", "is_standard": "Yes", "module": "CB ERP",
    }).insert(ignore_permissions=True)
    print("REPORT_CREATED")


def ensure_sidebar():
    if not frappe.db.exists("Sidebar", "Stock"):
        return
    sb = frappe.get_doc("Sidebar", "Stock")

    # 清理旧版 URL 入口（会被应用前缀拼错）
    kept = [i for i in sb.items if not ((i.link_type == "URL") and (i.url or "").startswith("/desk/"))]
    if len(kept) != len(sb.items):
        sb.set("items", [])
        for i in kept:
            sb.append("items", {k: i.get(k) for k in
                                ("label", "link_type", "link_to", "url", "icon", "route_options",
                                 "hidden", "open_in_new_tab", "indent", "collapsible")})

    anchor_idx = None
    for i in sb.items:
        if i.link_type == "DocType" and i.link_to == "Stock Entry":
            anchor_idx = i.idx
    if anchor_idx is None:
        return

    existing = {(i.link_type, i.link_to, i.get("route_options") or "") for i in sb.items}
    pos = anchor_idx
    added = 0
    for label, link_to, route_options in SIDEBAR_ADD:
        key = ("DocType", link_to, route_options or "")
        if key in existing:
            continue
        pos += 1
        row = sb.append("items", {"label": label, "link_type": "DocType", "link_to": link_to,
                                  "icon": "shelf-rack-soft", "route_options": route_options})
        row.idx = pos
        added += 1
    if added or len(kept) != len(sb.items):
        sb.save(ignore_permissions=True)
        frappe.db.commit()
        print("SIDEBAR_ADDED", added)


def ensure_ops_card():
    if not frappe.db.exists("Workspace", WS):
        return
    ws = frappe.get_doc("Workspace", WS)
    links = [l.as_dict() for l in ws.links]
    if any(l.get("type") == "Card Break" and l.get("label") == "业务操作" for l in links):
        return
    card = [
        {"type": "Card Break", "label": "业务操作", "link_count": 0, "hidden": 0, "onboard": 0},
    ]
    for label, lt, target in OPS_LINKS:
        card.append({"type": "Link", "label": label, "link_type": lt, "link_to": target,
                     "link_count": 0, "hidden": 0, "onboard": 0})
    links = card + links

    skip = ("name", "idx", "doctype", "parent", "parentfield", "parenttype",
            "creation", "modified", "modified_by", "owner")
    ws.set("links", [])
    for i, l in enumerate(links, start=1):
        row = {k: v for k, v in l.items() if k not in skip}
        row["idx"] = i
        ws.append("links", row)
    ws.save(ignore_permissions=True)
    print("OPS_CARD_ADDED")


def ensure_ops_content_block():
    """工作台卡片还需要 content 区块才会渲染。"""
    import json
    import uuid
    if not frappe.db.exists("Workspace", WS):
        return
    ws = frappe.get_doc("Workspace", WS)
    content = json.loads(ws.content or "[]")
    if any(b.get("type") == "card" and b.get("data", {}).get("card_name") == "业务操作" for b in content):
        return
    pos = 0
    for i, b in enumerate(content):
        if b.get("type") == "number_card":
            pos = i + 1
    content.insert(pos, {"id": uuid.uuid4().hex[:10], "type": "card",
                         "data": {"card_name": "业务操作", "col": 12}})
    ws.content = json.dumps(content)
    ws.save(ignore_permissions=True)
    print("OPS_CONTENT_ADDED")


def run():
    frappe.set_user("Administrator")
    ensure_report()
    ensure_ops_card()
    ensure_ops_content_block()
    ensure_sidebar()
    frappe.db.commit()
    frappe.clear_cache()
    return "OPS_SETUP_DONE"
