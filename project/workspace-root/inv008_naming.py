def main():
    import frappe, sys
    out=[]
    def w(x): out.append(str(x))
    try:
        # ---- GROUND TRUTH: all Stock Entries with REAL names ----
        se = frappe.get_all('Stock Entry', fields=['name','docstatus','purpose'])
        w(('ALL SE (real names+docstatus):'))
        for s in sorted(se, key=lambda x:x['name']):
            w(('   ', s))

        # ---- naming series counters for MAT-STE ----
        ns = frappe.get_all('Naming Series', filters={'series': ['like', 'MAT-STE-%']}, fields=['series','current'])
        w(('Naming Series rows:', ns))

        # what does the series NEXT produce?
        try:
            cur = frappe.db.get_value('Naming Series', {'series':'MAT-STE-.YYYY.-'}, 'current')
            w(('MAT-STE-.YYYY.- current counter =', cur))
        except Exception as e:
            w(('counter read err', repr(e)))

        # ---- CONTROLLED EXPERIMENT: can we force an explicit name on insert? ----
        w('---- EXPERIMENT A: new_doc + update(name) + insert ----')
        d = frappe.new_doc('Stock Entry')
        d.update({'company':'中巴机电（巴西）项目有限公司','naming_series':'MAT-STE-.YYYY.-',
                  'stock_entry_type':'Material Receipt','purpose':'Material Receipt',
                  'name':'MAT-STE-TEST-FORCE01'})
        try:
            d.insert(ignore_permissions=True)
            w(('A inserted, doc.name now =', d.name))
            got = frappe.db.get_value('Stock Entry', d.name, 'name')
            w(('A exists under assigned name?', got))
            # does MAT-STE-TEST-FORCE01 exist?
            w(('A explicit-name exists?', bool(frappe.db.exists('Stock Entry','MAT-STE-TEST-FORCE01'))))
            if d.name != 'MAT-STE-TEST-FORCE01':
                frappe.delete_doc('Stock Entry', d.name, force=True); w(('A cleaned up auto-named', d.name))
        except Exception as e:
            w(('A err', repr(e)))

        w('---- EXPERIMENT B: set name AFTER new_doc, before update ----')
        d2 = frappe.new_doc('Stock Entry')
        d2.name = 'MAT-STE-TEST-FORCE02'
        d2.update({'company':'中巴机电（巴西）项目有限公司','naming_series':'MAT-STE-.YYYY.-',
                   'stock_entry_type':'Material Receipt','purpose':'Material Receipt'})
        try:
            d2.insert(ignore_permissions=True)
            w(('B inserted, doc.name now =', d2.name))
            w(('B explicit-name exists?', bool(frappe.db.exists('Stock Entry','MAT-STE-TEST-FORCE02'))))
            if d2.name != 'MAT-STE-TEST-FORCE02':
                frappe.delete_doc('Stock Entry', d2.name, force=True); w(('B cleaned up auto-named', d2.name))
        except Exception as e:
            w(('B err', repr(e)))

        # ---- naming counter AFTER experiments ----
        try:
            w(('counter after =', frappe.db.get_value('Naming Series', {'series':'MAT-STE-.YYYY.-'}, 'current')))
        except Exception as e:
            w(('counter read err2', repr(e)))

        # cleanup any stray test docs just in case
        for nm in ['MAT-STE-TEST-FORCE01','MAT-STE-TEST-FORCE02']:
            if frappe.db.exists('Stock Entry', nm):
                dd = frappe.get_doc('Stock Entry', nm)
                if dd.docstatus==1: dd.cancel()
                dd.delete(force=True); w(('cleanup deleted', nm))
    except Exception as e:
        w(('FATAL', repr(e)))
    open('/home/frappe/naming_exp.txt','w',encoding='utf-8').write('\n'.join(out))
    sys.exit(0)
main()
