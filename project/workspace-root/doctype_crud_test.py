import frappe
def main():
    out=open("/home/frappe/doctype_crud_test.txt","w",encoding="utf-8")
    def w(s=""): out.write(str(s)+"\n")
    try:
        NAME="CB TEST DROP"
        # create custom doctype via API
        dt={
            "doctype":"DocType","name":NAME,"custom":1,"module":"Custom",
            "fields":[
                {"fieldname":"ref_stock_entry","fieldtype":"Link","label":"Ref SE","options":"Stock Entry"},
                {"fieldname":"sender_approver","fieldtype":"Link","label":"Sender Approver","options":"User"},
                {"fieldname":"receiver_approver","fieldtype":"Link","label":"Receiver Approver","options":"User"},
            ],
        }
        doc=frappe.get_doc(dt); doc.insert(); frappe.db.commit()
        w("inserted name="+str(doc.name))
        # correct table check (name only, no embedded backticks)
        tbl=[r[0] for r in frappe.db.sql("select table_name from information_schema.tables where table_schema=database() and table_name=%s",(NAME,),as_list=True)]
        w("table after insert (correct query)="+str(tbl))
        # try triggering sync for this doctype WITHOUT full migrate
        w("trying frappe.sync...")
        try:
            import frappe.doctype.doctype.doctype as dtd
            w("has sync module OK")
        except Exception as e:
            w("sync import err="+str(e))
        # delete and re-check table gone
        d2=frappe.get_doc("DocType",NAME); d2.delete(); frappe.db.commit()
        chk2=frappe.db.sql("select name from `tabDocType` where name=%s",(NAME,),as_list=True)
        w("post-delete exists="+str(chk2))
        tbl2=[r[0] for r in frappe.db.sql("select table_name from information_schema.tables where table_schema=database() and table_name=%s",(NAME,),as_list=True)]
        w("table after delete="+str(tbl2))
    except Exception as e:
        w("TOP ERR: "+str(e)); import traceback; out.write("\n"+traceback.format_exc())
    out.close()
main()
