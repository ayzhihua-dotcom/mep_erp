import frappe
from frappe.utils import get_url_to_form
from urllib.parse import urlparse

# 扫码解析的优先 doctype 顺序
DOCTYPE_PRIORITY = [
    "Purchase Order", "Material Request", "Design BOM", "Design Change Request",
    "Quality Inspection", "CB NCR", "CB Commissioning Record", "CB Shipment",
    "CB Import Case", "Stock Entry", "Project", "Task",
]


def _relative_route(dt, name):
    """返回站内相对路径，避免绝对域名（dev.localhost）导致跳转失败。"""
    url = get_url_to_form(dt, name)
    path = urlparse(url).path
    return path or url


@frappe.whitelist()
def resolve(code=None):
    """按单据编号解析并返回可打开的路由（供 /scan 扫码页调用）。"""
    code = (code or "").strip()
    if not code:
        return {"found": False, "code": code}

    for dt in DOCTYPE_PRIORITY:
        try:
            if frappe.db.exists(dt, code):
                return {"found": True, "doctype": dt, "name": code,
                        "route": _relative_route(dt, code)}
        except Exception:
            continue

    try:
        if frappe.db.exists("Item", code):
            return {"found": True, "doctype": "Item", "name": code,
                    "route": _relative_route("Item", code)}
    except Exception:
        pass

    return {"found": False, "code": code}
