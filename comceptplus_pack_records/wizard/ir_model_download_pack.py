# -*- coding: utf-8 -*-
import logging
import base64
import uuid
import shutil
import zipfile
import datetime
import stat

from odoo import api, fields, models, _
from odoo.exceptions import Warning, ValidationError
from odoo import os
from odoo.tools import config

_logger = logging.getLogger(__name__)


class ModelDownloadPack(models.TransientModel):
    _name = 'ir.model.download_pack'
    _description = 'Wizard to download a pack of records'

    name = fields.Char('File Name', readonly=True)

    #os.makedirs was not working?
    # recheck the thing about unmasking
    def create_folder(self, path):
        _logger.info("****** create_folder ******")
        if path:
            _logger.info(path)
            path = self.sanitize_path(path)

            if not os.path.isdir(path):
                try:
                    os.makedirs(path, exist_ok=True)
                except Exception as e:
                    _logger.info("ERROR: %s" % e)

    def zipdir(self, path, zip):
        _logger.info("ZIP %s FROM %s" % (zip,path))
        for root, dirs, files in os.walk(path):
            for file in files:
                aux = os.path.join(root, file)
                if aux != zip.filename:
                    zip.write(aux, os.path.relpath(aux, path))
        return True

    def sanitize_folder(self, folder=''):
        return ''.join(e for e in str(folder) if e.isalnum())

    def sanitize_path(self, path=''):
        return path.replace('//','/').replace('\\\\','\\')


    def pack_get_file_path(self):
        param = 'ir.model.download_pack.file_path'
        IRConfig = self.env['ir.config_parameter'].sudo()
        res = IRConfig.get_param(param)
        if not res:
            IRConfig.set_param(param, '/odoo/pack_records/')
            res = IRConfig.get_param(param)
        return res

    def pack_create_file_path(self, create=True):
        file_path = self.pack_get_file_path()
        if create:
            file_path += '/' + uuid.uuid4().hex
            if not os.path.isdir(file_path):
                try:
                    self.create_folder(file_path)
                    _logger.info("Resultado: %s" % os.path.isdir(file_path))
                except Exception as e:
                    _logger.error("Path creation: %s" % e)
                    file_path = ''
                    raise ValidationError(_(e))
        return file_path

    def pack_format_date(self, date, format=False):
        res = date
        if not format:
            format = '%Y%m%d'

        date = date.strftime('%Y-%m-%d')
        if len(date) == 10:
            date += ' 00:00:00.000'
        try:
            res = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f').strftime(format)
        except Exception as e1:
            _logger.error("Format date: %s" % e1)
            try:
                res = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime(format)
            except Exception as e2:
                _logger.error("Format date: %s" % e2)
                res = 'date'
                pass
        return res

    def pack_delete_useless_zip(self, att_id):
        if att_id:
            Attachment = self.env['ir.attachment'].sudo()
            att = Attachment.browse(att_id)
            if att:
                att_name = att.name
                try:
                    att.unlink()
                except Exception as e:
                    _logger.error("Delete zip attachment: %s" % e)
                    pass
                try:
                    file_path = self.pack_create_file_path(create=False)
                    os.remove(os.path.join(file_path, att_name))
                except Exception as e:
                    _logger.error("Delete useless ZIP file: %s" % e)
                    pass


    def pack_redirect(self, att_id=''):
        if att_id:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            action = {
                    'type' : 'ir.actions.act_url',
                    'url': base_url + '/web/content/%s' % (att_id),
                    'target': 'self'
                    }
            return action

    def pack_find_candidates(self):
        try:
            res = self.env[self._context.get('active_model')].search([
                                    ('id','in',self._context.get('active_ids'))
                                    ])
        except Exception as e:
            _logger.error("Find candidates: %s" % e)
            res = False
        return res

    def pack_render_folder_structure(self, rec, file_path):
        folder_structure = self._context.get('pack_folder_structure')
        if not folder_structure:
            folder_structure = ['create_date|%Y','create_date|%m','create_date|%d','id']
        else:
            folder_structure = folder_structure.split(',')

        aux_structure = []
        for f in folder_structure:
            try:
                #Date parts
                if '|' in f:
                    try:
                        aux_param = f.split('|')
                        aux_date = eval('rec.' + aux_param[0])
                        aux = self.pack_format_date(aux_date, aux_param[1])
                    except Exception as e2:
                        aux = aux_param[0]
                        _logger.error("Date parts: %s" % e2)
                        pass
                #Other fields
                else:
                    aux = eval('rec.' + f) or f
                aux_structure.append(self.sanitize_folder(aux))
            except Exception as e:
                aux_structure.append(f)
                _logger.error("Field: %s" % e)

        return file_path + os.path.sep + (os.path.sep).join(aux_structure)



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
                                shutil.copy(
                                            Attachment._full_path(att.store_fname),
                                            os.path.join(rec_folder, att.name)
                                            )
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


    def _get_comment(self):
        rec_ids = self.pack_find_candidates()
        if rec_ids:
            files = self.env['ir.attachment'].search([
                                                ('res_model','=',self._context['active_model']),
                                                ('res_id','in',[x.id for x in rec_ids])
                                                ])
            unique = []
            for f in files:
                if f.res_id not in unique:
                    unique.append(f.res_id)
            return _("You are about to pack %s records and %s files\
                        \n(records with no attachments are ignored)") \
                                % (len(unique), len(files))
        else:
            _logger.info("No records found")
            return _("No records found")

    comment = fields.Text('Comment', default=_get_comment)
