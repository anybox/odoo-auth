import functools
import logging
import ast
import urllib
import openerp.addons.web.http as openerpweb
import httplib2
import simplejson
import urlparse
import werkzeug.utils


from oauth2client.client import OAuth2WebServerFlow, FlowExchangeError
from oauth2client import GOOGLE_AUTH_URI
from oauth2client import GOOGLE_TOKEN_URI
from oauth2client import GOOGLE_REVOKE_URI

from openerp.addons.web.controllers.main import db_monodb, ensure_db, set_cookie_and_redirect, login_and_redirect
from openerp.addons.auth_signup.controllers.main import AuthSignupHome as Home
from openerp import http
from openerp.http import request
from openerp.modules.registry import RegistryManager
from openerp.addons.web.controllers.main import login_and_redirect
from openerp import SUPERUSER_ID
from openerp.tools import config
from openerp.tools.translate import _

DEFAULT_CLIENT_ID = ''
DEFAULT_CLIENT_SECRET = ''
DEFAULT_SCOPE = 'email'
DEFAULT_AUTH_URI = GOOGLE_AUTH_URI
DEFAULT_TOKEN_URI = GOOGLE_TOKEN_URI
DEFAULT_REVOKE_URI = GOOGLE_REVOKE_URI
DEFAULT_DATA_ENDPOINT = ''


CONTROLER_PATH = '/auth_oauth2'
LOGIN_METHOD = 'login'

_logger = logging.getLogger(__name__)


#----------------------------------------------------------
# helpers
#----------------------------------------------------------
def fragment_to_query_string(func):
    @functools.wraps(func)
    def wrapper(self, *a, **kw):
        kw.pop('debug', False)
        if not kw:
            return """<html><head><script>
                var l = window.location;
                var q = l.hash.substring(1);
                var r = l.pathname + l.search;
                if(q.length !== 0) {
                    var s = l.search ? (l.search === '?' ? '' : '&') : '?';
                    r = l.pathname + l.search + s + q;
                }
                if (r == l.pathname) {
                    r = '/';
                }
                window.location = r;
            </script></head><body></body></html>"""
        return func(self, *a, **kw)
    return wrapper


class OAuth2Login(Home):

    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        if request.httprequest.method == 'GET' and request.session.uid and request.params.get('redirect'):
            # Redirect if already logged in and redirect param is present
            return http.redirect_with_hash(request.params.get('redirect'))
        oauth2_provider = self.get_oauth2_provider()

        response = super(OAuth2Login, self).web_login(*args, **kw)
        if response.is_qweb:
            error = request.params.get('oauth_error')
            if error == '1':
                error = _("Sign up is not allowed on this database.")
            elif error == '2':
                error = _("Access Denied - {}".format(response.qcontext['error']))
            elif error == '3':
                error = _("You do not have access to this database or your invitation has expired. Please ask for an invitation and be sure to follow the link in your invitation email.")
            else:
                error = None

            response.qcontext['oauth2_provider'] = oauth2_provider
            if error:
                response.qcontext['error'] = error
        return response

    def get_state(self):
        redirect = request.params.get('redirect') or 'web'
        if not redirect.startswith(('//', 'http://', 'https://')):
            redirect = '%s%s' % (request.httprequest.url_root, redirect[1:] if redirect[0] == '/' else redirect)
        state = dict(
            d=request.session.db,
            p=1,
            r=werkzeug.url_quote_plus(redirect),
        )
        token = request.params.get('token')
        if token:
            state['t'] = token
        return state


    def get_oauth2_provider(self):
        authorize_uri = config.get('auth_oauth2.auth_uri', False)
        token_uri = config.get('auth_oauth2.token_uri', False)
        data_uri = config.get('auth_oauth2.data_uri', False)
        scopes = config.get('auth_oauth2.scope', False)
        client_id = config.get('auth_oauth2.client_id', False)
        client_secret = config.get('auth_oauth2.client_secret', False)
        redirect_uri = config.get('auth_oauth2.redirect_uri', False)
        params = dict(
            debug=request.debug,
            response_type='code',
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scopes,
            state=simplejson.dumps(self.get_state()),
        )
        return authorize_uri+'?'+ werkzeug.url_encode(params)


class OAuth2Controller(http.Controller):

    _cp_path = CONTROLER_PATH

    def get_oauth2_client_id(self, request, db):
        return config.get('auth_oauth2.client_id', DEFAULT_CLIENT_ID)

    def get_oauth2_client_secret(self, request, db):
        return config.get('auth_oauth2.client_secret', DEFAULT_CLIENT_SECRET)

    def get_oauth2_scope(self, request, db):
        return config.get('auth_oauth2.scope', DEFAULT_SCOPE)

    def get_oauth2_redirect_uri(self, request, db):
        url = config.get('auth_oauth2.redirect_uri', False)
        if not url:
            registry = RegistryManager.get(db)
            ir_conf = registry.get('ir.config_parameter')
            with registry.cursor() as cr:
                url = (ir_conf.get_param(cr, 1, 'web.base.url') +
                       CONTROLER_PATH + '/' + LOGIN_METHOD)
        return url

    def get_oauth2_auth_uri(self, request, db):
        return config.get('auth_oauth2.auth_uri', DEFAULT_AUTH_URI)

    def get_oauth2_token_uri(self, request, db):
        return config.get('auth_oauth2.token_uri', DEFAULT_TOKEN_URI)

    def get_oauth2_revoke_uri(self, request, db):
        return config.get('auth_oauth2.revoke_uri', DEFAULT_REVOKE_URI)

    def get_oauth2_data_endpoint(self, request, db):
        return config.get('auth_oauth2.data_endpoint', DEFAULT_DATA_ENDPOINT)

    def get_oauth2_flow(self, request, db):
        return OAuth2WebServerFlow(
            client_id=self.get_oauth2_client_id(request, db),
            client_secret=self.get_oauth2_client_secret(request, db),
            scope=self.get_oauth2_scope(request, db),
            redirect_uri=self.get_oauth2_redirect_uri(request, db),
            auth_uri=self.get_oauth2_auth_uri(request, db),
            token_uri=self.get_oauth2_token_uri(request, db),
            revoke_uri=self.get_oauth2_revoke_uri(request, db),
            data_endpoint=self.get_oauth2_data_endpoint(request, db),
        )

    @openerpweb.jsonrequest
    def get_oauth2_auth_url(self, request, db):
        flow = self.get_oauth2_flow(request, db)
        url = flow.step1_get_authorize_url()
        return {
            'value': url + '&' + urllib.urlencode(
                {'state': {'db': db, 'debug': request.debug}}
            )
        }

    def get_dbname(self, request, state):
        """
        Should we use that ?
        from openerp.addons.web import db_list
        dbs = db_list(req, True)
        # 1 try the db in the url
        db_url = req.params.get('db')
        if db_url and db_url in dbs:
            return (db_url, False)
        # 2 use the database from the cookie if it's listable and still listed
        cookie_db = req.httprequest.cookies.get('last_used_database')
        if cookie_db in dbs:
            db = cookie_db
        # 3 use monodb if len(dbs) == 1!
        """
        return state.get('d', False)

    def get_credentials(self, request, db, code):
        flow = self.get_oauth2_flow(request, db)
        return flow.step2_exchange(code)

    def retrieve_state(self, state):
        if not state:
            return {}
        return ast.literal_eval(urllib.unquote_plus(state))

    @http.route('/auth_oauth2/signin', type='http', auth='none')
    @fragment_to_query_string
    def login(self, **kwargs):
        state = self.retrieve_state(kwargs.get("state", False))
        code = kwargs.get('code', False)
        error = kwargs.get('error', False)
        dbname = self.get_dbname(request, state)
        result = self._validate_token(request, dbname, code, error)
        if not result or 'error' in result:
            return set_cookie_and_redirect('/web/login?oauth_error=2&' + urllib.urlencode(result))
        return login_and_redirect(
            dbname, result.get('login', False), result.get('token', False)
        )

    def _validate_token(self, request, db, code, error):
        res = {}
        data, user_id = False, False
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
        id_token = credentials.id_token
        email = id_token.get('email', False)
        # email not given in the id_token dictionnary so we have to request it
        if not email:
            http_credentials = credentials.authorize(httplib2.Http())
            response = http_credentials.request(self.get_oauth2_data_endpoint(request, db), 'POST')
            # django-oidc-provider case
            if response and isinstance(response, tuple):
                if isinstance(response[1], str):
                    data = ast.literal_eval(response[1])
            if data and data.get('email', False):
                email = data.get('email')
        token = credentials.access_token
        with registry.cursor() as cr:
            if email:
                user_mdl = registry.get('res.users')
                user_id = user_mdl.get_user_id_by_email(cr, SUPERUSER_ID, email)
            if not user_id:
                res['error'] = _(u"User email %s not found in the current db") % email
                return res
            user = user_mdl.read(cr, SUPERUSER_ID, user_id, ['login'])
            user_mdl.write(
                cr,
                SUPERUSER_ID,
                user_id,
                {'oauth_token': token, 'oauth_id_token': id_token},
            )
            res['login'] = user.get('login', False)
        res['token'] = token
        return res
