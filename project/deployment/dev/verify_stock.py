import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    print("=== ALL SLE ===")
    sles = frappe.get_all("Stock Ledger Entry",
                          fields=["name", "voucher_type", "voucher_no", "item_code", "warehouse", "actual_qty", "is_cancelled", "posting_date"],
                          order_by="posting_date asc, creation asc")
    for s in sles:
        print("SLE:", s.name, "|", s.voucher_type, "|", s.voucher_no, "|", s.item_code, "|", s.warehouse, "|", s.actual_qty, "| cancelled:", s.is_cancelled)
    print("SLE_TOTAL:", len(sles))
    print("=== SUM vs BIN ===")
    sums = frappe.db.sql("select item_code, warehouse, sum(actual_qty) q, count(*) c from `tabStock Ledger Entry` where is_cancelled=0 group by item_code, warehouse", as_dict=True)
    for x in sums:
        b = frappe.db.get_value("Bin", {"item_code": x.item_code, "warehouse": x.warehouse}, "actual_qty")
        print("SUM:", x.item_code, "|", x.warehouse, "| sle_sum:", x.q, "| sle_cnt:", x.c, "| bin:", b, "| match:", (x.q == b))
    print("=== ORPHAN SLE (voucher missing) ===")
    orphans = frappe.db.sql("""
        select s.name, s.voucher_type, s.voucher_no from `tabStock Ledger Entry` s
        where (s.voucher_type='Stock Entry' and not exists(select 1 from `tabStock Entry` se where se.name=s.voucher_no))
           or (s.voucher_type='Delivery Note' and not exists(select 1 from `tabDelivery Note` dn where dn.name=s.voucher_no))
           or (s.voucher_type='Purchase Receipt' and not exists(select 1 from `tabPurchase Receipt` pr where pr.name=s.voucher_no))
    """, as_dict=True)
    print("ORPHAN_COUNT:", len(orphans))
    for o in orphans:
        print("ORPHAN:", o)
    print("=== STOCK ENTRY LIST ===")
    for se in frappe.get_all("Stock Entry", fields=["name", "stock_entry_type", "purpose", "docstatus", "project"], order_by="name asc"):
        print("SE:", se.name, "| type:", se.stock_entry_type, "| purpose:", se.purpose, "| docstatus:", se.docstatus, "| project:", se.project)
    print("SE_COUNT:", frappe.db.count("Stock Entry"))
    sys.exit(0)
main()
