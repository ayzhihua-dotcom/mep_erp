def main():
    import frappe, sys, json, traceback
    out = []
    SRC = "巴西现场总仓 - 巴项"
    ITEM = "CB-GV-001"
    SEEDS = ("MAT-STE-2026-00001", "MAT-STE-2026-00002")
    def w(*a):
        out.append(" ".join(str(x) for x in a))
    def q1(sql, args=None):
        r = frappe.db.sql(sql, args)
        return r[0][0] if r else 0
    try:
        w("=== STEP A0 :: existing Stock Entries / stock state ===")
        se_names = [r[0] for r in frappe.db.sql("select name from `tabStock Entry` order by name")]
        w("all SE:", se_names)
        w("=== STEP A :: cleanup every MAT-STE placeholder (by exact name) ===")
        for nm in se_names:
            if nm in SEEDS and frappe.db.exists("Stock Entry", nm):
                w("keep", nm)
                continue
            ds = frappe.db.get_value("Stock Entry", nm, "docstatus")
            w("cleanup", nm, "docstatus", ds)
            if ds == 1:
                frappe.get_doc("Stock Entry", nm).cancel()
                w("cancelled", nm)
            frappe.delete_doc("Stock Entry", nm, force=True)
            w("deleted SE", nm)
        frappe.db.commit()
        w("--- orphan GL/SLE tied to vanished MAT-STE vouchers ---")
        for tbl in ("tabGL Entry", "tabStock Ledger Entry"):
            rows = frappe.db.sql("select voucher_no as v, count(*) as c from `" + tbl + "` where voucher_no like 'MAT-STE-%%' group by voucher_no", as_dict=1)
            for r in rows:
                v = r["v"]
                still = frappe.db.exists("Stock Entry", v)
                w(tbl, v, "rows", r["c"], "voucher_still_exists", bool(still))
                if not still:
                    frappe.db.sql("delete from `" + tbl + "` where voucher_no=%s", (v,))
                    frappe.db.commit()
                    w("force-removed orphan rows of", v, "from", tbl)
        w("--- rebuild Bin rows for item", ITEM, "---")
        bins = frappe.db.sql("select warehouse, actual_qty from `tabBin` where item_code=%s", (ITEM,), as_dict=1)
        w("bins before:", [(b.warehouse, b.actual_qty) for b in bins])
        frappe.db.sql("delete from `tabBin` where item_code=%s", (ITEM,))
        frappe.db.commit()
        w("bins for", ITEM, "purged; will be rebuilt on submit")
        w("=== STEP B :: restore exact names via flags.in_import ===")
        docs = json.load(open("/home/frappe/seed_docs.json", encoding="utf-8"))
        w("seed loaded:", [d.get("name") for d in docs])
        frappe.flags.in_import = True
        for d in docs:
            nm = d["name"]
            target_submit = (d.get("docstatus") == 1)
            work = dict(d)
            work["items"] = [dict(x) for x in d.get("items", [])]
            if target_submit:
                work["docstatus"] = 0
            doc = frappe.get_doc(work)
            doc.insert()
            w("inserted", doc.name, "docstatus", doc.docstatus)
            if target_submit:
                frappe.get_doc("Stock Entry", nm).submit()
                w("submitted", nm, "docstatus", q1("select docstatus from `tabStock Entry` where name=%s", (nm,)))
            frappe.db.commit()
        frappe.flags.in_import = False
        w("=== STEP C :: readback and field-by-field verify ===")
        mismatches = 0
        for src in docs:
            nm = src["name"]
            if not frappe.db.exists("Stock Entry", nm):
                w("MISSING", nm); mismatches += 1; continue
            cur = frappe.get_doc("Stock Entry", nm)
            want_ds = 1 if src.get("docstatus") == 1 else 0
            w(nm, "docstatus", cur.docstatus, "expected", want_ds)
            if cur.docstatus != want_ds:
                mismatches += 1
            keys = ["company","naming_series","stock_entry_type","purpose","posting_date",
                    "total_outgoing_value","total_incoming_value","value_difference","total_amount","letter_head"]
            for k in keys:
                cv, sv = cur.get(k), src.get(k)
                if isinstance(sv, float):
                    ok = (cv is not None) and abs(float(cv) - sv) < 1e-6
                else:
                    ok = (cv == sv)
                if not ok:
                    mismatches += 1
                    w("MISMATCH", nm, k, "cur=", cv, "src=", sv)
            src_items = src.get("items", [])
            if len(cur.items) != len(src_items):
                mismatches += 1
                w("MISMATCH", nm, "item count", len(cur.items), "vs", len(src_items))
            for ci, si in zip(cur.items, src_items):
                for k in ["item_code","item_name","qty","basic_rate","amount","t_warehouse","s_warehouse",
                          "uom","expense_account","cost_center","description","quality_inspection"]:
                    cv, sv = ci.get(k), si.get(k)
                    if isinstance(sv, float):
                        ok = (cv is not None) and abs(float(cv) - sv) < 1e-6
                    else:
                        ok = (cv == sv)
                    if not ok:
                        mismatches += 1
                        w("MISMATCH", nm, "item", k, "cur=", cv, "src=", sv)
            w("verified", nm, "with", len(keys) + 12 * len(src_items), "field checks")
        w("total mismatches:", mismatches)
        w("=== STEP D :: pristine checks ===")
        after_se = [r[0] for r in frappe.db.sql("select name from `tabStock Entry` order by name")]
        w("all SE after restore:", after_se)
        binv = frappe.db.get_value("Bin", {"item_code": ITEM, "warehouse": SRC}, "actual_qty")
        w("SRC bin actual_qty:", binv, "(expect 12)")
        sle = frappe.db.sql("select voucher_no, warehouse, actual_qty, is_cancelled from `tabStock Ledger Entry` where item_code=%s order by creation", (ITEM,), as_dict=1)
        w("SLE rows for", ITEM, ":", len(sle))
        for r in sle:
            w("  SLE", r.voucher_no, r.warehouse, r.actual_qty, "cancelled", r.is_cancelled)
        orphan = 0
        for r in sle:
            if not frappe.db.exists("Stock Entry", r.voucher_no):
                orphan += 1
        w("orphan SLE:", orphan, "(expect 0)")
        series = frappe.db.sql("select name, current from `tabSeries` where name like 'MAT-STE%'", as_dict=1)
        w("tabSeries MAT-STE counter:", series)
        allbins = frappe.db.sql("select warehouse, actual_qty from `tabBin` where item_code=%s", (ITEM,), as_dict=1)
        w("bins after restore:", [(b.warehouse, b.actual_qty) for b in allbins])
        ok = (after_se and set(after_se) == set(SEEDS) and mismatches == 0 and binv == 12 and orphan == 0)
        w("RESULT:", "PASS" if ok else "FAIL")
    except Exception as e:
        w("FATAL", repr(e))
        w(traceback.format_exc())
    finally:
        try:
            open("/home/frappe/inv009_out.txt", "w", encoding="utf-8").write("\n".join(out))
        except Exception:
            pass
    sys.exit(0)
main()
