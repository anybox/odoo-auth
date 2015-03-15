from openerp.osv import osv
from openerp.tools.translate import _


class res_users(osv.Model):
    _inherit = 'res.users'

    def get_user_id_by_email(self, cr, uid, email, context=None):
        if not context:
            context = {}
        res = self.search(cr, uid, [('email', 'ilike', email)], context=context)
        if len(res) == 0:
            return False
        return res[0]


class res_partner(osv.Model):
    _inherit = 'res.partner'

    _sql_constraints = [
        ('name_uniq', 'unique(email)', _(u"Email must be unique as long it's "
                                         u"for connexion")),
    ]
