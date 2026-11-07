import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    for dt in ["Material Request Item", "Stock Entry Detail", "Purchase Order Item", "Stock Reconciliation Item"]:
        m = frappe.get_meta(dt)
        f1 = m.get_field("custom_spec")
        f2 = m.get_field("custom_remark")
        print(dt, "| spec:", bool(f1), "ilv:", (f1.in_list_view if f1 else None),
              "| remark:", bool(f2), "ilv:", (f2.in_list_view if f2 else None),
              "| item_name:", bool(m.get_field("item_name")), "| qty:", bool(m.get_field("qty")))
    print("ITEM_custom_spec:", bool(frappe.get_meta("Item").get_field("custom_spec")))
    sys.exit(0)
main()
