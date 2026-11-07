import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    js = r"""
frappe.ui.form.on('Bulk Entry', {
  refresh: function(frm) {
    frm.add_custom_button('生成单据', function() {
      const kindMap = {'采购申请':'material_request','入库':'material_receipt','领料':'material_issue','退料':'material_return','盘点':'stock_reconciliation'};
      const kind = kindMap[frm.doc.kind];
      if (!kind) { frappe.msgprint('请先选择业务类型'); return; }
      const rows = parseRows(frm.doc.rows_text);
      if (!rows.length) { frappe.msgprint('请先在“粘贴数据”里粘贴行'); return; }
      frappe.call({
        method: 'cb_erp.cb_erp.bulk_ops.api_create',
        args: { kind: kind, rows: rows, project: frm.doc.project, warehouse: frm.doc.warehouse, posting_date: frm.doc.posting_date },
        freeze: true, freeze_message: '正在生成单据...',
        callback: function(r) {
          const res = r.message || {};
          let html = '<b>生成 ' + (res.count||0) + ' 张单据，共 ' + (res.total_rows||0) + ' 行</b><br><br>';
          (res.created||[]).forEach(function(c){ html += '✅ ' + c.name + '（' + c.rows + ' 行 / ' + (c.group||'') + '）<br>'; });
          (res.errors||[]).forEach(function(e){ html += '❌ ' + e + '<br>'; });
          frappe.msgprint(html);
        }
      });
    });
    frm.add_custom_button('上传 Excel/CSV', function() {
      const kindMap = {'采购申请':'material_request','入库':'material_receipt','领料':'material_issue','退料':'material_return','盘点':'stock_reconciliation'};
      const kind = kindMap[frm.doc.kind];
      if (!kind) { frappe.msgprint('请先选择业务类型'); return; }
      const input = document.createElement('input');
      input.type = 'file'; input.accept = '.csv,.xlsx,.xlsm';
      input.onchange = function() {
        const file = input.files[0]; if (!file) return;
        const fd = new FormData(); fd.append('file', file); fd.append('kind', kind);
        if (frm.doc.project) fd.append('project', frm.doc.project);
        if (frm.doc.warehouse) fd.append('warehouse', frm.doc.warehouse);
        if (frm.doc.posting_date) fd.append('posting_date', frm.doc.posting_date);
        frappe.dom.freeze('正在导入...');
        fetch('/api/method/cb_erp.cb_erp.bulk_ops.api_import_file', {
          method: 'POST', body: fd, headers: { 'X-Frappe-CSRF-Token': frappe.csrf_token }
        }).then(function(r){ return r.json(); }).then(function(j){
          frappe.dom.unfreeze();
          const res = j.message || {};
          let html = '<b>导入生成 ' + (res.count||0) + ' 张单据，共 ' + (res.total_rows||0) + ' 行</b><br><br>';
          (res.created||[]).forEach(function(c){ html += '✅ ' + c.name + '（' + c.rows + ' 行）<br>'; });
          (res.errors||[]).forEach(function(e){ html += '❌ ' + e + '<br>'; });
          frappe.msgprint(html);
        }).catch(function(e){ frappe.dom.unfreeze(); frappe.msgprint('上传失败：' + e); });
      };
      input.click();
    });
  }
});
function parseRows(text) {
  if (!text) return [];
  const lines = text.split(/\r?\n/);
  const rows = [];
  let start = 0;
  const first = (lines[0] || '').split(/\t|,/).map(function(s){ return s.trim().toLowerCase(); });
  if (first.indexOf('item_code') >= 0 || first.indexOf('物料编码') >= 0 || first.indexOf('物料') >= 0) start = 1;
  for (let i = start; i < lines.length; i++) {
    if (!lines[i].trim()) continue;
    const c = lines[i].split(/\t|,/).map(function(s){ return s.trim(); });
    if (!c[0]) continue;
    rows.push({ item_code: c[0], qty: parseFloat(c[1] || 0), warehouse: c[2] || undefined,
                project: c[3] || undefined, rate: c[4] ? parseFloat(c[4]) : undefined });
  }
  return rows;
}
"""
    if not frappe.db.exists("Client Script", {"dt": "Bulk Entry", "view": "Form"}):
        frappe.get_doc({"doctype": "Client Script", "name": "Bulk Entry-Form", "dt": "Bulk Entry", "view": "Form",
                        "enabled": 1, "script": js}).insert(ignore_permissions=True)
        frappe.db.commit()
        print("CLIENT_SCRIPT_CREATED")
    else:
        print("CLIENT_SCRIPT_EXISTS")
    frappe.clear_cache()
    print("CS_LIST:", frappe.get_all("Client Script", filters={"dt": "Bulk Entry"}, fields=["name", "view", "enabled"]))
    sys.exit(0)
main()
