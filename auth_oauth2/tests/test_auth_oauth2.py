from anybox.testing.openerp import SharedSetupTransactionCase
from openerp.addons.auth_oauth2.controlers import main as controler
from openerp.tools import config


class Test_auth_oauth2(SharedSetupTransactionCase):

    @classmethod
    def initTestData(cls):
        super(Test_auth_oauth2, cls).initTestData()
        cls.oauth2 = controler.OAuth2Controller()

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
