p="/home/frappe/frappe-bench/apps/erpnext/erpnext/locale/zh.po"
lines=open(p,encoding="utf-8").read().split("\n")
for i,l in enumerate(lines):
    if "生成会计凭证" in l:
        print("line",i+1,repr(l))
        for j in range(i-4,i+2):
            print("  ",lines[j])
