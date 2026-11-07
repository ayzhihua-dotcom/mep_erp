p="/home/frappe/frappe-bench/apps/erpnext/erpnext/controllers/stock_controller.py"
s=open(p,encoding="utf-8").read()
idx=s.find("valuation_rate")  # first occurrence overall = the check block at ~7140
print(s[idx-500:idx+700])
