def main():
    import frappe
    out=[]
    def w(x): out.append(str(x))
    try:
        rows = frappe.db.sql("SHOW VARIABLES LIKE '%binlog%'", as_dict=True)
        for r in rows: w(r)
    except Exception as e: w('ERR var:'+repr(e))
    try:
        logs = frappe.db.sql("SHOW BINARY LOGS", as_dict=True)
        w(('BINARY LOGS:', logs))
    except Exception as e: w('ERR binloglist:'+repr(e))
    open('/home/frappe/inv008_probe3.txt','w').write('\n'.join(out))
main()
