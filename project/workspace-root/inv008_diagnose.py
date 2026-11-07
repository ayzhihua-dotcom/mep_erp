def main():
    import frappe, sys
    out=[]
    def w(x): out.append(str(x))
    try:
        binrows = frappe.get_all('Bin', filters={'item_code':'CB-GV-001','warehouse':'巴西现场总仓 - 巴项'}, fields=['actual_qty'])
        w(('SRC bin actual_qty:', binrows))
        transit = frappe.get_all('Bin', filters={'item_code':'CB-GV-001','warehouse':'在途物料 - 巴项'}, fields=['actual_qty'])
        w(('TRANSIT bin actual_qty:', transit))
        sle = frappe.get_all('Stock Ledger Entry', fields=['voucher_no','warehouse','actual_qty'])
        w(('TOTAL SLE=', len(sle)))
        for s in sle: w(('  SLE', s['voucher_no'], s['warehouse'], s['actual_qty']))
    except Exception as e:
        w(('FATAL', repr(e)))
    open('/home/frappe/seed_diag.txt','w',encoding='utf-8').write('\n'.join(out))
    sys.exit(0)
main()
