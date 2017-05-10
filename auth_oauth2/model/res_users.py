from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
import openerp.exceptions


class res_users(osv.Model):
    _inherit = 'res.users'

    _columns = {
        'oauth_email': fields.char(
            u"Oauth2 email", size=64, help=u"Oauth2 email only used to connect to Odoo"
        ),
        'oauth_token': fields.char(u"Oauth2 token"),
        'oauth_id_token': fields.char(u"Oauth2 id_token"),
    }

    def check_credentials(self, cr, uid, password):
        """ Override this method to plug additional authentication methods"""
        try:
            res = super(res_users, self).check_credentials(cr, uid, password)
        except:
            res = self.search(
                cr, SUPERUSER_ID, [('id', '=', uid), ('oauth_token', '=', password)]
            )
            if not res:
                raise openerp.exceptions.AccessDenied()
        return

    def get_user_id_by_email(self, cr, uid, email, context=None):
        if not context:
            context = {}
        res = self.search(cr, uid, [('oauth_email', '=', email)], context=context)
        if len(res) == 0:
            return False
        return res[0]

    _sql_constraints = [
        ('oauth_email_uniq', 'unique(oauth_email)',
         _(u"User email must be unique. "
           u"You can't have two users with the same email address.")),
    ]
