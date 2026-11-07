# -*- coding: utf-8 -*-
import json


def run():
    import frappe
    frappe.set_user("Administrator")
    out = {}

    out["masters"] = {"disciplines": frappe.db.count("CB Discipline"), "systems": frappe.db.count("CB System")}
    orphan = frappe.db.sql("""select s.name from `tabCB System` s
                              left join `tabCB Discipline` d on d.name=s.discipline
                              where d.name is null""", as_dict=True)
    out["systems_without_discipline"] = [r["name"] for r in orphan]

    fields = frappe.db.sql("""select dt, fieldname, fieldtype, options from `tabCustom Field`
                              where fieldname in ('custom_discipline','custom_system')""", as_dict=True)
    out["custom_fields"] = {"total": len(fields),
                            "link": sum(1 for f in fields if f["fieldtype"] == "Link"),
                            "bad": [(f["dt"], f["fieldname"], f["fieldtype"]) for f in fields if f["fieldtype"] != "Link"]}

    proj_total = frappe.db.count("Project")
    proj_with = frappe.db.sql("""select count(distinct parent) c from `tabCB Project System`""", as_dict=True)[0]["c"]
    out["projects"] = {"total": proj_total, "with_config": proj_with, "without": proj_total - proj_with}

    fill = {}
    for dt in ["Material Request", "Purchase Order", "Stock Entry", "Stock Reconciliation",
               "Material Budget", "Material Commitment", "Design BOM", "Design Change Request",
               "CB Shipment", "CB Import Case"]:
        if not frappe.db.has_column(dt, "custom_discipline"):
            continue
        total = frappe.db.count(dt)
        filled = frappe.db.sql("""select count(*) c from `tab%s`
                                  where ifnull(custom_discipline,'')!='' and ifnull(custom_system,'')!=''""" % dt,
                               as_dict=True)[0]["c"]
        partial = frappe.db.sql("""select count(*) c from `tab%s`
                                   where (ifnull(custom_discipline,'')='') <> (ifnull(custom_system,'')='')""" % dt,
                                as_dict=True)[0]["c"]
        fill[dt] = {"total": total, "filled": filled, "partial": partial}
    out["fill_rate"] = fill

    bad = frappe.db.sql("""select count(*) c from `tabMaterial Request` x
                           where ifnull(x.custom_system,'')!='' and not exists
                             (select 1 from `tabCB System` s where s.name=x.custom_system)""", as_dict=True)[0]["c"]
    out["mr_invalid_system"] = bad

    out["purchase_receipt_has_disc"] = frappe.db.has_column("Purchase Receipt", "custom_discipline")
    out["quality_inspection_has_disc"] = frappe.db.has_column("Quality Inspection", "custom_discipline")

    # 报表与预警是否依赖这些字段
    rep = frappe.get_doc("Report", "业务汇总（专业系统责任人）")
    out["report_uses_discipline"] = "custom_discipline" in (rep.query or "")

    print(json.dumps(out, ensure_ascii=True, indent=1))
    return "OK"
