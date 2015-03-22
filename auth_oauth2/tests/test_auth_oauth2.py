from anybox.testing.openerp import SharedSetupTransactionCase
from openerp.addons.auth_oauth2.controlers import main as controler
from openerp.tools import config


class Test_auth_oauth2(SharedSetupTransactionCase):

    @classmethod
    def initTestData(cls):
        super(Test_auth_oauth2, cls).initTestData()
        cls.oauth2 = controler.OAuth2Controller()
        cls.dbname = cls.cr.dbname
        cls.user_mdl = cls.registry('res.users')
        cls.user_demo_id = cls.ref('base.user_demo')

    def test_get_default_values(self):
        self.assertEquals(
            config.get('auth_oauth2.client_id', controler.DEFAULT_CLIENT_ID),
            self.oauth2.get_oauth2_client_id(None, None))
        self.assertEquals(
            config.get('auth_oauth2.client_secret', controler.DEFAULT_CLIENT_SECRET),
            self.oauth2.get_oauth2_client_secret(None, None))
        self.assertEquals(
            config.get('auth_oauth2.scope', controler.DEFAULT_SCOPE),
            self.oauth2.get_oauth2_scope(None, None))
        self.assertEquals(
            config.get('auth_oauth2.auth_uri', controler.DEFAULT_AUTH_URI),
            self.oauth2.get_oauth2_auth_uri(None, None))
        self.assertEquals(
            config.get('auth_oauth2.token_uri', controler.DEFAULT_TOKEN_URI),
            self.oauth2.get_oauth2_token_uri(None, None))
        self.assertEquals(
            config.get('auth_oauth2.revoke_uri', controler.DEFAULT_REVOKE_URI),
            self.oauth2.get_oauth2_revoke_uri(None, None))

    def test_validate_token(self):
        # User cancel authorization
        self.assertDictContainsSubset(
            {'error': 'Access Denied'},
            self.oauth2._validate_token(None, self.dbname, None, 'Access Denied')
        )
        # Unexpected error
        self.assertDictContainsSubset(
            {'error': 'Unexpected return from Oauth2 Provider'},
            self.oauth2._validate_token(None, self.dbname, None, None)
        )

        # save get_credentials method and mock it for test purposes
        original_get_credentials = self.oauth2.get_credentials

        def mock_get_credentials(request, db, code):
            return code

        self.oauth2.get_credentials = mock_get_credentials
        self.assertDictContainsSubset(
            {'login': u'demo',
             'token': u'credential password'},
            self.oauth2._validate_token(None, self.dbname,
                                        self.get_mock_code(u'demo@example.com',
                                                           u'credential password'),
                                        None)
        )

        self.assertDictContainsSubset(
            {'error': u"User email gracinet@anybox.fr not found in the current db"},
            self.oauth2._validate_token(None, self.dbname,
                                        self.get_mock_code(u'gracinet@anybox.fr',
                                                           u'credential password'),
                                        None)
        )

        # set get_credentials method back
        self.oauth2.get_credentials = original_get_credentials

    def get_mock_code(self, email, access_token):
        class cred:
            id_token = None
            access_token = None

            def __init__(self, email, access_token):
                self.id_token = {'email': email}
                self.access_token = access_token
        return cred(email, access_token)

    def test_retrieve_state(self):
        self.assertDictContainsSubset(
            {'debug': 1, 'db': 'ma base'},
            self.oauth2.retrieve_state(
                u'%7B%27debug%27%3A+1%2C+%27db%27%3A+%27ma+base%27%7D')
        )
