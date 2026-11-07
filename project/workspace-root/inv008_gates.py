def main():
    import frappe
    out=[]
    def w(x): out.append(str(x))
    try:
        scripts = frappe.get_all('Server Script', fields=['name','reference_doctype','doctype_event','api_method','script','disabled'])
        for s in scripts:
            if 'INV' in (s.get('name') or '') or 'UCX04' in (s.get('name') or '') or 'IC02' in (s.get('name') or ''):
                w(('---', s['name'], s['reference_doctype'], s['doctype_event'], 'disabled=', s['disabled']))
                w(s.get('script',''))
    except Exception as e:
        w('ERR '+repr(e))
    open('/home/frappe/inv008_gates.txt','w').write('\n'.join(out))
main()
