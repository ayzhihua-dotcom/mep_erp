# -*- coding: utf-8 -*-
def run():
    import frappe, json
    frappe.set_user("Administrator")
    from frappe.desk.query_report import run as run_report
    for metric in ("已领用数量", "采购订单数量", "采购申请数量"):
        try:
            res = run_report("项目专业系统矩阵", filters={"metric": metric}, user="Administrator")
            rows = res.get("result") or []
            cols = res.get("columns") or []
            print(metric, "COLS:", len(cols), "ROWS:", len(rows), "MSG:", res.get("message"))
            sample = rows[0] if rows else None
            print("   sample:", json.dumps(sample, ensure_ascii=True, default=str)[:300])
        except Exception as e:
            print("ERR", metric, repr(e)[:200])
    return "OK"
