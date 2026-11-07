#!/bin/sh
B=/home/frappe/frappe-bench/apps
echo "JS_EXISTS:"; ls -l $B/cb_erp/cb_erp/public/js/discipline_system.js 2>/dev/null || echo missing
echo "FRAPPE_CSS:"; ls $B/frappe/frappe/public/dist/css 2>/dev/null | head -3
echo "FRAPPE_CSS_TARGET:"; ls -l $B/frappe/frappe/public/dist/css/desk.bundle.I4J4KAYZ.css 2>/dev/null || echo missing
echo "ERPNEXT_CSS:"; ls $B/erpnext/erpnext/public/dist/css 2>/dev/null | head -3
echo "SAME_INODE:"; ls -di $B/frappe/frappe/public 2>/dev/null
