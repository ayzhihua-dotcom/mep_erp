import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    from frappe.desk.doctype.number_card.number_card import get_result
    labels = ["在办项目", "在办任务", "未关闭预警", "缺料预警", "超预算预警"]
    for lb in labels:
        try:
            r = get_result(frappe.get_doc("Number Card", lb), {})
            print("VALUE:", lb, "=", r)
        except Exception as e:
            print("VALUE_ERR:", lb, repr(e))
    print("DB_PROJECT_OPEN:", frappe.db.count("Project", {"status": "Open"}))
    print("DB_TASK_OPEN_WORKING:", frappe.db.count("Task", {"status": ["in", ["Open", "Working"]]}))
    print("DB_ALERT_OPEN:", frappe.db.count("Alert Event", {"status": ["!=", "已关闭"]}))
    print("DB_ALERT_MISSING:", frappe.db.count("Alert Event", {"alert_type": "缺料", "status": ["!=", "已关闭"]}))
    print("DB_ALERT_OVERBUDGET:", frappe.db.count("Alert Event", {"alert_type": "超预算", "status": ["!=", "已关闭"]}))
    sys.exit(0)
main()
