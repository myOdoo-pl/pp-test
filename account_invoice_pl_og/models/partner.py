# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    Module account_invoice_pl_og is copyrighted by
#    Grzegorz Grzelak of OpenGLOBE (www.openglobe.pl) and Cirrus (www.cirrus.pl)
#    with the same rules as OpenObject and OpenERP platform
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api

class res_partner(models.Model):
    _inherit = 'res.partner'

    company_partner_id = fields.Many2one('res.partner', compute='compute_company_partner')
    post = fields.Char('Post Office', size=64, help="If different than the City")
    bank_home_id = fields.Many2one('res.partner.bank', 'Bank Account For Customer', help='Bank account number to which customer pays you', domain="[('partner_id', '=', company_partner_id)]")

    def compute_company_partner(self):
        for partner in self:
            partner.company_partner_id = partner.company_id.partner_id


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
