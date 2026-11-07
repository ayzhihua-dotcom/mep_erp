def main():
    import frappe, json
    out = []
    for n in ['MAT-STE-2026-00001','MAT-STE-2026-00002']:
        doc = frappe.get_doc('Stock Entry', n)
        d = doc.as_dict()
        # keep only fields that survive round-trip cleanly; drop meta/child internal junk we don't need
        out.append(d)
    with open('/home/frappe/seed_docs.json','w',encoding='utf-8') as f:
        json.dump(out, f, default=str, ensure_ascii=False, indent=1)
    # also print counts for sanity
    print('DUMP_OK', len(out), [x['name'] for x in out], 'docstatus=', [x['docstatus'] for x in out])
main()
