def main():
    import frappe, sys
    out=[]
    def w(x): out.append(str(x))
    try:
        rows = frappe.db.sql("SELECT name FROM `tabServer Script` WHERE disabled=0", as_dict=False)
        w(('non-disabled SS count=', len(rows)))
        for (nm,) in rows:
            try:
                doc = frappe.get_doc('Server Script', nm)
            except Exception as e:
                w((' read err', nm, repr(e))); continue
            src = getattr(doc,'script','') or ''
            ref = getattr(doc,'reference_doctype','') or ''
            ev = getattr(doc,'doctype_event',None)
            api = getattr(doc,'api_method',None)
            stype = getattr(doc,'script_type',None)
            w(('===== SS:', nm, '| doctype=', ref, '| event=', ev, '| api=', api, '| type=', stype, '| len=', len(src)))
            w(('----- SCRIPT -----'))
            w(src)
            w('------------------')
    except Exception as e:
        w(('FATAL', repr(e)))
    open('/home/frappe/all_ss.txt','w',encoding='utf-8').write('\n'.join(out))
    sys.exit(0)
main()
