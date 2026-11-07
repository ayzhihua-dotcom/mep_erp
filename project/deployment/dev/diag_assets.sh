#!/bin/sh
cd /home/frappe/frappe-bench/sites/assets || exit 1
echo "TOP:"; ls -la | head -12
echo "SIZE_FRAPPE_DIST:"; du -sh frappe/dist 2>/dev/null || echo na
echo "SIZE_ERPNEXT_DIST:"; du -sh erpnext/dist 2>/dev/null || echo na
echo "SIZE_ALL:"; du -sh . 2>/dev/null || echo na
