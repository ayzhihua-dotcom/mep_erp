def main():
    import frappe, os, glob
    out=[]
    def w(x): out.append(str(x))
    try:
        rows = frappe.db.sql("SHOW VARIABLES LIKE 'general_log_file'", as_dict=True)
        for r in rows: w(('general_log_file=', r['Value']))
    except Exception as e: w('ERR gl:'+repr(e))
    try:
        rows = frappe.db.sql("SELECT @@log_bin AS lb, @@log_bin_basename AS bb, @@general_log AS gl, @@general_log_file AS glf", as_dict=True)
        for r in rows: w(r)
    except Exception as e: w('ERR logbin:'+repr(e))
    # data dir listing for bin files
    try:
        d = frappe.db.sql("SELECT @@datadir AS dd", as_dict=True)[0].dd
        w(('DATADIR=', d))
        fs = sorted(os.listdir(d))
        w(('FILES:', [f for f in fs if 'bin' in f or f.endswith('.index')]))
    except Exception as e: w('ERR datadir:'+repr(e))
    open('/home/frappe/inv008_probe4.txt','w').write('\n'.join(out))
main()
