# Copyright (c) 2025, prathamesh walvekar and contributors
# For license information, please see license.txt

# import frappe
import frappe
import re
from frappe.model.document import Document

class companyreg(Document):
	def before_save(self):
		email = self.email
		email_pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

		if not email_pattern.match(email):
			frappe.throw('Please enter a valid Email.....')

		mobile = self.mobile
		mobile_pattern = re.compile(r'^[6789]\d{9}$')

		if not mobile_pattern.match(mobile):
			frappe.throw('Please enter a valid Indian mobile number.')

		if self.select_one == 'GST':
			self.pan=None
			gst = self.gst
			gst_pattern = re.compile(r'^\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d{1}[Z]{1}[A-Z\d]{1}$')
			if not gst_pattern.match(gst):
				frappe.throw('Please enter a valid GST......')

		if self.select_one == 'PAN':
			self.gst=None
			pan = self.pan
			pan_pattern = re.compile(r'^[A-Z]{5}[0-9]{4}[A-Z]$')

			if not pan_pattern.match(pan):
				frappe.throw('Please enter a valid PAN.......')

	
		if self.password != self.confirm_password:
			frappe.throw("password not matching")

	
		
        # Check for duplicate company


		if self.mobile:
			if frappe.get_all('companyreg', filters={'mobile': self.mobile}):
				frappe.throw('Mobile Number already exists.')

		if self.company_name:
			if frappe.get_all('companyreg', filters={'company_name': self.company_name}):
				frappe.throw('Company already exists.')

		# Check for duplicate GST
		if self.gst:
			if frappe.get_all('companyreg', filters={'gst': self.gst}):
				frappe.throw('GST already exists.')

		# Check for duplicate PAN
		if self.pan:
			if frappe.get_all('companyreg', filters={'pan': self.pan}):
				frappe.throw('PAN already exists.')

		

		doc1 = frappe.new_doc('Company')
		doc1.company_name=self.company_name
		doc1.default_currency=self.currency
		doc1.country=self.country
		doc1.insert(ignore_permissions=True)
		self.doc_company=doc1.name
		self.company_name=self.company_name
  
		doc1.save()
	# frappe.throw(str(self.company_name))
		doc = frappe.new_doc('User')
		doc.first_name= self.first_name
		doc.last_name=self.last_name
		doc.email=self.email
		doc.mobile_no=self.mobile
		doc.company_name=self.company_name
		doc.new_password=self.password
		doc.role_profile_name="Admin"
		# doc.module_profile="Visitor Admin"
		doc.insert(ignore_permissions=True)
		self.doc_user=doc.name
		doc.save()
		
  

		k = frappe.new_doc('User Permission')
		k.user = self.email
		k.allow='Company'
		k.for_value=self.company_name
		k.apply_to_all_doctypes =1
		k.insert(ignore_permissions=True)
		self.doc_user_permission=k.name
		k.save()

		
	def on_trash(self):
		self.delete_company_name_field_from_user_permission()
		self.delete_company_document()
		self.delete_company_name_field_from_user()
	
	def delete_company_name_field_from_user_permission(self):
		frappe.delete_doc("User Permission",self.doc_user_permission,force=True)

	def delete_company_document(self):
		frappe.delete_doc("Company", self.doc_company,force=True)

	def delete_company_name_field_from_user(self):
		frappe.delete_doc("User",self.doc_user,force=True)

									