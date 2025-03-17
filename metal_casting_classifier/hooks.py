from castingap import api


app_name = "metal_casting_classifier"
app_title = "metal_casting_classifier"
app_publisher = "prathamesh walvekar"
app_description = "metal_casting_classifier"
app_email = "walvekarprat@gamil.com"
app_license = "mit"


api.include = [
    "casting_classification.api.upload_image",
    "casting_classification.api.get_images",
    "casting_classification.api.train_model",
    "casting_classification.api.predict"
]

cors = ["http://localhost:5173"]

def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

def apply_cors_middleware(app):
    @app.after_request
    def handle_cors(response):
        return add_cors_headers(response)

hooks = {
    "after_request": [apply_cors_middleware],  # Apply the CORS middleware globally
}



# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "metal_casting_classifier",
# 		"logo": "/assets/metal_casting_classifier/logo.png",
# 		"title": "metal_casting_classifier",
# 		"route": "/metal_casting_classifier",
# 		"has_permission": "metal_casting_classifier.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/metal_casting_classifier/css/metal_casting_classifier.css"
# app_include_js = "/assets/metal_casting_classifier/js/metal_casting_classifier.js"

# include js, css files in header of web template
# web_include_css = "/assets/metal_casting_classifier/css/metal_casting_classifier.css"
# web_include_js = "/assets/metal_casting_classifier/js/metal_casting_classifier.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "metal_casting_classifier/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "metal_casting_classifier/public/icons.svg"

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

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "metal_casting_classifier.utils.jinja_methods",
# 	"filters": "metal_casting_classifier.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "metal_casting_classifier.install.before_install"
# after_install = "metal_casting_classifier.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "metal_casting_classifier.uninstall.before_uninstall"
# after_uninstall = "metal_casting_classifier.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "metal_casting_classifier.utils.before_app_install"
# after_app_install = "metal_casting_classifier.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "metal_casting_classifier.utils.before_app_uninstall"
# after_app_uninstall = "metal_casting_classifier.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "metal_casting_classifier.notifications.get_notification_config"

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

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
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
# 		"metal_casting_classifier.tasks.all"
# 	],
# 	"daily": [
# 		"metal_casting_classifier.tasks.daily"
# 	],
# 	"hourly": [
# 		"metal_casting_classifier.tasks.hourly"
# 	],
# 	"weekly": [
# 		"metal_casting_classifier.tasks.weekly"
# 	],
# 	"monthly": [
# 		"metal_casting_classifier.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "metal_casting_classifier.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "metal_casting_classifier.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "metal_casting_classifier.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["metal_casting_classifier.utils.before_request"]
# after_request = ["metal_casting_classifier.utils.after_request"]

# Job Events
# ----------
# before_job = ["metal_casting_classifier.utils.before_job"]
# after_job = ["metal_casting_classifier.utils.after_job"]

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
# 	"metal_casting_classifier.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

