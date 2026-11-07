def main():
    import frappe, sys, datetime
    out = []
    SRC = "巴西现场总仓 - 巴项"
    ITEM = "CB-GV-001"
    SEEDS = ("MAT-STE-2026-00001", "MAT-STE-2026-00002")
    def w(*a):
        out.append(" ".join(str(x) for x in a))
    def eq(cv, sv):
        if isinstance(cv, datetime.date):
            return isinstance(sv, str) and str(cv) == sv
        if isinstance(sv, float) or isinstance(cv, float):
            try:
                return abs(float(cv) - float(sv)) < 1e-6
            except Exception:
                return False
        if sv is None or cv is None:
            return cv == sv
        return str(cv) == str(sv)
    try:
        docs = json.load(open("/home/frappe/seed_docs.json", encoding="utf-8")) if False else __import__("json").load(open("/home/frappe/seed_docs.json", encoding="utf-8"))
        mismatches = 0
        checks = 0
        w("=== readback verify (type-safe) ===")
        for src in docs:
            nm = src["name"]
            cur = frappe.get_doc("Stock Entry", nm)
            want_ds = 1 if src.get("docstatus") == 1 else 0
            checks += 1
            if cur.docstatus != want_ds:
                mismatches += 1; w("MISMATCH", nm, "docstatus")
            for k in ["company","naming_series","stock_entry_type","purpose","posting_date","posting_time",
                      "total_outgoing_value","total_incoming_value","value_difference","total_amount","letter_head","is_opening"]:
                checks += 1
                if not eq(cur.get(k), src.get(k)):
                    mismatches += 1; w("MISMATCH", nm, k, "cur=", repr(cur.get(k)), "src=", repr(src.get(k)))
            checks += 1
            if len(cur.items) != len(src.get("items", [])):
                mismatches += 1; w("MISMATCH", nm, "item count")
            for ci, si in zip(cur.items, src.get("items", [])):
                for k in ["item_code","item_name","qty","basic_rate","amount","basic_amount","t_warehouse","s_warehouse",
                          "uom","stock_uom","conversion_factor","expense_account","cost_center","description",
                          "quality_inspection","valuation_rate","transfer_qty","item_group"]:
                    checks += 1
                    if not eq(ci.get(k), si.get(k)):
                        mismatches += 1; w("MISMATCH", nm, "item", k, "cur=", repr(ci.get(k)), "src=", repr(si.get(k)))
            w("verified", nm)
        w("checks:", checks, "mismatches:", mismatches)
        w("=== pristine ===")
        after_se = [r[0] for r in frappe.db.sql("select name from `tabStock Entry` order by name")]
        w("all SE:", after_se)
        binv = frappe.db.get_value("Bin", {"item_code": ITEM, "warehouse": SRC}, "actual_qty")
        w("SRC bin:", binv)
        sle = frappe.db.sql("select voucher_no, warehouse, actual_qty, is_cancelled from `tabStock Ledger Entry` where item_code=%s", (ITEM,), as_dict=1)
        w("SLE rows:", [(r.voucher_no, r.actual_qty) for r in sle])
        orphan = sum(1 for r in sle if not frappe.db.exists("Stock Entry", r.voucher_no))
        w("orphan SLE:", orphan)
        qa = frappe.db.get_value("Stock Entry Detail", {"parent": "MAT-STE-2026-00002"}, "quality_inspection")
        qa_exists = frappe.db.exists("Quality Inspection", "MAT-QA-2026-00001")
        w("00002 item QA link:", qa, "QA doc exists:", bool(qa_exists))
        gl = frappe.db.sql("select voucher_no, count(*) as c from `tabGL Entry` where voucher_no like 'MAT-STE-%%' group by voucher_no", as_dict=1)
        w("GL rows:", [(r.v, r.c) for r in gl])
        ok = (set(after_se) == set(SEEDS) and mismatches == 0 and binv == 12 and orphan == 0 and len(sle) == 1)
        w("RESULT:", "PASS" if ok else "FAIL")
    except Exception as e:
        import traceback
        w("FATAL", repr(e))
        w(traceback.format_exc())
    finally:
        try:
            open("/home/frappe/inv010_out.txt", "w", encoding="utf-8").write("\n".join(out))
        except Exception:
            pass
    sys.exit(0)
main()
