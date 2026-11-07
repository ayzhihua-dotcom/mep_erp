import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    name = "项目总览"
    sql = """
    select p.name as `项目`, ifnull(p.project_name, '') as `项目名称`,
      ifnull(p.percent_complete, 0) as `进度`,
      coalesce(t.total, 0) as `任务数`, coalesce(t.done, 0) as `已完成`, coalesce(t.overdue, 0) as `逾期任务`,
      coalesce(mb.budgets, 0) as `预算单`, coalesce(mc.commits, 0) as `承诺单`,
      coalesce(po.pos, 0) as `采购订单`, coalesce(iss.issued_qty, 0) as `已出库数量`,
      coalesce(al.open_alerts, 0) as `未关闭预警`
    from `tabProject` p
    left join (select project, count(*) total,
                 sum(case when status = 'Completed' then 1 else 0 end) done,
                 sum(case when status not in ('Completed', 'Cancelled') and exp_end_date < now() then 1 else 0 end) overdue
               from `tabTask` group by project) t on t.project = p.name
    left join (select project, count(*) budgets from `tabMaterial Budget` where docstatus < 2 group by project) mb on mb.project = p.name
    left join (select project, count(*) commits from `tabMaterial Commitment` where docstatus < 2 group by project) mc on mc.project = p.name
    left join (select custom_cb_project as project, count(*) pos from `tabPurchase Order` where docstatus < 2 group by custom_cb_project) po on po.project = p.name
    left join (select se.project as project, sum(sed.qty) issued_qty
               from `tabStock Entry` se join `tabStock Entry Detail` sed on sed.parent = se.name
               where se.docstatus = 1 and se.purpose = 'Material Issue' group by se.project) iss on iss.project = p.name
    left join (select project, count(*) open_alerts from `tabAlert Event` where status <> '已关闭' group by project) al on al.project = p.name
    order by p.name
    """
    if frappe.db.exists("Report", name):
        rep = frappe.get_doc("Report", name)
        rep.query = sql; rep.report_type = "Query Report"; rep.ref_doctype = "Project"
        rep.is_standard = 0; rep.disabled = 0; rep.add_total_row = 0
        rep.save(ignore_permissions=True)
        print("REPORT_UPDATED:", name)
    else:
        rep = frappe.get_doc({"doctype": "Report", "report_name": name, "ref_doctype": "Project",
                              "report_type": "Query Report", "is_standard": 0, "query": sql,
                              "disabled": 0, "add_total_row": 0})
        rep.insert(ignore_permissions=True)
        print("REPORT_CREATED:", name)
    frappe.db.commit()
    from frappe.desk.query_report import run
    res = run(name, filters={})
    print("COLUMNS:", [c.get("label") for c in (res.get("columns") or [])])
    rows = res.get("result") or []
    print("ROW_COUNT:", len(rows))
    for r in rows:
        print("ROW:", r)
    ws = frappe.get_doc("Workspace", "CB 机电总控")
    if not any(l.link_to == name for l in ws.links):
        ws.append("links", {"type": "Link", "label": "项目总览", "link_to": name, "link_type": "Report", "is_query_report": 1})
        ws.save(ignore_permissions=True); frappe.db.commit()
        print("WS_LINK_ADDED:", name)
    else:
        print("WS_LINK_EXISTS:", name)
    sys.exit(0)
main()
