import sys, hashlib
def main():
    import frappe
    frappe.set_user("Administrator")
    DISC_MAP = {"管道与阀门": "管道", "电气与电缆": "电气", "仪表与自控": "仪表", "暖通空调": "暖通",
                "给排水": "给排水", "消防": "消防", "钢结构与建筑": "钢结构", "机电设备与主材": "机械设备",
                "焊接与辅材": "焊接", "防腐保温": "防腐保温", "安全与临时设施": "安全环保",
                "弱电与通信": "电气", "五金辅材": "其他", "其他": "其他"}
    SYS_MAP = {"管道": "工艺系统", "电气": "电气系统", "仪表": "仪表自控系统", "暖通": "暖通空调系统",
               "给排水": "给排水系统", "消防": "消防系统", "钢结构": "工艺系统", "机械设备": "工艺系统",
               "焊接": "工艺系统", "防腐保温": "工艺系统", "安全环保": "其他", "其他": "其他"}

    def l1_of(group):
        g = group
        while g:
            parent = frappe.db.get_value("Item Group", g, "parent_item_group")
            if not parent or parent == "所有物料组":
                return g
            g = parent
        return "其他"

    def first_item(dt, name):
        child = {"Material Request": "Material Request Item", "Stock Entry": "Stock Entry Detail",
                 "Purchase Order": "Purchase Order Item", "Stock Reconciliation": "Stock Reconciliation Item"}.get(dt)
        if not child:
            return None
        rows = frappe.get_all(child, filters={"parent": name}, fields=["item_code"], limit=1)
        return rows[0].item_code if rows else None

    targets = ["Material Request", "Stock Entry", "Purchase Order", "Stock Reconciliation"]
    for dt in targets:
        proj_field = "custom_cb_project" if dt in ("Material Request", "Purchase Order") else "project"
        rows = frappe.get_all(dt, fields=["name", "owner", proj_field], limit=0)
        n = 0
        for r in rows:
            item = first_item(dt, r.name)
            group = frappe.db.get_value("Item", item, "item_group") if item else None
            l1 = l1_of(group) if group else "其他"
            disc = DISC_MAP.get(l1, "其他")
            sysm = SYS_MAP.get(disc, "其他")
            proj = r.get(proj_field) or r.name
            h = int(hashlib.md5(str(proj).encode("utf-8")).hexdigest(), 16)
            resp = "eng%02d@cb.local" % ((h % 50) + 1)
            frappe.db.set_value(dt, r.name, {"custom_discipline": disc, "custom_system": sysm,
                                             "custom_responsible": resp}, update_modified=False)
            n += 1
        frappe.db.commit()
        print("BACKFILL", dt, n)

    # in_standard_filter
    alltargets = ["Material Request", "Stock Entry", "Stock Reconciliation", "Purchase Order", "Material Budget",
                  "Material Commitment", "CB Import Case", "CB Shipment", "Design BOM", "Design Change Request"]
    for t in alltargets:
        for fn in ["custom_discipline", "custom_system", "custom_responsible"]:
            nm = frappe.db.get_value("Custom Field", {"dt": t, "fieldname": fn}, "name")
            if nm:
                frappe.db.set_value("Custom Field", nm, "in_standard_filter", 1, update_modified=False)
    frappe.db.commit()
    print("IN_STANDARD_FILTER_SET")

    # summary report
    name = "业务汇总（专业系统责任人）"
    sql = """
    select custom_discipline as `专业`, custom_system as `系统`, custom_responsible as `责任人`,
      sum(case when dt='MR' then 1 else 0 end) as `采购申请`,
      sum(case when dt='SE' then 1 else 0 end) as `库存移动`,
      sum(case when dt='PO' then 1 else 0 end) as `采购订单`,
      count(*) as `合计`
    from (
      select custom_discipline, custom_system, custom_responsible, 'MR' as dt from `tabMaterial Request`
      union all
      select custom_discipline, custom_system, custom_responsible, 'SE' from `tabStock Entry`
      union all
      select custom_discipline, custom_system, custom_responsible, 'PO' from `tabPurchase Order`
    ) x
    where ifnull(custom_discipline, '') <> ''
    group by custom_discipline, custom_system, custom_responsible
    order by `专业`, `系统`, `责任人`
    """
    if frappe.db.exists("Report", name):
        rep = frappe.get_doc("Report", name)
        rep.query = sql; rep.report_type = "Query Report"; rep.ref_doctype = "Material Request"
        rep.is_standard = 0; rep.disabled = 0; rep.add_total_row = 0
        rep.save(ignore_permissions=True); print("REPORT_UPDATED")
    else:
        frappe.get_doc({"doctype": "Report", "report_name": name, "ref_doctype": "Material Request",
                        "report_type": "Query Report", "is_standard": 0, "query": sql,
                        "disabled": 0, "add_total_row": 0}).insert(ignore_permissions=True)
        print("REPORT_CREATED")
    frappe.db.commit()
    from frappe.desk.query_report import run
    res = run(name, filters={})
    print("REPORT_COLS:", [c.get("label") for c in (res.get("columns") or [])])
    rows = res.get("result") or []
    print("REPORT_ROWS:", len(rows))
    for r in rows[:8]:
        print("ROW:", r)
    frappe.clear_cache()
    sys.exit(0)
main()
