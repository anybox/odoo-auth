openerp.auth_oauth2 = function(instance) {

    //translation needs
    var _t = instance.web._t,
        _lt = instance.web._lt;

    //template instance
    var QWeb = instance.web.qweb;

    instance.web.WebClient = instance.web.WebClient.extend({
        display_error: function (error) {
            return instance.web.dialog($('<div>'), {
                modal: true,
                title: error.title,
                buttons: [
                    {text: _t("Ok"), click: function() { $(this).dialog("close"); }}
                ]
            }).html(error.error);
        },

        on_logout: function() {
            var self = this;
            if (!this.has_uncommitted_changes()) {
                this.session.session_logout().done(function (result) {
                    $(window).unbind('hashchange', self.on_hashchange);
                    self.do_push_state({});
                    if (result.error) {
                        self.display_error(result);
                        window.setTimeout(function(){
                            window.location.reload()
                        }, 12000);
                    }
                    else {
                        window.location.reload();
                    }
                });
            }
        },

    });

};
