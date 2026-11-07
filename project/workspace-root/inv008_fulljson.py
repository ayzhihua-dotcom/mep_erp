def main():
    import frappe, json
    out=[]
    def w(x): out.append(str(x))
    for n in ['MAT-STE-2026-00001','MAT-STE-2026-00002']:
        try:
            doc = frappe.get_doc('Stock Entry', n)
            d = doc.as_dict()
            # strip internal-only keys we don't need to preserve exactly
            w(('###JSONSTART', n, 'docstatus=', d.get('docstatus')))
            w(json.dumps(d, default=str, ensure_ascii=False))
            w('###JSONEND')
        except Exception as e:
            w(('ERR', n, repr(e)))
    open('/home/frappe/inv008_fulljson.txt','w').write('\n'.join(out))
main()
