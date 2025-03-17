// Copyright (c) 2025, prathamesh walvekar and contributors
// For license information, please see license.txt

frappe.ui.form.on("Add Member", {
	setup: function(frm) {
		frm.set_query("role", function(doc) {
			return {
				filters: [
				    ['Role Profile', 'name', 'in', ["Visitor Administrator","web user"]],
				]
			};
		});
	},
    validate: function(frm) {
    
        var email = frm.doc.email;

        var EmailPatttern = /^[\w\.-]+@[\w\.-]+\.\w+$/

        if (!EmailPatttern.test(email)){
            frappe.throw('Please enter a valid Email.');
            frappe.validated = false; // Prevent form submission
        }

        var mobile = frm.doc.mobile;

        var indianMobilePattern = /^[6789]\d{9}$/

        if (!indianMobilePattern.test(mobile)) {
            frappe.throw('Please enter a valid Indian mobile number.');
            frappe.validated = false; // Prevent form submission
        }
    }
});
