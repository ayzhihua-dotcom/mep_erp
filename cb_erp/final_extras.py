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
"""

PRINT_HTML = """
<div style="font-family: Arial, 'Microsoft YaHei', sans-serif; font-size: 11px;">
  <h3 style="margin:0 0 8px 0;">{{ doc.doctype }} {{ doc.name }}</h3>
  <table style="width:100%; border-collapse: collapse;">
    <thead>
      <tr style="background:#f0f0f0;">
        <th style="border:1px solid #999; padding:4px;">序号</th>
        <th style="border:1px solid #999; padding:4px;">编码</th>
        <th style="border:1px solid #999; padding:4px;">名称</th>
        <th style="border:1px solid #999; padding:4px;">规格参数</th>
        <th style="border:1px solid #999; padding:4px;">单位</th>
        <th style="border:1px solid #999; padding:4px;">数量</th>
        <th style="border:1px solid #999; padding:4px;">使用项目</th>
        <th style="border:1px solid #999; padding:4px;">责任人</th>
        <th style="border:1px solid #999; padding:4px;">备注</th>
      </tr>
    </thead>
    <tbody>
      {% for row in doc.items %}
      <tr>
        <td style="border:1px solid #ccc; padding:4px;">{{ row.get('custom_seq') or loop.index }}</td>
        <td style="border:1px solid #ccc; padding:4px;">{{ row.item_code }}</td>
        <td style="border:1px solid #ccc; padding:4px;">{{ row.item_name or row.get('custom_item_name') or '' }}</td>
        <td style="border:1px solid #ccc; padding:4px;">{{ row.get('custom_spec') or '' }}</td>
        <td style="border:1px solid #ccc; padding:4px;">{{ row.get('custom_uom') or row.uom or '' }}</td>
        <td style="border:1px solid #ccc; padding:4px; text-align:right;">{{ row.qty }}</td>
        <td style="border:1px solid #ccc; padding:4px;">{{ row.get('custom_use_project') or row.project or '' }}</td>
        <td style="border:1px solid #ccc; padding:4px;">{{ row.get('custom_responsible') or '' }}</td>
        <td style="border:1px solid #ccc; padding:4px;">{{ row.get('custom_remark') or '' }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
"""

REPORT_NAME = "物料明细（九列）"
REPORT_SQL = """
select '采购申请' as `单据类型`, parent as `单据编号`, custom_seq as `序号`, item_code as `编码`,
  item_name as `名称`, custom_spec as `规格参数`, custom_uom as `单位`, qty as `数量`,
  custom_use_project as `使用项目`, custom_responsible as `责任人`, custom_remark as `备注`
from `tabMaterial Request Item`
union all
select '库存移动', parent, custom_seq, item_code, item_name, custom_spec, custom_uom, qty, custom_use_project, custom_responsible, custom_remark
from `tabStock Entry Detail`
union all
select '采购订单', parent, custom_seq, item_code, item_name, custom_spec, custom_uom, qty, custom_use_project, custom_responsible, custom_remark
from `tabPurchase Order Item`
union all
select '盘点', parent, custom_seq, item_code, ifnull(custom_item_name, ''), custom_spec, custom_uom, qty, custom_use_project, custom_responsible, custom_remark
from `tabStock Reconciliation Item`
"""


def run():
    import frappe
    frappe.set_user("Administrator")
    # 1) client script auto-fill
    cs = frappe.get_doc("Client Script", "Bulk Entry-Form")
    cs.script = JS
    cs.save(ignore_permissions=True)
    frappe.db.commit()
    print("CS_UPDATED")
    # 2) print formats
    for dt, label in [("Material Request", "采购申请"), ("Stock Entry", "库存移动"),
                      ("Purchase Order", "采购订单"), ("Stock Reconciliation", "盘点")]:
        name = "物料明细九列（%s）" % label
        if frappe.db.exists("Print Format", name):
            pf = frappe.get_doc("Print Format", name)
            pf.html = PRINT_HTML
            pf.save(ignore_permissions=True)
        else:
            frappe.get_doc({"doctype": "Print Format", "name": name, "doc_type": dt,
                            "print_format_type": "Jinja", "html": PRINT_HTML,
                            "standard": "No", "disabled": 0}).insert(ignore_permissions=True)
    frappe.db.commit()
    print("PRINT_FORMATS_DONE")
    # 3) export report
    if frappe.db.exists("Report", REPORT_NAME):
        rep = frappe.get_doc("Report", REPORT_NAME)
        rep.query = REPORT_SQL
        rep.report_type = "Query Report"
        rep.ref_doctype = "Stock Entry"
        rep.save(ignore_permissions=True)
    else:
        frappe.get_doc({"doctype": "Report", "report_name": REPORT_NAME, "ref_doctype": "Stock Entry",
                        "report_type": "Query Report", "is_standard": 0, "query": REPORT_SQL,
                        "disabled": 0, "add_total_row": 0}).insert(ignore_permissions=True)
    frappe.db.commit()
    # 4) workspace link
    ws = frappe.get_doc("Workspace", "CB 机电总控")
    if not any(l.link_to == REPORT_NAME for l in ws.links):
        ws.append("links", {"type": "Link", "label": "物料明细（九列）", "link_to": REPORT_NAME,
                            "link_type": "Report", "is_query_report": 1})
        ws.save(ignore_permissions=True)
        frappe.db.commit()
    frappe.clear_cache()
    print("REPORT_DONE")
    return "FINAL_EXTRAS_DONE"
