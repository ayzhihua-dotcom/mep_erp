def main():
    import frappe, os, glob
    out=[]
    def w(x): out.append(str(x))
    # 1. Current Stock Entries
    try:
        se = frappe.get_all('Stock Entry', fields=['name','stock_entry_type','purpose','docstatus','company'])
        w(('SE COUNT:', len(se)))
        for s in se: w(s)
    except Exception as e: w('ERR se:'+repr(e))
    # 2. All doctypes with docs (sample counts)
    try:
        for dt in ['Material Request','Purchase Order','Stock Entry','Delivery Note','Sales Order']:
            c = frappe.get_count(dt)
            w((dt, 'count=', c))
    except Exception as e: w('ERR cnt:'+repr(e))
    # 3. Site language config
    try:
        sc = frappe.get_site_config()
        w(('SITE LANG key present:', 'language' in sc, '| value=', sc.get('language')))
    except Exception as e: w('ERR sitecfg:'+repr(e))
    try:
        ss = frappe.get_single_doc if False else None
        # system settings language
        try:
            sysset = frappe.get_doc('System Settings')
            w(('SystemSettings.language=', repr(sysset.language), '| number_format=', getattr(sysset,'number_format',None)))
        except Exception as e: w('ERR sysset:'+repr(e))
    except Exception as e: w('ERR ss2:'+repr(e))
    # 4. ToDo status options + translation
    try:
        m = frappe.get_meta('ToDo')
        f = m.get_field('status')
        w(('TODO status options:', repr(f.options)))
    except Exception as e: w('ERR todoopt:'+repr(e))
    # 5. Look for backups on disk (site)
    try:
        p='/home/frappe/frappe-bench/sites/dev.localhost/backups'
        w(('backups dir exists:', os.path.isdir(p)))
        if os.path.isdir(p):
            w(('backups contents:', os.listdir(p)))
    except Exception as e: w('ERR backups:'+repr(e))
    # 6. frappe_docker backup volume
    try:
        p2='/shared/backups'
        w(('shared/backups exists:', os.path.isdir(p2), os.listdir(p2) if os.path.isdir(p2) else ''))
    except Exception as e: w('ERR shared:'+repr(e))
    open('/home/frappe/inv008_probe2.txt','w').write('\n'.join(out))
main()
