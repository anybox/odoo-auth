##############################################################################
#
#    auth_oauth2 module for Odoo, OAuth2 Authentication module
#    Copyright (C) 2014-2015 Anybox (<https://anybox.fr>)
#
#    This file is a part of auth_oauth2
#
#    auth_oauth2 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    auth_oauth2 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'OAuth2 Authentication',
    'version': '8.0.0.1',
    'category': 'Tools',
    'description': """
        Allow users to sign up through OAuth2 Provider.

        Please, visit https://github.com/anybox/auth_oauth2 to get more
        informations.
    """,
    'author': 'Anybox',
    'website': 'http://anybox.fr',
    'license': 'AGPL-3',
    'support': 'support@anybox.fr',
    'depends': ['base', 'web', 'share'],
    'external_dependencies': {
        'python': ['oauth2client'],
    },
    'data': [
        'data/res_users_view.xml',
        'static/src/xml/auth_oauth2.xml',
        'views/auth_oauth2_view.xml',
    ],
    'demo': [
        'demo/res_users.xml',
    ],
    'js': [
        'static/src/js/auth_oauth2.js'
    ],
    'css': [],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
