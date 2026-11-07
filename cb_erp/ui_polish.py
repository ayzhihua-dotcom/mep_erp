# -*- coding: utf-8 -*-
"""工作台链接彩色图标。"""
import frappe

WS = "巴西机电ERP系统测试"

ICONS = {
    "操作台": "layout-dashboard",
    "批量录入": "zap",
    "采购申请": "file-text",
    "采购订单": "shopping-cart",
    "采购入库": "package",
    "物料领用/退料": "log-out",
    "库存盘点": "clipboard-list",
    "专业系统矩阵": "chart-bar-stacked",
    "设计BOM": "layers",
    "设计变更申请": "pencil-line",
    "材料预算": "chart-pie",
    "材料承诺": "clipboard-list",
    "询价单": "search",
    "供应商报价": "users",
    "采购订单": "shopping-cart",
    "材料承诺台账": "clipboard-list",
    "装运管理": "truck",
    "进口案件": "globe",
    "成本审计日志": "file-text",
    "进口费用分摊": "dollar-sign",
    "质检单": "check-circle",
    "库存收发": "package",
    "物料": "box",
    "供应商": "users",
    "项目": "folder",
    "专业": "award",
    "系统": "layers",
    "项目视图": "layout-dashboard",
    "项目任务": "check-circle",
    "项目预警": "bell",
    "预警规则": "settings",
    "项目文档台账": "folder",
    "项目总览": "bar-chart-2",
    "物料分类": "layers",
    "业务汇总（专业/系统/责任人）": "bar-chart-2",
    "物料明细（九列）": "file-text",
}


def run():
    frappe.set_user("Administrator")
    ws = frappe.get_doc("Workspace", WS)
    norm = {k.replace(" ", ""): v for k, v in ICONS.items()}
    n = 0
    for l in ws.links:
        icon = norm.get((l.label or "").replace(" ", "").strip())
        if icon and l.icon != icon:
            l.icon = icon
            n += 1
    if n:
        ws.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.clear_cache()
    print("ICONS_UPDATED", n)
    return "OK"
