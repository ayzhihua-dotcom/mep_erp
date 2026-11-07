# -*- coding: utf-8 -*-
def run():
    import frappe
    frappe.set_user("Administrator")
    rows = frappe.db.sql("""select dt, fieldname, fieldtype, options from `tabCustom Field`
                            where fieldname in ('custom_discipline','custom_system')
                            order by dt, fieldname""", as_dict=True)
    for r in rows[:6]:
        print(r)
    print("TOTAL:", len(rows))
    print("LINK_COUNT:", sum(1 for r in rows if r["fieldtype"] == "Link"))
    m = frappe.get_meta("Material Request")
    f = m.get_field("custom_discipline")
    print("META_MR discipline:", f.fieldtype if f else None, f.options if f else None)
    f2 = m.get_field("custom_system")
    print("META_MR system:", f2.fieldtype if f2 else None, f2.options if f2 else None)
    print("MASTERS:", frappe.db.count("CB Discipline"), frappe.db.count("CB System"))
    print("PROJECT_FIELD:", frappe.db.exists("Custom Field", {"dt": "Project", "fieldname": "custom_project_systems"}))
    return "OK"
