import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    from frappe.desk.query_report import run
    for rep in ["项目总览", "项目物料执行台账", "项目文档台账"]:
        try:
            res = run(rep, filters={})
            print("REPORT", rep, "-> rows:", len(res.get("result") or []), "cols:", len(res.get("columns") or []))
        except Exception as e:
            print("REPORT_ERR", rep, repr(e))
    from frappe.desk.doctype.number_card.number_card import get_result
    for lb in ["在办项目", "在办任务", "未关闭预警", "缺料预警", "超预算预警", "逾期任务"]:
        try:
            print("CARD", lb, "=", get_result(frappe.get_doc("Number Card", lb), {}))
        except Exception as e:
            print("CARD_ERR", lb, repr(e))
    print("--- ALERT BREAKDOWN ---")
    for r in frappe.db.sql("select rule_code, alert_type, count(*) c from `tabAlert Event` group by rule_code, alert_type order by rule_code", as_dict=True):
        print("ALERT", r.rule_code, "|", r.alert_type, "|", r.c)
    print("MR_OWNERS:", frappe.db.sql("select owner, count(*) c from `tabMaterial Request` group by owner order by c desc limit 12", as_dict=True))
    print("PO_SUBMITTED:", frappe.db.count("Purchase Order", {"docstatus": 1, "custom_cb_project": ["is", "set"]}))
    print("ISSUE_SE_SUBMITTED:", frappe.db.count("Stock Entry", {"docstatus": 1, "purpose": "Material Issue"}))
    print("RECEIPT_SE_SUBMITTED:", frappe.db.count("Stock Entry", {"docstatus": 1, "purpose": "Material Receipt"}))
    sys.exit(0)
main()
