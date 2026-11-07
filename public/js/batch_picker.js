// 统一批量物料选择器 v3
//  顶部：一级分类 / 二级子类 两个下拉框 + 搜索 + 分页结果（行内数量/单位）
//  底部：已选清单（可改数量/单位/删除） + 批量粘贴 / 导入文件（预览校验） / 模板
// 供：单据表单（batch_entry）与首页/操作台快速操作（cb_ops）共用。
(function () {
	function esc(s) {
		return frappe.utils.escape_html(s == null ? "" : s);
	}

	function open(opts) {
		opts = opts || {};
		var selected = {}; // item_code -> row
		var state = { group: "", keyword: "", start: 0, total: 0, items: [] };

		var html =
			'<div class="cb-batch cb-batch-v2">' +
			'<div class="cb-b2-filters">' +
			'<select class="form-control cb-cat"><option value="">全部分类</option></select>' +
			'<select class="form-control cb-subcat"><option value="">全部子类</option></select>' +
			"</div>" +
			'<div class="cb-b2-body">' +
			'<div class="cb-b2-main">' +
			'<div class="cb-b2-search">' +
			'<input class="form-control cb-kw" placeholder="搜索 编码 / 名称 / 规格 / 英文名 / 葡语名">' +
			'<button class="btn btn-sm btn-primary cb-search" type="button">搜索</button>' +
			'<button class="btn btn-sm btn-default cb-allgroup" type="button" style="display:none">整类添加</button>' +
			'<span class="cb-count"></span>' +
			"</div>" +
			'<div class="cb-results"></div>' +
			'<div style="text-align:center;margin-top:8px"><button class="btn btn-xs btn-default cb-more" type="button" style="display:none">加载更多</button></div>' +
			"</div></div>" +
			'<div class="cb-b2-selected"><div class="cb-b2-sel-h">已选 <b class="cb-sel-n">0</b> 行</div><div class="cb-sel-list"></div></div>' +
			'<div class="cb-b2-actions">' +
			'<button class="btn btn-sm btn-default cb-paste-btn" type="button">📋 批量粘贴</button>' +
			'<button class="btn btn-sm btn-default cb-import-btn" type="button">📂 导入文件</button>' +
			'<button class="btn btn-sm btn-default cb-tpl" type="button">⬇ 下载模板</button>' +
			'<span class="cb-b2-tip">Excel / CSV / 粘贴：编码,数量,单位,备注（每行一条）</span>' +
			"</div>" +
			'<textarea class="form-control cb-paste" rows="4" placeholder="CB-EL-001,10,米,备注" style="margin-top:8px;display:none"></textarea>' +
			'<input type="file" class="cb-file" accept=".csv,.xlsx,.xls,.xlsm,.txt" style="display:none">' +
			"</div>";

		var d = new frappe.ui.Dialog({
			title: opts.title || "批量添加物料",
			size: "extra-large",
			fields: [{ fieldtype: "HTML", fieldname: "body", options: html }],
			primary_action_label: "添加选中",
			primary_action: function () {
				finish();
			},
		});
		d.show();

		var $w = d.fields_dict.body.$wrapper;
		var $res = $w.find(".cb-results");
		var $kw = $w.find(".cb-kw");
		var $cnt = $w.find(".cb-count");
		var $sel = $w.find(".cb-sel-list");
		var $selN = $w.find(".cb-sel-n");
		var $paste = $w.find(".cb-paste");
		var $file = $w.find(".cb-file");
		var $more = $w.find(".cb-more");
		var $cat = $w.find(".cb-cat");
		var $sub = $w.find(".cb-subcat");

		function upsert(row) {
			var old = selected[row.item_code];
			if (old) {
				old.qty = (old.qty || 0) + (row.qty || 0);
			} else {
				selected[row.item_code] = {
					item_code: row.item_code,
					item_name: row.item_name || "",
					spec: row.spec || "",
					uom: row.uom || "",
					qty: row.qty || 1,
					rate: row.rate || 0,
					loss_rate: row.loss_rate || 0,
					remark: row.remark || "",
					controlled: row.controlled == null ? 1 : row.controlled,
				};
			}
			renderSelected();
			syncResultState();
		}

		function remove(code) {
			delete selected[code];
			renderSelected();
			syncResultState();
		}

		function renderSelected() {
			var keys = Object.keys(selected);
			$selN.text(keys.length);
			if (!keys.length) {
				$sel.html('<div class="cb-sel-empty">还没有选择物料。可在上方搜索勾选，或使用底部粘贴/导入。</div>');
				return;
			}
			var h = "";
			keys.forEach(function (k) {
				var r = selected[k];
				h +=
					'<div class="cb-sel-row" data-code="' + esc(k) + '">' +
					'<span class="cb-sel-name"><b>' + esc(k) + "</b> " + esc(r.item_name) + "</span>" +
					'<input type="number" class="form-control cb-sel-qty" value="' + (r.qty || 1) + '" min="0" step="any" title="数量">' +
					'<span class="cb-sel-uom">' + esc(r.uom || "") + "</span>" +
					'<a href="#" class="cb-sel-del" title="移除">✕</a>' +
					"</div>";
			});
			$sel.html(h);
		}

		$sel.on("input", ".cb-sel-qty", function () {
			var code = $(this).closest(".cb-sel-row").attr("data-code");
			if (selected[code]) selected[code].qty = parseFloat($(this).val()) || 0;
		});
		$sel.on("click", ".cb-sel-del", function (e) {
			e.preventDefault();
			remove($(this).closest(".cb-sel-row").attr("data-code"));
		});

		function syncResultState() {
			$res.find(".cb-row").each(function () {
				var code = $(this).attr("data-code");
				var on = !!selected[code];
				$(this).toggleClass("is-selected", on);
				$(this).find(".cb-chk").prop("checked", on);
				if (on) $(this).find(".cb-qty").val(selected[code].qty);
			});
		}

		function renderResults(items, append) {
			if (!append) $res.empty();
			if (!items.length && !append) {
				$res.html('<div class="cb-empty">没有匹配的物料，请换个关键字或分类。</div>');
				return;
			}
			var h = "";
			items.forEach(function (it) {
				var sel = selected[it.item_code];
				h +=
					'<div class="cb-row' + (sel ? " is-selected" : "") + '" data-code="' + esc(it.item_code) + '"' +
					' data-name="' + esc(it.item_name || "") + '" data-spec="' + esc(it.custom_spec || "") + '" data-uom="' + esc(it.stock_uom || "") + '"' +
					' data-controlled="' + (it.custom_controlled ? 1 : 0) + '">' +
					'<input type="checkbox" class="cb-chk"' + (sel ? " checked" : "") + ">" +
					'<span class="cb-row-name"><b>' + esc(it.item_code) + "</b> " + esc(it.item_name || "") +
					(it.custom_spec ? ' <span class="cb-muted">' + esc(it.custom_spec) + "</span>" : "") +
					' <span class="cb-tag">' + (it.custom_controlled ? "受控" : "辅材") + "</span></span>" +
					'<input type="number" class="form-control cb-qty" value="' + (sel ? sel.qty : 1) + '" min="0" step="any">' +
					'<span class="cb-row-uom">' + esc(it.stock_uom || "") + "</span>" +
					"</div>";
			});
			$res.append(h);
			$more.toggle(state.start + state.items.length < state.total);
			$cnt.text("共 " + state.total + " 条" + (state.items.length < state.total ? "，已显示 " + state.items.length : ""));
		}

		$res.on("click", ".cb-row", function (e) {
			if ($(e.target).is("input")) return;
			var $c = $(this).find(".cb-chk");
			$c.prop("checked", !$c.prop("checked")).trigger("change");
		});
		$res.on("change", ".cb-chk", function () {
			var $row = $(this).closest(".cb-row");
			var code = $row.attr("data-code");
			if (this.checked) {
				upsert({
					item_code: code,
					item_name: $row.attr("data-name"),
					spec: $row.attr("data-spec"),
					uom: $row.attr("data-uom"),
					qty: parseFloat($row.find(".cb-qty").val()) || 1,
					controlled: $row.attr("data-controlled") === "1" ? 1 : 0,
				});
			} else {
				remove(code);
			}
		});
		$res.on("input", ".cb-qty", function () {
			var $row = $(this).closest(".cb-row");
			var code = $row.attr("data-code");
			if (selected[code]) selected[code].qty = parseFloat($(this).val()) || 0;
			if ($row.find(".cb-chk").prop("checked")) renderSelected();
		});

		function load(start, append) {
			frappe.call({
				method: "cb_erp.cb_erp.bulk_ops.api_item_search",
				args: {
					keyword: state.keyword,
					group: state.group,
					start: start,
					page_length: 50,
				},
				callback: function (r) {
					var m = r.message || {};
					state.items = append ? state.items.concat(m.items || []) : m.items || [];
					state.total = m.total || 0;
					state.start = start;
					renderResults(m.items || [], append);
				},
			});
		}

		function search() {
			state.keyword = ($kw.val() || "").trim();
			load(0, false);
		}

		$w.find(".cb-search").on("click", search);
		$kw.on("keydown", function (e) {
			if (e.key === "Enter") {
				e.preventDefault();
				search();
			}
		});
		$more.on("click", function () {
			load(state.start + 50, true);
		});

		// 分类：一级 / 二级 下拉框
		function loadCategories() {
			frappe.call({
				method: "cb_erp.cb_erp.bulk_ops.api_list_categories",
				callback: function (r) {
					(r.message || []).forEach(function (c) {
						$cat.append('<option value="' + esc(c) + '">' + esc(c) + "</option>");
					});
				},
			});
		}

		function loadSubgroups(parent) {
			$sub.html('<option value="">全部子类</option>');
			if (!parent) return;
			frappe.call({
				method: "cb_erp.cb_erp.bulk_ops.api_list_subgroups",
				args: { parent: parent },
				callback: function (r) {
					(r.message || []).forEach(function (g) {
						var nm = typeof g === "string" ? g : g.name;
						if (nm) $sub.append('<option value="' + esc(nm) + '">' + esc(nm) + "</option>");
					});
				},
			});
		}

		function applyGroup() {
			state.group = $sub.val() || $cat.val() || "";
			state.keyword = ($kw.val() || "").trim();
			$w.find(".cb-allgroup").toggle(!!state.group);
			load(0, false);
		}

		$cat.on("change", function () {
			loadSubgroups($cat.val());
			applyGroup();
		});
		$sub.on("change", applyGroup);
		loadCategories();

		$w.find(".cb-allgroup").on("click", function () {
			if (!state.group) {
				frappe.msgprint("请先选择一个分类。");
				return;
			}
			var limit = 1000;
			frappe.confirm("将当前分类下最多 " + limit + " 个物料全部加入已选，继续？", function () {
				frappe.call({
					method: "cb_erp.cb_erp.bulk_ops.api_group_items",
					args: { group: state.group, limit: limit },
					freeze: true,
					callback: function (r) {
						var rows = r.message || [];
						rows.forEach(function (x) {
							upsert({
								item_code: x.item_code,
								item_name: x.item_name,
								spec: x.custom_spec,
								uom: x.stock_uom,
								qty: 1,
								controlled: x.custom_controlled == null ? 1 : x.custom_controlled,
							});
						});
						frappe.show_alert({ message: "已加入 " + rows.length + " 个物料", indicator: "green" });
					},
				});
			});
		});

		// 粘贴
		$w.find(".cb-paste-btn").on("click", function () {
			$paste.toggle();
			if ($paste.is(":visible")) $paste.trigger("focus");
		});
		function parsePaste() {
			var txt = ($paste.val() || "").trim();
			if (!txt) return 0;
			var n = 0;
			txt.split(/\r?\n/).forEach(function (line) {
				if (!line.trim()) return;
				var p = line.split(/[\t,;，；]/);
				var code = (p[0] || "").trim();
				if (!code || /^(编码|item_code|物料编码)$/i.test(code)) return;
				upsert({
					item_code: code,
					qty: parseFloat((p[1] || "1").trim()) || 1,
					uom: (p[2] || "").trim(),
					remark: (p[3] || "").trim(),
				});
				n++;
			});
			$paste.val("").toggle(false);
			return n;
		}
		$paste.on("blur", function () {
			var n = parsePaste();
			if (n) frappe.show_alert({ message: "已从粘贴内容加入 " + n + " 行", indicator: "green" });
		});

		// 导入
		$w.find(".cb-import-btn").on("click", function () {
			$file.trigger("click");
		});
		$file.on("change", function () {
			var file = this.files && this.files[0];
			if (!file) return;
			var fd = new FormData();
			fd.append("file", file);
			frappe
				.call({
					method: "cb_erp.cb_erp.bulk_ops.api_parse_preview",
					type: "POST",
					data: fd,
					processData: false,
					contentType: false,
					freeze: true,
				})
				.then(function (r) {
					var m = r.message || {};
					showPreview(m);
					$file.val("");
				});
		});

		function showPreview(m) {
			var rows = m.rows || [];
			var valid = rows.filter(function (x) {
				return x.valid;
			});
			var invalid = rows.filter(function (x) {
				return !x.valid;
			});
			var h =
				'<div style="margin-bottom:8px">共 ' + rows.length + " 行：有效 <b style='color:#059669'>" + valid.length +
				"</b> 行，无效 <b style='color:#dc2626'>" + invalid.length + "</b> 行</div>" +
				'<div style="max-height:320px;overflow:auto;border:1px solid #e2e8f0;border-radius:8px">' +
				'<table class="table table-sm" style="margin:0"><thead><tr><th>行</th><th>编码</th><th>数量</th><th>单位</th><th>状态</th></tr></thead><tbody>';
			rows.forEach(function (x, i) {
				h +=
					"<tr" + (x.valid ? "" : ' style="background:#fef2f2"') + "><td>" + (i + 1) + "</td><td>" + esc(x.item_code) +
					"</td><td>" + (x.qty == null ? "" : x.qty) + "</td><td>" + esc(x.uom || "") + "</td><td>" +
					(x.valid ? '<span style="color:#059669">有效</span>' : '<span style="color:#dc2626">' + esc(x.reason || "无效") + "</span>") +
					"</td></tr>";
			});
			h += "</tbody></table></div>";
			var pd = new frappe.ui.Dialog({
				title: "导入预览",
				size: "large",
				fields: [{ fieldtype: "HTML", fieldname: "body", options: h }],
				primary_action_label: "导入 " + valid.length + " 行有效数据",
				primary_action: function () {
					valid.forEach(function (x) {
						upsert({
							item_code: x.item_code,
							item_name: x.item_name,
							spec: x.spec,
							uom: x.uom,
							qty: x.qty,
							rate: x.rate,
							loss_rate: x.loss_rate,
							remark: x.remark,
							controlled: x.controlled,
						});
					});
					pd.hide();
					frappe.show_alert({ message: "已导入 " + valid.length + " 行", indicator: "green" });
				},
			});
			pd.show();
		}

		// 模板
		$w.find(".cb-tpl").on("click", function (e) {
			e.preventDefault();
			frappe.call({
				method: "cb_erp.cb_erp.bulk_ops.api_batch_template_xlsx",
				callback: function (r) {
					var m = r.message || {};
					if (m.content_b64) {
						var bin = atob(m.content_b64);
						var bytes = new Uint8Array(bin.length);
						for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
						var a = document.createElement("a");
						a.href = URL.createObjectURL(new Blob([bytes], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" }));
						a.download = m.filename || "物料批量录入模板.xlsx";
						a.click();
					}
				},
			});
		});

		function finish() {
			var rows = Object.keys(selected).map(function (k) {
				return selected[k];
			});
			if (!rows.length) {
				frappe.msgprint("请先选择物料，或使用粘贴 / 导入。");
				return;
			}
			if (opts.onAdd) opts.onAdd(rows);
			d.hide();
			frappe.show_alert({ message: "已添加 " + rows.length + " 行", indicator: "green" });
		}

		renderSelected();
		load(0, false);
		if (opts.startImport) setTimeout(function () {
			$file.trigger("click");
		}, 300);
	}

	window.CBPicker = { open: open };
})();
