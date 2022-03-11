from odoo import api, fields, models, _


class ModelDownloadPack(models.TransientModel):
    _inherit = 'ir.model.download_pack'

    def pack_get_file_path(self):
        """Set path for created package.

        :return: Parameter with file path.
        """
        param = 'ir.model.download_pack.file_path'
        ir_config = self.env['ir.config_parameter'].sudo()
        res = ir_config.get_param(param)

        if not res:
            # TODO: Change filepath when on sh.
            ir_config.set_param(param, '/home/odoo/pack_records/')
            res = ir_config.get_param(param)

        return res

    def pack_render_folder_structure(self, rec, file_path):
        return file_path
