import json
import traceback


def run():
    import frappe
    from frappe.desk.query_report import run

    names = ["采购与领用台账", "物资四量台账", "采购下单追踪", "项目专业系统矩阵",
             "里程碑齐套检查", "实物量进度", "项目物料执行台账", "项目文档台账",
             "项目总览", "业务汇总（专业系统责任人）", "物料明细（九列）"]
    out = {}
    for n in names:
        try:
            r = run(n, filters={})
            cols = len(r.get("columns") or [])
            rows = len(r.get("result") or [])
            out[n] = "OK %s cols / %s rows" % (cols, rows)
        except Exception:
            out[n] = "FAIL: " + traceback.format_exc().splitlines()[-1][:160]
    print(json.dumps(out, ensure_ascii=True, default=str))


# noqa
