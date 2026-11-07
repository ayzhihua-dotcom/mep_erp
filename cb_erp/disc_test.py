# -*- coding: utf-8 -*-
"""专业/系统 联动与项目门控的自动化验证。"""
def run():
    import frappe
    frappe.set_user("Administrator")
    results = []

    # 清理上次测试残留
    for p in frappe.get_all("Project", filters={"project_name": ["like", "ZZ-TEST-DISC%"]}, pluck="name"):
        try:
            frappe.delete_doc("Project", p, force=1, ignore_permissions=True)
        except Exception:
            pass
    frappe.db.commit()

    wh = frappe.get_all("Warehouse", filters={"is_group": 0, "disabled": 0}, pluck="name", limit=1)[0]
    company = frappe.db.get_value("Warehouse", wh, "company")

    # 1) 新建项目：不填专业系统 -> 应报错
    p = frappe.new_doc("Project")
    p.project_name = "ZZ-TEST-DISC-无配置"
    p.company = company
    try:
        p.insert(ignore_permissions=True)
        results.append(("新建项目不填专业系统被拒", "FAIL", "居然保存成功"))
        frappe.delete_doc("Project", p.name, force=1, ignore_permissions=True)
    except frappe.ValidationError as e:
        results.append(("新建项目不填专业系统被拒", "PASS", str(e)[:60]))

    # 2) 新建项目：带一条专业系统 -> 应成功
    p2 = frappe.new_doc("Project")
    p2.project_name = "ZZ-TEST-DISC-有配置"
    p2.company = company
    p2.append("custom_project_systems", {"discipline": "管道", "system": "管道-工艺系统"})
    try:
        p2.insert(ignore_permissions=True)
        frappe.db.commit()
        results.append(("新建项目带专业系统", "PASS", p2.name))
    except Exception as e:
        results.append(("新建项目带专业系统", "FAIL", repr(e)[:120]))
        return results

    # 3) 系统与专业不匹配 -> 应报错
    p3 = frappe.new_doc("Project")
    p3.project_name = "ZZ-TEST-DISC-错配"
    p3.company = company
    p3.append("custom_project_systems", {"discipline": "电气", "system": "管道-工艺系统"})
    try:
        p3.insert(ignore_permissions=True)
        results.append(("项目内专业/系统错配被拒", "FAIL", "居然保存成功"))
        frappe.delete_doc("Project", p3.name, force=1, ignore_permissions=True)
    except frappe.ValidationError as e:
        results.append(("项目内专业/系统错配被拒", "PASS", str(e)[:60]))

    # 4) 采购申请：项目内配置的专业系统 -> 通过
    item = frappe.get_all("Item", filters={"disabled": 0}, pluck="name", limit=1)[0]
    mr = frappe.new_doc("Material Request")
    mr.material_request_type = "Purchase"
    mr.company = company
    mr.custom_cb_project = p2.name
    mr.custom_discipline = "管道"
    mr.custom_system = "管道-工艺系统"
    mr.append("items", {"item_code": item, "qty": 1, "uom": frappe.db.get_value("Item", item, "stock_uom"),
                        "warehouse": wh, "schedule_date": frappe.utils.today()})
    try:
        mr.insert(ignore_permissions=True)
        frappe.db.commit()
        results.append(("采购申请-项目内专业系统", "PASS", mr.name))
    except Exception as e:
        results.append(("采购申请-项目内专业系统", "FAIL", repr(e)[:150]))
        mr = None

    # 5) 采购申请：项目未配置的专业系统 -> 应报错
    mr2 = frappe.new_doc("Material Request")
    mr2.material_request_type = "Purchase"
    mr2.company = company
    mr2.custom_cb_project = p2.name
    mr2.custom_discipline = "电气"
    mr2.custom_system = "电气-电气系统"
    mr2.append("items", {"item_code": item, "qty": 1, "uom": frappe.db.get_value("Item", item, "stock_uom"),
                         "warehouse": wh, "schedule_date": frappe.utils.today()})
    try:
        mr2.insert(ignore_permissions=True)
        results.append(("采购申请-项目外专业系统被拒", "FAIL", "居然保存成功"))
        frappe.delete_doc("Material Request", mr2.name, force=1, ignore_permissions=True)
    except frappe.ValidationError as e:
        results.append(("采购申请-项目外专业系统被拒", "PASS", str(e)[:60]))

    # 6) 系统与专业不一致 -> 应报错
    mr3 = frappe.new_doc("Material Request")
    mr3.material_request_type = "Purchase"
    mr3.company = company
    mr3.custom_discipline = "电气"
    mr3.custom_system = "管道-工艺系统"
    mr3.append("items", {"item_code": item, "qty": 1, "uom": frappe.db.get_value("Item", item, "stock_uom"),
                         "warehouse": wh, "schedule_date": frappe.utils.today()})
    try:
        mr3.insert(ignore_permissions=True)
        results.append(("系统/专业不一致被拒", "FAIL", "居然保存成功"))
        frappe.delete_doc("Material Request", mr3.name, force=1, ignore_permissions=True)
    except frappe.ValidationError as e:
        results.append(("系统/专业不一致被拒", "PASS", str(e)[:60]))

    # 清理
    for d in (mr, p2):
        if d and d.name and frappe.db.exists(d.doctype, d.name):
            if d.docstatus == 0:
                frappe.delete_doc(d.doctype, d.name, force=1, ignore_permissions=True)
    frappe.db.commit()

    print("=== RESULTS")
    for name, status, detail in results:
        print("%-28s %s  %s" % (name, status, detail))
    return results
