# -*- coding: utf-8 -*-
def run():
    import frappe
    frappe.set_user("Administrator")

    print("=== 1) 自定义字段：专业/系统/责任人")
    rows = frappe.get_all("Custom Field",
                          filters={"fieldname": ["in", ["custom_discipline", "custom_system", "custom_responsible"]]},
                          fields=["dt", "fieldname", "fieldtype", "options", "in_standard_filter", "in_list_view"],
                          order_by="dt, fieldname")
    for r in rows:
        print("  %-32s %-20s %-10s %s" % (r["dt"], r["fieldname"], r["fieldtype"], (r["options"] or "")[:60]))

    print("=== 2) Project 上的相关字段")
    for f in frappe.get_meta("Project").fields:
        if "discipline" in f.fieldname or "system" in f.fieldname or "custom_cb" in f.fieldname:
            print("  ", f.fieldname, f.fieldtype, f.options)

    print("=== 3) 各单据存量专业/系统分布")
    tables = {
        "Material Request": "tabMaterial Request",
        "Purchase Order": "tabPurchase Order",
        "Stock Entry": "tabStock Entry",
        "Purchase Receipt": "tabPurchase Receipt",
        "Quality Inspection": "tabQuality Inspection",
    }
    for dt, tb in tables.items():
        if not frappe.db.has_column(dt, "custom_discipline"):
            print("  SKIP(no field):", dt)
            continue
        rows = frappe.db.sql("""select ifnull(custom_discipline,'') d, ifnull(custom_system,'') s, count(*) c
                                from `%s` group by d, s order by c desc""" % tb, as_dict=True)
        print("  --", dt, "total:", frappe.db.count(dt))
        for r in rows[:15]:
            print("     [%s] / [%s] -> %s" % (r["d"], r["s"], r["c"]))

    print("=== 4) 自定义 DocType 上的专业/系统（材料预算/承诺等）")
    for dt in frappe.get_all("DocType", filters={"name": ["like", "CB%"]}, pluck="name"):
        if frappe.db.has_column(dt, "custom_discipline"):
            rows = frappe.db.sql("""select ifnull(custom_discipline,'') d, ifnull(custom_system,'') s, count(*) c
                                    from `tab%s` group by d, s order by c desc""" % dt, as_dict=True)
            print("  --", dt)
            for r in rows[:8]:
                print("     [%s] / [%s] -> %s" % (r["d"], r["s"], r["c"]))

    print("=== 5) 现有 Report / Server Script 是否引用专业系统")
    for r in frappe.get_all("Report", filters={"name": ["like", "%专业%"]}, fields=["name", "report_type", "ref_doctype"]):
        print("  REPORT:", r)
    for s in frappe.get_all("Server Script", fields=["name", "script_type", "reference_doctype"]):
        doc = frappe.get_doc("Server Script", s["name"])
        src = doc.script or ""
        if "custom_discipline" in src or "custom_system" in src:
            print("  SERVER_SCRIPT:", s["name"], s["script_type"], s["reference_doctype"])

    print("=== 6) Bulk Entry 字段")
    for f in frappe.get_meta("Bulk Entry").fields:
        if f.fieldname in ("discipline", "system", "responsible", "project"):
            print("  ", f.fieldname, f.fieldtype, (f.options or "")[:50])

    return "OK"
