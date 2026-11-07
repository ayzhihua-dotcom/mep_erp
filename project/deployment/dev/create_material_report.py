import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    name = "项目物料执行台账"
    sql = """
    select x.project as `项目`, x.item_code as `物料编码`, i.item_name as `物料名称`,
      sum(x.budget_qty) as `预算数量`, sum(x.commit_qty) as `承诺数量`,
      sum(x.po_qty) as `采购数量`, sum(x.issue_qty) as `已出库数量`,
      (sum(x.budget_qty) - sum(x.issue_qty)) as `待出库数量`
    from (
      select mb.project as project, mbd.item_code as item_code, mbd.qty as budget_qty, 0 as commit_qty, 0 as po_qty, 0 as issue_qty
      from `tabMaterial Budget` mb join `tabMaterial Budget Detail` mbd on mbd.parent = mb.name
      where mb.docstatus < 2
      union all
      select mc.project, mc.item_code, 0, mc.qty_committed, 0, 0
      from `tabMaterial Commitment` mc where mc.docstatus < 2
      union all
      select po.custom_cb_project, poi.item_code, 0, 0, poi.qty, 0
      from `tabPurchase Order` po join `tabPurchase Order Item` poi on poi.parent = po.name
      where po.docstatus < 2 and ifnull(po.custom_cb_project, '') != ''
      union all
      select se.project, sed.item_code, 0, 0, 0, sed.qty
      from `tabStock Entry` se join `tabStock Entry Detail` sed on sed.parent = se.name
      where se.docstatus = 1 and se.purpose = 'Material Issue' and ifnull(se.project, '') != ''
    ) x
    left join `tabItem` i on i.name = x.item_code
    group by x.project, x.item_code, i.item_name
    order by x.project, x.item_code
    """
    if frappe.db.exists("Report", name):
        rep = frappe.get_doc("Report", name)
        rep.query = sql
        rep.report_type = "Query Report"
        rep.ref_doctype = "Project"
        rep.is_standard = 0
        rep.disabled = 0
        rep.add_total_row = 0
        rep.save(ignore_permissions=True)
        print("REPORT_UPDATED:", name)
    else:
        rep = frappe.get_doc({
            "doctype": "Report",
            "report_name": name,
            "ref_doctype": "Project",
            "report_type": "Query Report",
            "is_standard": 0,
            "query": sql,
            "disabled": 0,
            "add_total_row": 0,
        })
        rep.insert(ignore_permissions=True)
        print("REPORT_CREATED:", rep.name)
    frappe.db.commit()
    from frappe.desk.query_report import run
    res = run(name, filters={})
    print("RESULT_KEYS:", list(res.keys()))
    print("COLUMNS:", res.get("columns"))
    rows = res.get("result") or []
    print("ROW_COUNT:", len(rows))
    for r in rows[:5]:
        print("ROW:", r)
    sys.exit(0)
main()
