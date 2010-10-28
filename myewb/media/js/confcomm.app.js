;(function() {
    // needs the following globals
    // routes, current_user
    /* SERVER ROUTES */
    var DEBUG = true;
    console.log('just before debug');
    if (!DEBUG) { // leave a bunch of global variables so I can get at them through the console
        console.log('not debug');
        var routes;
        var current_username;
        // holds the current users' profile
        var current_profile;
        // holds the profiles collection
        var profiles;
        // holds the profile summary collection
        var profile_summaries;
        /* Extended BaseView of Backbone.SPWA.View */
        /* VIEW VARIABLES */
        var filters_view;
        // var browser_view;
        var login_view;
        var my_profile_view;
        var news_view;
        var stats_view;
    }   
    routes = CONFCOMM_GLOBALS.routes;
    current_username = CONFCOMM_GLOBALS.username;

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
            $.facebox({div:'#profile'});
            // self.handleEvents();
        }
    });
    var ProfileFormView = BaseView.extend({
        content_holder: '#profile-form-container',
        el: $('#profile-form-container'),
        template_name: 'profile_form.html',
        events: {'submit form': 'update_profile'},
        update_profile: function() {
            var self = this;
            var inputs = self.$('form').find('.profile-input');
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
            // since our form is in the facebox we have to do some monkey business here
            // use content_holder to render the template
            $(self.content_holder).html(_.template(self.template(), {model:self.model}));
            $.facebox({div:self.content_holder});
            // after facebox copies the html to its own div, reset self.el to the 
            // content in the facebox
            self.el = $('#facebox').find('.content').first();
            // re-delegate the events so they are attached to the facebox copy of the
            // form
            self.delegateEvents();
        }});
    var ProfilesView = BaseView.extend({
        el: $('#profile-list'),
        template_name: 'profile_list.html',
        render: function() {
            var self = this;
            $(self.el).html(_.template(self.template(), {collection:self.collection}));
        }});
    var FiltersView = BaseView.extend({
        el: $('#filters'),
        template_name: 'filters.html',
        render: function() {
            var self = this;
            $(self.el).html(_.template(self.template()));
        }});
    var NewsView = BaseView.extend({
        el: $('#news'),
        template_name: 'news.html',
        render: function() {
            var self = this;
            $(self.el).html(_.template(self.template()));
        }});
    var MyProfileView = BaseView.extend({
        el: $('#my-profile'),
        template_name: 'my_profile.html',
        render: function() {
            var self = this;
            $(self.el).html(_.template(self.template(), {model: self.model}));
        }});
    var StatsView = BaseView.extend({
        el: $('#stats'),
        template_name: 'stats.html',
        render: function() {
            var self = this;
            $(self.el).html(_.template(self.template()));
        }});
    var LoginView = BaseView.extend({
        el: $('#cc-login'),
        template_name: 'cc_login.html',
        render: function() {
            var self = this;
            $(self.el).html(_.template(self.template()));
        }});
    var BrowserView = BaseView.extend({
        el: $('#browser'),
        template_name: 'browser.html',
        render: function() {
            var self = this;
            $(self.el).html(_.template(self.template(), {collection: self.collection}));
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
            // self.hideAll();
            var view = self.getView('Main');
            view.show();
        },
        profile: function(args) {
            var self = this;
            // self.hideAll();
            var view = self.getView('Profile');
            var id = args.id ? args.id : current_username;
            view.model = profiles.get(id);
            if (!view.model) {
                var profile_to_get = new ConferenceProfile({
                    id: id
                });
                // get our nice facebox loading spinner
                $.facebox(function() {
                profile_to_get.fetch({success: function(){
                    profiles.add(profile_to_get);
                    view.model = profile_to_get;
                    view.render();
                    }
                    });
                });
            }
            else {
                view.render();
            }
        },
        edit_profile: function(args) {
            var self = this;
            // self.hideAll();
            var view = self.getView('ProfileForm');
            var id = current_username;
            view.model = profiles.get(id);
            console.log(view.model);
            view.render();
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
            browser_view = new BrowserView();
            browser_view.collection = profile_summaries;
            browser_view.show();
            // var v = new ProfilesView();
            // v.collection = profile_summaries;
            // v.render();
        }});
       /* Load all the default templates */
       news_view = new NewsView;
       news_view.show();
       stats_view = new StatsView;
       stats_view.show();
       login_view = new LoginView;
       login_view.show();
       filters_view = new FiltersView;
       filters_view.show();
       current_profile.fetch({success: function(){
           profiles.add(current_profile);
           // if (!location.hash) {
           //     location.hash = '/';
           // }
           // else {
           //     $(window).hashchange();
           // }
           my_profile_view = new MyProfileView();
           my_profile_view.model = current_profile;
           my_profile_view.render();
       }});
    });
})();
