import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    try:
        html = frappe.get_print("Stock Entry", "MAT-STE-2026-00054", "物料明细九列（库存移动）")
        print("LEN:", len(html))
        for k in ["序号", "编码", "名称", "规格参数", "单位", "数量", "使用项目", "责任人", "备注", "DN150", "eng02", "米"]:
            print("HAS", k, ":", k in html)
    except Exception as e:
        print("PRINT_ERR:", repr(e)[:300])
    sys.exit(0)
main()
