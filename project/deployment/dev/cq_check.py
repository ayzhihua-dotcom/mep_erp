import sys
def main():
    import frappe
    from frappe.utils import nowdate, add_days
    frappe.set_user("Administrator")
    try:
        cg = frappe.db.sql("select name from `tabCustomer Group` order by name", as_dict=True)
        print("CUSTOMER_GROUPS:", [c.name for c in cg])
        ter = frappe.db.sql("select name from `tabTerritory` order by name", as_dict=True)
        print("TERRITORIES:", [t.name for t in ter])
    except Exception as e:
        print("ERR:", repr(e))
    sys.exit(0)
main()
