def main():
    import frappe
    out=[]
    def w(x): out.append(str(x))
    # current SE list + SRC bin
    try:
        se = frappe.get_all('Stock Entry', fields=['name','docstatus'])
        w(('SE:', [(s['name'], s['docstatus']) for s in se]))
    except Exception as e: w('ERR se:'+repr(e))
    try:
        binrows = frappe.get_all('Bin', filters={'item':'CB-GV-001','warehouse':'巴西现场总仓 - 巴项'}, fields=['item','warehouse','qty_on_hand'])
        w(('SRC BIN:', binrows))
    except Exception as e: w('ERR bin:'+repr(e))
    # QA doc existence
    try:
        q = frappe.db.get_value('Quality Inspection', 'MAT-QA-2026-00001', ['name'])
        w(('QA MAT-QA-2026-00001 exists:', q))
    except Exception as e: w('ERR qa:'+repr(e))
    # item qc_required flag
    try:
        qc = frappe.db.get_value('Item', 'CB-GV-001', 'custom_qc_required')
        w(('CB-GV-001 custom_qc_required:', qc))
    except Exception as e: w('ERR itemqc:'+repr(e))
    # company + warehouse existence
    try:
        c = frappe.db.get_value('Company', '中巴机电（巴西）项目有限公司', ['name'])
        w(('Company exists:', c))
    except Exception as e: w('ERR comp:'+repr(e))
    open('/home/frappe/inv008_devcheck.txt','w').write('\n'.join(out))
main()
