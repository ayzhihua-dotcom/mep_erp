import sys
p="/home/frappe/frappe-bench/apps/erpnext/erpnext/stock/doctype/stock_entry/stock_entry.py"
s=open(p,encoding="utf-8").read()
for kw in ["def make_gl_entries","def get_gl_entries","def validate_stock_qty","allow_zero_charge","zero_valuation","Cost Item","cost price","valuation_rate == 0","def validate"]:
    idx=s.find(kw)
    print("====",kw,"found at",idx)
    if idx>=0:
        print(repr(s[idx-20:idx+260]))
