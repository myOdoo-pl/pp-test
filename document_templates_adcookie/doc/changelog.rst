v3.8.1
======
* Updated account move form view.

v3.8
====
* Changed Sale Date on print from invoice_sale_date to date.
* Changed invoice_sale_date field to invisible on invoice page.
* Changed translation of Accounting Date.

v3.7.4
======
* Change "To Pay" to "To Pay(gross)" on correction template
* Updated transtaltion

v3.7.3
======
* Change "To Refund" to "To Pay" on correction template
* Updated transtaltion

v3.7.2
======
* Fix line_tax_summing (Removed spliting name)
* Fix correction_line_tax_summing (Added missing taxed_value to values)

v3.7.1
======
* Updated translation.

v3.7
====
* Fixed template overwrite.
* Updated translation.

v3.6
====
* Added invoice duplicate.
* Updated translation.

v3.5
====
* Separate table for taxes and summary in invoices.
* Updated translation.

v3.4
====
* Printing extended information about tax positions in summary table for every invoice document.
* Updated translation.

v3.3
====
* Modified invoice view for adding sale date.
* Moved origin SO field to downpayment_modification module.

v3.2
====
* Order Date field in sale.order model is no longer set to readonly.

v3.12
=====
* Made field date visible in every state and readonly if invoice was or is posted
* Added field date to the printout of the invoice
* Updated translations

v3.11
=====
* Unlink SO sale date from invoice_report_template.xml
* Add field invoice_sale_date in account_move
* Replace sale date in invoice_report_template.xml with invoice_sale_date

v3.10
=====
* Modify self.correction_ref and self.correction_reason in account_move.py
* Modify object reference to 'doc' from 'o' in sale_report_template.xml

v3.9
====
* Add reason to refund.
* Add fields correction_ref, correction_reason to account_move (original field ref separated to reference and reason).
* Add field main_so_id to account_move.
* Updated translation.
* Changed widget='date' to t-options="{'widget': 'date'}".

v3.8
====
* Add field Sale Date to invoice_report_template

v3.7
====
* Modified XML markup to translate Client and Seller fields

v3.6
====
* Change open tag to posted in invoice_report_template

v3.5
====
* Change color motive from #875A7B to #f37224

v3.4
====
* Updated translation.

v3.3
====
* Refactoring invoice correction document.

v3.2
====
* Refactoring sale document.

v3.1
====
* Refactored fields to match Odoo 14 version (removed dates conversion methods).
* Refactored main invoice document.

v3.0
====
* Refactored to Odoo 14.

v2.5.1
======
* Updated translations.

v2.5
====
* Added duplicates support.

v2.4
====
* Updated translations.e

v2.3
====
* Remove hours from templates in sales.

v2.2.2
======
* Small aesthetic changes in code.

v2.2.1
======
* Small update for proper string on template based on refund type.

v2.2
====
* Updated translations.

v2.1.1
======
* Section support in invoices.

v2.1
====
* Section support in sales.

v2.0
====
* New templates after OpenGlobe module updates.

v1.0
====
* Added translations. - full release.

v0.9.2_beta
===========
* Final fixes before v1.0.

v0.9.1_beta
===========
* "Your bank account" field added.

v0.9_beta
=========
* Fixed alpha issues. Release beta version.

v0.8_alpha
==========
* Last corrections and release alpha version.

v0.7
====
* Transfer previous changes to other supported documents.

v0.6
====
* Edited additional template for invoice summary.

v0.5
====
* Changed element sizes.

v0.4
====
* Changed font colors.

v0.3
====
* First conversion from standard template to background.

v0.2
====
* Added content from base template.

v0.1
====
* Module creation.
