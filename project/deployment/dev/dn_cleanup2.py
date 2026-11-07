import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    dn_name = "MAT-DN-2026-00001"
    so_name = "SAL-ORD-2026-00001"
    cust = "测试客户-BR-DEMO"
    wh = "巴西现场总仓 - 巴项"
    item = "CB-GV-001"
    try:
        print("== orphan SLE cleanup (exact voucher_no) ==")
        names = [r[0] for r in frappe.db.sql(
            "select name from `tabStock Ledger Entry` where voucher_no in (%s,%s)",
            (dn_name, so_name))]
        print("ORPHAN_SLE_BEFORE:", names)
        for n in names:
            frappe.delete_doc("Stock Ledger Entry", n, force=True)
        frappe.db.commit()
        rem = frappe.db.count("Stock Ledger Entry", {"voucher_no": dn_name})
        print("ORPHAN_SLE_REMAINING:", rem)

        print("== bin pristine check (expect 12.0) ==")
        bin_after = frappe.db.get_value("Bin", {"item_code": item, "warehouse": wh}, "actual_qty")
        print("BIN_QTY_AFTER_CLEANUP:", bin_after)

        print("== delete demo customer to restore CUSTOMERS_COUNT=0 ==")
        if frappe.db.exists("Customer", cust):
            frappe.delete_doc("Customer", cust, force=True); frappe.db.commit(); print("CUSTOMER DELETED")
        else:
            print("CUSTOMER_GONE")

        print("== final counts ==")
        print("CUSTOMERS_COUNT:", frappe.db.count("Customer"))
        print("DELIVERY_NOTE_COUNT:", frappe.db.count("Delivery Note"))
        print("SALES_ORDER_COUNT:", frappe.db.count("Sales Order"))
        print("TOTAL_SLE:", frappe.db.count("Stock Ledger Entry"))
        frappe.db.commit()
        print("CLEANUP_OK:1")
    except Exception as e:
        print("CLEANUP_ERR:", repr(e))
        import traceback; traceback.print_exc()
        try: frappe.db.rollback()
        except Exception: pass
    sys.exit(0)
main()
