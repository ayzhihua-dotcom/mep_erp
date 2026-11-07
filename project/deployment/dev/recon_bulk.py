import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    print("PAGE_FIELDS:", [f.fieldname for f in frappe.get_meta("Page").fields])
    print("PAGES:", frappe.get_all("Page", fields=["name", "page_name", "module", "standard"], limit=10))
    print("STOCK_RECON_FIELDS:", [(f.fieldname, f.fieldtype) for f in frappe.get_meta("Stock Reconciliation").fields if f.fieldname in ("company", "purpose", "posting_date", "set_warehouse", "items", "expense_account", "cost_center")])
    sr_child = frappe.get_meta("Stock Reconciliation Item")
    print("SR_ITEM_FIELDS:", [(f.fieldname, f.fieldtype) for f in sr_child.fields if f.fieldname in ("item_code", "warehouse", "qty", "valuation_rate", "batch_no", "serial_no", "current_qty", "current_valuation_rate")])
    sed = frappe.get_meta("Stock Entry Detail")
    print("SE_DETAIL_RETURN_FIELDS:", [(f.fieldname, f.fieldtype) for f in sed.fields if f.fieldname in ("is_return", "against_stock_entry", "against_stock_entry_detail", "s_warehouse", "t_warehouse", "project", "qty", "basic_rate", "transfer_qty")])
    se = frappe.get_meta("Stock Entry")
    print("SE_HEADER_FIELDS:", [(f.fieldname, f.fieldtype) for f in se.fields if f.fieldname in ("is_return", "purpose", "stock_entry_type", "company", "project", "set_warehouse", "from_warehouse", "to_warehouse", "posting_date")])
    try:
        import openpyxl
        print("OPENPYXL: yes", getattr(openpyxl, "__version__", ""))
    except Exception as e:
        print("OPENPYXL: no", repr(e))
    sys.exit(0)
main()
