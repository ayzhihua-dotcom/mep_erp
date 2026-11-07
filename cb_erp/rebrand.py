# -*- coding: utf-8 -*-
"""品牌与命名优化：
1) Module Def "CB ERP" 的显示标题改为「工作台」（纯显示，不动内部名）；
2) 工作台链接标签去掉 CB 前缀：装运管理 / 进口案件 / 成本审计日志 / 进口费用分摊。
"""
import frappe

WS = "巴西机电ERP系统测试"

LABEL_MAP = {
    "CB装运": "装运管理",
    "CB进口案件": "进口案件",
    "CB成本审计日志": "成本审计日志",
    "CB进口费用分摊": "进口费用分摊",
}


def run():
    frappe.set_user("Administrator")

    # 1) 品牌词条：模块名 "CB ERP" 在界面显示为「工作台」（纯翻译，零风险）
    for src, tr in (("CB ERP", "工作台"), ("Cb Erp", "工作台")):
        nm = frappe.db.get_value("Translation", {"language": "zh", "source_text": src}, "name")
        if nm:
            frappe.db.set_value("Translation", nm, "translated_text", tr, update_modified=False)
        else:
            try:
                frappe.get_doc({"doctype": "Translation", "language": "zh",
                                "source_text": src, "translated_text": tr}).insert(ignore_permissions=True)
            except Exception as e:
                print("TR_ERR", src, repr(e)[:100])

    # 2) 工作台链接标签去掉 CB 前缀（兼容「CB 装运」带空格写法）
    ws = frappe.get_doc("Workspace", WS)
    n = 0
    for l in ws.links:
        label = (l.label or "").replace(" ", "")
        new = LABEL_MAP.get(label)
        if new:
            l.label = new
            n += 1
    if n:
        ws.save(ignore_permissions=True)
        frappe.db.commit()
    frappe.clear_cache()
    print("LABELS_RENAMED", n)
    return "REBRAND_DONE"
