#!/bin/sh
cd /home/frappe/frappe-bench || exit 1
python -m py_compile apps/cb_erp/cb_erp/cb_erp/ops_setup.py || exit 1
for f in apps/cb_erp/cb_erp/cb_erp/report/*/*.py; do
  python -m py_compile "$f" || exit 1
done
echo COMPILE_OK
