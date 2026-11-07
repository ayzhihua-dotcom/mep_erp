def main():
    import frappe, sys, inspect
    out = []
    def w(*a): out.append(' '.join(str(x) for x in a))
    try:
        import frappe.model.naming as N
        w('MODULE FILE:', N.__file__)
        for fn in ['make_series','get_next_number','format_with_series','get_naming_series_num','get_series']:
            f = getattr(N, fn, None)
            if f is None:
                w(('MISSING', fn)); continue
            try:
                src = inspect.getsource(f)
            except Exception as e:
                w((fn, 'nosrc', repr(e))); continue
            w(('===== def %s =====' % fn))
            w(src)
        w('----- Naming Series rows for MAT-STE -----')
        try:
            ns = frappe.get_all('Naming Series', filters={'series': ['like', 'MAT-STE-%']}, fields=['name','series','current','disabled'])
            for r in ns: w(('   ', r))
        except Exception as e:
            w(('ns read err', repr(e)))
        w('----- cache hash naming_series_numbers -----')
        try:
            w(('  ', frappe.cache().hget('naming_series_numbers')))
        except Exception as e:
            w(('cache err', repr(e)))
    except Exception as e:
        w(('FATAL', repr(e)))
    open('/home/frappe/namingsrc.txt','w',encoding='utf-8').write('\n'.join(out))
    sys.exit(0)
main()
