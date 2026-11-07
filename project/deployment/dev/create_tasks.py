import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    proj = "PROJ-0001"
    plan = [
        {"subject": "设计出图与评审", "start": "2026-11-01 09:00:00", "end": "2026-11-20 18:00:00", "status": "Working", "priority": "High", "progress": 40, "milestone": 1},
        {"subject": "采购下单", "start": "2026-11-15 09:00:00", "end": "2026-12-10 18:00:00", "status": "Open", "priority": "High", "progress": 0, "milestone": 1},
        {"subject": "进口清关", "start": "2026-12-10 09:00:00", "end": "2027-01-15 18:00:00", "status": "Open", "priority": "Medium", "progress": 0, "milestone": 1},
        {"subject": "到货验收与质检", "start": "2027-01-15 09:00:00", "end": "2027-02-05 18:00:00", "status": "Open", "priority": "High", "progress": 0, "milestone": 1},
        {"subject": "现场安装", "start": "2027-02-01 09:00:00", "end": "2027-03-15 18:00:00", "status": "Open", "priority": "Medium", "progress": 0, "milestone": 0},
        {"subject": "调试与竣工验收", "start": "2027-03-15 09:00:00", "end": "2027-04-10 18:00:00", "status": "Open", "priority": "High", "progress": 0, "milestone": 1},
    ]
    created = []
    for t in plan:
        if frappe.db.exists("Task", {"subject": t["subject"], "project": proj}):
            print("SKIP_EXISTS:", t["subject"])
            continue
        d = frappe.get_doc({
            "doctype": "Task",
            "subject": t["subject"],
            "project": proj,
            "status": t["status"],
            "priority": t["priority"],
            "progress": t["progress"],
            "exp_start_date": t["start"],
            "exp_end_date": t["end"],
            "is_milestone": t["milestone"],
            "description": "AI 代拟草案（项目任务分解示例，承接 TP-PRJ），待项目经理确认/调整。",
        })
        d.insert(ignore_permissions=True)
        created.append(d.name)
    frappe.db.commit()
    print("TASKS_CREATED:", created)
    ws = frappe.get_doc("Workspace", "CB 机电总控")
    have = {l.link_to for l in ws.links}
    for link_to, label in [("Task", "项目任务"), ("Alert Event", "项目预警"), ("Alert Rule", "预警规则")]:
        if link_to not in have:
            ws.append("links", {"type": "Link", "label": label, "link_to": link_to, "link_type": "DocType"})
    ws.save(ignore_permissions=True)
    frappe.db.commit()
    print("WS_LINKS:", [(l.type, l.label, l.link_to) for l in frappe.get_doc("Workspace", "CB 机电总控").links])
    for t in frappe.get_all("Task", fields=["name", "subject", "status", "is_milestone", "progress", "exp_start_date", "exp_end_date"], order_by="exp_start_date asc"):
        print("TASK:", t.name, "|", t.subject, "|", t.status, "| milestone:", t.is_milestone, "| prog:", t.progress, "|", t.exp_start_date, "->", t.exp_end_date)
    print("TASK_COUNT:", frappe.db.count("Task"))
    sys.exit(0)
main()
