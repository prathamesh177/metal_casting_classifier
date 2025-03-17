# Copyright (c) 2025, prathamesh walvekar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AddMember(Document):
	def before_save(self):
		if self.password != self.confirm_password:
			frappe.throw("password not matching")

		doc = frappe.new_doc('User')
		doc.first_name= self.first_name
		doc.last_name=self.last_name
		doc.email=self.email   
		doc.mobile_no=self.mobile
		doc.company=self.company
		doc.new_password=self.password
		doc.role_profile_name=self.role
		# doc.module_profile="Team Member"
		doc.insert(ignore_permissions=True)
		doc.save()	

		k = frappe.new_doc('User Permission')
		k.user = self.email
		k.allow='Company'
		k.for_value=self.company
		k.apply_to_all_doctypes =1
		k.insert()
		k.save()
	
		frappe.set_value("User",self.email,"role_profile_name",self.role)
