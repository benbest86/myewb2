;(function() {
    // needs the following globals
    // routes, current_user
    /* SERVER ROUTES */
    var DEBUG = true;
    if (!DEBUG) { // leave a bunch of global variables so I can get at them through the console
        var routes;
        var current_username;
        var filter_lists;
        // holds the current users' profile
        var current_profile;
        // holds the profiles collection
        var profiles;
        // holds the profile summary collection
        var profile_summaries;
        /* VIEW VARIABLES */
        var filters_view;
        var browser_view;
        var login_view;
        var my_profile_view;
        var news_view;
        var stats_view;
        var browser_pagination_view;
        var loading_image;
    }
    routes = CONFCOMM_GLOBALS.routes;
    current_username = CONFCOMM_GLOBALS.username;
    filter_lists = CONFCOMM_GLOBALS.filter_lists;
    loading_image = CONFCOMM_GLOBALS.loading_image;

    /* Extended BaseView of Backbone.SPWA.View */
    var BaseView = Backbone.SPWA.View.extend({
        _template_cache: {},
        // get a template - either from the cache or from the network.
        // leave out tname to get the views' default template
        template: function(tname) {
            var self = this;
            // return empty string if no template name given.
            tname = tname || self.template_name;
            if (!tname) {
                return "";
            }
            // check the cache first
            var t = self._template_cache[tname];
            if (!t) {
                // synchronously grab template from the server otherwise
                // TODO: find a better non-blocking way
                $.ajax(
                    {
                    url:routes.templates_base + tname,
                    async: false,
                    success: function(data){
                        self._template_cache[tname] = data;
                        t = data;
                }});
            }
            return t;
        },
        loading: function() {
            var self = this;
            if (!self.el) {
                return false;
            }
            $(self.el).html(_.template(self.template('loading.html'), {loading_image: loading_image}));
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
    var SummaryProfile = Backbone.Model.extend({
        initialize: function() {
            var self = this;
            if (!self.id) self.id = self.get('username');
        },
        hash: function() {
            var self = this;
            return '#/profile/?id=' + self.id;
        }
    });
    var Paginator = Backbone.Model.extend({
        initialize: function(data) {
            var self = this;
            // make sure we've got ints
            data['current'] = data['current'] - 0;
            data['last'] = data['last'] - 0;
            self.set(data);
        }
    });
    /* COLLECTIONS */
    var ProfileStore = Backbone.Collection.extend({
        model: ConferenceProfile
    });
    var SummaryStore = Backbone.Collection.extend({
        model: SummaryProfile,
        parse: function(resp) {
            return resp.models;
        },
        url: function() {
            return this.qs ? this.base_url + '?' + this.qs : this.base_url;
        },
        qs: ''
    });
    /* VIEWS */
    var ProfileView = BaseView.extend({
        el: $('#profile'),
        template_name: 'profile.html',
        render: function() {
            var self = this;
            $(self.el).html(_.template(self.template(), {model:self.model}));
            $.facebox({div:'#profile'});
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
    var FiltersView = BaseView.extend({
        el: $('#filters'),
        template_name: 'filters.html',
        render: function() {
            var self = this;
            $(self.el).html(_.template(self.template(), {filter_lists: filter_lists}));
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
            self.paginator.render();
        }});
    var BrowserPaginationView = BaseView.extend({
        el: $('#paginator'),
        template_name: 'browser_paginator.html',
        render: function() {
            var self = this;
            self.el = $('#paginator');
            $(self.el).html(_.template(self.template(), {model: self.model}));
        }});
    /* CONTROLLER */
    var Controller = Backbone.SPWA.Controller.extend({
        routes: {
            '/profile/': 'profile',
            '/profile/edit/': 'edit_profile',
            '/': 'browser'
        },
        views: {
            'Profile': ProfileView,
            'ProfileForm': ProfileFormView,
            'Browser': BrowserView
        },
        browser: function(args) {
            var self = this;
            var view = self.getView('Browser');
            // fetch the next page of results
            // and render only if the state has changed
            if (!(args === self.last_state)){
                view.loading();
                page = args['page'] || 1;
                profile_summaries.qs = 'page=' + page;
                profile_summaries.fetch({
                    success:function(self, resp) {
                        browser_pagination_view.model = new Paginator(resp.pagination);
                        view.collection = self;
                        view.paginator = browser_pagination_view;
                        view.render();
                        self.last_state = args;
                    }
                });
            }
        },
        profile: function(args) {
            var self = this;
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
            var view = self.getView('ProfileForm');
            var id = current_username;
            view.model = profiles.get(id);
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
        profile_summaries = new SummaryStore(); // 
        profile_summaries.base_url = routes.profiles_base;
       // don't render this guy just wait - wait until we've fetched the profile_summaries
       // and rendered the first BrowserView on page load
       browser_pagination_view = new BrowserPaginationView;
       browser_view = new BrowserView;
       browser_view.collection = profile_summaries;
       /* Load all the default templates */
       news_view = new NewsView;
       news_view.loading();
       news_view.render();
       stats_view = new StatsView;
       stats_view.loading();
       stats_view.render();
       login_view = new LoginView;
       login_view.loading();
       login_view.render();
       filters_view = new FiltersView;
       filters_view.loading();
       filters_view.render();
       my_profile_view = new MyProfileView();
       my_profile_view.loading();
       current_profile.fetch({success: function(){
           profiles.add(current_profile);
           my_profile_view.model = current_profile;
           my_profile_view.render();
       }});
       if (!location.hash) {
           location.hash = '/';
       }
       else {
           $(window).hashchange();
       }
       // bind some events to facebox to help with nav
       // change back to the last hash when we close a facebox
       $(document).bind('close.facebox', function() {
           location.hash = $(document).data('last_hash');
       });
       // keep track of the last hash so we can return to it after
       // closing a facebox
       $(window).hashchange(function() {
           $(document).data('last_hash', $(document).data('this_hash'));
           $(document).data('this_hash', location.hash);
       });
    });
})();
