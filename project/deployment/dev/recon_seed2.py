import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    for s in frappe.get_all("Server Script", fields=["name", "reference_doctype", "doctype_event", "disabled"]):
        doc = frappe.get_doc("Server Script", s.name)
        print("=== SCRIPT:", s.name, "|", s.reference_doctype, "|", s.doctype_event, "| disabled:", doc.disabled, "===")
        print((doc.script or "")[:900])
        print("=== END ===")
    uoms = frappe.get_all("UOM", pluck="name")
    print("UOM_LIST:", uoms)
    print("UOM_COUNT:", len(uoms))
    print("ITEM_FIELDS_CHECK:", [f.fieldname for f in frappe.get_meta("Item").fields if f.fieldname in ("valuation_rate", "is_stock_item", "stock_uom", "item_group", "has_batch_no", "has_serial_no")])
    print("SUPPLIER_REQD:", [(f.fieldname, f.reqd) for f in frappe.get_meta("Supplier").fields if f.reqd])
    print("PROJECT_REQD:", [(f.fieldname, f.reqd) for f in frappe.get_meta("Project").fields if f.reqd])
    sys.exit(0)
main()
