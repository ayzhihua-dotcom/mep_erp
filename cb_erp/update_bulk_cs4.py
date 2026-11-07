# -*- coding: utf-8 -*-
JS = r"""
frappe.ui.form.on('Bulk Entry', {
  refresh: function(frm) {
    frm.set_query('discipline', function(){ return { filters: { enabled: 1 } }; });
    frm.set_query('system', function(){ return { filters: { discipline: frm.doc.discipline || '' } }; });
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
    frm.add_custom_button('选择物料（多选）', function() { openItemPicker(frm); });
    frm.add_custom_button('添加物料行', function() {
      const d = frappe.prompt([
        { fieldname: 'item_code', fieldtype: 'Link', options: 'Item', label: '物料编码', reqd: 1 },
        { fieldname: 'item_name', fieldtype: 'Data', label: '名称' },
        { fieldname: 'spec', fieldtype: 'Data', label: '规格参数' },
        { fieldname: 'unit', fieldtype: 'Link', options: 'UOM', label: '单位' },
        { fieldname: 'qty', fieldtype: 'Float', label: '数量', default: 1, reqd: 1 },
        { fieldname: 'remark', fieldtype: 'Data', label: '备注' }
      ], function(v) {
        const line = [v.item_code, v.item_name || '', v.spec || '', v.unit || '', v.qty, v.remark || ''].join('\t');
        const cur = frm.doc.rows_text || '';
        frm.set_value('rows_text', cur ? (cur + '\n' + line) : line);
      }, '添加物料行', '添加');
      d.fields_dict.item_code.$input.on('change blur', function() {
        const code = d.get_value('item_code');
        if (!code) return;
        frappe.db.get_value('Item', code, ['item_name', 'stock_uom']).then(function(r) {
          const v = r.message || {};
          if (v.item_name) d.set_value('item_name', v.item_name);
          if (v.stock_uom) d.set_value('unit', v.stock_uom);
        });
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
      const text = '物料编码,物料名称,规格参数,单位,数量,备注\nSIM-PV-0001,钢管-DN100,φ114×4.0,米,10,示例备注\n';
      const blob = new Blob([text], { type: 'text/csv;charset=utf-8;' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = '批量录入模板.csv';
      a.click();
    });
  },
  discipline: function(frm) {
    frm.set_value('system', '');
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
                unit: c[3] || undefined, qty: parseFloat(c[4] || 0), remark: c[5] || undefined });
  }
  return rows;
}
function openItemPicker(frm) {
  let items = [];
  const dlg = new frappe.ui.Dialog({
    title: '选择物料（可多选）',
    size: 'large',
    fields: [
      { fieldtype: 'HTML', fieldname: 'filters', options:
        '<div style="display:flex;gap:8px;margin-bottom:8px;">' +
        '<select class="form-control" id="cb-cat" style="width:180px;"><option value="">全部分类</option></select>' +
        '<select class="form-control" id="cb-sub" style="width:180px;"><option value="">全部细分</option></select>' +
        '<input class="form-control" id="cb-kw" placeholder="编码 / 名称 / 规格 关键词" style="flex:1;">' +
        '<button class="btn btn-primary btn-sm" id="cb-search">搜索</button>' +
        '</div>' },
      { fieldtype: 'HTML', fieldname: 'results', options: '<div id="cb-results" style="max-height:380px;overflow:auto;"></div>' }
    ],
    primary_action_label: '添加选中',
    primary_action: function() {
      const picked = [];
      document.querySelectorAll('.cb-pick:checked').forEach(function(cb){
        const it = items[parseInt(cb.getAttribute('data-idx'))];
        if (it) picked.push(it);
      });
      if (!picked.length) { frappe.msgprint('请先勾选物料'); return; }
      const lines = picked.map(function(it){
        return [it.item_code, it.item_name || '', it.custom_spec || '', it.stock_uom || '', 1, ''].join('\t');
      });
      const cur = frm.doc.rows_text || '';
      frm.set_value('rows_text', cur ? (cur + '\n' + lines.join('\n')) : lines.join('\n'));
      dlg.hide();
    }
  });
  dlg.show();
  var catTries = 0;
  function fillCategories() {
    var sel = document.getElementById('cb-cat');
    if (!sel) { if (catTries++ < 30) { setTimeout(fillCategories, 150); } return; }
    if (sel.options.length > 1) return;
    frappe.call({ method: 'cb_erp.cb_erp.bulk_ops.api_list_categories', callback: function(r){
      var s2 = document.getElementById('cb-cat');
      if (!s2 || s2.options.length > 1) return;
      (r.message || []).forEach(function(c){ var o = document.createElement('option'); o.value = c; o.textContent = c; s2.appendChild(o); });
    }});
  }
  setTimeout(fillCategories, 200);
  function fillSubgroups() {
    var catEl = document.getElementById('cb-cat');
    var subEl = document.getElementById('cb-sub');
    if (!subEl) return;
    subEl.innerHTML = '<option value="">全部细分</option>';
    var cat = catEl ? catEl.value : '';
    if (!cat) return;
    frappe.call({ method: 'cb_erp.cb_erp.bulk_ops.api_list_subgroups', args: { parent: cat }, callback: function(r){
      var s = document.getElementById('cb-sub');
      if (!s) return;
      (r.message || []).forEach(function(g){
        var o = document.createElement('option');
        o.value = g.name;
        o.textContent = g.name + (g.is_group ? '' : '');
        s.appendChild(o);
      });
    }});
  }
  function doSearch(){
    var catEl = document.getElementById('cb-cat');
    var subEl = document.getElementById('cb-sub');
    var kwEl = document.getElementById('cb-kw');
    var cat = (subEl && subEl.value) || (catEl ? catEl.value : '');
    var kw = kwEl ? kwEl.value : '';
    frappe.call({ method: 'cb_erp.cb_erp.bulk_ops.api_search_items', args: { category: cat, keyword: kw, limit: 50 }, callback: function(r){
      items = r.message || [];
      const box = document.getElementById('cb-results');
      if (!box) return;
      if (!items.length) { box.innerHTML = '<div class="text-muted" style="padding:8px;">无匹配物料</div>'; return; }
      let html = '<table class="table table-bordered" style="font-size:12px;"><thead><tr>' +
        '<th style="width:28px;"></th><th>编码</th><th>名称</th><th>规格参数</th><th>单位</th><th>分类</th></tr></thead><tbody>';
      items.forEach(function(it, idx){
        const e = frappe.utils.escape_html;
        html += '<tr><td><input type="checkbox" class="cb-pick" data-idx="' + idx + '"></td>' +
          '<td>' + e(it.item_code) + '</td><td>' + e(it.item_name || '') + '</td>' +
          '<td>' + e(it.custom_spec || '') + '</td><td>' + e(it.stock_uom || '') + '</td>' +
          '<td>' + e(it.category || '') + '</td></tr>';
      });
      html += '</tbody></table>';
      box.innerHTML = html;
    }});
  }
  var bindTries = 0;
  function bindPicker() {
    var s = document.getElementById('cb-search');
    var k = document.getElementById('cb-kw');
    var c = document.getElementById('cb-cat');
    if (!s || !k || !c) { if (bindTries++ < 30) { setTimeout(bindPicker, 150); } return; }
    s.addEventListener('click', doSearch);
    k.addEventListener('keydown', function(e){ if (e.key === 'Enter') { e.preventDefault(); doSearch(); } });
    if (!c.getAttribute('data-bound')) {
      c.setAttribute('data-bound', '1');
      c.addEventListener('change', function(){ fillSubgroups(); doSearch(); });
    }
    var sub = document.getElementById('cb-sub');
    if (sub && !sub.getAttribute('data-bound')) {
      sub.setAttribute('data-bound', '1');
      sub.addEventListener('change', doSearch);
    }
    doSearch();
  }
  setTimeout(bindPicker, 300);}
"""


def run():
    import frappe
    frappe.set_user("Administrator")
    cs = frappe.get_doc("Client Script", "Bulk Entry-Form")
    cs.script = JS
    cs.save(ignore_permissions=True)
    frappe.db.commit()
    frappe.clear_cache()
    print("UPDATED")
    return "BULK_CS_V4_DONE"
