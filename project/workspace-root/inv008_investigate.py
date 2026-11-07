def main():
    import frappe, sys
    out=[]
    def w(x): out.append(str(x))
    try:
        # Server Script table columns (discover via sql)
        cols = [c[0] for c in frappe.db.sql("SHOW COLUMNS FROM `tabServer Script`")]
        w(('SS columns:', cols))

        rows = frappe.db.sql(
            "SELECT name, reference_doctype, disabled FROM `tabServer Script` WHERE disabled=0",
            as_dict=True)
        w(('non-disabled SS count=', len(rows)))
        for r in rows:
            try:
                doc = frappe.get_doc('Server Script', r['name'])
            except Exception as e:
                w((' read err', r['name'], repr(e))); continue
            src = getattr(doc,'script','') or ''
            if 'Stock Entry' in src or 'stock_entry' in src.lower() or 'STE-' in src or '00030' in src or '00024' in src:
                w((' *** SS refs:', r['name'], '| doctype=', r['reference_doctype'], '| len=', len(src)))
                w(('     snippet:', src[:500].replace(chr(10),' | ')))

        # any custom method registered anywhere for stock entry submit? check all hooks keys present in module
        import cb_erp.hooks as H
        for k in ['doc_events','after_submit','before_submit','after_insert','before_insert','scheduler_events']:
            if hasattr(H,k): w(('HOOK KEY', k, getattr(H,k)))

        binrows = frappe.get_all('Bin', filters={'item_code':'CB-GV-001','warehouse':'巴西现场总仓 - 巴项'}, fields=['actual_qty'])
        w(('SRC bin actual_qty:', binrows))
    except Exception as e:
        w(('FATAL', repr(e)))
    open('/home/frappe/seed_diag.txt','w',encoding='utf-8').write('\n'.join(out))
    sys.exit(0)
main()
