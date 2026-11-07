def main():
    import frappe, json, sys
    out=[]
    def w(x): out.append(str(x))
    try:
        # =========================================================
        # STEP A: clean up stray auto-named placeholder docs (00030 draft, 00031 submitted) + their SLEs -> SRC=0
        # =========================================================
        stray = [n for n in ['MAT-STE-2026-00031','MAT-STE-2026-00030'] if frappe.db.exists('Stock Entry', n)]
        w(('STEP A stray docs to clean:', stray))
        for nm in stray:
            d = frappe.get_doc('Stock Entry', nm)
            if d.docstatus == 1:
                d.cancel()          # reverses inventory (SRC +12 -> 0), creates -12 SLE
                w(('STEP A cancelled', nm))
            d.delete(force=True)    # remove doc row
            w(('STEP A deleted doc', nm))
        # delete ALL SLE rows for these vouchers directly (bin already corrected by cancel/reverse)
        sle_rows = frappe.get_all('Stock Ledger Entry', filters={'voucher_no': ['in', stray]}, fields=['name'])
        for r in sle_rows:
            frappe.db.delete('Stock Ledger Entry', {'name': r['name']})
        w(('STEP A deleted SLE rows:', len(sle_rows)))
        frappe.db.commit()
        srcA = frappe.get_all('Bin', filters={'item_code':'CB-GV-001','warehouse':'巴西现场总仓 - 巴项'}, fields=['actual_qty'])
        w(('STEP A SRC bin after cleanup (expect 0.0):', srcA))

        # =========================================================
        # STEP B: load seed JSON
        # =========================================================
        with open('/home/frappe/seed_docs.json','r',encoding='utf-8') as f:
            data = json.load(f)
        w(('STEP B loaded %d seed docs' % len(data)))

        def insert_and_rename(target_name, want_submit):
            # find matching source by intended name in JSON
            src = None
            for d in data:
                if d['name'] == target_name:
                    src = d; break
            if not src:
                w(('STEP B no source for', target_name)); return False
            doc = frappe.new_doc('Stock Entry')
            doc.update(src)                 # includes naming_series + all fields (NO explicit name override)
            doc.docstatus = 0
            doc.name = None                 # let Frappe auto-assign
            try:
                doc.insert(ignore_permissions=True)
            except Exception as e:
                w(('STEP B insert ERR for', target_name, repr(e))); return False
            auto = doc.name
            w(('STEP B inserted (auto-named)', target_name, '-> actual name', auto))
            # RENAME to exact target while draft (no SLEs yet)
            try:
                frappe.rename_doc('Stock Entry', auto, target_name)
                w(('STEP B renamed', auto, '->', target_name))
            except Exception as e:
                w(('STEP B rename ERR', repr(e)))
                # reload by target if it exists
            doc.reload()
            if want_submit and doc.docstatus == 0:
                try:
                    doc.submit()
                    w(('STEP B submitted', target_name, 'docstatus=', doc.docstatus))
                except Exception as e:
                    w(('STEP B submit ERR', target_name, repr(e)))
            return True

        insert_and_rename('MAT-STE-2026-00001', want_submit=False)
        insert_and_rename('MAT-STE-2026-00002', want_submit=True)

        # =========================================================
        # STEP C: IMMEDIATE re-read in same session (guard against surprises)
        # =========================================================
        frappe.db.commit()
        for n in ['MAT-STE-2026-00001','MAT-STE-2026-00002']:
            v = frappe.db.get_value('Stock Entry', n, ['name','docstatus']) if frappe.db.exists('Stock Entry',n) else None
            w(('STEP C re-read', n, v))

        # =========================================================
        # STEP D: pristine verification
        # =========================================================
        se_all = frappe.get_all('Stock Entry', fields=['name','docstatus','purpose'])
        w(('STEP D ALL SE now:', sorted(se_all, key=lambda x:x['name'])))
        srcD = frappe.get_all('Bin', filters={'item_code':'CB-GV-001','warehouse':'巴西现场总仓 - 巴项'}, fields=['actual_qty'])
        w(('STEP D SRC bin (expect actual_qty=12.0):', srcD))
        transitD = frappe.get_all('Bin', filters={'item_code':'CB-GV-001','warehouse':'在途物料 - 巴项'}, fields=['actual_qty'])
        w(('STEP D TRANSIT bin:', transitD))
        sle = frappe.get_all('Stock Ledger Entry', fields=['voucher_no','warehouse','item_code','actual_qty'])
        w(('STEP D TOTAL SLE=', len(sle)))
        for s in sorted(sle, key=lambda x:x['voucher_no']):
            w(('   SLE', s['voucher_no'], s['warehouse'], s['item_code'], s['actual_qty']))
        # detail of 00002
        if frappe.db.exists('Stock Entry','MAT-STE-2026-00002'):
            d2 = frappe.get_doc('Stock Entry','MAT-STE-2026-00002')
            w(('STEP D 00002 qty/rate/amount/qa:', d2.items[0].item_code, d2.items[0].qty, d2.items[0].rate, d2.items[0].amount, 'QA=', (d2.items[0].quality_inspection if d2.items else None)))
    except Exception as e:
        w(('FATAL', repr(e)))
    open('/home/frappe/seed_final_restore.txt','w',encoding='utf-8').write('\n'.join(out))
    sys.exit(0)
main()
