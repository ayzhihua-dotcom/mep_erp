import os
import json

# 范围收敛（2026-11-04 用户拍板：项目管理导向）
# 1) 隐藏与项目无关的标准 Workspace（影响 Workspace 列表/侧边栏）。
HIDE_WORKSPACES = [
    "Selling", "Accounting", "Financial Reports", "Invoicing", "Payments",
    "Assets", "Manufacturing", "CRM", "Support", "Website",
    "Automation", "Build", "Email", "Integrations", "Printing",
]

# 2) 按用户屏蔽模块导航（v16 顶部模块栏由 module_sidebars 驱动，只认 User.block_modules）。
#    保留：CB ERP / Projects / Stock / Buying / Quality + Setup / Users / System（管理）。
BLOCK_MODULES = [
    "Accounts", "Selling", "Assets", "Manufacturing", "CRM", "Support",
    "Website", "Automation", "Build", "Email", "Integrations", "Printing",
    "Contacts", "Data", "Geo", "Workflow", "Portal",
]

CB_WORKSPACE_NAME = "巴西机电ERP系统测试"


def hide_unused_workspaces():
    import frappe
    for name in HIDE_WORKSPACES:
        if frappe.db.exists("Workspace", name):
            frappe.db.set_value("Workspace", name, "is_hidden", 1, update_modified=False)


def block_project_irrelevant_modules():
    """为所有非管理员启用账号设置 block_modules（幂等）。"""
    import frappe
    users = frappe.get_all(
        "User",
        filters={"enabled": 1, "user_type": "System User"},
        fields=["name"],
    )
    for row in users:
        uname = row["name"]
        if uname in ("Administrator", "Guest"):
            continue
        u = frappe.get_doc("User", uname)
        existing = {b.module for b in u.block_modules}
        missing = [m for m in BLOCK_MODULES if m not in existing]
        if not missing:
            continue
        try:
            for m in missing:
                u.append("block_modules", {"module": m})
            u.flags.ignore_permissions = True
            u.save()
        except Exception:
            import frappe as _frappe
            _frappe.log_error(title="cb_erp: block_modules failed", message=uname)


def ensure_cb_workspace():
    import frappe
    if frappe.db.exists("Workspace", CB_WORKSPACE_NAME):
        return
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fixtures", "workspace.json")
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    d = frappe.get_doc(data[0])
    d.standard = 0
    d.is_hidden = 0
    d.public = 1
    d.for_user = None
    d.flags.ignore_links = True
    d.insert(ignore_permissions=True, set_name=CB_WORKSPACE_NAME)


def ensure_project_report_perm():
    """Custom DocPerm 覆盖标准 DocPerm：为所有被覆盖的 doctype 的读取角色补 report=1，
    并确保存在 System Manager 全权限行（否则连管理员都可能打不开报表）。"""
    import frappe
    FULL = dict(read=1, write=1, create=1, delete=1, report=1, export=1, print=1,
                email=1, share=1, submit=1, cancel=1, amend=1)
    parents = sorted({c.parent for c in frappe.get_all("Custom DocPerm", fields=["parent"], limit=0)})
    for dt in parents:
        rows = frappe.get_all("Custom DocPerm", filters={"parent": dt},
                              fields=["name", "role", "read", "report"])
        for r in rows:
            if r.read and not r.report:
                frappe.db.set_value("Custom DocPerm", r.name, "report", 1, update_modified=False)
        if not any(r.role == "System Manager" for r in rows):
            frappe.get_doc({"doctype": "Custom DocPerm", "parent": dt, "parenttype": "DocType",
                            "parentfield": "permissions", "role": "System Manager", **FULL}).insert(ignore_permissions=True)


def _rail_key(row):
    return (row.get("link_type"), row.get("link_to") or row.get("url"))


def ensure_app_switcher_dock():
    """确保「框架 / ERPNext / 巴西机电ERP系统测试」三个应用之间互相切换的侧栏入口。

    v16 的「应用」菜单在「框架」应用里会退化成只有 All apps（且 /apps 页在本环境是空的），
    所以框架的侧栏必须自己带一条回到 CB 的入口；ERPNext 侧栏也补一条，保证任意方向都能回去。
    只写「站点级编排」，不动应用自带的 Dock 文件，也不覆盖用户个人的编排。
    """
    import frappe
    from frappe.desk.doctype.dock.dock import get_site_dock, resolve_app_dock, save_site_dock

    ws_row = {
        "link_type": "Workspace",
        "link_to": CB_WORKSPACE_NAME,
        "icon": "factory-soft",
        "title": CB_WORKSPACE_NAME,
    }
    erp_row = {"link_type": "URL", "url": "/desk/home", "icon": "home-soft", "title": "ERPNext 主页"}

    plans = {"frappe": [erp_row, ws_row], "erpnext": [ws_row]}
    for app, extras in plans.items():
        try:
            current = get_site_dock(app)
            if not current:
                current = resolve_app_dock(app, upto="app", gated=False)
            items = [dict(r) for r in current]
            have = {_rail_key(r) for r in items}
            missing = [r for r in extras if _rail_key(r) not in have]
            if missing:
                save_site_dock(app, items + missing)
        except Exception as e:
            frappe.log_error("ensure_app_switcher_dock %s: %s" % (app, repr(e)[:200]))


def ensure_master_links():
    """工作台「主数据」区补上 专业 / 系统 两个主数据入口（幂等）。"""
    import frappe
    if not frappe.db.exists("Workspace", CB_WORKSPACE_NAME):
        return
    ws = frappe.get_doc("Workspace", CB_WORKSPACE_NAME)
    links = [l.as_dict() for l in ws.links]
    existing = {(l.get("link_type"), l.get("link_to")) for l in links}
    want = [("专业", "CB Discipline"), ("系统", "CB System")]
    missing = [(lbl, dt) for lbl, dt in want if ("DocType", dt) not in existing]
    if not missing:
        return

    start = None
    for i, l in enumerate(links):
        if l.get("type") == "Card Break" and l.get("label") == "主数据":
            start = i
            break
    if start is None:
        # 没有「主数据」卡片就新建一个卡片放在最后
        links.append({"type": "Card Break", "label": "主数据", "link_count": 0, "hidden": 0, "onboard": 0})
        start = len(links) - 1
    end = len(links)
    for j in range(start + 1, len(links)):
        if links[j].get("type") == "Card Break":
            end = j
            break

    at = end
    for label, dt in missing:
        links.insert(at, {"type": "Link", "label": label, "link_type": "DocType",
                          "link_to": dt, "link_count": 0, "hidden": 0, "onboard": 0})
        at += 1

    skip = ("name", "idx", "doctype", "parent", "parentfield", "parenttype",
            "creation", "modified", "modified_by", "owner")
    ws.set("links", [])
    for i, l in enumerate(links, start=1):
        row = {k: v for k, v in l.items() if k not in skip}
        row["idx"] = i
        ws.append("links", row)
    ws.save(ignore_permissions=True)
    print("WORKSPACE_MASTER_LINKS_ENSURED")


def ensure_zh_terms():
    """补充主数据的中文名（DocType 名用于侧栏/列表显示）。"""
    import frappe
    terms = {
        "CB Discipline": "专业",
        "CB System": "系统",
        "CB Project System": "项目专业与系统",
        "CB Discipline-custom_spec": None,
    }
    for src, dst in terms.items():
        if not dst:
            continue
        if frappe.db.exists("Translation", {"source_text": src, "language": "zh"}):
            name = frappe.db.get_value("Translation", {"source_text": src, "language": "zh"})
            frappe.db.set_value("Translation", name, "translated_text", dst, update_modified=False)
        else:
            frappe.get_doc({"doctype": "Translation", "language": "zh",
                            "source_text": src, "translated_text": dst}).insert(ignore_permissions=True)


def ensure_ops_entries():
    """工作台「业务操作」卡片（防止 migrate/fixtures 回滚）。"""
    import frappe
    try:
        from cb_erp.cb_erp.ops_setup import ensure_ops_card, ensure_ops_content_block
        ensure_ops_card()
        ensure_ops_content_block()
    except Exception as e:
        frappe.log_error("ensure_ops_entries: %s" % repr(e)[:200])


def after_migrate():
    import frappe
    hide_unused_workspaces()
    ensure_cb_workspace()
    block_project_irrelevant_modules()
    ensure_project_report_perm()
    ensure_app_switcher_dock()
    ensure_master_links()
    ensure_zh_terms()
    ensure_ops_entries()
    frappe.db.commit()
    frappe.clear_cache()
