import sys
def main():
    import frappe, json
    frappe.set_user("Administrator")
    # 1) seed PRJ rules
    rules = [
        {"rule_code": "PRJ-001", "alert_type": "其他", "threshold_days": 0, "assignee_role": "PM 项目经理",
         "remark": "任务逾期：未完成/未取消且计划完成日<今天，度量=逾期天数。"},
        {"rule_code": "PRJ-002", "alert_type": "其他", "threshold_days": 7, "assignee_role": "PM 项目经理",
         "remark": "里程碑临期：里程碑任务未完成且计划完成日在未来 N=7 天内。"},
    ]
    for r in rules:
        if frappe.db.exists("Alert Rule", r["rule_code"]):
            d = frappe.get_doc("Alert Rule", r["rule_code"])
            for k, v in r.items():
                setattr(d, k, v)
            d.notify_email = 1; d.notify_system = 1; d.enabled = 1; d.rule_version = "v2026.11.04-1"
            d.save(ignore_permissions=True)
            print("RULE_UPDATED:", r["rule_code"])
        else:
            d = frappe.get_doc({"doctype": "Alert Rule", "notify_email": 1, "notify_system": 1,
                                "enabled": 1, "rule_version": "v2026.11.04-1", **r})
            d.insert(ignore_permissions=True)
            print("RULE_CREATED:", r["rule_code"])
    frappe.db.commit()
    # 2) project progress (Task Progress = avg task progress)
    tasks = frappe.get_all("Task", filters={"project": "PROJ-0001"}, fields=["progress"])
    avg = (sum((x.progress or 0) for x in tasks) / len(tasks)) if tasks else 0
    p = frappe.get_doc("Project", "PROJ-0001")
    p.percent_complete_method = "Task Progress"
    p.percent_complete = round(avg, 2)
    p.save(ignore_permissions=True)
    frappe.db.commit()
    p2 = frappe.get_doc("Project", "PROJ-0001")
    print("PROJECT_PROGRESS:", p2.percent_complete, "| method:", p2.percent_complete_method, "| tasks:", len(tasks))
    # 3) number card 逾期任务 -> attach
    label = "逾期任务"
    filters = [["rule_code", "=", "PRJ-001"], ["status", "!=", "已关闭"]]
    if frappe.db.exists("Number Card", label):
        nc = frappe.get_doc("Number Card", label)
    else:
        nc = frappe.new_doc("Number Card"); nc.label = label
    nc.type = "Document Type"; nc.document_type = "Alert Event"; nc.function = "Count"; nc.is_public = 1
    nc.filters_json = json.dumps(filters, ensure_ascii=False)
    nc.save(ignore_permissions=True) if frappe.db.exists("Number Card", label) else nc.insert(ignore_permissions=True)
    frappe.db.commit()
    ws = frappe.get_doc("Workspace", "CB 机电总控")
    if label not in {r.number_card_name for r in ws.number_cards}:
        ws.append("number_cards", {"number_card_name": label, "label": label})
    content = json.loads(ws.content or "[]")
    if label not in {b.get("data", {}).get("number_card_name") for b in content if b.get("type") == "number_card"}:
        ws.content = json.dumps([{"id": frappe.generate_hash(length=10), "type": "number_card",
                                  "data": {"number_card_name": label, "col": 4}}] + content, ensure_ascii=False)
    ws.save(ignore_permissions=True)
    frappe.db.commit()
    print("CARD_ATTACHED:", label)
    print("ALL_RULES:", [(r.name, r.alert_type, r.enabled, r.threshold_days) for r in frappe.get_all("Alert Rule", fields=["name", "alert_type", "enabled", "threshold_days"])])
    print("WS_NUMCARDS:", [r.number_card_name for r in frappe.get_doc("Workspace", "CB 机电总控").number_cards])
    sys.exit(0)
main()
