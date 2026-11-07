import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    rows = frappe.get_all("Design Change Request", fields=["name", "design_bom"],
                          order_by="design_bom asc, name asc")
    seen = set()
    dups = []
    for r in rows:
        if r.design_bom in seen:
            dups.append(r.name)
        else:
            seen.add(r.design_bom)
    for n in dups:
        d = frappe.get_doc("Design Change Request", n)
        if d.docstatus == 1:
            d.cancel()
            frappe.db.commit()
        frappe.delete_doc("Design Change Request", n, force=True)
    frappe.db.commit()
    print("DCR_DUPLICATES_REMOVED:", len(dups))
    print("DCR_COUNT:", frappe.db.count("Design Change Request"))
    print("BOM_COUNT:", frappe.db.count("Design BOM"))
    print("QI_COUNT:", frappe.db.count("Quality Inspection"))
    print("FINAL_COUNTS:", {
        "items": frappe.db.count("Item"),
        "suppliers": frappe.db.count("Supplier"),
        "projects": frappe.db.count("Project"),
        "engineers": frappe.db.count("User", {"email": ["like", "eng%@cb.local"]}),
        "bom": frappe.db.count("Design BOM"),
        "dcr": frappe.db.count("Design Change Request"),
        "budgets": frappe.db.count("Material Budget"),
        "commitments": frappe.db.count("Material Commitment"),
        "mrs": frappe.db.count("Material Request"),
        "pos": frappe.db.count("Purchase Order"),
        "import_cases": frappe.db.count("CB Import Case"),
        "shipments": frappe.db.count("CB Shipment"),
        "qi": frappe.db.count("Quality Inspection"),
        "tasks": frappe.db.count("Task"),
        "stock_entries": frappe.db.count("Stock Entry"),
        "alert_events": frappe.db.count("Alert Event"),
    })
    sys.exit(0)
main()
