Allow users to sign up through OAuth2 Provider
==============================================

This module allow your user to connect through a specific OAuth2 provider,
if you expect to let user to choice his provider prefer Official `auth_oauth`
module.

This module let you make the configuration at server level.

Benefit:
 * let make different settings per environements (production server, test server)

inconvenience:
 * it's not possible to make settings per database, if you are in saas mode.


Settings
--------

 * **auth_oauth2.client_id**: Client Id given by your OAuth2 Provider
   (*may looks like*: ***google-key***.apps.googleusercontent.com)
 * **auth_oauth2.client_secret**: A secret code given by your Oauth2 provider
 * **auth_oauth2.auth_uri**: OAuth2 provider URL to authenticate users
   (*default*: Google uri https://accounts.google.com/o/oauth2/auth)
 * **auth_oauth2.scope**: string or iterable of strings, OAUth user data desired to access
   (*default*: email)
 * **auth_oauth2.token_uri**: OAuth provider URL to validate tokens
   (*default*: Google uri https://accounts.google.com/o/oauth2/token)
 * **auth_oauth2.data_endpoint**: Data URL

Not implemented:
 * **auth_oauth2.revoke_uri**: OAuth provider URL to revoke authorizations
   (*default*: Google uri https://accounts.google.com/o/oauth2/revoke)
 * **auth_oauth2.redirect_uri**: actualy calculated by this module
 * **auth_oauth2.user_agent**: string, HTTP User-Agent to provide for this application.

Probably we could go deeper with thoses available attibutes:
Provides any state that might be useful to your application
'state': fields.char('state')
'access_type': fields.selection([('online', u"On line"), ('offline', u"Off line")])
'approval_prompt': fields.selection([('force', u"Force"), ('auto', u"Auto")])

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

How to get it works with google oauth2
--------------------------------------

* connect to the developer console and create https://console.developers.google.com
* Create a new project
* Go to API & authentication to create a new ID
* In Oauth section create client ID
* set your allowed sources uri: [protocole]://[hostname] (ie: https://anybox.fr)
* set redirect uri with: [protocole]://[hostname]/auth_oauth2/login
  (ie: https://anybox.fr/auth_oauth2/login)
* Define in odoo your Google OAuth2 Provider

TODO
----

* Manages DB name through redirects
* Handle errorr parameter when user refused to give access to odoo
* well manage error message and translate them
* test differents use cases and try to make unit test them
    - User cancel auth
    - Unknown user
    - missing scope auth
    - bad secret code
    - wrong redirect uri set in google console
    - wrong origine host set in google console
* Have a look if we are concerned by the way we got an existed session that sould
  not work (cf controllers in Odoo `auth_oauth` module)
* add revoke button and find out if there is differences with log out, if yes
  implement both

License
-------

Affero General Public License
