openerp.auth_oauth2 = function(instance) {

    //translation needs
    var _t = instance.web._t,
        _lt = instance.web._lt;

    //template instance
    var QWeb = instance.web.qweb;

    instance.web.Login = instance.web.Login.extend({

        is_oauth2_cnx: false,

        start: function() {
            var self = this;
            if(this.params.hasOwnProperty('loginerror')){
                var message = "Access Denied"
                if (this.params.hasOwnProperty('error')){
                    message = this.params.error;
                }
                self.$(".oe_login_pane").fadeIn("fast", function() {
                    self.show_error(_t(message));
                });
            }
            if(!this.params.hasOwnProperty('login,password')){
                cnx_form = this.$el.find('.oe_login_pane form > ul:last-child()');
                cnx_form.hide()
                $(QWeb.render('auth_oauth2.login')).insertAfter(cnx_form);
                this.is_oauth2_cnx = true;
            }
            return this._super();
        },

        on_submit: function(ev) {
            if(!this.is_oauth2_cnx){
                this._super(ev);
            }else{
                if(ev) {
                    ev.preventDefault();
                }
                this.hide_error();
                this.$(".oe_login_pane").fadeOut("slow");
                var db = this.$el.find("form [name=db]").val();
                this.do_oauth2_login(db);
            }
        },

        do_oauth2_login: function(db) {
            var self = this;
            this.rpc('/auth_oauth2/get_oauth2_auth_url', {'db': db}).done(
                function(result) {
                    if (result.error) {
                        self.do_warn(result.title, result.error);
                        return;
                    }
                    window.location.replace(result.value);
            });
        },
    });

    instance.web.OauthWebClient = instance.web.WebClient.extend({
    
        bind_hashchange: function() {
            var self = this;
            $(window).bind('hashchange', this.on_hashchange);

            var state = $.bbq.getState(true);
            if (state.hasOwnProperty('login,password')) {
                delete state['login,password'];
            }
            if (_.isEmpty(state) || state.action == "login") {
                self.menu.has_been_loaded.done(function() {
                    new instance.web.Model("res.users").call("read", [self.session.uid, ["action_id"]]).done(function(data) {
                        if(data.action_id) {
                            self.action_manager.do_action(data.action_id[0]);
                            self.menu.open_action(data.action_id[0]);
                        } else {
                            var first_menu_id = self.menu.$el.find("a:first").data("menu");
                            if(first_menu_id)
                                self.menu.menu_click(first_menu_id);
                        }
                    });
                });
            } else {
                $(window).trigger('hashchange');
            }
    },

    });

};
