frappe.query_reports["项目专业系统矩阵"] = {
	filters: [
		{
			fieldname: "metric",
			label: "指标",
			fieldtype: "Select",
			options: "已领用数量\n采购订单数量\n采购申请数量",
			default: "已领用数量",
			reqd: 1,
		},
		{
			fieldname: "discipline",
			label: "专业",
			fieldtype: "Link",
			options: "CB Discipline",
		},
		{
			fieldname: "project",
			label: "项目",
			fieldtype: "Link",
			options: "Project",
		},
		{
			fieldname: "top_projects",
			label: "显示项目数",
			fieldtype: "Int",
			default: 12,
		},
	],
};
