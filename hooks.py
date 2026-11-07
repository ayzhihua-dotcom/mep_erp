app_name = "cb_erp"
app_title = "MEP"
app_publisher = "CB-ERP Project"
app_description = "China-Brazil Industrial M+E ERP Custom App"
app_email = "sys@cb.local"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "cb_erp",
# 		"logo": "/assets/cb_erp/logo.png",
# 		"title": "CB ERP",
# 		"route": "/cb_erp",
# 		"has_permission": "cb_erp.api.permission.has_app_permission",
# 	}
# ]

# The dock, the rail down the left of the desk, is a document rather than a hook. Author it in
# Manage Dock on a developer-mode site and press Export to App, and it is written to
# `cb_erp/dock/cb_erp/cb_erp.json` for git to carry. An app that ships none has no
# rail: its sidebar gets a switcher in the header instead.
#
# A companion app, one that extends a host app rather than standing on its own, says so with
# `mount_on` on that same record, and its entries are appended to the host's rail. Mounting keeps
# the companion off the apps screen, so it takes precedence over any add_to_apps_screen above.

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/cb_erp/css/cb_erp_theme.css?v=27"
app_include_js = [
	"/assets/cb_erp/js/app_switch_guard.js?v=3",
	"/assets/cb_erp/js/discipline_system.js?v=3",
	"/assets/cb_erp/js/theme_switcher.js?v=3",
	"/assets/cb_erp/js/ui_beautify.js?v=7",
	"/assets/cb_erp/js/home_workbench.js?v=13",
	"/assets/cb_erp/js/nav_controls.js?v=9",
	"/assets/cb_erp/js/cb_ops.js?v=2",
	"/assets/cb_erp/js/link_picker.js?v=1",
	"/assets/cb_erp/js/sidebar_fix.js?v=4",
	"/assets/cb_erp/js/item_control.js?v=2",
	"/assets/cb_erp/js/batch_picker.js?v=4",
	"/assets/cb_erp/js/batch_entry.js?v=11",
]

# /desk 固定进入 MEP 工作台（避免落到空白的 /apps 应用选择页）
after_request = ["cb_erp.cb_erp.redirects.redirect_desk_home"]

# Desk 品牌（apps 首页 tile / 侧栏 logo）
app_logo_url = "/assets/cb_erp/images/cb-erp-logo.svg?v=2"

# Applications
# ------------------
# 在 /desk 应用选择页显示为独立 tile（工作台直连路由）
add_to_apps_screen = [
	{
		"name": "cb_erp",
		"logo": "/assets/cb_erp/images/cb-erp-logo.svg",
		"title": "巴西机电ERP系统测试",
		"route": "/app/巴西机电ERP系统测试",
	}
]

# 每次安装/同步应用时自动导回的配置（v16 不允许 DocType 入 fixtures：
# DocType 定义经 export_to_files 落为应用内 DocType/*.json 随 sync 同步）
fixtures = [
	{"dt": "Workspace", "filters": [["module", "=", "CB ERP"]]},
	{"dt": "Custom DocPerm",
	 "filters": [["parent", "in", ["Item", "Supplier", "Project", "Purchase Order",
	                              "Material Request", "Request for Quotation",
	                              "Supplier Quotation", "Quality Inspection", "Stock Entry"]]]},
	{"dt": "Alert Rule", "filters": [["rule_code", "in", ["ALR-001", "ALR-002", "CST-007"]]]},
]

# 列表多选批量操作：为常用可提交单据加载列表脚本（“批量提交”动作）
doctype_list_js = {
	"Material Request": "public/js/bulk_list.js",
	"Stock Entry": "public/js/bulk_list.js",
	"Material Budget": "public/js/bulk_list.js",
	"Material Commitment": "public/js/bulk_list.js",
	"Purchase Order": "public/js/bulk_list.js",
	"CB Import Case": "public/js/bulk_list.js",
	"CB Shipment": "public/js/bulk_list.js",
	"Design BOM": "public/js/bulk_list.js",
	"Design Change Request": "public/js/bulk_list.js",
}

# DocType Events
# ---------------

# include js, css files in header of web template
# web_include_css = "/assets/cb_erp/css/cb_erp.css"
# web_include_js = "/assets/cb_erp/js/cb_erp.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "cb_erp/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_kanban_js = {"doctype" : "public/js/doctype_kanban.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "cb_erp/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "cb_erp.utils.jinja_methods",
# 	"filters": "cb_erp.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "cb_erp.install.before_install"
# after_install = "cb_erp.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "cb_erp.uninstall.before_uninstall"
# after_uninstall = "cb_erp.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "cb_erp.utils.before_app_install"
# after_app_install = "cb_erp.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "cb_erp.utils.before_app_uninstall"
# after_app_uninstall = "cb_erp.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "cb_erp.build.after_build"

# To hook into the build process of other apps
# The list of apps being built is passed as an argument

# after_app_build = "cb_erp.build.after_app_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "cb_erp.notifications.get_notification_config"

# Awesome Bar
# -----------
# Extra search results: list of dicts with label, description, route, index.
# route: ["List", "ToDo"], "/desk/docs/some/page", or "https://example.com"
# awesomebar_search = ["cb_erp.search.awesomebar_results"]

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"cb_erp.tasks.all"
# 	],
# 	"daily": [
# 		"cb_erp.tasks.daily"
# 	],
# 	"hourly": [
# 		"cb_erp.tasks.hourly"
# 	],
# 	"weekly": [
# 		"cb_erp.tasks.weekly"
# 	],
# 	"monthly": [
# 		"cb_erp.tasks.monthly"
# 	],
# }

# DocType Events
# ---------------
# S5 / TP-CST-004：进口费用分摊（IMP-009）。CB Import Allocation 为 custom DocType，
# 控制逻辑统一经 doc_events 挂接（与全应用 custom DocType 形态一致）。
doc_events = {
	"CB Import Allocation": {
		"validate": "cb_erp.cb_erp.import_allocation.validate_allocation",
		"before_submit": "cb_erp.cb_erp.import_allocation.before_submit_allocation",
		"on_submit": "cb_erp.cb_erp.import_allocation.on_submit_allocation",
		"on_cancel": "cb_erp.cb_erp.import_allocation.on_cancel_allocation",
	},
	"Stock Entry": {
		"on_cancel": "cb_erp.cb_erp.import_allocation.on_se_cancel",
		"validate": "cb_erp.cb_erp.disc_validate.validate_doc",
		"before_submit": [
			"cb_erp.cb_erp.quota.validate_issue_quota",
			"cb_erp.cb_erp.quota.validate_receipt_project",
			"cb_erp.cb_erp.linkage.on_se_submit",
		],
	},
	"Alert Event": {
		"validate": "cb_erp.cb_erp.alerts.validate_alert_event",
	},
	"Project": {
		"validate": "cb_erp.cb_erp.disc_validate.project_validate",
	},
	"Material Request": {
		"validate": "cb_erp.cb_erp.disc_validate.validate_doc",
		"before_submit": "cb_erp.cb_erp.linkage.on_mr_submit",
	},
	"Purchase Order": {
		"validate": "cb_erp.cb_erp.disc_validate.validate_doc",
		"before_save": "cb_erp.cb_erp.quota.default_po_name",
		"before_submit": [
			"cb_erp.cb_erp.quota.validate_po_quota",
			"cb_erp.cb_erp.linkage.on_po_submit",
		],
	},
	"Stock Reconciliation": {
		"validate": "cb_erp.cb_erp.disc_validate.validate_doc",
	},
	"Material Budget": {
		"validate": "cb_erp.cb_erp.disc_validate.validate_doc",
	},
	"Material Commitment": {
		"validate": "cb_erp.cb_erp.disc_validate.validate_doc",
	},
	"Design BOM": {
		"validate": "cb_erp.cb_erp.disc_validate.validate_doc",
	},
	"CB Installation Record": {
		"validate": "cb_erp.cb_erp.linkage.on_install_validate",
	},
	"Design Change Request": {
		"validate": "cb_erp.cb_erp.disc_validate.validate_doc",
		"on_submit": "cb_erp.cb_erp.change_bom.on_submit_change",
	},
	"CB Shipment": {
		"validate": "cb_erp.cb_erp.disc_validate.validate_doc",
	},
	"CB Import Case": {
		"validate": "cb_erp.cb_erp.disc_validate.validate_doc",
	},
	"Purchase Receipt": {
		"validate": "cb_erp.cb_erp.disc_validate.validate_doc",
	},
	"Quality Inspection": {
		"validate": "cb_erp.cb_erp.disc_validate.validate_doc",
	},
}

# 预警引擎调度（TP-ALRBI-001）：每 15 分钟跑一次全部已启用的 Alert Rule。
scheduler_events = {
	"cron": {
		"*/15 * * * *": [
			"cb_erp.cb_erp.alerts.run_all_rules",
		],
	},
}

# After Migrate
# -------------
# 范围收敛（2026-11-04，项目管理导向）：每次迁移后重新隐藏销售/财务/生产等无关
# 标准 Workspace，并确保「CB 机电总控」工作台存在（防 migrate 重置/孤儿清理）。
after_migrate = "cb_erp.cb_erp.workspace_setup.after_migrate"

# Testing
# -------

# before_tests = "cb_erp.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "cb_erp.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "cb_erp.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "cb_erp.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["cb_erp.utils.before_request"]
# after_request = ["cb_erp.utils.after_request"]

# Job Events
# ----------
# before_job = ["cb_erp.utils.before_job"]
# after_job = ["cb_erp.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"cb_erp.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

