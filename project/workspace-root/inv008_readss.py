def main():
    import frappe, sys
    out=[]
    def w(x): out.append(str(x))
    try:
        for nm in ['CB-UCX03-退料冲减项目成本','CB-UCX05-退料关联拦截','CB-IC02-领料调拨内控']:
            doc = frappe.get_doc('Server Script', nm)
            w(('========== '+nm+' =========='))
            w(('reference_doctype=', doc.reference_doctype, '| event_type field=', getattr(doc,'doctype_event',None), getattr(doc,'api_method',None)))
            w(('SCRIPT:\n'+doc.script))
            w(('==================== END '+nm+' ===================='))
    except Exception as e:
        w(('FATAL', repr(e)))
    open('/home/frappe/seed_diag.txt','w',encoding='utf-8').write('\n'.join(out))
    sys.exit(0)
main()
