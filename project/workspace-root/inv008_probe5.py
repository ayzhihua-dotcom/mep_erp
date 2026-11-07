def main():
    import frappe
    out=[]
    def w(x): out.append(str(x))
    # current site identity
    try: w(('SITE:', frappe.site))
    except Exception as e: w('ERR site:'+repr(e))
    # any Stock Entries at all?
    try:
        se = frappe.get_all('Stock Entry', fields=['name','stock_entry_type','purpose','docstatus'])
        w(('SE COUNT:', len(se)))
        for s in se[:50]: w(s)
    except Exception as e: w('ERR se:'+repr(e))
    # any MAT-STE anywhere
    try:
        docs = frappe.get_all('Stock Entry', filters={'name': ['like', 'MAT-STE-%']}, fields=['name'])
        w(('MAT-STE docs:', len(docs), [d['name'] for d in docs][:30]))
    except Exception as e: w('ERR matste:'+repr(e))
    # all doctypes that might hold seed sample docs
    try:
        for dt in ['Purchase Order','Delivery Note','Sales Order','Material Request','Quality Inspection','Stock Entry']:
            try:
                c = frappe.get_count(dt)
                w((dt, 'count=', c))
            except Exception as e: w((dt,'cnt-err',repr(e)))
    except Exception as e: w('ERR all:'+repr(e))
    open('/home/frappe/inv008_probe5.txt','w').write('\n'.join(out))
main()
