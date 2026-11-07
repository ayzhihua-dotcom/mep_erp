def main():
    import frappe, sys, inspect, pkgutil, importlib
    out = []
    def w(*a): out.append(' '.join(str(x) for x in a))
    try:
        # 1) find every function named make_series / get_next_number anywhere in loaded modules
        targets = ['make_series','get_next_number','format_with_series','get_naming_series_num',
                   'get_series','make_dynamic_series','naming_series']
        found = {}
        for name, mod in list(sys.modules.items()):
            if not mod or not name.startswith('frappe'):
                continue
            for t in targets:
                obj = getattr(mod, t, None)
                if callable(obj) and (t not in found):
                    found[t] = (name, obj)
        for t in targets:
            if t in found:
                mn, obj = found[t]
                w(('FOUND', t, 'in', mn))
                try:
                    w(('   file:', inspect.getsourcefile(obj)))
                except Exception as e:
                    w(('   nosrc', repr(e)))
            else:
                w(('not found as module attr:', t))
        # 2) show naming.py public names
        import frappe.model.naming as N
        w(('naming.py public names:', [x for x in dir(N) if not x.startswith('_')]))
        # 3) how does Stock Entry resolve name? look at its autoname / naming_series meta
        try:
            meta = frappe.get_meta('Stock Entry')
            w(('SE autoname:', meta.autoname))
            nsf = meta.get_field('naming_series')
            w(('SE naming_series options:', nsf.options if nsf else None))
            w(('SE naming_series reqd:', nsf.reqd if nsf else None))
        except Exception as e:
            w(('meta err', repr(e)))
        # 4) search for a table that stores series counters (grep db tables)
        try:
            tbls = [r[0] for r in frappe.db.sql("show tables")]
            ser = [t for t in tbls if 'naming' in t.lower() or 'series' in t.lower()]
            w(('tables with naming/series:', ser))
        except Exception as e:
            w(('tbl err', repr(e)))
    except Exception as e:
        w(('FATAL', repr(e)))
    open('/home/frappe/namingsrc2.txt','w',encoding='utf-8').write('\n'.join(out))
    sys.exit(0)
main()
