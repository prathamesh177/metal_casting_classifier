// Copyright (c) 2025, prathamesh walvekar and contributors
// For license information, please see license.txt

frappe.ui.form.on("companyreg", {
    validate: function(frm) {    
        var email = frm.doc.email;
        var emailPattern = /^[\w\.-]+@[\w\.-]+\.\w+$/;

        if (!emailPattern.test(email)){
            frappe.msgprint('Please enter a valid Email.');
            frappe.validated = false; // Prevent form submission
        } 

        var mobile = frm.doc.mobile;
        var indianMobilePattern = /^[6789]\d{9}$/;

        if (!indianMobilePattern.test(mobile)) {
            frappe.msgprint('Please enter a valid Indian mobile number.');
            frappe.validated = false; // Prevent form submission
        }     

        if (frm.doc.select_one === 'GST') {
            var gst = frm.doc.gst;
            var gstPattern = /^\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d{1}[Z]{1}[A-Z\d]{1}$/;

            if (!gstPattern.test(gst)){
                frappe.msgprint('Please enter a valid GST.');
                frappe.validated = false; // Prevent form submission
            }
        }

        if (frm.doc.select_one === 'PAN' ) {
            var pan = frm.doc.pan;
            var panPattern = /^[A-Z]{5}[0-9]{4}[A-Z]$/;

            if (!panPattern.test(pan)){
                frappe.msgprint('Please enter a valid PAN.');
                frappe.validated = false; // Prevent form submission
            }
        }
    }
});
