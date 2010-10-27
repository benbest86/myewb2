;(function() {
    // needs the following globals
    // routes, current_user
    /* SERVER ROUTES */
    var routes = CONFCOMM_GLOBALS.routes;
    var current_username = CONFCOMM_GLOBALS.username;
    // holds the current users' profile
    var current_profile;
    // holds the profiles collection
    var profiles;
    // holds the profile summary collection
    var profile_summaries;
    /* Extended BaseView of Backbone.SPWA.View */
    var BaseView = Backbone.SPWA.View.extend({
        _template_cache: {},
        // get the current template - either from the cache or from the network.
        template: function() {
            var self = this;
            // return empty string if no template name given.
            if (!self.template_name) {
                return "";
            }
            // check the cache first
            var t = self._template_cache[self.template_name];
            if (!t) {
                // synchronously grab template from the server otherwise
                // TODO: find a better non-blocking way
                $.ajax(
                    {
                    url:routes.templates_base + self.template_name,
                    async: false,
                    success: function(data){
                        self._template_cache[self.template_name] = data;
                        t = data;
                }});
            }
            return t;
        }
    });
    var ConferenceProfile = Backbone.Model.extend({
        initialize: function() {
            var self = this;
            if (!self.id) self.id = self.get('username');
        },
        url: function() {
            var self = this;
            return routes.profile_base + self.id + '/';
        },
        hash: function() {
            var self = this;
            return '#/profile/?id=' + self.id;
        }
    });
    /* COLLECTIONS */
    var ProfileStore = Backbone.Collection.extend({
        model: ConferenceProfile
    });
    /* VIEWS */
    var MainView = BaseView.extend({
        el: $('#main-view'),
        template_name: 'main.html',
        render: function() {
            var self = this;
            $(self.el).html(_.template(self.template(), {model: current_profile}));
        }
    });
    var ProfileView = BaseView.extend({
        el: $('#profile'),
        template_name: 'profile.html',
        render: function() {
            var self = this;
            $(self.el).html(_.template(self.template(), {model:self.model}));
            // self.handleEvents();
        }
    });
    var ProfileFormView = BaseView.extend({
        el: $('#profile-form-container'),
        template_name: 'profile_form.html',
        events: {'submit #profile-form': 'update_profile'},
        update_profile: function() {
            var self = this;
            var inputs = $('#profile-form').find('.profile-input');
            var data = {}
            _.each(inputs, function(i) {
                if (i.name) data[i.name] = i.value;
            });
            // self.model.set(data);
            self.model.save(data, {success: function(){location.hash='/profile/'}});
            return false;
        },
        render: function() {
            var self = this;
            $(self.el).html(_.template(self.template(), {model:self.model}));
        }});
    var ProfilesView = BaseView.extend({
        el: $('#profile-list'),
        template_name: 'profile_list.html',
        render: function() {
            var self = this;
            $(self.el).html(_.template(self.template(), {collection:self.collection}));
        }});
    /* CONTROLLER */
    var Controller = Backbone.SPWA.Controller.extend({
        routes: {
            '/': 'main',
            '/profile/': 'profile',
            '/profile/edit/': 'edit_profile'
        },
        views: {
            'Profile': ProfileView,
            'ProfileForm': ProfileFormView,
            'Main': MainView
        },
        main: function(args) {
            var self = this;
            self.hideAll();
            var view = self.getView('Main');
            view.show();
        },
        profile: function(args) {
            var self = this;
            self.hideAll();
            var view = self.getView('Profile');
            var id = args.id ? args.id : current_username;
            view.model = profiles.get(id);
            if (!view.model) {
                var profile_to_get = new ConferenceProfile({
                    id: id
                });
                profile_to_get.fetch({success: function(){
                    profiles.add(profile_to_get);
                    view.model = profile_to_get;
                    view.show();
                    }
                });
            }
            else {
                view.show();
            }
        },
        edit_profile: function(args) {
            var self = this;
            self.hideAll();
            var view = self.getView('ProfileForm');
            var id = current_username;
            view.model = profiles.get(id);
            view.show();
        }
    });

    app = new Controller();

    /* GO TIME */
    $(function() {
        current_profile = new ConferenceProfile({
            id: current_username
        });
        profiles = new ProfileStore();
        profile_summaries = new ProfileStore(); // 
        profile_summaries.url = routes.profiles_base;
        profile_summaries.fetch({success: function() {
            var v = new ProfilesView();
            v.collection = profile_summaries;
            v.render();
        }});
        current_profile.fetch({success: function(){
            profiles.add(current_profile);
            if (!location.hash) {
                location.hash = '/';
            }
            else {
                $(window).hashchange();
            }
        }});
    });
})();
