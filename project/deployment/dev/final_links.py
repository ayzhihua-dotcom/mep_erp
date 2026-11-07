import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    name = "业务汇总（专业系统责任人）"
    ws = frappe.get_doc("Workspace", "CB 机电总控")
    if not any(l.link_to == name for l in ws.links):
        ws.append("links", {"type": "Link", "label": "业务汇总（专业/系统/责任人）", "link_to": name,
                            "link_type": "Report", "is_query_report": 1})
        ws.save(ignore_permissions=True); frappe.db.commit(); print("WS_LINK_ADDED")
    else:
        print("WS_LINK_EXISTS")
    from frappe.desk.query_report import run
    res = run(name, filters={})
    rows = res.get("result") or []
    print("REPORT_ROWS:", len(rows))
    for r in rows[:6]:
        print("ROW:", r)
    print("=== 管控门控在役 ===")
    for s in frappe.get_all("Server Script", fields=["name", "reference_doctype", "doctype_event", "disabled"], order_by="name"):
        print("GATE:", s.name, "|", s.reference_doctype, "|", s.doctype_event, "| disabled:", s.disabled)
    print("ALERT_RULES:", frappe.get_all("Alert Rule", fields=["rule_code", "enabled"], order_by="rule_code"))
    sys.exit(0)
main()
