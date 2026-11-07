def main():
    import frappe, json
    with open('/home/frappe/seed_docs.json','r',encoding='utf-8') as f:
        data = json.load(f)
    out=[]
    def w(x): out.append(str(x))
    w(('LOADED', len(data), [x['name'] for x in data]))
    for d in data:
        w((d['name'], 'docstatus=', d['docstatus'], 'company=', d.get('company')))
        for r in d.get('items',[]):
            w(('  item', r.get('item_code'), 'qty=', r.get('qty'), 't_wh=', r.get('t_warehouse'), 'qc=', r.get('quality_inspection'), 'cc=', r.get('cost_center'), 'uom=', r.get('uom')))
    open('/home/frappe/seed_verify.txt','w',encoding='utf-8').write('\n'.join(out))
main()
