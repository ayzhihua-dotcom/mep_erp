def main():
    import frappe, json, sys
    out=[]
    def w(x): out.append(str(x))
    try:
        # ===== STEP 0: confirm current state =====
        se0 = frappe.get_all('Stock Entry', fields=['name','docstatus'])
        w(('STEP0 pre-state SE:', sorted(se0, key=lambda x:x['name'])))
        bin0 = frappe.get_all('Bin', filters={'item_code':'CB-GV-001','warehouse':'巴西现场总仓 - 巴项'}, fields=['actual_qty'])
        w(('STEP0 SRC bin before:', bin0))

        # ===== STEP 1: delete placeholder recovery artifact MAT-STE-2026-00030 + orphan SLEs =====
        if frappe.db.exists('Stock Entry','MAT-STE-2026-00030'):
            d30 = frappe.get_doc('Stock Entry','MAT-STE-2026-00030')
            w(('STEP1 00030 docstatus=', d30.docstatus))
            if d30.docstatus==1:
                d30.cancel()
                w(('STEP1 cancelled 00030'))
            d30.delete(force=True)
            w(('STEP1 force-deleted 00030'))
        rows = frappe.get_all('Stock Ledger Entry', filters={'voucher_no':'MAT-STE-2026-00030'}, fields=['name'])
        for r in rows:
            try:
                frappe.db.delete('Stock Ledger Entry', {'name':r['name']})
                w(('STEP1 deleted orphan SLE', r['name']))
            except Exception as e:
                w(('STEP1 orphan SLE del err', repr(e)))
        rem = frappe.db.count('Stock Ledger Entry', {'voucher_no':'MAT-STE-2026-00030'})
        w(('STEP1 orphan SLE remaining=', rem))
        frappe.db.commit()
        bin_after_del = frappe.get_all('Bin', filters={'item_code':'CB-GV-001','warehouse':'巴西现场总仓 - 巴项'}, fields=['actual_qty'])
        w(('STEP1 SRC bin after delete placeholder:', bin_after_del))

        # ===== STEP 2: restore originals from JSON =====
        with open('/home/frappe/seed_docs.json','r',encoding='utf-8') as f:
            data = json.load(f)
        for d in data:
            name = d['name']
            want_submit = d.get('docstatus')==1
            if frappe.db.exists('Stock Entry', name):
                w(('STEP2 SKIP exists', name)); continue
            doc = frappe.new_doc('Stock Entry')
            doc.update(d)
            doc.docstatus = 0
            doc.name = name
            try:
                doc.insert(ignore_permissions=True)
                w(('STEP2 inserted', name, 'docstatus=', doc.docstatus))
            except Exception as e:
                w(('STEP2 insert ERR', name, repr(e))); continue
            if want_submit:
                try:
                    doc.submit()
                    w(('STEP2 submitted', name, 'docstatus=', doc.docstatus))
                except Exception as e:
                    w(('STEP2 submit ERR', name, repr(e)))
                    try:
                        dd = frappe.get_doc('Stock Entry', name)
                        if dd.docstatus==1: dd.cancel()
                        dd.delete(force=True)
                        w(('STEP2 rolled back', name))
                    except Exception as e2: w(('rollback err', repr(e2)))

        # ===== STEP 3: IMMEDIATE re-read within same session (guard against swap) =====
        frappe.db.commit()
        for n in ['MAT-STE-2026-00001','MAT-STE-2026-00002']:
            v = frappe.db.get_value('Stock Entry', n, ['name','docstatus']) if frappe.db.exists('Stock Entry',n) else None
            w(('STEP3 immediate DB re-read', n, v))
        se3 = frappe.get_all('Stock Entry', fields=['name','docstatus'])
        w(('STEP3 ALL SE now:', sorted(se3, key=lambda x:x['name'])))

        # ===== STEP 4: pristine verification =====
        bin12 = frappe.get_all('Bin', filters={'item_code':'CB-GV-001','warehouse':'巴西现场总仓 - 巴项'}, fields=['actual_qty'])
        w(('STEP4 SRC bin (expect actual_qty=12):', bin12))
        transit = frappe.get_all('Bin', filters={'item_code':'CB-GV-001','warehouse':'在途物料 - 巴项'}, fields=['actual_qty'])
        w(('STEP4 TRANSIT bin:', transit))
        sle = frappe.get_all('Stock Ledger Entry', fields=['voucher_no','warehouse','actual_qty'])
        w(('STEP4 TOTAL SLE=', len(sle)))
        for s in sorted(sle, key=lambda x:x['voucher_no']):
            w(('   SLE', s['voucher_no'], s['warehouse'], s['actual_qty']))
    except Exception as e:
        w(('FATAL', repr(e)))
    open('/home/frappe/seed_restore.txt','w',encoding='utf-8').write('\n'.join(out))
    sys.exit(0)
main()
