import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    item = "CB-GV-001"
    wh = "巴西现场总仓 - 巴项"
    proj = "PROJ-0001"
    qty = 2
    company = "中巴机电（巴西）项目有限公司"
    vr = frappe.db.get_value("Item", item, "valuation_rate") or 850
    uom = frappe.db.get_value("Item", item, "stock_uom")
    bin_before = frappe.db.get_value("Bin", {"item_code": item, "warehouse": wh}, "actual_qty")
    print("BIN_BEFORE:", bin_before, "| valuation_rate:", vr, "| uom:", uom)
    se_name = None
    try:
        se = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Issue",
            "company": company,
            "project": proj,
            "items": [{"item_code": item, "qty": qty, "s_warehouse": wh, "uom": uom, "basic_rate": vr, "project": proj}],
        })
        se.insert(ignore_permissions=True)
        se_name = se.name
        print("SE_INSERTED:", se.name, "| derived purpose:", se.purpose)
        se.submit()
        frappe.db.commit()
        print("SE_SUBMITTED:", se.name, "| docstatus:", frappe.db.get_value("Stock Entry", se.name, "docstatus"))
        print("BIN_AFTER:", frappe.db.get_value("Bin", {"item_code": item, "warehouse": wh}, "actual_qty"))
        sle = frappe.db.sql("select name, actual_qty, warehouse from `tabStock Ledger Entry` where voucher_no=%s order by name", (se.name,), as_dict=True)
        for s in sle:
            print("SLE:", s.name, "| qty:", s.actual_qty, "| wh:", s.warehouse)
        from frappe.desk.query_report import run
        res = run("项目物料执行台账", filters={})
        for r in (res.get("result") or []):
            if r.get("项目") == proj and r.get("物料编码") == item:
                print("REPORT_AFTER_ISSUE -> 预算:", r.get("预算数量"), "已出库:", r.get("已出库数量"), "待出库:", r.get("待出库数量"))
    except Exception as e:
        print("SE_ERR:", repr(e))
        import traceback
        traceback.print_exc()
        try:
            frappe.db.rollback()
        except Exception:
            pass
    finally:
        try:
            if se_name and frappe.db.exists("Stock Entry", se_name):
                d = frappe.get_doc("Stock Entry", se_name)
                if d.docstatus == 1:
                    d.cancel()
                    frappe.db.commit()
                    print("SE_CANCELLED")
                frappe.delete_doc("Stock Entry", se_name, force=True)
                frappe.db.commit()
                print("SE_DELETED")
            if se_name:
                names = [r[0] for r in frappe.db.sql("select name from `tabStock Ledger Entry` where voucher_no=%s", (se_name,))]
                for n in names:
                    frappe.delete_doc("Stock Ledger Entry", n, force=True)
                frappe.db.commit()
                print("ORPHAN_SLE_DELETED:", len(names))
            print("BIN_FINAL:", frappe.db.get_value("Bin", {"item_code": item, "warehouse": wh}, "actual_qty"))
            from frappe.desk.query_report import run as run2
            res2 = run2("项目物料执行台账", filters={})
            for r in (res2.get("result") or []):
                if r.get("项目") == proj and r.get("物料编码") == item:
                    print("REPORT_AFTER_ROLLBACK -> 已出库:", r.get("已出库数量"), "待出库:", r.get("待出库数量"))
            print("SE_COUNT:", frappe.db.count("Stock Entry"), "| SLE_COUNT:", frappe.db.count("Stock Ledger Entry"))
        except Exception as e:
            print("ROLLBACK_ERR:", repr(e))
            import traceback
            traceback.print_exc()
    sys.exit(0)
main()
