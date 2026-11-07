import sys
def main():
    import frappe
    from frappe.utils import nowdate, add_days
    frappe.set_user("Administrator")
    company = "中巴机电（巴西）项目有限公司"
    cust_name = "测试客户-BR-DEMO"
    wh = "巴西现场总仓 - 巴项"
    try:
        print("== COMPANY CHECK ==")
        print("COMPANY_EXISTS:", frappe.db.exists("Company", company))
        cur = frappe.db.get_value("Company", company, "default_currency")
        print("DEFAULT_CURRENCY:", cur)

        print("== 0) MISSING MASTER (Customer Group / Territory) ==")
        if not frappe.db.exists("Customer Group", "All Customer Groups"):
            frappe.get_doc({"doctype": "Customer Group", "customer_group_name": "All Customer Groups", "parent_customer_group": None, "is_group": False}).insert(ignore_permissions=True)
            print("CREATED CUSTOMER GROUP")
        else:
            print("CG EXISTS")
        if not frappe.db.exists("Territory", "All Territories"):
            frappe.get_doc({"doctype": "Territory", "territory_name": "All Territories", "parent_territory": None}).insert(ignore_permissions=True)
            print("CREATED TERRITORY")
        else:
            print("TERR EXISTS")

        print("== 1) CUSTOMER (草案待追认) ==")
        if not frappe.db.exists("Customer", cust_name):
            c = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": cust_name,
                "customer_type": "Company",
                "customer_group": "All Customer Groups",
                "territory": "All Territories",
            })
            c.insert(ignore_permissions=True)
            print("INSERTED CUSTOMER:", cust_name)
        else:
            print("CUSTOMER_EXISTS:", cust_name)

        print("== 2) SALES ORDER (草案待追认) ==")
        uom = frappe.db.get_value("Item", "CB-GV-001", "stock_uom")
        print("UOM:", uom)
        pl = frappe.db.get_value("Price List", {"selling": 1}, "name")
        if not pl:
            frappe.get_doc({"doctype": "Price List", "price_list_name": "Selling", "selling": 1, "currency": cur or "BRL"}).insert(ignore_permissions=True)
            pl = "Selling"
            print("CREATED PRICE LIST")
        else:
            print("PRICE LIST:", pl)
        pc = frappe.db.get_value("Price List", pl, "currency")
        so_dict = {
            "doctype": "Sales Order",
            "company": company,
            "customer": cust_name,
            "selling_price_list": pl,
            "price_list_currency": pc,
            "plc_conversion_rate": 1.0,
            "transaction_date": nowdate(),
            "delivery_date": add_days(nowdate(), 7),
            "items": [{"item_code": "CB-GV-001", "qty": 5, "uom": uom, "rate": 100.0, "amount": 500.0, "warehouse": wh}],
        }
        if cur:
            so_dict["currency"] = cur
        so = frappe.get_doc(so_dict)
        so.insert(ignore_permissions=True)
        so.submit()
        print("SO_INSERTED:", so.name, "status:", so.status)

        bin_before = frappe.db.get_value("Bin", {"item_code": "CB-GV-001", "warehouse": wh}, "actual_qty")
        print("BIN_QTY_BEFORE_DN:", bin_before)

        print("== 3) DELIVERY NOTE from SO (草案待追认) ==")
        dn_dict = {
            "doctype": "Delivery Note",
            "company": company,
            "customer": cust_name,
            "selling_price_list": pl,
            "price_list_currency": pc,
            "plc_conversion_rate": 1.0,
            "against_sales_order": so.name,
            "items": [{"item_code": "CB-GV-001", "qty": 5, "uom": uom, "rate": 100.0, "amount": 500.0, "warehouse": wh, "sales_order": so.name}],
        }
        if cur:
            dn_dict["currency"] = cur
        dn = frappe.get_doc(dn_dict)
        dn.insert(ignore_permissions=True)
        dn.submit()
        print("DN_INSERTED:", dn.name, "status:", dn.status, "docstatus:", dn.docstatus)

        bin_after = frappe.db.get_value("Bin", {"item_code": "CB-GV-001", "warehouse": wh}, "actual_qty")
        print("BIN_QTY_AFTER_DN:", bin_after)
        sle_count = frappe.db.count("Stock Ledger Entry", {"voucher_no": dn.name})
        print("SLE_FOR_DN:", sle_count)
        frappe.db.commit()
        print("COMMIT_DONE")
        print("EVIDENCE_OK:1")
    except Exception as e:
        print("STEP_ERR:", repr(e))
        import traceback; traceback.print_exc()
        try: frappe.db.rollback()
        except Exception: pass
    sys.exit(0)
main()
