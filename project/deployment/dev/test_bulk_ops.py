import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    from cb_erp.cb_erp.bulk_ops import api_create
    WH = "巴西现场总仓 - 巴项"
    PROJ = "PROJ-0001"
    ITEM = "SIM-PV-0001"
    created = []
    def run(kind, rows, **kw):
        try:
            res = api_create(kind, rows, **kw)
            print("RESULT", kind, "=>", res)
            for c in res.get("created", []):
                created.append((c["kind"], c["name"]))
        except Exception as e:
            print("RUN_ERR", kind, repr(e)[:300])
    run("material_request", [{"item_code": ITEM, "qty": 3, "project": PROJ}], project=PROJ)
    run("material_receipt", [{"item_code": ITEM, "qty": 20, "warehouse": WH, "rate": 100}], warehouse=WH)
    run("material_issue", [{"item_code": ITEM, "qty": 2, "warehouse": WH, "project": PROJ}], project=PROJ)
    run("material_return", [{"item_code": ITEM, "qty": 1, "warehouse": WH, "project": PROJ}], project=PROJ)
    run("stock_reconciliation", [{"item_code": ITEM, "qty": 18, "warehouse": WH}], warehouse=WH)
    print("CREATED:", created)
    # cleanup
    try:
        for kind, name in reversed(created):
            dt = "Material Request" if kind == "material_request" else ("Stock Reconciliation" if kind == "stock_reconciliation" else "Stock Entry")
            if not frappe.db.exists(dt, name):
                continue
            d = frappe.get_doc(dt, name)
            if d.docstatus == 1:
                d.cancel(); frappe.db.commit()
            frappe.delete_doc(dt, name, force=True); frappe.db.commit()
            if dt != "Material Request":
                for r in frappe.get_all("Stock Ledger Entry", filters={"voucher_no": name}, pluck="name"):
                    try: frappe.delete_doc("Stock Ledger Entry", r, force=True)
                    except Exception: pass
                frappe.db.commit()
            print("CLEANED", dt, name)
        print("AFTER_CLEAN SLE:", frappe.db.count("Stock Ledger Entry"))
    except Exception as e:
        print("CLEANUP_ERR", repr(e)[:300])
    sys.exit(0)
main()
