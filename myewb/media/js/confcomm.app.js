;(function(GLOBALS) {

    // variable definitions so we don't grab
    // global scope.
    var routes;
    var current_username;
    var filter_lists;
    var anon;
    // holds the current users' profile
    var current_profile;
    var show_opt_links;
    // holds the profiles collection
    var profiles;
    // holds the cohort summary collection
    var cohort_summaries;
    /* VIEW VARIABLES */
    var filters_view;
    var browser_view;
    var get_chapter_view;
    var login_view;
    var my_profile_view;
    var news_view;
    var quick_cohorts_view;
    var browser_pagination_view;
    var loading_image;
    var name_filter_view;
    var hash_history;
    var facebox_history;
    var invitation_view;
    var messages;

    // keeps track of whether the twitter script has been loaded yet
    var twitter_loaded;

    // keeps track of whether or not there are unsaved changes
    var unsaved_changes = false;

    // needs the following globals
    // routes, current_user
    /* SERVER ROUTES */
    routes = GLOBALS.routes;
    current_username = GLOBALS.username;
    filter_lists = GLOBALS.filter_lists;
    loading_image = GLOBALS.loading_image;
    anon = GLOBALS.anon;
    show_opt_links = true;
    twitter_loaded = false;

    /* MODELS */
    var ConferenceProfile = Backbone.Model.extend({
        // set id to the username provided
        initialize: function() {
            var self = this;
            if (!self.id) self.id = self.get('username');
            var props = ['conference_question', 'conference_goals', 'text_interests', 'what_now'];
            _.each(props, function(p) {
                if (!self.get(p)) {
                    self.set({p:""});
                }
            });
        },
        // grab what might be the top most important cohorts
        quick_cohorts: function() {
            var self = this;
            if (self['_quick_cohorts']) {
                return self._quick_cohorts;
            }
            // sort the cohorts into quick_cohorts and
            // slice to 5 items
            var cohorts = self.get('cohorts');
            if (cohorts && cohorts.length) {
                var sorted_cohorts = _.sortBy(cohorts, function(c) {
                    // jf, aps and prof are top priority
                    if (_.include(['j', 's', 'f'], c.role)) {
                        return 1;
                    }
                    // then president
                    else if (c.role === 'p') {
                        return 2;
                    }
                    // then exec
                    else if (c.role === 'e') {
                        return 3
                    }
                    // then other
                    else {
                        return 4;
                    }
                });
                self._quick_cohorts = sorted_cohorts.slice(0, 6);
                return self._quick_cohorts;
            }
        },
        url: function() {
            var self = this;
            return routes.profile_base + self.id + '/';
        },
        // internal to the app hash function
        hash: function() {
            var self = this;
            return '/profile/?id=' + self.id;
        },
        profile_active: function() {
            var self = this;
            return self.get('registered') || self.get('active');
        }
    });
    var SummaryProfile = Backbone.Model.extend({
        initialize: function() {
            var self = this;
            if (!self.id) self.id = self.get('username');
            if (!self.get('blurb')) {
                self.set({blurb:''});
            }
            if (!self.get('name')) {
                self.set({name:''});
            }
        },
        hash: function() {
            var self = this;
            return (self.get('active') || self.get('registered')) ? '/profile/?id=' + self.id : self.invite_hash();
        },
        invite_hash: function() {
            var self = this;
            return '/invitation/?id=' + self.id;
        },
        profile_active: function() {
            var self = this;
            return self.get('registered') || self.get('active');
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
            var self = this;
            this.id = resp.cohort.id;
            this.user_is_member = resp.cohort.user_is_member;
            this.display = resp.cohort.display;
            this.abstract = resp.cohort.abstract;
            return resp.models;
        },
        url: function() {
            return this._qs ? this.base_url + '?' + this._qs : this.base_url;
        },
        // takes an object of query args to be serialized
        // and removes illegal args
        set_qs: function(qs_args) {
            allowed_args = ['page', 'chapter', 'role', 'year', 'last_name','search', 'registered'];
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
        // private state variable
        _state: {},
        // private function that filters state when setting state
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
        // default loading function when view is loading
        loading: function(extra_content) {
            var self = this;
            if (!self.el) {
                return false;
            }
            $(self.el).html(_.template(
                self.template('loading.html'), 
                {
                    loading_image: loading_image,
                    extra_content: extra_content
                }
            ));
        },
        // render function when the view needs to asynchronously fetch data
        async_render: function(id, collection, user_callbacks) {
            var self = this;
            self.model = collection.get(id);
            if (!self.model) {
                var model_to_get = new collection.model({
                    id: id
                });
                // set up callbacks
                callbacks = {};
                callbacks.success = function(model, resp) {
                    collection.add(model_to_get);
                    self.model = model_to_get;
                    self.render();
                    if (user_callbacks['success']) {
                        user_callbacks.success(model, resp);
                    }
                }
                if (user_callbacks['error']) {
                    callbacks.error = user_callbacks.error;
                }
                self.loading();
                model_to_get.fetch(callbacks);
            }
            else {
                self.render();
            }
        },
        // default context to use when using draw function to render
        // this is a function so literals (i.e. anon) are always their
        // current value
        _default_context: function() {
            return {
                globals: GLOBALS,
                routes: routes,
                show_opt_links: show_opt_links,
                anon: anon
            }
        },
        // replace self.el with the template including the default context
        draw: function(extra_context) {
            var self = this;
            var context = _.extend(self._default_context(), extra_context);
            $(self.el).html(_.template(self.template(), context));
        }
    });

    // view for an individual profile
    var ProfileView = BaseView.extend({
        el: $('#profile .profile-content'),
        template_name: 'profile.html',
        loading: function() {
            $('#loading-widget').show();
        },
        to_cohort: function(e) {
            // pop one off the facebox stack since we don't want
            // to go back when closing the facebox
            facebox_history.pop();
            $(document).trigger('close.facebox');
        },
        render: function() {
            $('#loading-widget').hide();
            var self = this;
            self.draw({model: self.model});
            // put contents of #profile into a facebox
            facebox_history.push(location.hash);
            $.facebox({div:'#profile'});
            // set up events inside of facebox
            $('#facebox a.cohort-link').click(self.to_cohort);
        }
    });
    // view for a user to update their profile
    // renders profile form in a facebox
    var ProfileFormView = BaseView.extend({
        // require a content holder since our view will
        // be rendered in the facebox
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
            // validate input - make sure there are no errors
            var reqd = {
                'conference_goals': 'What you are excited about', 
                'conference_question': 'What you want to discuss',
                'text_interests': 'Your current interests',
                'what_now': 'What you are doing now'
            }
            var errors = [];
            for (f in reqd) {
                if (!data[f]) {
                    errors.push(reqd[f]);
                }
            }
            if (errors.length > 0) {
                messages.error('Please fill out all of the questions in the form before submitting. The following fields are missing: ' + errors.join(', '));
                return;
            }
            var id = self.model.username || self.model.id;
            // set unsaved_changes to false because even if we error after this
            // we can't get our form values back for now
            unsaved_changes = false;
            self.loading();
            if (data['avatar']) {
                // submit form through iframe
                self.$('form').ajaxSubmit({
                    beforeSubmit: function() {
                        messages.info('You are uploading a new photo - this may take some time.', {header: 'Photo uploading'});
                    },
                    success: function() {
                        delete data['avatar'];
                        messages.info('Photo uploaded successfully.', {header: 'Photo uploaded successfully.'});
                        self.model.save(data, {success: function(){
                            location.hash=self.model.hash();
                            messages.info('Your profile information has been successfully updated.', {'header': 'Profile Updated'});
                            my_profile_view.render();
                            }});
                    }});
            }
            else {
                messages.info('Updating profile...');
                self.model.save(data, {success: function(){
                    location.hash=self.model.hash();
                    messages.info('Your profile information has been successfully updated.', {'header': 'Profile Updated'});
                }});
                return false;
            }
        },
        render: function() {
            var self = this;
            // if we don't have a model, cancel
            if (!self.model) {
                return;
            }
            // since our form is in the facebox we have to do some monkey business here
            // use content_holder to render the template
            // reset el to the content_holder for draw
            self.el = $(self.content_holder);
            self.draw({model: self.model});
            $.facebox({div:self.content_holder});
            // after facebox copies the html to its own div, reset self.el to the 
            // content in the facebox. We need this to grab the form contents on submit.
            self.el = $('#facebox').find('.content').first();
            // re-delegate the events so they are attached to the facebox copy of the
            // form
            self.$('form').submit(function() { self.update_profile(); return false;});
            self.$('form textarea').each(function() {
            	$(this).focus(function() {
            		if (!$(this).data('original'))
            			$(this).data('original', $(this).val());
            	});
            	$(this).blur(function() {
            		var orig = $(this).data('original');
            		if (orig != $(this).val())
            			unsaved_changes = true;
            	});
            });
        }});
    var FiltersView = BaseView.extend({
        el: $('#filters'),
        template_name: 'filters.html',
        events: {
            'keyup #search': 'trigger_search',
            'click #registered-filter': 'refresh_hidden'
        },
        _search_queue: [],
        trigger_search: function(e) {
            var self = this;
            self._search_queue.push('event');
            setTimeout(function() {
                self._search_queue.pop();
                if (self._search_queue.length === 0) {
                    self.refresh_hidden(e);
                }
            }, 350);
        },
        refresh_hidden: function(e) {
            var self = this;
            // update hidden form vals
            self.$('#hidden-name').val(self.$('#search').val());
            self.$('#hidden-registered').val(self.$('#registered-filter').attr('checked'));
            // call change on hidden-name to refresh the search url
            self.$('#hidden-name').change();
        },
        update_from_args: function(args) {
            var self = this;
            _.each(self.$('.filter'), function(elem) {
                elem = $(elem);
                var val = args[elem.attr('name')];
                if (val) {
                    elem.val(val);
                }
                else {
                    // except roles since the default is 'm' instead of ''
                    if (elem.attr('name') === 'role') {
                        elem.val('m');
                    }
                    else {
                        elem.val('');
                    }
                }
                if (elem.attr('name') === 'last_name') {
                    if (elem.val()) {
                        name_filter_view.current_letter = elem.val();
                    }
                    else {
                        name_filter_view.current_letter = 'All';
                    }
                    name_filter_view.render();
                }
            });
            // need to reset the visible counterparts to the
            // hidden controls too
            self.$('#search').val(self.$('#hidden-name').val());
            if (self.$('#hidden-registered').val() == 'true')  {
                self.$('#registered-filter').attr('checked', 'checked');
            }
            else {
                self.$('#registered-filter').removeAttr('checked');
            }
        },
        render: function() {
            var self = this;
            self.draw();
            self.delegateEvents();
        }});

    var NewsView = BaseView.extend({
        el: $('#news'),
        template_name: 'news.html',
        render: function() {
            var self = this;
            self.draw({current_profile: current_profile});
            // load tweet this widget
            if (twitter_loaded === false) {
                var l = location.href;
                if (l.match(/^https/)) {
                    // no ssl compliant twitter button unfortunately
                    $('#twitter-share').hide();
                }
                else {
                    $.getScript('http://platform.twitter.com/widgets.js');
                }
                twitter_loaded = true;
            }
        }});

    var MyProfileView = BaseView.extend({
        el: $('#my-profile'),
        events: {
            'click a.edit-profile':'edit_profile',
            'click a#logout': 'logout'
        },
        edit_profile: function (e) {
            if (e) {
                e.preventDefault();
            }
            if (anon) {
                return
            }
            var self = this;
            profile_form_view.model = profiles.get(current_username);
            profile_form_view.render();
        },
        logout: function(e) {
            var self = this;
            self.loading();
            $.ajax({
                url: routes.logout_url,
                success: function() {
                    self.hide();
                    messages.info('You are now logged out. Hope you come back soon!', {header: 'Logged out.'});
                    anon = true;
                    news_view.render();
                    current_username = null;
                    login_view.error_message = "";
                    // XXX this should be tied to an event someday probably
                    login_view.show();
                    // go back to the home page
                    location.hash = '#/';
                },
                error: function() {
                    self.render();
                }
            });
            e.preventDefault();
        },
        template_name: 'my_profile.html',
        render: function() {
            var self = this;
            self.draw({model:self.model});
        },
        show: function() {
            var self = this;
            current_profile = new ConferenceProfile({
                id: current_username
            });
            $(self.el).show();
            self.loading();
            current_profile.fetch({success: function(){
                messages.info('Welcome ' + current_profile.get('member_profile').name + '!', {header: 'Logged in.'});
                profiles.add(current_profile);
                self.model = current_profile;
                self.render();
                // XXX bit of a hack here
                news_view.render();
                quick_cohorts_view.model = current_profile;
                quick_cohorts_view.render();
                if (!current_profile.get('active')) {
                    messages.info('Please take a moment to update your profile.', {life: 3000});
                    self.edit_profile();
                }
            }});
        }
        });
    var QuickCohortsView = BaseView.extend({
        el: $('#quick-cohorts'),
        template_name: 'quick_cohorts.html',
        render: function() {
            var self = this;
            $(self.el).html(_.template(self.template(), {model: self.model}));
        }});
    var LoginView = BaseView.extend({
        el: $('#cc-login'),
        template_name: 'cc_login.html',
        error_message: "",
        login_name: "",
        login: function() {
            var self = this;
            $.ajax({
                url: routes.login_url,
                type: 'post',
                data: self.$('form').serialize(),
                dataType: 'json',
                success: function(data) {
                    if (data.success) {
                        self.hide();
                        current_username = data.username;
                        anon = false;
                        // XXX hack - should be event driven
                        my_profile_view.show();
                        // XXX bit of a hack... oh the last minute shortcuts
                        // should be event driven
                        app.getView('Browser').render();
                    }
                    else {
                        self.error_message = data.message;
                        self.login_name = data.login_name;
                        self.render();
                    }
                }
            });
            self.loading();
        },
        render: function() {
            var self = this;
            self.draw({error_message: self.error_message, login_name: self.login_name});

            self.$('form').unbind('submit').bind('submit', function() {
                self.login();
                return false;
            });
        }});
    var GetChapterView = BaseView.extend({
        el: $('#cohort-opt-in'),
        events: {
            'click a.cohort-add-with-chapter': 'add_to_cohort_with_chapter',
            'click a.cancel': 'cancel_add'
        },
        template_name: 'get_cohort_chapter.html',
        add_to_cohort_with_chapter: function(e) {
            e.preventDefault();
            var self = this;
            var chapter = self.$('#cohort-chapter-input').val();
            if (!chapter) {
                messages.info("Please select a chapter.");
                return;
            }
            var target = $(e.target).attr('href').split('#/')[1];
            var data = JSON.stringify({chapter: $('#cohort-chapter-input').val()});
            self.loading();
            $.ajax({
                url: routes.cohort_members_base + target,
                type: 'post',
                data: data,
                contentType: 'application/json',
                success: function(resp, status) {
                    messages.info('Added to group.');
                    // if no username in the target
                    // fetch the current_profile
                    // since it is being updated
                    var no_username = /^\d+\/$/
                    if (target.match(no_username)) {
                        current_profile.fetch();
                    }
                    // XXX hack - should be event driven
                    browser_view.collection.fetch({success: function() {
                        browser_view.render();
                    }});
                },
                error: function(resp, status) {
                    messages.error('Could not add to group.');
                    self.render();
                }
            });
        },
        cancel_add: function(e) {
            $(self.el).remove();
            messages.info('Cancelled.');
        },
        render: function() {
            var self = this;
            self.el = $('#cohort-opt-in');
            self.draw({target: self.target});
            self.delegateEvents();
        }
    });
    var BrowserView = BaseView.extend({
        el: $('#browser-container'),
        events: {
            'click a.invitation': 'open_invite',
            'click a.cohort-add' : 'add_to_cohort',
            'click a.cohort-add-abstract' : 'get_chapter',
            'click a.cohort-remove' : 'remove_from_cohort',
            'click a.hide-opt-links' : 'hide_opt_links'
        },
        // attach some events that are outside of the scope of el
        bind_to_filters: function() {
            var self = this;
            $('.filter').bind('change', function() {
                self.update_filters();
            });
        },
        // XXX should be event driven some day to some thing like filter_change
        _filter_state: function(state) {
            var new_state = {};
            _.each(['chapter', 'role', 'year', 'last_name', 'page', 'search', 'registered'], function(f) {
                if (state[f]) {
                    new_state[f] = state[f];
                }
            });
            return new_state;
        },
        template_name: 'browser.html',
        update_filters: function() {
            var qs = $('#filter-controls').serialize();
            // serialize turns spaces into +
            // we don't want that
            qs = qs.replace(/\+/g, '%20');
            location.hash = '/?' + qs;
        },
        open_invite: function(e) {
            var self = this;
            e.preventDefault();
            if (anon) {
                messages.info("Please login to send an invite.", {header: 'Please login.'});
                $("#id_login_name").focus();
                return;
            }
            // dependent on having a .profile-summary div with an id of <id>-summary
            var idx = $(e.target).parents('div.profile-summary').first().attr('id').lastIndexOf('-');
            var id = $(e.target).parents('div.profile-summary').first().attr('id').substring(0, idx);
            if (!id) {
                return;
            }
            // XXX hack - should be event driven
            var view = invitation_view;
            view.async_render(id, cohort_summaries, {
                error: function () {
                    $(document).trigger('close.facebox');
                }
            });
        },
        add_to_cohort: function(e) {
            var self = this;
            e.preventDefault();
            var target = $(e.target).attr('href').split('#/')[1];
            self.loading();
            $.ajax({
                url: routes.cohort_members_base + target,
                type: 'post',
                data: '{}',
                contentType: 'application/json',
                success: function(resp, status) {
                    messages.info('Added to cohort.');
                    // if no username is provided
                    // reset the currrent profile
                    var no_username = /^\d+\/$/
                    if (target.match(no_username)) {
                        current_profile.fetch();
                    }
                    self.collection.fetch({success: function() {
                        self.render();
                    }});
                },
                error: function(resp, status) {
                    messages.error('Could not add to cohort.');
                    self.render();
                }
            });
        },
        get_chapter: function(e) {
            e.preventDefault();
            var target = $(e.target).attr('href').split('#/')[1];
            // XXX minor hack - should probably be event driven but maybe not
            get_chapter_view.target = target;
            get_chapter_view.render();
        },
        remove_from_cohort: function(e) {
            var self = this;
            e.preventDefault();
            if (!confirm('Are you sure?')) {
                return;
            }
            var target = $(e.target).attr('href').split('#/')[1];
            self.loading();
            $.ajax({
                url: routes.cohort_members_base + target,
                type: 'delete',
                success: function(resp, status) {
                    // update the current_profile if no username
                    // given when removing
                    var no_username = /^\d+\/$/
                    if (target.match(no_username)) {
                        current_profile.fetch();
                    }
                    // XXX undo - someday...
                    messages.info('Removed from group.'); // <a class="undo-removal" href="#/' + target + '">Undo</a>', {sticky: true});
                    // $('.undo-removal').click(self.add_to_cohort);
                    self.collection.fetch({success: function() {
                        self.render();
                    }});
                },
                error: function(resp, status) {
                    messages.error('Could not remove from group.');
                    self.render();
                }
            });
        },
        hide_opt_links: function(e) {
            e.preventDefault();
            show_opt_links = false;
            $('.cohort-opt-out').hide();
            $('.cohort-opt-in').hide();
        },
        render: function() {
            var self = this;
            self.draw({
                collection: self.collection
            });
            self.paginator.render();
            self.delegateEvents();
        }});
    var BrowserPaginationView = BaseView.extend({
        el: $('#paginator'),
        template_name: 'browser_paginator.html',
        render: function() {
            var self = this;
            self.el = $('.paginator');    // @@@ SEAN
            self.draw({model: self.model});
        }});
    // separate view for filter by last name
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
            self.draw({current_letter: self.current_letter});
            self.delegateEvents();
        }
    });
    var InvitationView = BaseView.extend({
        template_name: 'invitation.html',
        content_holder: '#invitation',
        el: $('#invitation'),
        send_invitation: function(e) {
            e.preventDefault();
            var self = this;
            var inputs = self.$('form').find('.invitation-input');
            var data = {};
            _.each(inputs, function(i) {
                if (i.name) data[i.name] = i.value;
            });
            data['sender'] = current_username;
            // we no longer have unsaved changes on the form
            // even if it errors below we can't get it back for now
            unsaved_changes = false;
            self.loading();
            $.ajax({url: routes.email, data:data, type:'post',
                success:function(resp) {
                    $(document).trigger('close.facebox');
                    messages.info('Your invitation has been sent.', {header: 'Invitation sent'})
                    },
                error:function(resp) {
                    $(document).trigger('close.facebox');
                    messages.error('Your invitation could not be sent.')
                }
            });
        },
        render: function() {
            var self = this;
            // since our form is in the facebox we have to do some monkey business here
            // use content_holder to render the template
            // grab the first name
            var sender_name = current_profile.get('member_profile').name.split(' ')[0];
            $(self.content_holder).html(_.template(self.template(), {model: self.model, site_url: routes.site_url, sender_name:sender_name, routes:GLOBALS.routes}));
            $.facebox({div:self.content_holder});
            // after facebox copies the html to its own div, reset self.el to the
            // content in the facebox - required to grab the form elements later
            self.el = $('#facebox').find('.content').first();
            // re-delegate the events so they are attached to the facebox copy of the
            // form
            self.$('form').bind('submit', function(e){self.send_invitation(e)});
            self.$('form textarea').each(function() {
            	$(this).focus(function() {
            		if (!$(this).data('original'))
            			$(this).data('original', $(this).val());
            	});
            	$(this).blur(function() {
            		var orig = $(this).data('original');
            		if (orig != $(this).val())
            			unsaved_changes = true;
            	});
            });
        }
    });
    /* CONTROLLER */
    var Controller = Backbone.SPWA.Controller.extend({
        routes: {
            '/profile/': 'profile',
            '/': 'browser'
        },
        views: {
            'Profile': ProfileView,
            'Browser': BrowserView
        },
        browser: function(args) {
            // when using the back or forward button we might have an open
            // facebox - pop one off the top of facebox_history since we don't
            // want to change the url and close it
            facebox_history.pop();
            $(document).trigger('close.facebox');
            var self = this;
            var view = self.getView('Browser');
            // unescape all of our arguments since some have spaces
            for (arg in args) {
                args[arg] = unescape(args[arg]);
            }
            // XXX a bit of an ugly hack here
            filters_view.update_from_args(args);
            // fetch the next page of results
            // and render only if the state has changed
            args['page'] = args['page'] || 1;
            if (!view.compare_state(args)){
                view.loading();
                params = {}
                // set our querystring
                cohort_summaries.set_qs(args);
                cohort_summaries.fetch({
                    success:function(collection, resp) {
                        browser_pagination_view.model = new Paginator(resp.pagination);
                        view.collection = collection;
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
                messages.error('Error fetching profile.');
                $(document).trigger('close.facebox');
            }}
            );
        }
    });

    app = new Controller();
    // set up an alert if users exit a box with unsaved changes
    //
    $(document).unbind('close.facebox').bind('close.facebox', function(e) {
        // check for unsaved changes and show confirm box
        if (unsaved_changes) {
            if (!confirm('You have unsaved changes on this page. Are you sure you want to exit?')) {
                return;
            }
            else {
                unsaved_changes = false;
            }
        }
        // the original close.facebox
        $(document).unbind('keydown.facebox');
        $('#facebox').fadeOut(function() {
          $('#facebox .content').removeClass().addClass('content');
          // substituting raw code
          // hideOverlay();
          // and again for skipOverlay
          // if (!skipOverlay()) {
          if (!($.facebox.settings.overlay == false || $.facebox.settings.opacity === null )) {
              $('#facebox_overlay').fadeOut(200, function(){
                  $("#facebox_overlay").removeClass("facebox_overlayBG");
                  $("#facebox_overlay").addClass("facebox_hide");
                  $("#facebox_overlay").remove();
              });
          }
          $('#facebox .loading').remove()
        })
    });
    
    // abstract away our messaging to jGrowl
    messages = {
        info: function(m, o) {
            o = o || {};
            o = _.extend({header: 'Info', theme:'confcomm-theme'}, o);
            $.jGrowl(m, o);
        },
        error: function(m, o) {
            o = o || {};
            o = _.extend({header: 'Error', theme:'error'}, o);
            $.jGrowl(m, o);
        }
    }
    // set up a global error message
    $.ajaxSetup({
        error: function(obj, status, ex) {
            messages.error('Whoops! An error occurred. We\'re looking into it :)', {header: 'Error: ' + status})
        }
    });

    /* GO TIME */
    $(function() {

        hash_history = ['#/'];
        facebox_history = [];
        profiles = new ProfileStore();
        cohort_summaries = new SummaryStore();
        cohort_summaries.base_url = routes.cohorts_base;
        // don't render this guy just wait - wait until we've fetched the cohort_summaries
        // and rendered the first BrowserView on page load
        browser_pagination_view = new BrowserPaginationView;
        browser_view = new BrowserView;
        browser_view.collection = cohort_summaries;
        /* Load all the default templates */
        get_chapter_view = new GetChapterView;
        news_view = new NewsView;
        news_view.loading();
        quick_cohorts_view = new QuickCohortsView;
        // anon gets the default hard-coded html
        if (!anon) {
            quick_cohorts_view.loading();
        }
        // quick_cohorts_view.render();
        filters_view = new FiltersView;
        filters_view.loading();
        filters_view.render();
        name_filter_view = new NameFilterView;
        name_filter_view.render();
        // XXX: fix this - a bit of an ugly hack.
        browser_view.bind_to_filters();
        invitation_view = new InvitationView;
        // show the my_profile view if the user is logged in
        profile_form_view = new ProfileFormView;
        login_view = new LoginView;
        my_profile_view = new MyProfileView();
        if (!anon) {
            my_profile_view.show();
        }
        // show the login view if the user is not logged in
        else {
            $(login_view.el).show();
            login_view.loading();
            login_view.render();
            news_view.render();
        }
        if (!location.hash) {
            location.hash = '#/';
        }
        else {
            $(window).hashchange();
        }
        // bind some events to facebox to help with nav
        // change back to the last hash when we close a facebox
        // if appropriate
        $(document).bind('close.facebox', function() {
            // get rid of the top most history entry (the facebox url)
            if (facebox_history.pop() !== undefined) {
                hash_history.pop();
                // pop the last entry off of the hash_history and set location.hash to it
                // hashchange() will fire and push this value back onto the stack
                var next_hash = hash_history.pop();
                // sometimes close.facebox fires twice - causing weird behaviour
                // like undefined hashes. if there is no hash on the stack then
                // set location.hash to home
                if (next_hash) {
                    location.hash = next_hash;
                }
                else {
                    location.hash = '#/'
                }
            }
        });
        // keep track of the last hash so we can return to it after
        // closing a facebox
        $(window).hashchange(function() {
            hash_history.push(location.hash);
            while( hash_history.length > 4) {
                hash_history.shift();
            }
        });
    });
})(CONFCOMM_GLOBALS);
