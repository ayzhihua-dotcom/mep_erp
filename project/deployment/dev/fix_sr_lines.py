import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    try:
        frappe.db.sql("""update `tabStock Reconciliation Item` i
            join `tabItem` it on it.name = i.item_code
            set i.custom_seq = i.idx, i.custom_uom = it.stock_uom,
                i.custom_item_name = it.item_name""")
        frappe.db.commit()
        print("SR_BACKFILLED")
    except Exception as e:
        print("SR_ERR", repr(e)[:150])
    sys.exit(0)
main()
