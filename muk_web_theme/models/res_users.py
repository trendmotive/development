###################################################################################
#
#    Copyright (c) 2017-today MuK IT GmbH.
#
<<<<<<< HEAD
#    This file is part of MuK Theme
#    (see https://mukit.at).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
=======
#    This file is part of MuK Backend Theme
#    (see https://mukit.at).
#
#    License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
>>>>>>> 2a75c67 ([FEATURE] add the themes modules)
#
###################################################################################

from odoo import models, fields, api


class ResUsers(models.Model):
    
    _inherit = 'res.users'
    
    #----------------------------------------------------------
<<<<<<< HEAD
    # Defaults
    #----------------------------------------------------------
    
    @api.model
    def _default_sidebar_type(self):
        return self.env.user.company_id.default_sidebar_preference or 'large'
    
    @api.model
    def _default_chatter_position(self):
        return self.env.user.company_id.default_chatter_preference or 'sided'
    
    #----------------------------------------------------------
    # Database
=======
    # Properties
    #----------------------------------------------------------
    
    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + [
            'sidebar_type',
        ]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + [
            'sidebar_type',
        ]

    #----------------------------------------------------------
    # Fields
>>>>>>> 2a75c67 ([FEATURE] add the themes modules)
    #----------------------------------------------------------
    
    sidebar_type = fields.Selection(
        selection=[
            ('invisible', 'Invisible'),
            ('small', 'Small'),
            ('large', 'Large')
        ], 
<<<<<<< HEAD
        required=True,
        string="Sidebar Type",
        default=lambda self: self._default_sidebar_type()
    )
    
    chatter_position = fields.Selection(
        selection=[
            ('normal', 'Normal'),
            ('sided', 'Sided'),
        ], 
        required=True,
        string="Chatter Position", 
        default=lambda self: self._default_chatter_position()
    )
    
    #----------------------------------------------------------
    # Setup
    #----------------------------------------------------------

    def __init__(self, pool, cr):
        init_res = super(ResUsers, self).__init__(pool, cr)
        theme_fields = ['sidebar_type', 'chatter_position']
        readable_fields = list(self.SELF_READABLE_FIELDS)
        writeable_fields = list(self.SELF_WRITEABLE_FIELDS)
        readable_fields.extend(theme_fields)
        writeable_fields.extend(theme_fields)
        type(self).SELF_READABLE_FIELDS = readable_fields
        type(self).SELF_WRITEABLE_FIELDS = writeable_fields
        return init_res
=======
        string="Sidebar Type",
        default='large',
        required=True,
    )
>>>>>>> 2a75c67 ([FEATURE] add the themes modules)
