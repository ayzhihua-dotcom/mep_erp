# -*- coding: utf-8 -*-
def run():
    import frappe
    frappe.set_user("Administrator")
    frappe.db.sql("""update `tabDocField` set fieldtype='Link', options='CB Discipline'
                     where parent='Bulk Entry' and fieldname='discipline'""")
    frappe.db.sql("""update `tabDocField` set fieldtype='Link', options='CB System'
                     where parent='Bulk Entry' and fieldname='system'""")
    frappe.db.commit()
    frappe.clear_cache()
    m = frappe.get_meta("Bulk Entry")
    print("BULK_ENTRY discipline:", m.get_field("discipline").fieldtype, m.get_field("discipline").options)
    print("BULK_ENTRY system:", m.get_field("system").fieldtype, m.get_field("system").options)
    return "OK"
