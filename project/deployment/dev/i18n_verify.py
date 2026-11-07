import sys
def main():
    import frappe
    frappe.set_user('chenzhihua@cb.local')
    frappe.local.lang = 'zh'
    for k in ['Design BOM','Material Budget','Material Commitment','Bulk Entry','Stock Entry','Draft','Submitted','Last Edited By','Item','Warehouse','Project']:
        print('CHECK', k, '->', frappe._(k))
    sys.exit(0)
main()
