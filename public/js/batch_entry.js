// 单据表单统一批量录入：设计BOM / 设计变更 / 材料预算 / 采购申请 / 采购订单 / 采购入库 / 库存收发 / 盘点 / 询价单 / 供应商报价
// 明细表上方固定工具条：选择物料（多选）/ 粘贴 / 导入文件 / 下载模板 / 从BOM生成
(function () {
	var T7 = "";
	try {
		if (frappe && frappe.datetime) T7 = frappe.datetime.add_days(frappe.datetime.get_today(), 7) || "";
	} catch (e) {
		T7 = "";
	}

	var CONFIG = {
		"Design BOM": {
			table: "bom_items",
			merge: true,
			map: function (frm, r) {
				return { item_code: r.item_code, item_name: r.item_name, spec: r.spec || "", qty: r.qty, uom: r.uom || "", loss_rate: r.loss_rate || 0, remark: r.remark || "", custom_controlled: r.controlled == null ? 1 : r.controlled };
			},
		},
		"Design Change Request": {
			table: "change_items",
			merge: true,
			from_bom: true,
			map: function (frm, r) {
				return { item_code: r.item_code, item_name: r.item_name, old_qty: r.old_qty || 0, new_qty: r.qty, delta: (r.qty || 0) - (r.old_qty || 0), remark: r.remark || "" };
			},
		},
		"Material Budget": {
			table: "budget_items",
			merge: true,
			from_bom: true,
			map: function (frm, r) {
				return { item_code: r.item_code, item_name: r.item_name, qty: r.qty, uom: r.uom || "", rate: r.rate || 0, amount: (r.rate || 0) * r.qty };
			},
		},
		"Material Request": {
			table: "items",
			from_gap: true,
			map: function (frm, r) {
				return { item_code: r.item_code, item_name: r.item_name, qty: r.qty, uom: r.uom || "", warehouse: frm.doc.set_warehouse || "", schedule_date: T7 };
			},
		},
		"Purchase Order": {
			table: "items",
			from_gap: true,
			map: function (frm, r) {
				return { item_code: r.item_code, item_name: r.item_name, qty: r.qty, uom: r.uom || "", rate: r.rate || 0, warehouse: frm.doc.set_warehouse || "", schedule_date: T7 };
			},
		},
		"Purchase Receipt": {
			table: "items",
			map: function (frm, r) {
				return { item_code: r.item_code, item_name: r.item_name, qty: r.qty, uom: r.uom || "", rate: r.rate || 0, warehouse: frm.doc.set_warehouse || "" };
			},
		},
		"Stock Entry": {
			table: "items",
			map: function (frm, r) {
				return {
					item_code: r.item_code,
					item_name: r.item_name,
					qty: r.qty,
					uom: r.uom || "",
					s_warehouse: frm.doc.from_warehouse || "",
					t_warehouse: frm.doc.to_warehouse || (frm.doc.purpose === "Material Receipt" ? frm.doc.set_warehouse || "" : ""),
				};
			},
		},
		"Stock Reconciliation": {
			table: "items",
			map: function (frm, r) {
				return { item_code: r.item_code, item_name: r.item_name, qty: r.qty, warehouse: frm.doc.warehouse || "" };
			},
		},
		"Request for Quotation": {
			table: "items",
			map: function (frm, r) {
				return { item_code: r.item_code, item_name: r.item_name, qty: r.qty, uom: r.uom || "", schedule_date: T7 };
			},
		},
		"Supplier Quotation": {
			table: "items",
			map: function (frm, r) {
				return { item_code: r.item_code, item_name: r.item_name, qty: r.qty, uom: r.uom || "", rate: r.rate || 0, warehouse: frm.doc.set_warehouse || "" };
			},
		},
	};

	function dropEmpty(frm, table) {
		var grid = frm.fields_dict[table] && frm.fields_dict[table].grid;
		if (!grid) return;
		var rows = frm.doc[table] || [];
		for (var i = rows.length - 1; i >= 0; i--) {
			if (!rows[i].item_code && grid.grid_rows[i]) grid.grid_rows[i].remove();
		}
	}

	function addRows(frm, cfg, rows) {
		var added = 0;
		dropEmpty(frm, cfg.table);
		(rows || []).forEach(function (r) {
			if (!r || !r.item_code) return;
			var line = cfg.map(frm, r);
			if (cfg.merge) {
				var found = null;
				(frm.doc[cfg.table] || []).forEach(function (d) {
					if (d.item_code === r.item_code && (d.uom || "") === (line.uom || d.uom || "")) found = d;
				});
				if (found) {
					if (cfg.table === "change_items") found.new_qty = (found.new_qty || 0) + (line.new_qty || 0);
					else found.qty = (found.qty || 0) + (line.qty || 0);
					if (cfg.table === "budget_items") found.amount = (found.qty || 0) * (found.rate || 0);
					if (cfg.table === "change_items") found.delta = (found.new_qty || 0) - (found.old_qty || 0);
					added++;
					return;
				}
			}
			frm.add_child(cfg.table, line);
			added++;
		});
		frm.refresh_field(cfg.table);
		if (cfg.table === "budget_items") {
			var total = 0;
			(frm.doc[cfg.table] || []).forEach(function (d) {
				total += (d.amount || (d.qty || 0) * (d.rate || 0));
			});
			frm.set_value("total_amount", total);
		}
		frm.dirty();
		frappe.show_alert({ message: "已添加 " + added + " 行", indicator: "green" });
	}

	function download(filename, text) {
		var blob = new Blob([text], { type: "text/csv;charset=utf-8" });
		var a = document.createElement("a");
		a.href = URL.createObjectURL(blob);
		a.download = filename;
		a.click();
	}

	function downloadB64(filename, b64) {
		var bin = atob(b64);
		var bytes = new Uint8Array(bin.length);
		for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
		var a = document.createElement("a");
		a.href = URL.createObjectURL(new Blob([bytes], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" }));
		a.download = filename;
		a.click();
	}

	function toolbar(frm, cfg) {
		var gf = frm.fields_dict[cfg.table];
		if (!gf || !gf.$wrapper) return;
		var $w = gf.$wrapper;
		$w.find(".cb-batch-bar").remove();

		var html =
			'<div class="cb-batch-bar">' +
			'<button type="button" class="btn btn-primary btn-sm cb-pick">＋ 选择物料（可多选）</button>' +
			'<button type="button" class="btn btn-default btn-sm cb-import">导入文件</button>' +
			'<button type="button" class="btn btn-default btn-sm cb-tpl">下载模板</button>' +
			(cfg.from_bom ? '<button type="button" class="btn btn-default btn-sm cb-from-bom">从设计BOM生成</button>' : "") +
			(cfg.from_gap ? '<button type="button" class="btn btn-default btn-sm cb-from-gap">按BOM缺口生成</button>' : "") +
			'<span class="cb-batch-tip">支持 Excel / CSV，可一次导入上千行</span>' +
			'<a href="#" class="cb-adv">高级：手工加行</a>' +
			"</div>";

		var $bar = $(html);
		var $head = $w.find(".grid-head-toolbar").first();
		if ($head.length) $head.before($bar);
		else $w.prepend($bar);

		$bar.find(".cb-pick").on("click", function () {
			openPicker(frm, cfg);
		});
		$bar.find(".cb-import").on("click", function () {
			openPicker(frm, cfg, true);
		});
		$bar.find(".cb-tpl").on("click", function (e) {
			e.preventDefault();
			frappe.call({
				method: "cb_erp.cb_erp.bulk_ops.api_batch_template_xlsx",
				callback: function (r) {
					var m = r.message || {};
					if (m.content_b64) downloadB64(m.filename || "物料批量录入模板.xlsx", m.content_b64);
					else download("物料批量录入模板.csv", m.content || "");
				},
			});
		});
		$bar.find(".cb-adv").on("click", function (e) {
			e.preventDefault();
			var $row = gf.grid && gf.grid.wrapper ? gf.grid.wrapper.find(".grid-add-row") : $w.find(".grid-add-row");
			var show = $row.is(":visible");
			$row.toggle(!show);
			$(this).text(show ? "高级：手工加行" : "收起手工加行");
		});

		if (cfg.from_bom) {
			$bar.find(".cb-from-bom").on("click", function () {
				var p = frm.doc.project || frm.doc.custom_cb_project;
				var d = frm.doc.custom_discipline;
				var s = frm.doc.custom_system;
				var load = function (proj, disc, sys) {
					if (!proj) {
						frappe.msgprint("请先选择项目（或选择设计BOM）。");
						return;
					}
					frappe.call({
						method: "cb_erp.cb_erp.bulk_ops.api_bom_rows",
						args: { project: proj, discipline: disc, system: sys },
						freeze: true,
						callback: function (r) {
							var rows = r.message || [];
							if (!rows.length) {
								frappe.msgprint("当前项目/专业/系统下没有已提交的设计BOM。");
								return;
							}
							rows.forEach(function (x) {
								x.qty = x.qty || x.new_qty || 0;
								if (x.old_qty == null) x.old_qty = x.qty;
								x.controlled = x.custom_controlled == null ? 1 : x.custom_controlled;
							});
							addRows(frm, cfg, rows);
						},
					});
				};
				if (p) {
					load(p, d, s);
				} else if (frm.doc.design_bom) {
					frappe.db
						.get_value("Design BOM", frm.doc.design_bom, ["project", "custom_discipline", "custom_system"])
						.then(function (r) {
							var m = r.message || {};
							if (!d && m.custom_discipline) {
								frm.set_value("custom_discipline", m.custom_discipline);
								d = m.custom_discipline;
							}
							if (!s && m.custom_system) {
								frm.set_value("custom_system", m.custom_system);
								s = m.custom_system;
							}
							load(m.project, d, s);
						});
				} else {
					frappe.msgprint("请先选择项目或设计BOM。");
				}
			});
		}

		if (cfg.from_gap) {
			$bar.find(".cb-from-gap").on("click", function () {
				var p = frm.doc.custom_cb_project || frm.doc.project;
				if (!p) {
					frappe.msgprint("请先选择项目。");
					return;
				}
				frappe.call({
					method: "cb_erp.cb_erp.bulk_ops.api_bom_gap",
					args: {
						project: p,
						discipline: frm.doc.custom_discipline,
						system: frm.doc.custom_system,
						kind: frm.doctype === "Purchase Order" ? "po" : "mr",
					},
					freeze: true,
					callback: function (r) {
						var rows = r.message || [];
						if (!rows.length) {
							frappe.msgprint("没有可生成的缺口行（可能已全部覆盖或未维护设计BOM）。");
							return;
						}
						addRows(frm, cfg, rows);
					},
				});
			});
		}
	}

	function openPicker(frm, cfg, startImport) {
		if (!window.CBPicker) {
			frappe.msgprint("物料选择器未加载，请刷新页面。");
			return;
		}
		window.CBPicker.open({
			title: "批量添加物料",
			startImport: !!startImport,
			onAdd: function (rows) {
				addRows(frm, cfg, rows);
			},
		});
	}

	function setup(frm) {
		var cfg = CONFIG[frm.doctype];
		if (!cfg) return;
		// 默认隐藏"添加行"，统一走批量选择；高级模式可展开
		try {
			var gf = frm.fields_dict[cfg.table];
			if (gf && gf.grid && gf.grid.wrapper) gf.grid.wrapper.find(".grid-add-row").hide();
		} catch (e) {}
		toolbar(frm, cfg);
	}

	Object.keys(CONFIG).forEach(function (dt) {
		frappe.ui.form.on(dt, {
			refresh: function (frm) {
				setup(frm);
			},
		});
	});

	// 设计变更：选设计BOM后自动带出专业/系统（项目在BOM上）
	frappe.ui.form.on("Design Change Request", {
		design_bom: function (frm) {
			if (!frm.doc.design_bom) return;
			frappe.db
				.get_value("Design BOM", frm.doc.design_bom, ["project", "custom_discipline", "custom_system"])
				.then(function (r) {
					var m = r.message || {};
					if (m.custom_discipline) frm.set_value("custom_discipline", m.custom_discipline);
					// 专业联动会清空系统，稍后再回填
					setTimeout(function () {
						if (m.custom_system) frm.set_value("custom_system", m.custom_system);
					}, 500);
				});
		},
	});

	// 物料分类树：本组（含子组）批量设置受控
	frappe.ui.form.on("Item Group", {
		refresh: function (frm) {
			if (!frm.doc.is_group) return;
			frm.add_custom_button("本组物料设为受控", function () {
				setGroupControlled(frm, 1);
			});
			frm.add_custom_button("本组物料设为非受控", function () {
				setGroupControlled(frm, 0);
			});
		},
	});

	function setGroupControlled(frm, val) {
		frappe.confirm("将「" + frm.doc.name + "」及全部子组的物料设为" + (val ? "受控" : "非受控") + "？", function () {
			frappe.call({
				method: "cb_erp.cb_erp.bulk_ops.api_set_group_controlled",
				args: { group: frm.doc.name, controlled: val },
				freeze: true,
				callback: function (r) {
					var m = r.message || {};
					frappe.show_alert({
						message: "已更新 " + (m.items || 0) + " 个物料为" + (m.controlled ? "受控" : "非受控"),
						indicator: "green",
					});
				},
			});
		});
	}
})();
