from openerp.osv import osv, fields
from openerp.tools.translate import _


class res_users(osv.Model):
    _inherit = 'res.users'

    _columns = {
        'oauth_email': fields.char(u"Oauth2 email",
                                   size=64,
                                   help=u"Oauth2 email used to connect to odoo"),
    }

    def get_user_id_by_email(self, cr, uid, email, context=None):
        if not context:
            context = {}
        res = self.search(cr, uid, [('oauth_email', 'ilike', email)], context=context)
        if len(res) == 0:
            return False
        return res[0]

    _sql_constraints = [
        ('oauth_email_uniq', 'unique(oauth_email)',
         _(u"User email must be unique. "
           u"You can't have two users with the same email address.")),
    ]
