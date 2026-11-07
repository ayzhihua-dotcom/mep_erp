p="/home/frappe/frappe-bench/apps/erpnext/erpnext/controllers/stock_controller.py"
s=open(p,encoding="utf-8").read()
idx=s.find("def get_gl_entries")
# find the valuation check after it
cand=s.find("valuation_rate", idx)
print(s[cand-400:cand+600])
