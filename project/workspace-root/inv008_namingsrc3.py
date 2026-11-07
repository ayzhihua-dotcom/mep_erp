def main():
    import frappe, sys, inspect
    out = []
    def w(*a): out.append(' '.join(str(x) for x in a))
    try:
        import frappe.model.naming as N
        for fn in ['set_new_name','getseries','set_name_from_naming_options','parse_naming_series','make_autoname','append_number_if_name_exists']:
            f = getattr(N, fn, None)
            if not f:
                w(('MISSING', fn)); continue
            w(('===== %s :: %s =====' % (fn, inspect.getsourcefile(f))))
            try:
                w(inspect.getsource(f))
            except Exception as e:
                w(('nosrc', repr(e)))
        w('===== tabSeries columns =====')
        try:
            w(frappe.db.sql('desc tabSeries', as_dict=False))
        except Exception as e:
            w(('desc err', repr(e)))
        w('===== tabSeries rows (MAT-STE) =====')
        try:
            for r in frappe.get_all('Series', filters={'name': ['like', 'MAT-STE-%']}, fields=['*']):
                w(('   ', r))
        except Exception as e:
            w(('series read err', repr(e)))
        w('===== ALL Series rows =====')
        try:
            for r in frappe.get_all('Series', fields=['name','current','disabled']):
                w(('   ', r))
        except Exception as e:
            w(('all series err', repr(e)))
    except Exception as e:
        w(('FATAL', repr(e)))
    open('/home/frappe/namingsrc3.txt','w',encoding='utf-8').write('\n'.join(out))
    sys.exit(0)
main()
