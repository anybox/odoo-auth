Allow users to sign up through OAuth2 Provider
==============================================

- This module allow Odoo users to connect through a specific OAuth2 provider,
  if you expect to let users choose its provider prefer Official `auth_oauth`
  module.

- This module let you make the configuration at server level

*Benefit:*
 * let make different settings per environements (production server, test server)

*inconvenience:*
 * it's not possible to make settings per database, if you are in saas mode.

- This module is based on `oauth2client <https://github.com/google/oauth2client>`_
  library to manage oauth2 connexion.

Settings
--------

* **auth_oauth2.client_id**: Client Id given by your OAuth2 Provider
  (*may looks like*: ***google-key***.apps.googleusercontent.com)
* **auth_oauth2.client_secret**: A secret code given by your Oauth2 provider
* **auth_oauth2.auth_uri**: OAuth2 provider URL to authenticate users
  (*default*: Google uri https://accounts.google.com/o/oauth2/auth)
* **auth_oauth2.scope**: string or iterable of strings, OAUth user data desired
  to access (*default*: email)
* **auth_oauth2.token_uri**: OAuth provider URL to validate tokens
  (*default*: Google uri https://accounts.google.com/o/oauth2/token)
* **auth_oauth2.data_endpoint**: Data URL
* **auth_oauth2.redirect_uri**: This should be
  `http[s]://your.host.name[:port]/auth_oauth2/login` if it's not set, this
  module will construct if from `web.base.url` set in `ir.config_parameter` +
  `/auth_oauth2/login`


Not implemented:

* **auth_oauth2.revoke_uri**: OAuth provider URL to revoke authorizations
  (*default*: Google uri https://accounts.google.com/o/oauth2/revoke)
* **auth_oauth2.user_agent**: string, HTTP User-Agent to provide for this
  application.

Probably we could go deeper with thoses available attibutes:

* 'state': fields.char('state') Provides any state that might be useful to your
  application. *Today it's only used to pass the db name*
* 'access_type': fields.selection([('online', u"On line"), ('offline', u"Off line")])
* 'approval_prompt': fields.selection([('force', u"Force"), ('auto', u"Auto")])


What we could do in depends modules
-----------------------------------

Actually the token is saved in password field for convenience. So you could
retreivied it to use in other module to consume Providers API, like this::

    from oauth2client.client import AccessTokenCredentials as ATC
    import httplib2
    ...
    access_token = user_model.read(cr, uid, user_id, ['password'])['password']
    credentials = ATC(access_token, None)
    http = httplib2.Http()
    http = credentials.authorize(http)
    (resp_headers, content) = http.request(
        "https://www.googleapis.com/plus/v1/people/me", "GET")


On that case you may have to add keys in the `scope` attribute to get token
autorization from user to acces to his data.


How to get it works with google oauth2
--------------------------------------

* connect to the developer console and create https://console.developers.google.com
* Create a new project
* Go to API & authentication to create a new ID
* In Oauth section create client ID
* set your allowed sources uri: [protocole]://[hostname] (ie: https://anybox.fr)
* set redirect uri with: [protocole]://[hostname]/auth_oauth2/login
  (ie: https://anybox.fr/auth_oauth2/login)
* Install this module
* add setings in you `openerp.cfg` configuration file
* restart odoo!

.. Note::

    Add `#login,password` in the URL if you want to connect with an odoo account
    (like admin users) to disable the login forms used by this module

TODO
----

* translate error messages
* Have a look if we are concerned by the way we got an existed session that sould
  not work (cf controllers in Odoo `auth_oauth` module)
* add revoke button and find out if there is differences with log out, if yes
  implement both
* get all params and hash parameters from uri (not only the db name)to pass it
  in state before redirect user to the oauth provider. Later retrieved them
  before set the connection uri. To do that we will avoid to lost link to an
  object during connection.

License
-------

Affero General Public License
