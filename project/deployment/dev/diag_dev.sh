#!/bin/sh
cd /home/frappe/frappe-bench || exit 1
echo "APPS:"; cat sites/apps.txt
echo "PY_IMPORT:"; ./env/bin/python -c 'import cb_erp; print(cb_erp.__file__)' 2>&1 | tail -2
echo "ASSETS_SIZE:"; du -sh sites/assets 2>/dev/null || echo no-du
echo "CSS_FILES:"; ls sites/assets/frappe/dist/css 2>/dev/null | head -3
echo "ASSETS_JSON:"; grep -o 'desk.bundle.[A-Z0-9]*.css' sites/assets/assets.json 2>/dev/null | head -2
