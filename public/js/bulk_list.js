(function () {
  var DTS = ["Material Request", "Stock Entry", "Material Budget", "Material Commitment",
             "Purchase Order", "CB Import Case", "CB Shipment", "Design BOM", "Design Change Request"];
  function namesOf(listview) {
    return (listview.get_checked_items() || []).map(function (d) { return d.name; });
  }
  function report(m) {
    m = m || {};
    var msg = "<b>成功 " + ((m.ok || []).length) + " 张</b>";
    if ((m.ok || []).length) msg += "<br>" + (m.ok || []).join("<br>");
    if ((m.err || []).length) msg += "<br><br>❌ 失败 " + m.err.length + " 张<br>" + m.err.join("<br>");
    frappe.msgprint(msg);
  }
  DTS.forEach(function (dt) {
    frappe.listview_settings[dt] = frappe.listview_settings[dt] || {};
    if (frappe.listview_settings[dt].__cb_bulk_patched) return;
    frappe.listview_settings[dt].__cb_bulk_patched = true;
    var orig = frappe.listview_settings[dt].onload;
    frappe.listview_settings[dt].onload = function (listview) {
      if (orig) orig(listview);
      listview.page.add_action_item(__("批量提交"), function () {
        var names = namesOf(listview);
        if (!names.length) { frappe.msgprint(__("请先勾选单据")); return; }
        frappe.call({ method: "cb_erp.cb_erp.bulk_ops.api_bulk_submit", args: { doctype: dt, names: names },
          freeze: true, freeze_message: __("正在批量提交..."), callback: function (r) { report(r.message); listview.refresh(); } });
      });
      listview.page.add_action_item(__("批量取消"), function () {
        var names = namesOf(listview);
        if (!names.length) { frappe.msgprint(__("请先勾选单据")); return; }
        frappe.confirm(__("确定取消选中的 {0} 张单据？", [names.length]), function () {
          frappe.call({ method: "cb_erp.cb_erp.bulk_ops.api_bulk_cancel", args: { doctype: dt, names: names },
            freeze: true, freeze_message: __("正在批量取消..."), callback: function (r) { report(r.message); listview.refresh(); } });
        });
      });
      listview.page.add_action_item(__("批量删除"), function () {
        var names = namesOf(listview);
        if (!names.length) { frappe.msgprint(__("请先勾选单据")); return; }
        frappe.confirm(__("确定删除选中的 {0} 张单据？此操作不可恢复！", [names.length]), function () {
          frappe.call({ method: "cb_erp.cb_erp.bulk_ops.api_bulk_delete", args: { doctype: dt, names: names },
            freeze: true, freeze_message: __("正在批量删除..."), callback: function (r) { report(r.message); listview.refresh(); } });
        });
      });
      listview.page.add_action_item(__("批量改项目"), function () {
        var names = namesOf(listview);
        if (!names.length) { frappe.msgprint(__("请先勾选单据")); return; }
        frappe.prompt([{ fieldname: "project", fieldtype: "Link", options: "Project", label: __("项目"), reqd: 1 }],
          function (v) {
            frappe.call({ method: "cb_erp.cb_erp.bulk_ops.api_bulk_set_project",
              args: { doctype: dt, names: names, project: v.project },
              freeze: true, freeze_message: __("正在批量改项目..."), callback: function (r) { report(r.message); listview.refresh(); } });
          }, __("批量改项目"), __("确定"));
      });
    };
  });
})();
