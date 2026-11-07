import sys
def main():
    import frappe, json
    frappe.set_user("Administrator")
    defs = {
        "在办项目": [["Project", "status", "=", "Open"]],
        "在办任务": [["Task", "status", "in", ["Open", "Working"]]],
        "未关闭预警": [["Alert Event", "status", "!=", "已关闭"]],
        "缺料预警": [["Alert Event", "alert_type", "=", "缺料"], ["Alert Event", "status", "!=", "已关闭"]],
        "超预算预警": [["Alert Event", "alert_type", "=", "超预算"], ["Alert Event", "status", "!=", "已关闭"]],
        "逾期任务": [["Alert Event", "rule_code", "=", "PRJ-001"], ["Alert Event", "status", "!=", "已关闭"]],
    }
    for lb, flt in defs.items():
        d = frappe.get_doc("Number Card", lb)
        d.filters_json = json.dumps(flt, ensure_ascii=False)
        d.save(ignore_permissions=True)
    frappe.db.commit()
    from frappe.desk.doctype.number_card.number_card import get_result
    for lb, flt in defs.items():
        d = frappe.get_doc("Number Card", lb)
        try:
            val = get_result(d, flt)
        except Exception as e:
            val = "ERR:" + repr(e)
        print("VALUE", lb, "=", val)
    sys.exit(0)
main()
