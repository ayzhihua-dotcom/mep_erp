# -*- coding: utf-8 -*-
JS = r"""
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
        args: { kind: kind, rows: rows, project: frm.doc.project, warehouse: frm.doc.warehouse, posting_date: frm.doc.posting_date, discipline: frm.doc.discipline, system: frm.doc.system, responsible: frm.doc.responsible },
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
    frm.add_custom_button('添加物料行', function() {
      frappe.prompt([
        { fieldname: 'item_code', fieldtype: 'Link', options: 'Item', label: '物料编码', reqd: 1 },
        { fieldname: 'item_name', fieldtype: 'Data', label: '名称' },
        { fieldname: 'spec', fieldtype: 'Data', label: '规格参数' },
        { fieldname: 'qty', fieldtype: 'Float', label: '数量', default: 1, reqd: 1 },
        { fieldname: 'remark', fieldtype: 'Data', label: '备注' }
      ], function(v) {
        const line = [v.item_code, v.item_name || '', v.spec || '', v.qty, v.remark || ''].join('\t');
        const cur = frm.doc.rows_text || '';
        frm.set_value('rows_text', cur ? (cur + '\n' + line) : line);
      }, '添加物料行', '添加');
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
        if (frm.doc.discipline) fd.append('discipline', frm.doc.discipline);
        if (frm.doc.system) fd.append('system', frm.doc.system);
        if (frm.doc.responsible) fd.append('responsible', frm.doc.responsible);
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
    frm.add_custom_button('下载模板', function() {
      const text = '物料编码,物料名称,规格参数,数量,备注\nSIM-PV-0001,钢管-DN100,φ114×4.0,10,示例备注\n';
      const blob = new Blob([text], { type: 'text/csv;charset=utf-8;' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = '批量录入模板.csv';
      a.click();
    });
  }
});
function parseRows(text) {
  if (!text) return [];
  const lines = text.split(/\r?\n/);
  const rows = [];
  let start = 0;
  const first = (lines[0] || '').split(/\t|,/).map(function(s){ return s.trim().toLowerCase(); });
  if (first.indexOf('物料编码') >= 0 || first.indexOf('item_code') >= 0 || first.indexOf('编码') >= 0) start = 1;
  for (let i = start; i < lines.length; i++) {
    if (!lines[i].trim()) continue;
    const c = lines[i].split(/\t|,/).map(function(s){ return s.trim(); });
    if (!c[0]) continue;
    rows.push({ item_code: c[0], item_name: c[1] || undefined, spec: c[2] || undefined,
                qty: parseFloat(c[3] || 0), remark: c[4] || undefined });
  }
  return rows;
}
"""


def run():
    import frappe
    frappe.set_user("Administrator")
    # update rows_text description
    dt = frappe.get_doc("DocType", "Bulk Entry")
    for f in dt.fields:
        if f.fieldname == "rows_text":
            f.description = "每行：物料编码,物料名称,规格参数,数量,备注（制表符或逗号分隔）；首行可为表头。项目/仓库取上方默认值。"
    dt.save(ignore_permissions=True)
    frappe.db.commit()
    # update client script
    cs = frappe.get_doc("Client Script", "Bulk Entry-Form")
    cs.script = JS
    cs.save(ignore_permissions=True)
    frappe.db.commit()
    frappe.clear_cache()
    print("UPDATED")
    return "BULK_CS_V2_DONE"
