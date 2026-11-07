def main():
    import frappe, json, base64
    out=[]
    def w(x): out.append(str(x))
    r = frappe.get_doc('Stock Entry','MAT-STE-2026-00002').items[0]
    for k in ['uom','stock_uom','cost_center','description','item_group']:
        v = r.get(k) or ''
        w((k, base64.b64encode(str(v).encode('utf-8')).decode('ascii')))
    # Item record core fields
    it = frappe.get_doc('Item','CB-GV-001')
    for k in ['stock_uom','uom','item_group','item_name','name']:
        v = getattr(it,k,'')
        w(('ITEM.'+k, base64.b64encode(str(v).encode('utf-8')).decode('ascii')))
    # cost center from company
    cc = frappe.db.get_value('Company','中巴机电（巴西）项目有限公司','cost_center')
    w(('COSTCENTER.company', base64.b64encode(str(cc).encode('utf-8')).decode('ascii')))
    open('/home/frappe/inv008_b64.txt','w').write('\n'.join(out))
main()
