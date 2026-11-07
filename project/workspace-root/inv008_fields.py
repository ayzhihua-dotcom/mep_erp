def main():
    import frappe, json
    out=[]
    def w(x): out.append(str(x))
    for n in ['MAT-STE-2026-00001','MAT-STE-2026-00002']:
        doc = frappe.get_doc('Stock Entry', n)
        r = doc.items[0]
        w(('===', n))
        for k in ['uom','stock_uom','conversion_factor','cost_center','description','item_group','basic_rate','valuation_rate','amount','qty','transfer_qty','quality_inspection','expense_account']:
            w((k, repr(r.get(k))))
    open('/home/frappe/inv008_fields.txt','w').write('\n'.join(out))
main()
