# -*- coding: utf-8 -*-
"""操作台页面：Page 记录 + 工作台入口。"""
import frappe

WS = "巴西机电ERP系统测试"
PAGE = "ops-console"
TITLE = "操作台"


def ensure_page():
    if frappe.db.exists("Page", PAGE):
        return
    roles = ["System Manager", "SYS 系统管理员", "PM 项目经理", "ENG 工程人员",
             "WHS 仓库管理员", "WHS 仓库人员", "PRC 中国采购", "BRA 巴西采购",
             "LOG 物流专员", "MGT 管理层", "CUS 清关人员", "FIN 财务人员"]
    rows = [{"role": r} for r in roles if frappe.db.exists("Role", r)]
    frappe.get_doc({
        "doctype": "Page", "name": PAGE, "page_name": PAGE, "title": TITLE,
        "module": "CB ERP", "standard": "No", "roles": rows,
    }).insert(ignore_permissions=True)
    print("PAGE_CREATED")


def ensure_ws_link():
    if not frappe.db.exists("Workspace", WS):
        return
    ws = frappe.get_doc("Workspace", WS)
    links = [l.as_dict() for l in ws.links]
    if any(l.get("link_type") == "Page" and l.get("link_to") == PAGE for l in links):
        return
    out = []
    inserted = False
    for l in links:
        out.append(l)
        if (not inserted) and l.get("type") == "Card Break" and l.get("label") == "业务操作":
            out.append({"type": "Link", "label": TITLE, "link_type": "Page", "link_to": PAGE,
                        "link_count": 0, "hidden": 0, "onboard": 0})
            inserted = True
    if not inserted:
        out.insert(0, {"type": "Card Break", "label": "业务操作", "link_count": 0, "hidden": 0, "onboard": 0})
        out.insert(1, {"type": "Link", "label": TITLE, "link_type": "Page", "link_to": PAGE,
                       "link_count": 0, "hidden": 0, "onboard": 0})

    skip = ("name", "idx", "doctype", "parent", "parentfield", "parenttype",
            "creation", "modified", "modified_by", "owner")
    ws.set("links", [])
    for i, l in enumerate(out, start=1):
        row = {k: v for k, v in l.items() if k not in skip}
        row["idx"] = i
        ws.append("links", row)
    ws.save(ignore_permissions=True)
    print("WS_LINK_ADDED")


def run():
    frappe.set_user("Administrator")
    ensure_page()
    ensure_ws_link()
    frappe.db.commit()
    frappe.clear_cache()
    return "CONSOLE_DONE"
