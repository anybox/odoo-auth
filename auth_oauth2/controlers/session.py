# coding: utf-8
import ast
import httplib2
import logging
from openerp.addons.web import http
from openerp.addons.web.controllers.main import Session as session
from openerp.tools import config
from openerp.osv import osv
from oauth2client.client import AccessTokenCredentials as ATC
from socket import timeout

openerpweb = http


class Session(session):

    @http.route('/web/session/destroy', type='json', auth="user")
    def destroy(self, req):
        import pdb
        pdb.set_trace()
        uid = req.session._uid
        user_values = req.session.model('res.users').read(
            uid, ['oauth_id_token', 'oauth_token']
        )
        id_token = user_values['oauth_id_token']
        token = user_values['oauth_token']
        exceptions = False
        if not id_token:
            req.session.logout()
            return {}
        id_token = ast.literal_eval(id_token)
        cred = ATC(token, None)
        http_credentials = cred.authorize(httplib2.Http(timeout=10))
        user_id = id_token['sub']
        uri = config.get('auth_oauth2.end_session_endpoint')
        client_id = config.get('auth_oauth2.client_id')
        client_secret = config.get('auth_oauth2.client_secret')
        req_body = {
            'user_id': int(user_id),
            'client_id': client_id,
            'client_secret': client_secret,
        }
        try:
            logging.info("oauth2 end session")
            response = http_credentials.request(uri, 'POST', body=str(req_body))
            if response[0].status != 200:
                exceptions = True
        except timeout:
            logging.error("oauth2 end session error : timeout")
            exceptions = True
        except Exception as e:
            logging.error("oauth2 end session error : %s" % (e))
            exceptions = True
        req.session.logout()
        if exceptions:
            return {
                'error': (
                    u"Attention, vous avez bien été déconnecté d'OpenERP, cependant une erreur "
                    u"semble s'être produite lors de la déconnexion SSO, veuillez vérifier que "
                    u"vous êtes bien déconnecté de celui-ci"
                ),
                'title': 'Erreur déconnexion SSO'
            }
        return {}
