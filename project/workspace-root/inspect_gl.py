import sys
for p in [
 "/home/frappe/frappe-bench/apps/erpnext/erpnext/accounts/general_ledger.py",
 "/home/frappe/frappe-bench/apps/erpnext/erpnext/controllers/stock_controller.py",
]:
    print("########## FILE:",p)
    try:
        s=open(p,encoding="utf-8").read()
    except Exception as e:
        print("ERR",e); continue
    for kw in ["zero valuation","valuation_rate","Cost Item","cost price","make_gle","def get_gl_entries","allow_zero_valuation_rate","process_gl_map"]:
        idx=s.find(kw)
        if idx>=0:
            print("====",kw,"@",idx)
            print(repr(s[idx-60:idx+220]))
