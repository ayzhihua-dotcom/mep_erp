import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    names = [r[0] for r in frappe.db.sql(
        "select name from `tabStock Ledger Entry` where voucher_no=%s and is_cancelled=1",
        ("MAT-STE-2026-00031",))]
    print("TO_DELETE:", names)
    for n in names:
        frappe.delete_doc("Stock Ledger Entry", n, force=True)
    frappe.db.commit()
    print("DELETED_COUNT:", len(names))
    left = frappe.db.sql("select name, voucher_type, voucher_no, actual_qty, is_cancelled from `tabStock Ledger Entry`", as_dict=True)
    print("SLE_REMAINING_COUNT:", len(left))
    for s in left:
        print("SLE_LEFT:", s.name, "|", s.voucher_no, "| qty:", s.actual_qty, "| cancelled:", s.is_cancelled)
    print("BIN_CB-GV-001:", frappe.db.get_value("Bin", {"item_code": "CB-GV-001", "warehouse": "巴西现场总仓 - 巴项"}, "actual_qty"))
    orphans = frappe.db.sql("select name from `tabStock Ledger Entry` s where s.voucher_type='Stock Entry' and not exists(select 1 from `tabStock Entry` se where se.name=s.voucher_no)", as_list=True)
    print("ORPHANS_LEFT:", len(orphans))
    print("SE_COUNT:", frappe.db.count("Stock Entry"))
    sys.exit(0)
main()
