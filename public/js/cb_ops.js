// 统一快速操作（留在当前页面，不跳转链接）：
// 首页 / 操作台点「采购申请·采购下单·到货入库·物料领用·物料退料·库存盘点」→ 弹出操作窗，
// 表头信息（均匀3列）+ 物料行（批量选择/粘贴/导入文件）+ 生成单据，一气呵成。
(function () {
	if (!window.frappe) return;

	var KIND_API = {
		"采购申请": "material_request",
		"采购订单": "purchase_order",
		"到货入库": "material_receipt",
		"物料领用": "material_issue",
		"物料退料": "material_return",
		"库存盘点": "stock_reconciliation",
	};

	// 快捷操作恢复为「页面内批量录入」：Bulk Entry 的 kind 选项
	var BULK_KIND = {
		"采购申请": "采购申请",
		"采购订单": "采购订单",
		"到货入库": "入库",
		"物料领用": "领料",
		"物料退料": "退料",
		"库存盘点": "盘点",
	};

	function goto(kind) {
		var k = BULK_KIND[kind] || kind || "采购申请";
		window.location.href = "/desk/cb-erp/bulk-entry/new?kind=" + encodeURIComponent(k);
	}
	var T7 = "";
	try {
		T7 = frappe.datetime.add_days(frappe.datetime.get_today(), 7) || "";
	} catch (e) {}

	var esc = function (s) {
		return frappe.utils.escape_html(s == null ? "" : s);
	};

	function bodyHtml() {
		return (
			'<div class="cb-opsq">' +
			'<div class="cb-opsq-h">物料行</div>' +
			'<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:8px">' +
			'<button class="btn btn-sm btn-primary cb-opsq-pick" type="button">⚡ 批量选择物料</button>' +
			'<button class="btn btn-sm btn-default cb-opsq-paste-btn" type="button">📋 批量粘贴</button>' +
			'<button class="btn btn-sm btn-default cb-opsq-import-btn" type="button">📂 导入文件</button>' +
			'<button class="btn btn-sm btn-default cb-opsq-tpl" type="button">⬇ 下载模板</button>' +
			'<button class="btn btn-sm btn-default cb-opsq-clear" type="button">🗑 清空</button>' +
			'<span class="cb-opsq-cnt" style="color:#64748b;font-size:12px"></span>' +
			"</div>" +
			'<textarea class="form-control cb-opsq-paste" rows="3" placeholder="编码,数量,单位,备注（每行一条）" style="display:none"></textarea>' +
			'<input type="file" class="cb-opsq-file" accept=".csv,.xlsx,.xls,.xlsm" style="display:none">' +
			'<div class="cb-opsq-rows" style="max-height:220px;overflow:auto;border:1px solid #e2e8f0;border-radius:8px"></div>' +
			"</div>"
		);
	}

	function open(kind) {
		var kinds = Object.keys(KIND_API);
		if (!kind || kinds.indexOf(kind) < 0) kind = "采购申请";
		var fields = [
			{ fieldtype: "Section Break", label: "单据信息" },
			{ fieldtype: "Select", fieldname: "kind", label: "业务类型", reqd: 1, options: kinds, default: kind },
			{ fieldtype: "Column Break" },
			{ fieldtype: "Link", fieldname: "project", label: "项目", options: "Project" },
			{ fieldtype: "Column Break" },
			{ fieldtype: "Link", fieldname: "warehouse", label: "仓库", options: "Warehouse" },
			{ fieldtype: "Section Break", label: "" },
			{ fieldtype: "Date", fieldname: "posting_date", label: "单据日期", default: frappe.datetime.get_today() },
			{ fieldtype: "Column Break" },
			{ fieldtype: "Link", fieldname: "discipline", label: "专业", options: "CB Discipline" },
			{ fieldtype: "Column Break" },
			{ fieldtype: "Link", fieldname: "system", label: "系统", options: "CB System" },
			{ fieldtype: "Section Break", label: "" },
			{ fieldtype: "Link", fieldname: "responsible", label: "责任人", options: "User" },
			{ fieldtype: "Column Break" },
			{
				fieldtype: "Link",
				fieldname: "supplier",
				label: "供应商",
				options: "Supplier",
				depends_on: "eval:doc.kind=='采购订单'",
			},
			{ fieldtype: "Column Break" },
			{
				fieldtype: "Link",
				fieldname: "budget",
				label: "材料预算",
				options: "Material Budget",
				depends_on: "eval:doc.kind=='采购订单'",
			},
			{ fieldtype: "Section Break", label: "", depends_on: "eval:doc.kind=='采购订单'" },
			{ fieldtype: "Data", fieldname: "order_name", label: "自定义下单名称" },
			{ fieldtype: "Section Break", label: "" },
			{ fieldtype: "HTML", fieldname: "opsbody", options: bodyHtml() },
		];

		var d = new frappe.ui.Dialog({
			title: "快速操作",
			size: "extra-large",
			fields: fields,
			primary_action_label: "生成单据",
			primary_action: function () {
				generate(d, rows);
			},
		});
		d.show();

		var $w = d.fields_dict.opsbody.$wrapper;
		var $rows = $w.find(".cb-opsq-rows");
		var $cnt = $w.find(".cb-opsq-cnt");
		var $paste = $w.find(".cb-opsq-paste");
		var $file = $w.find(".cb-opsq-file");
		var rows = [];

		var pasteToRows = function () {
			var txt = ($paste.val() || "").trim();
			if (!txt) return [];
			var out = [];
			txt.split(/\r?\n/).forEach(function (line) {
				if (!line.trim()) return;
				var p = line.split(/[\t,]/);
				if (!(p[0] || "").trim()) return;
				out.push({
					item_code: (p[0] || "").trim(),
					qty: parseFloat((p[1] || "1").trim()) || 1,
					uom: (p[2] || "").trim(),
					remark: (p[3] || "").trim(),
				});
			});
			return out;
		};

		function renderRows() {
			if (!rows.length) {
				$rows.html('<div style="padding:14px;color:#94a3b8;text-align:center">暂无物料行：请用上方按钮批量选择 / 粘贴 / 导入</div>');
				$cnt.text("");
				return;
			}
			var h = '<table class="table table-sm" style="margin:0"><thead><tr>' +
				"<th style=\"width:130px;border-top:none\">编码</th><th style=\"border-top:none\">名称/规格</th>" +
				"<th style=\"width:90px;border-top:none\">数量</th><th style=\"width:70px;border-top:none\">单位</th>" +
				"<th style=\"border-top:none\">备注</th><th style=\"width:36px;border-top:none\"></th></tr></thead><tbody>";
			rows.forEach(function (r, i) {
				h += '<tr style="border-bottom:1px solid #f1f5f9">' +
					"<td><b>" + esc(r.item_code) + "</b></td>" +
					"<td style=\"font-size:12px\">" + esc(r.item_name || "") + (r.spec ? ' <span style="color:#94a3b8">' + esc(r.spec) + "</span>" : "") + "</td>" +
					'<td><input type="number" class="form-control form-control-sm cb-opsq-qty" value="' + (r.qty || 1) + '" min="0" step="any"></td>' +
					"<td>" + esc(r.uom || "") + "</td><td>" + esc(r.remark || "") + "</td>" +
					'<td><a href="javascript:void(0)" class="cb-opsq-del text-danger" data-i="' + i + '">✕</a></td>' +
					"</tr>";
			});
			h += "</tbody></table>";
			$rows.html(h);
			$cnt.text(rows.length + " 行");
			$rows.find(".cb-opsq-qty").on("change", function () {
				var i = $(this).closest("tr").find(".cb-opsq-del").attr("data-i");
				rows[i].qty = parseFloat($(this).val()) || 1;
			});
			$rows.find(".cb-opsq-del").on("click", function () {
				rows.splice(parseInt($(this).attr("data-i"), 10), 1);
				renderRows();
			});
		}

		function merge(newRows) {
			(newRows || []).forEach(function (n) {
				var key = (n.item_code || "").trim();
				if (!key) return;
				var dup = rows.find(function (r) {
					return r.item_code === key;
				});
				if (dup) dup.qty = (parseFloat(dup.qty) || 0) + (parseFloat(n.qty) || 1);
				else rows.push({ item_code: key, item_name: n.item_name || "", spec: n.spec || "", uom: n.uom || "", qty: parseFloat(n.qty) || 1, rate: n.rate || 0, remark: n.remark || "" });
			});
			renderRows();
		}

		$w.find(".cb-opsq-pick").on("click", function () {
			window.CBPicker.open({
				title: "批量添加物料",
				onAdd: function (rs) {
					merge(rs);
				},
			});
		});
		$w.find(".cb-opsq-paste-btn").on("click", function () {
			$paste.css("display", $paste.css("display") === "none" ? "block" : "none");
		});
		$w.find(".cb-opsq-import-btn").on("click", function () {
			$file.trigger("click");
		});
		$file.on("change", function () {
			var file = this.files && this.files[0];
			if (!file) return;
			var fd = new FormData();
			fd.append("file", file);
			frappe
				.call({
					method: "cb_erp.cb_erp.bulk_ops.api_parse_rows",
					type: "POST",
					data: fd,
					processData: false,
					contentType: false,
				})
				.then(function (r) {
					var data = (r.message && r.message.rows) || [];
					if (!data.length) {
						frappe.msgprint("文件未解析到有效物料行（需含 编码/item_code 列）。");
						return;
					}
					merge(
						data.map(function (n) {
							return {
								item_code: n.item_code,
								item_name: n.item_name,
								spec: n.spec,
								uom: n.uom,
								qty: parseFloat(n.qty) || 1,
								rate: parseFloat(n.rate) || 0,
								remark: n.remark || "",
							};
						})
					);
					frappe.show_alert({ message: "已导入 " + data.length + " 行", indicator: "green" });
				});
		});
		$w.find(".cb-opsq-tpl").on("click", function () {
			frappe.call({
				method: "cb_erp.cb_erp.bulk_ops.api_batch_template",
				callback: function (r) {
					var blob = new Blob([r.message || ""], { type: "text/csv;charset=utf-8" });
					var a = document.createElement("a");
					a.href = URL.createObjectURL(blob);
					a.download = "物料批量录入模板.csv";
					a.click();
				},
			});
		});
		$w.find(".cb-opsq-clear").on("click", function () {
			rows = [];
			renderRows();
		});

		function generate(dialog) {
			var pasteRows = pasteToRows();
			if (pasteRows.length) merge(pasteRows);
			var all = rows.slice();
			if (!all.length) {
				frappe.msgprint("请先添加物料行（批量选择 / 粘贴 / 导入）。");
				return;
			}
			var v = dialog.get_values(true) || {};
			var apiKind = KIND_API[v.kind];
			if (!apiKind) {
				frappe.msgprint("业务类型不可用");
				return;
			}
			var payload = all.map(function (r) {
				return {
					item_code: r.item_code,
					item_name: r.item_name || undefined,
					qty: parseFloat(r.qty) || 1,
					unit: r.uom || undefined,
					warehouse: v.warehouse || undefined,
					project: v.project || undefined,
					rate: r.rate || undefined,
					remark: r.remark || undefined,
				};
			});
			frappe.call({
				method: "cb_erp.cb_erp.bulk_ops.api_create",
				args: {
					kind: apiKind,
					rows: payload,
					project: v.project || "",
					warehouse: v.warehouse || "",
					posting_date: v.posting_date || "",
					discipline: v.discipline || "",
					system: v.system || "",
					responsible: v.responsible || "",
					supplier: v.supplier || "",
					budget: v.budget || "",
					order_name: v.order_name || "",
				},
				freeze: true,
				freeze_message: "正在生成单据…",
				callback: function (res) {
					var r = res.message || {};
					if (r.errors && r.errors.length) {
						frappe.msgprint({
							indicator: "red",
							title: "部分失败",
							message: "成功 " + (r.count || 0) + " 张，失败 " + r.errors.length + " 个：<br>" + r.errors.map(esc).join("<br>"),
						});
					} else {
						var names = (r.created || []).map(function (c) {
							return c.name;
						});
						frappe.show_alert({ message: "已生成 " + (r.count || 0) + " 张单据：" + names.join("、"), indicator: "green" });
					}
					if (r.count > 0) {
						rows = [];
						$paste.val("");
						renderRows();
					}
				},
			});
		}

		renderRows();
	}

	window.CBOps = { open: open, goto: goto, KIND_API: KIND_API };
})();
