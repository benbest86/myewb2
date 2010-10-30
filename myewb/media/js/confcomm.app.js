;(function() {
    // needs the following globals
    // routes, current_user
    /* SERVER ROUTES */
    var DEBUG = false;
    if (!DEBUG) { // leave a bunch of global variables so I can get at them through the console
        var routes;
        var current_username;
        var filter_lists;
        var anon;
        // holds the current users' profile
        var current_profile;
        // holds the profiles collection
        var profiles;
        // holds the cohort summary collection
        var cohort_summaries;
        /* VIEW VARIABLES */
        var filters_view;
        var browser_view;
        var login_view;
        var my_profile_view;
        var news_view;
        var stats_view;
        var browser_pagination_view;
        var loading_image;
        var name_filter_view;
        var this_hash;
        var last_hash;
    }
    routes = CONFCOMM_GLOBALS.routes;
    current_username = CONFCOMM_GLOBALS.username;
    filter_lists = CONFCOMM_GLOBALS.filter_lists;
    loading_image = CONFCOMM_GLOBALS.loading_image;
    anon = CONFCOMM_GLOBALS.anon;

    /* MODELS */
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
            return '/profile/?id=' + self.id;
        }
    });
    var SummaryProfile = Backbone.Model.extend({
        initialize: function() {
            var self = this;
            if (!self.id) self.id = self.get('username');
        },
        hash: function() {
            var self = this;
            return self.get('has_profile') ? '/profile/?id=' + self.id : self.invite_hash();
        },
        invite_hash: function() {
            var self = this;
            return '/invitation/?id=' + self.id;
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
            return this._qs ? this.base_url + '?' + this._qs : this.base_url;
        },
        // takes an object of query args to be serialized
        // and removes illegal args
        set_qs: function(qs_args) {
            allowed_args = ['page', 'chapter', 'role', 'year', 'last_name',];
            qs_obj = {}
            _.each(allowed_args, function(a) {
                if (qs_args[a]){
                    qs_obj[a] = qs_args[a]
                }
            });
            this._qs = $.param(qs_obj);
        },
        _qs: ''
    });

    /* VIEWS */
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
        _state: {},
        _filter_state: function(state) {
            // override this to filter state values
            return state;
        },
        set_state: function(state) {
            this._state = this._filter_state(state);
        },
        get_state: function(state) {
            return this._state;
        },
        // pass in a state to compare to the current state of the view
        compare_state: function(state) {
            var self = this;
            var new_state = self._filter_state(state);
            var new_state_keys = _.keys(new_state);
            // see if the key length is the same - if not state has changed.
            if (new_state_keys.length != _.keys(self._state).length) {
                return false;
            }
            // check each property in the state for differences
            for (k in new_state) {
                if (new_state[k] !== self._state[k]) {
                    return false;
                }
            }
            // everything has passed so state is the same
            return true;
        },
        loading: function() {
            var self = this;
            if (!self.el) {
                return false;
            }
            $(self.el).html(_.template(self.template('loading.html'), {loading_image: loading_image}));
        },
        async_render: function(id, collection, callbacks) {
            var self = this;
            self.model = collection.get(id);
            if (!self.model) {
                var model_to_get = new collection.model({
                    id: id
                });
                // get our nice facebox loading spinner
                callbacks['success'] = function() {
                            collection.add(model_to_get);
                            self.model = model_to_get;
                            self.render();
                }
                // get our loading function. not appropriate if we're not faceboxing though?
                $.facebox(function() {
                    // model_to_get.fetch({
                    //     success: function(){
                    //         collection.add(model_to_get);
                    //         self.model = model_to_get;
                    //         self.render();
                    //     },
                    //     error: function() {
                    //         // close the facebox on an error
                    //         // TODO: Add error message
                    //         $(document).trigger('close.facebox');
                    //     }
                    // });
                    model_to_get.fetch(callbacks);
                });
            }
            else {
                self.render();
            }
        }
    });

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
        // events: {'submit form': 'update_profile'},
        update_profile: function() {
            var self = this;
            var inputs = self.$('form').find('.profile-input');
            var data = {}
            _.each(inputs, function(i) {
                if (i.name) data[i.name] = i.value;
            });
            var id = self.model.username || self.model.id;
            $.facebox(function() {
                self.model.save(data, {success: function(){location.hash='/profile/?id=' + id}});
            });
            return false;
        },
        render: function() {
            var self = this;
            // if we don't have a model, cancel
            if (!self.model) {
                return;
            }
            // since our form is in the facebox we have to do some monkey business here
            // use content_holder to render the template
            $(self.content_holder).html(_.template(self.template(), {model:self.model}));
            $.facebox({div:self.content_holder});
            // after facebox copies the html to its own div, reset self.el to the 
            // content in the facebox
            self.el = $('#facebox').find('.content').first();
            // re-delegate the events so they are attached to the facebox copy of the
            // form
            // XXX: Might not work in IE with submit event so have to manually go
            //self.delegateEvents();
            self.$('form').bind('submit', function() { self.update_profile(); return false;});
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
        events: {'click a.edit-profile':'edit_profile'},
        edit_profile: function () {
            if (anon) {
                return
            }
            var self = this;
            profile_form_view.model = profiles.get(current_username);
            profile_form_view.render();
        },
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
        // events: {'change .filter': 'update_filters'},
        // attach some events that are outside of the scope of el
        bind_to_filters: function() {
            var self = this;
            $('.filter').bind('change', function() {
                self.update_filters();
            });
        },
        _filter_state: function(state) {
            var new_state = {};
            _.each(['chapter', 'role', 'year', 'last_name', 'page'], function(f) {
                if (state[f]) {
                    new_state[f] = state[f];
                }
            });
            return new_state;
        },
        template_name: 'browser.html',
        update_filters: function() {
            var qs = $('#filter-controls').serialize();
            location.hash = '/?' + qs;
        },
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
            self.el = $('.paginator');    // @@@ SEAN
            $(self.el).html(_.template(self.template(), {model: self.model}));
        }});
    var NameFilterView = BaseView.extend({
        template_name: 'last_name_filter.html',
        current_letter: 'All',
        events: {'click a': 'update_last_name'},
        update_last_name: function(e) {
            var self = this;
            self.el = $('#name-filter');
            var v = $(e.target).html();
            self.current_letter = v;
            if (v === 'All') {
                v = ''
            }
            $('#hidden-last-name').val(v);
            $('#hidden-last-name').trigger('change');
            // redraw
            self.render();
            return false;
        },
        render: function() {
            var self = this;
            self.el = $('#name-filter');
            $(self.el).html(_.template(self.template(), {current_letter: self.current_letter}));
            self.delegateEvents();
        }
    });
    var InvitationView = BaseView.extend({
        template_name: 'invitation.html',
        el: '#invitation',
        render: function() {
            var self = this;
            $(self.el).html(_.template(self.template(), {model: self.model}));
            $.facebox({'div':self.el});
        }
    });
    /* CONTROLLER */
    var Controller = Backbone.SPWA.Controller.extend({
        routes: {
            '/profile/': 'profile',
            '/': 'browser',
            '/invitation/': 'invitation'
        },
        views: {
            'Profile': ProfileView,
            'Browser': BrowserView,
            'Invitation': InvitationView
        },
        browser: function(args) {
            var self = this;
            var view = self.getView('Browser');
            // fetch the next page of results
            // and render only if the state has changed
            args['page'] = args['page'] || 1;
            if (!view.compare_state(args)){
                view.loading();
                params = {}
                // set our querystring
                cohort_summaries.set_qs(args);
                cohort_summaries.fetch({
                    success:function(self, resp) {
                        browser_pagination_view.model = new Paginator(resp.pagination);
                        view.collection = self;
                        view.paginator = browser_pagination_view;
                        view.render();
                        view.set_state(args);
                    }
                });
            }
        },
        profile: function(args) {
            var self = this;
            var view = self.getView('Profile');
            var id = args.id;
            if (!id) {
                return
            }
            view.async_render(id, profiles, {
                error: function(){
                // close the facebox on an error
                // TODO: Add error message
                $(document).trigger('close.facebox');
            }}
            );
        },
        invitation: function(args) {
            var self = this;
            if (anon) {
                // TODO: redirect to login or signup
                return;
            }
            var id = args.id;
            if (!id) {
                // TODO: send error message?
                return;
            }
            var self = this;
            var view = self.getView('Invitation');
            view.async_render(id, cohort_summaries, {
                error: function () {
                    $(document).trigger('close.facebox');
                }
            });
        }
    });

    app = new Controller();

    /* GO TIME */
    $(function() {
        profiles = new ProfileStore();
        cohort_summaries = new SummaryStore();
        cohort_summaries.base_url = routes.cohorts_base;
        // don't render this guy just wait - wait until we've fetched the cohort_summaries
        // and rendered the first BrowserView on page load
        browser_pagination_view = new BrowserPaginationView;
        browser_view = new BrowserView;
        browser_view.collection = cohort_summaries;
        /* Load all the default templates */
        news_view = new NewsView;
        news_view.loading();
        news_view.render();
        stats_view = new StatsView;
        stats_view.loading();
        stats_view.render();
        filters_view = new FiltersView;
        filters_view.loading();
        filters_view.render();
        name_filter_view = new NameFilterView;
        name_filter_view.render();
        // TODO: fix this - a bit of an ugly hack.
        browser_view.bind_to_filters();
        // show the my_profile view if the user is logged in
        profile_form_view = new ProfileFormView;
        if (!anon) {
            current_profile = new ConferenceProfile({
                id: current_username
            });
            my_profile_view = new MyProfileView();
            $(my_profile_view.el).show();
            my_profile_view.loading();
            current_profile.fetch({success: function(){
                profiles.add(current_profile);
                my_profile_view.model = current_profile;
                my_profile_view.render();
            }});
        }
        // show the login view if the user is not logged in
        else {
            login_view = new LoginView;
            $(login_view.el).show();
            login_view.loading();
            login_view.render();
        }
        this_hash = '/';
        if (!location.hash) {
            location.hash = '/';
        }
        else {
            $(window).hashchange();
        }
        // bind some events to facebox to help with nav
        // change back to the last hash when we close a facebox
        $(document).bind('close.facebox', function() {
            location.hash = last_hash;
        });
        // keep track of the last hash so we can return to it after
        // closing a facebox
        $(window).hashchange(function() {
            last_hash = this_hash;
            this_hash = location.hash;
        });
    });
})();
