def main():
    import frappe, json
    out=[]
    def w(x): out.append(str(x))
    names = ['MAT-STE-2026-00001','MAT-STE-2026-00002']
    for n in names:
        try:
            doc = frappe.get_doc('Stock Entry', n)
            w(('==== ', n, 'docstatus=', doc.docstatus))
            # top-level fields of interest
            for k in ['stock_entry_type','purpose','company','item_name','s_warehouse','t_warehouse','purpose','total_outgoing_qty','total_valuation','moving_avg_rate','set_posting_date','posting_date','remarks','naming_series']:
                if hasattr(doc,k): w((k, '=', getattr(doc,k)))
            w(('--- rows ---'))
            for r in doc.get('items',[]):
                row = {kk: r.get(kk) for kk in ['item_code','item_name','qty','stock_qty','uom','stock_uom','warehouse','s_warehouse','t_warehouse','valuation_rate','basic_rate','amount','t_warehouse']}
                w(row)
        except Exception as e:
            w(('ERR', n, repr(e)))
    open('/home/frappe/inv008_dump.txt','w').write('\n'.join(out))
main()
