import sys
def main():
    import frappe
    frappe.set_user('Administrator')
    from cb_erp.cb_erp.bulk_ops import api_search_items, api_list_categories
    print('CATS:', api_list_categories())
    for label, kw, cat in [('all','',None), ('kw_steel','钢',None), ('cat_pipe',None,'管道与阀门')]:
        r = api_search_items(keyword=kw, category=cat, limit=3)
        print(label, '->', [(x['item_code'], x['item_name'], x['custom_spec'], x['stock_uom'], x['category']) for x in r])
    sys.exit(0)
main()
