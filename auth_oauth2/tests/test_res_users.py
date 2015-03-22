from anybox.testing.openerp import SharedSetupTransactionCase
from psycopg2 import IntegrityError


class test_res_users(SharedSetupTransactionCase):

    @classmethod
    def initTestData(cls):
        super(test_res_users, cls).initTestData()
        cls.user_mdl = cls.registry('res.users')
        cls.user_demo_id = cls.ref('base.user_demo')
        partner_mdl = cls.registry('res.partner')
        partner_id = partner_mdl.create(cls.cr, cls.uid,
                                        {'name': u"Pierre Verkest",
                                         'company_ids': cls.ref("base.main_company"),
                                         'email': u"petrus-v@hotmail.fr"})
        cls.user_id = cls.user_mdl.create(cls.cr, cls.uid,
                                          {'partner_id': partner_id,
                                           'login': 'pverkest',
                                           'passwd': '1234',
                                           'oauth_email': u"pverkest@anybox.fr",
                                           'company_id': cls.ref("base.main_company"),
                                           'group_ids': [(6, 0,
                                                          [cls.ref('base.group_user'),
                                                           cls.ref('base.group_partner_manager')])],
                                           })

    def test_uniq_email(self):
        vals = {
            'oauth_email': u"pverkest@anybox.fr"
        }
        self.assertRaises(IntegrityError,
                          self.user_mdl.write, self.cr, self.uid,
                          [self.user_demo_id], vals)

    def test_get_user_id_by_email(self):
        self.assertEquals(self.user_id,
                          self.user_mdl.get_user_id_by_email(self.cr, self.uid,
                                                             u"pverkest@anybox.fr"))

        self.assertFalse(self.user_mdl.get_user_id_by_email(self.cr, self.uid,
                                                            u"petrus-v@hotmail.fr"))
