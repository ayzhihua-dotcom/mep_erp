# -*- coding: utf-8 -*-
import json


def run():
    import frappe
    frappe.set_user("Administrator")

    # 清理联调产生的测试单据
    removed = []
    for name in ("MAT-MR-2026-00065", "MAT-MR-2026-00062"):
        if frappe.db.exists("Material Request", name):
            doc = frappe.get_doc("Material Request", name)
            if doc.docstatus == 0:
                frappe.delete_doc("Material Request", name, force=1, ignore_permissions=True)
                removed.append(name)
    for p in frappe.get_all("Project", filters={"project_name": ["like", "ZZ-TEST-DISC%"]}, pluck="name"):
        try:
            frappe.delete_doc("Project", p, force=1, ignore_permissions=True)
            removed.append(p)
        except Exception:
            pass
    frappe.db.commit()

    print("REMOVED:", removed)

    # 报表检查
    rep = frappe.get_doc("Report", "业务汇总（专业系统责任人）")
    print("REPORT_QUERY_HEAD:", (rep.query or "")[:220].replace("\n", " "))
    try:
        from frappe.desk.query_report import run as run_report
        res = run_report("业务汇总（专业系统责任人）", filters={}, user="Administrator")
        cols = [c.get("label") for c in (res.get("columns") or [])]
        print("REPORT_COLS:", json.dumps(cols, ensure_ascii=True))
        print("REPORT_ROWS:", len(res.get("result") or []))
        rows = (res.get("result") or [])[:3]
        print("REPORT_SAMPLE:", json.dumps(rows, ensure_ascii=True, default=str)[:500])
    except Exception as e:
        print("REPORT_ERR:", repr(e)[:200])

    # 汇总
    print("DISC:", frappe.db.count("CB Discipline"), "SYS:", frappe.db.count("CB System"))
    print("PROJ_WITH_CFG:", frappe.db.sql("select count(distinct parent) c from `tabCB Project System`", as_dict=True)[0]["c"],
          "/", frappe.db.count("Project"))
    print("ITEMS:", frappe.db.count("Item"), "GROUPS:", frappe.db.count("Item Group"))
    return "OK"
