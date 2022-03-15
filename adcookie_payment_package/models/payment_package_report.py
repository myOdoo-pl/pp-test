from openerp import api, models
import sys
import importlib


class PaymentPackageReport(models.AbstractModel):
    _name = 'report.adcookie_payment_package.payment_package_report'

    # def render_html(self, data=None):
    #     report_obj = self.env['report']
    #
    #     report = report_obj._get_report_from_name('adcookie_payment_package.payment_package_report')
    #
    #     docargs = {
    #         'doc_ids': self._ids,
    #         'doc_model': report.model,
    #         'docs': self,
    #         'set_windows_coding': self._set_windows_coding,
    #         'set_default_coding': self._set_default_coding
    #     }
    #
    #     return report_obj.render('adcookie_payment_package.payment_package_report', docargs)

    def _get_report_values(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('adcookie_payment_package.payment_package_report')

        return {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'set_windows_coding': self._set_windows_coding,
            'set_default_coding': self._set_default_coding
        }

    def _set_windows_coding(self):
        importlib.reload(sys)
        sys.setdefaultencoding('cp1250')

    def _set_default_coding(self):
        importlib.reload(sys)
        sys.setdefaultencoding('utf-8')
