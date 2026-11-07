import sys
def main():
    import frappe
    from frappe.model.document import Document
    def safe(fn, label):
        try:
            print(label, "->", fn())
        except Exception as e:
            print(label, "ERR:", repr(e))
    try:
        site = frappe.local.site
        conf = frappe.get_site_config(site) if False else None
        # read site config file directly via bench path
        import os, json
        cfg_path = os.path.join(frappe.local.sites_path, site, "site_config.json")
        try:
            with open(cfg_path) as f:
                cfg = json.load(f)
            print("TRUSTED_HOSTS:", cfg.get("trusted_hosts"))
            print("HOST_NAME:", cfg.get("host_name"))
            print("DB_NAME:", cfg.get("db_name"))
        except Exception as e:
            print("CFG_READ_ERR:", repr(e))
        print("--- BUSINESS DATA ---")
        custs = frappe.db.sql("select name, disabled from `tabCustomer` order by name", as_dict=True)
        print("CUSTOMERS_COUNT:", len(custs))
        for c in custs[:15]:
            print("  CUST:", c.name, "disabled" if c["disabled"] else "")
        item = frappe.db.get_value("Item", "CB-GV-001", ["name","is_stock_item","stock_uom"])
        print("ITEM_CB_GV_001:", item)
        bins = frappe.db.sql("select warehouse, actual_qty from `tabBin` where item_code='CB-GV-001'", as_dict=True)
        print("BINS_CB_GV_001:")
        for b in bins:
            print("  WH:", b.warehouse, "QTY:", b.actual_qty)
        whs = frappe.db.sql("select name from `tabWarehouse` where name like %s", ("%%巴项%%",), as_dict=True)
        print("WAREHOUSES_巴项:")
        for w in whs:
            print("  WH:", w.name)
        so_count = frappe.db.count("Sales Order")
        print("SALES_ORDERS_COUNT:", so_count)
        print("DONE:1")
    except Exception as e:
        print("FATAL:", repr(e))
    sys.exit(0)
main()
