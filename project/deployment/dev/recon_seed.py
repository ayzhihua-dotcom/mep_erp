import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    print("COMPANIES:", frappe.get_all("Company", pluck="name"))
    print("ITEM_GROUPS:", [(g.name, g.is_group) for g in frappe.get_all("Item Group", fields=["name", "is_group"], order_by="name")])
    print("SUPPLIER_GROUPS:", frappe.get_all("Supplier Group", pluck="name"))
    print("UOMS:", frappe.get_all("UOM", pluck="name")[:20])
    print("WAREHOUSES:", [(w.name, w.company) for w in frappe.get_all("Warehouse", fields=["name", "company"])])
    print("COUNTS item/supplier/project/user:",
          frappe.db.count("Item"), frappe.db.count("Supplier"), frappe.db.count("Project"), frappe.db.count("User"))
    print("STOCK_SETTINGS:", {k: frappe.db.get_single_value("Stock Settings", k) for k in ["enable_perpetual_inventory", "auto_insert_price_list_rate_if_missing"]})
    print("SERVER_SCRIPTS:", frappe.get_all("Server Script", fields=["name", "reference_doctype", "doctype_event", "disabled"]))
    print("ITEM_DEFAULT_FIELDS:", [(f.fieldname, f.fieldtype, f.reqd) for f in frappe.get_meta("Item").fields if f.fieldname in ("item_code", "item_name", "item_group", "stock_uom", "is_stock_item", "valuation_rate", "brand", "description")])
    print("SUPPLIER_FIELDS:", [(f.fieldname, f.fieldtype, f.reqd) for f in frappe.get_meta("Supplier").fields if f.fieldname in ("supplier_name", "supplier_group", "supplier_type", "country")])
    print("PROJECT_FIELDS:", [(f.fieldname, f.fieldtype, f.reqd) for f in frappe.get_meta("Project").fields if f.fieldname in ("project_name", "company", "status", "expected_start_date", "expected_end_date", "percent_complete_method")])
    sys.exit(0)
main()
