import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    print("MODULE_PATH_CB_ERP:", frappe.get_module_path("CB ERP"))
    print("APP_PATH_CB_ERP:", frappe.get_app_path("cb_erp"))
    po_meta = frappe.get_meta("Purchase Order")
    print("PO_HAS_custom_cb_project:", bool(po_meta.get_field("custom_cb_project")))
    print("SE_PURPOSES:", [r[0] for r in frappe.db.sql("select distinct purpose from `tabStock Entry`", as_list=True)])
    sql = """
    select x.project, x.item_code, i.item_name,
      sum(x.budget_qty) as budget_qty, sum(x.commit_qty) as commit_qty,
      sum(x.po_qty) as po_qty, sum(x.issue_qty) as issue_qty
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
    rows = frappe.db.sql(sql, as_dict=True)
    print("REPORT_ROWS:", len(rows))
    for r in rows:
        print("ROW:", r.project, "|", r.item_code, "|", r.item_name, "| budget:", r.budget_qty, "| commit:", r.commit_qty, "| po:", r.po_qty, "| issue:", r.issue_qty)
    sys.exit(0)
main()
