import frappe
def main():
    out=open("/home/frappe/clean_final.txt","w",encoding="utf-8")
    def w(s=""): out.write(str(s)+"\n")
    try:
        WH_SRC="巴西现场总仓 - 巴项"
        # 1) current Stock Entries list (confirm 00025/00028 deleted)
        allse=[r[0] for r in frappe.db.sql("select name from `tabStock Entry` order by name",as_list=True)]
        w("current Stock Entries count="+str(len(allse)))
        w("  00025 present? "+str("MAT-STE-2026-00025" in allse))
        w("  00028 present? "+str("MAT-STE-2026-00028" in allse))

        # 2) find orphan vouchers (SLE voucher_no not a real Stock Entry)
        orph=set()
        for r in frappe.db.sql("select distinct voucher_no from `tabStock Ledger Entry` where voucher_type='Stock Entry'",as_list=True):
            if r[0] not in allse: orph.add(r[0])
        w("orphan vouchers="+str(sorted(orph)))

        # 3) SAFETY: net actual_qty per (item,warehouse) across ALL orphan SLEs must be zero everywhere
        w("===== net per (item,warehouse) for orphan SLEs =====")
        allzero=True
        for r in frappe.db.sql("select item_code,warehouse,sum(actual_qty) as net from `tabStock Ledger Entry` where voucher_no in %s group by item_code,warehouse",(list(orph),),as_list=True):
            w("   "+str(r))
            if r[2]!=0: allzero=False
        w("ALL NET ZERO="+str(allzero))

        before=frappe.db.get_value("Bin",{"item_code":"CB-GV-001","warehouse":WH_SRC},"actual_qty")
        w("BIN CB-GV-001 @ SRC BEFORE delete="+str(before))

        # also check any GL Entry orphan vouchers (GL referencing deleted voucher)
        glbad=[]
        for r in frappe.db.sql("select distinct voucher_no from `tabGL Entry` where voucher_type='Stock Entry'",as_list=True):
            if r[0] not in allse: glbad.append(r[0])
        w("orphan GL vouchers="+str(glbad))

        if allzero:
            n=frappe.db.sql("delete from `tabStock Ledger Entry` where voucher_no in %s",(list(orph),))
            frappe.db.commit()
            w("DELETED orphan SLE rows count="+str(n))
            # clean orphan GL entries too (net zero check)
            glrows=[]
            for r in frappe.db.sql("select name,voucher_type,voucher_no,debit,credit from `tabGL Entry` where voucher_type='Stock Entry' and voucher_no in %s",(list(orph),),as_list=True):
                glrows.append(r)
            w("orphan GL rows to delete="+str(len(glrows)))
            if glrows:
                frappe.db.sql("delete from `tabGL Entry` where voucher_type='Stock Entry' and voucher_no in %s",(list(orph),))
                frappe.db.commit()
                w("DELETED orphan GL rows")

        after=frappe.db.get_value("Bin",{"item_code":"CB-GV-001","warehouse":WH_SRC},"actual_qty")
        w("BIN CB-GV-001 @ SRC AFTER delete="+str(after)+" (must equal BEFORE "+str(before)+")")

        # verify no orphans remain
        remaining=[]
        for r in frappe.db.sql("select distinct voucher_no from `tabStock Ledger Entry` where voucher_type='Stock Entry'",as_list=True):
            if r[0] not in allse: remaining.append(r[0])
        w("remaining orphan SLE vouchers="+str(remaining))
        w("total SLE rows now="+str(frappe.db.sql("select count(*) from `tabStock Ledger Entry`",as_list=True)[0][0]))
        w("total GL rows now="+str(frappe.db.sql("select count(*) from `tabGL Entry`",as_list=True)[0][0]))

        w("===== all bins CB-GV-001 =====")
        for r in frappe.db.sql("select warehouse,actual_qty from `tabBin` where item_code='CB-GV-001' order by actual_qty DESC",as_list=True):
            w("   "+str(r))
    except Exception as e:
        w("TOP ERR: "+str(e)); import traceback; out.write("\n"+traceback.format_exc())
    out.close()
main()
