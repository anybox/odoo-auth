import logging
import openerp.addons.web.http as openerpweb

from oauth2client.client import OAuth2WebServerFlow, FlowExchangeError
from oauth2client import GOOGLE_AUTH_URI
from oauth2client import GOOGLE_TOKEN_URI
from oauth2client import GOOGLE_REVOKE_URI

from openerp.modules.registry import RegistryManager
from openerp.addons.web.controllers.main import login_and_redirect
from openerp.addons.web.controllers.main import set_cookie_and_redirect
from openerp import SUPERUSER_ID
from openerp.tools import config

DEFAULT_DB_NAME = 'oauth2'
DEFAULT_CLIENT_ID = ''
DEFAULT_CLIENT_SECRET = ''
DEFAULT_SCOPE = 'email'
DEFAULT_AUTH_URI = GOOGLE_AUTH_URI
DEFAULT_TOKEN_URI = GOOGLE_TOKEN_URI
DEFAULT_REVOKE_URI = GOOGLE_REVOKE_URI

_logger = logging.getLogger(__name__)


class OAuth2Controller(openerpweb.Controller):

    _cp_path = '/auth_oauth2'

    def get_oauth2_client_id(self, request, db):
        return config.get('auth_oauth2.client_id', DEFAULT_CLIENT_ID)

    def get_oauth2_client_secret(self, request, db):
        return config.get('auth_oauth2.client_secret', DEFAULT_CLIENT_SECRET)

    def get_oauth2_scope(self, request, db):
        return config.get('auth_oauth2.scope', DEFAULT_SCOPE)

    def get_oauth2_redirect_uri(self, request, db):
        return 'http://localhost:8069/auth_oauth2/login'

    def get_oauth2_auth_uri(self, request, db):
        return config.get('auth_oauth2.auth_uri', DEFAULT_AUTH_URI)

    def get_oauth2_token_uri(self, request, db):
        return config.get('auth_oauth2.token_uri', DEFAULT_TOKEN_URI)

    def get_oauth2_revoke_uri(self, request, db):
        return config.get('auth_oauth2.revoke_uri', DEFAULT_REVOKE_URI)

    def get_oauth2_flow(self, request, db):
        return OAuth2WebServerFlow(
            client_id=self.get_oauth2_client_id(request, db),
            client_secret=self.get_oauth2_client_secret(request, db),
            scope=self.get_oauth2_scope(request, db),
            redirect_uri=self.get_oauth2_redirect_uri(request, db),
            auth_uri=self.get_oauth2_auth_uri(request, db),
            token_uri=self.get_oauth2_token_uri(request, db),
            revoke_uri=self.get_oauth2_revoke_uri(request, db)
            )

    @openerpweb.jsonrequest
    def get_oauth2_auth_url(self, request, db):
        flow = self.get_oauth2_flow(request, db)
        url = flow.step1_get_authorize_url()
        return {'value': url, 'session_id': request.session_id}

    def get_dbname(self, request):
        return getattr(request.session, 'dbname',
                       config.get('db_name', DEFAULT_DB_NAME))

    def get_credentials(self, request, db, code):
        flow = self.get_oauth2_flow(request, db)
        return flow.step2_exchange(code)

    @openerpweb.httprequest
    def login(self, request, code=None, error=None, *kward):
        dbname = self.get_dbname(request)
        result = self._validate_token(request, dbname, code, error)
        if not result or 'error' in result:
            # TODO: return nice error message to the brower
            return set_cookie_and_redirect(request, '/#action=login&loginerror=1')
        return login_and_redirect(request, dbname, result.get('login', False),
                                  result.get('token', False))

    def _validate_token(self, request, db, code, error):
        res = {}
        if error or not code:
            res['error'] = error if error else "Unexpected return from Oauth2 Provider"
            return res

        try:
            credentials = self.get_credentials(request, db, code)
            # Once we get credentials we could request api like that
            # notice that we could directly use credentials.authorize(http)
            # what we can see on the snipet bellow it's that we can re-create
            # the OAuth2Credentials (credentials/cred) from the access_token attribute
            # which we could save in db.
            #
            # (Pdb) from oauth2client.client import AccessTokenCredentials as ATC
            # (Pdb) cred = ATC(credentials.access_token, None)
            # (Pdb) import httplib2
            # (Pdb) http = httplib2.Http()
            # (Pdb) http = cred.authorize(http)
            # (resp_headers, content) = http.request(
            #     "https://www.googleapis.com/plus/v1/people/me", "GET")
        except FlowExchangeError as err:
            res['error'] = u"%r" % err
            return res

        registry = RegistryManager.get(db)
        email = credentials.id_token.get('email', False)
        token = credentials.access_token
        with registry.cursor() as cr:
            user_mdl = registry.get('res.users')
            user_ids = user_mdl.search(cr, SUPERUSER_ID, [('email', 'ilike', email)])
            if not user_ids:
                res['error'] = u"User email %s not find in the current db" % email
                return res
            user = user_mdl.read(cr, SUPERUSER_ID, user_ids[0], ['login'])
            user_mdl.write(cr, SUPERUSER_ID, user_ids[0], {'password': token})
            res['login'] = user.get('login', False)
        res['token'] = token
        return res
