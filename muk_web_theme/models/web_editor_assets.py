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

import re
import uuid
import base64

from odoo import models, fields, api
from odoo.modules import module


class ScssEditor(models.AbstractModel):
    
    _inherit = 'web_editor.assets'

    # ----------------------------------------------------------
    # Helper
    # ----------------------------------------------------------

<<<<<<< HEAD
    def _get_variable(self, content, variable):
=======
    def _get_theme_variable(self, content, variable):
>>>>>>> 2a75c67 ([FEATURE] add the themes modules)
        regex = r'{0}\:?\s(.*?);'.format(variable)
        value = re.search(regex, content)
        return value and value.group(1)

<<<<<<< HEAD
    def _get_variables(self, content, variables):
        return {var: self._get_variable(content, var) for var in variables}

    def _replace_variables(self, content, variables):
=======
    def _get_theme_variables(self, content, variables):
        return {var: self._get_theme_variable(content, var) for var in variables}

    def _replace_theme_variables(self, content, variables):
>>>>>>> 2a75c67 ([FEATURE] add the themes modules)
        for variable in variables:
            variable_content = '{0}: {1};'.format(
                variable['name'],
                variable['value']
            )
            regex = r'{0}\:?\s(.*?);'.format(variable['name'])
            content = re.sub(regex, variable_content, content)
        return content

    # ----------------------------------------------------------
    # Functions
    # ----------------------------------------------------------

<<<<<<< HEAD
    def get_variables_values(self, url, bundle, variables):
        custom_url = self.make_custom_asset_file_url(url, bundle)
        content = self.get_asset_content(custom_url)
        if not content:
            content = self.get_asset_content(url)
        return self._get_variables(content.decode('utf-8'), variables)
    
    def replace_variables_values(self, url, bundle, variables):
        original = self.get_asset_content(url).decode('utf-8')
        content = self._replace_variables(original, variables)
        self.save_asset(url, bundle, content, 'scss')
=======
    def get_theme_variables_values(self, url, bundle, variables):
        custom_url = self._make_custom_asset_url(url, bundle)
        content = self._get_content_from_url(custom_url)
        if not content:
            content = self._get_content_from_url(url)
        return self._get_theme_variables(content.decode('utf-8'), variables)
    
    def replace_theme_variables_values(self, url, bundle, variables):
        original = self._get_content_from_url(url).decode('utf-8')
        content = self._replace_theme_variables(original, variables)
        self.with_context(theme_variables=True).save_asset(
            url, bundle, content, 'scss'
        )
>>>>>>> 2a75c67 ([FEATURE] add the themes modules)
