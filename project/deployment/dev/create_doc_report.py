import sys
def main():
    import frappe, json
    frappe.set_user("Administrator")
    name = "项目文档台账"
    sql = """
    select project as `项目`, '设计BOM' as `单据类型`, name as `单据编号`, date(creation) as `日期`,
      case docstatus when 0 then '草稿' when 1 then '已提交' when 2 then '已取消' else '' end as `状态`,
      ifnull(professional, '') as `备注`
    from `tabDesign BOM` where ifnull(project, '') <> ''
    union all
    select project, '材料预算', name, date(creation),
      case docstatus when 0 then '草稿' when 1 then '已提交' when 2 then '已取消' else '' end,
      ''
    from `tabMaterial Budget` where ifnull(project, '') <> ''
    union all
    select project, '材料承诺', name, date(creation),
      case docstatus when 0 then '草稿' when 1 then '已提交' when 2 then '已取消' else '' end,
      concat(ifnull(item_code, ''), ' x ', ifnull(qty_committed, ''))
    from `tabMaterial Commitment` where ifnull(project, '') <> ''
    union all
    select ifnull(custom_cb_project, ''), '采购申请', name, date(creation),
      case docstatus when 0 then '草稿' when 1 then '已提交' when 2 then '已取消' else '' end,
      ''
    from `tabMaterial Request` where ifnull(custom_cb_project, '') <> ''
    union all
    select ifnull(custom_cb_project, ''), '采购订单', name, date(transaction_date),
      case status when 'Draft' then '草稿' when 'On Hold' then '暂停'
        when 'To Receive and Bill' then '待收货开票' when 'To Bill' then '待开票'
        when 'To Receive' then '待收货' when 'Completed' then '已完成'
        when 'Closed' then '已关闭' when 'Cancelled' then '已取消' else ifnull(status, '') end,
      ifnull(supplier, '')
    from `tabPurchase Order` where ifnull(custom_cb_project, '') <> ''
    union all
    select ifnull(po.custom_cb_project, ''), '进口案件', ic.name, date(ic.creation),
      ifnull(ic.customs_status, ''),
      ifnull(ic.purchase_order, '')
    from `tabCB Import Case` ic join `tabPurchase Order` po on po.name = ic.purchase_order
    where ifnull(po.custom_cb_project, '') <> ''
    union all
    select ifnull(po.custom_cb_project, ''), '装运', sh.name, date(sh.creation),
      ifnull(sh.shipment_status, ''),
      concat(ifnull(sh.carrier, ''), ' ', ifnull(sh.tracking_no, ''))
    from `tabCB Shipment` sh join `tabPurchase Order` po on po.name = sh.purchase_order
    where ifnull(po.custom_cb_project, '') <> ''
    union all
    select ifnull(project, ''), '库存移动', name, date(posting_date),
      ifnull(purpose, ''),
      concat('docstatus ', docstatus)
    from `tabStock Entry` where ifnull(project, '') <> ''
    union all
    select ifnull(project, ''), '任务', name, date(ifnull(exp_start_date, creation)),
      case status when 'Open' then '待开始' when 'Working' then '进行中'
        when 'Completed' then '已完成' when 'Cancelled' then '已取消'
        when 'Overdue' then '已逾期' when 'Pending Review' then '待评审' else ifnull(status, '') end,
      ifnull(subject, '')
    from `tabTask` where ifnull(project, '') <> ''
    union all
    select ifnull(project, ''), '预警', name, date(ifnull(computed_at, creation)),
      ifnull(status, ''),
      concat(ifnull(alert_type, ''), ' ', ifnull(alert_summary, ''))
    from `tabAlert Event` where ifnull(project, '') <> ''
    order by `项目`, `日期` desc
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
    # attach to workspace
    ws = frappe.get_doc("Workspace", "CB 机电总控")
    if not any(l.link_to == name for l in ws.links):
        ws.append("links", {"type": "Link", "label": "项目文档台账", "link_to": name, "link_type": "Report", "is_query_report": 1})
        ws.save(ignore_permissions=True); frappe.db.commit()
        print("WS_LINK_ADDED:", name)
    else:
        print("WS_LINK_EXISTS:", name)
    sys.exit(0)
main()
