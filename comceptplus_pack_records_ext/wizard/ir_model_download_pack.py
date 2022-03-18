from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo import os
import base64
import datetime
import logging
import shutil
import zipfile
from os.path import exists

_logger = logging.getLogger(__name__)


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

    def pack_act_getfile(self):
        Attachment = self.env['ir.attachment']

        file_path = self.pack_create_file_path()
        file_path = self.sanitize_path(file_path)
        if file_path:
            msg = []
            counter = 0
            for rec in self.pack_find_candidates():
                # Process the structure
                rec_folder = self.pack_render_folder_structure(rec, file_path)

                _logger.info("This folder is %s" % rec_folder)

                # Create a folder
                try:
                    self.create_folder(rec_folder)
                except Exception as e:
                    msg.append(_(e))
                    _logger.error("Folder creation %s" % e)
                    pass

                # Copy attachments
                if os.path.isdir(rec_folder):
                    for att in Attachment.search([
                                                ('res_model','=',self._context['active_model']),
                                                ('res_id','=',rec.id)
                                                ]):
                        try:
                            if att.db_datas:
                                f = open(rec_folder + '/' + att.name, 'wb')
                                f.write(Attachment._file_read(att.db_datas))
                                f.close()

                            else:
                                f_path = os.path.join(rec_folder, att.name)

                                # If file with the same name exists, add number to file path
                                if not exists(f_path):
                                    shutil.copy(Attachment._full_path(att.store_fname), f_path)
                                else:
                                    name_parts = att.name.split('.')
                                    i = 1
                                    while i < 10:
                                        new_file_name = name_parts[0] + "(" + str(i) + ")." + name_parts[1]
                                        new_f_path = os.path.join(rec_folder, new_file_name)
                                        if not exists(new_f_path):
                                            shutil.copy(Attachment._full_path(att.store_fname), new_f_path)
                                            break
                                        i += 1

                        except Exception as e2:
                            msg.append(_(e2))
                            _logger.error("File copy: %s" % e2)
                            pass

                counter += 1
                msg.append(_('%s files processed') % counter)

            # Create the zip file
            zip_created = False
            if counter:
                try:
                    zip_file = file_path.split(os.path.sep)[-1] + '.zip'
                    _logger.info("ZIP FILE NAME: %s" % zip_file)

                    zip_file_path = os.path.join(self.pack_get_file_path(), zip_file)
                    zipf = zipfile.ZipFile(zip_file_path, 'w')
                    _logger.info("zip_file_path: %s" % zip_file_path)

                    #aqui está o problema - qual a pasta onde deve de começar o zip?
                    self.zipdir(file_path, zipf)
                    zipf.close()
                    zip_created = True
                    _logger.info("ZIP file (%s) was created in %s" % (zip_file, zip_file_path))
                except Exception as e:
                    _logger.error("ZIP creation: %s" % e)
                    msg.append(_(e))
                    pass

            # Create an attachment for the zipped file
            if zip_created:
                try:
                    af = open(zip_file_path, 'rb')
                    datas = base64.encodestring(af.read())
                    af.close()
                    att = Attachment.sudo().create({
                                                    'name': zip_file,
                                                    'type': 'binary',
                                                    'datas': datas,
                                                    'store_fname': zip_file,
                                                    })

                    # Create a task to delete the zip file (1 hour after this)
                    cron_name = 'Delete useless zip file (%s)' % att.id
                    model_id = self.env['ir.model'].sudo().search([
                                                ('model','=',self._name)
                                                ])
                    self.env['ir.cron'].sudo().create({
                                                    'name': cron_name,
                                                    'model_id': model_id.id,
                                                    'state': 'code',
                                                    'code': 'model.pack_delete_useless_zip(%s)' % att.id,
                                                    'interval_number': 3,
                                                    'interval_type': 'minutes',
                                                    'nextcall': datetime.datetime.now() \
                                                                + datetime.timedelta(minutes = 30),
                                                    'numbercall': 1,
                                                    'doall': True
                                                    })
                except Exception as e:
                    _logger.error("ZIP attachment: %s" % e)
                    msg.append(_(e))
                    pass

            # Delete the source files
            try:
                shutil.rmtree(file_path)
            except Exception as e:
                _logger.info("Source files deletion: %s" % e)
                _logger.info(file_path)
                msg.append(_(e))
                pass

            if zip_created:
                return self.pack_redirect(att.id)
            else:
                _logger.error(_('A ZIP file was not created:\n%s') % '\n'.join(msg))
                raise ValidationError(_('A ZIP file was not created:\n%s') % '\n'.join(msg))
