//     (c) 2010 Chris Pickett
//     Backbone.SPWA may be freely distributed under the MIT license.
//     For all details and documentation:
//     http://github.com/bunchesofdonald/backbone-spwa

(function(){
  
  // Module namespace
  Backbone.SPWA = {};
  
  // Current version of the module
  Backbone.SPWA.VERSION = '0.1.0';
  
  // For the purposes of Backbone.SPWA, jQuery and Underscore own the '$' and '_' variables respectively.
  var _ = this._;
  var $ = this.jQuery;
  
  // Backbone.SPWA.View
  // -------------

  // TODO:
  // Add hide (and/or destroy), show and sub-views.
  Backbone.SPWA.View = Backbone.View.extend({
    subviews : {},
    
    show : function() {
      this.render();
      $(this.el).show();
    },
    
    hide : function() {
      $(this.el).hide(); 
    },
    
    destroy : function() {
      $(this.el).remove();
    },
    
    _configure : function(options) {
      Backbone.View.prototype._configure.call(this, {});
    }
  });
  
  // Backbone.SPWA.Controller
  // ------------------------
  // A subclass of this will essentially be your application.
  
  Backbone.SPWA.Controller = function(options) {
    if(!this.routes) { this.routes = {}; }
    if(!this.views) { this.views = {}; }
    this._configure(options)
    Backbone.SPWA.InitializeViews(this.views);
    if(this.initialize) { this.initialize(); }
  };
  
  _.extend(Backbone.SPWA.Controller.prototype, Backbone.Events, {
    getView : function(view_name) {
      return this.views[view_name];
    },
    
    hideAll : function() {
      _.each(this.views,function(view){
        if(view.hide) { view.hide(); }
      });
    },
    
    _configure : function(options) {
      Backbone.SPWA.bindHashChange(this);
    },
    
    _router : function(hash) {
      var args = this._getArguments(hash);
      
      var method = this.routes[args._route];
      if(this[method]) { this[method](args); }
    },
    
    _getArguments : function(hash) {
      if(hash.charAt(0) == '#') { hash = hash.substr(1); }
      var args_kv = {};
      
      var args = hash.split('?');
      args_kv['_route'] = args.shift();
      if(args_kv['_route'] == '') { args_kv['_route'] = '/'; }
      
      if(args.length > 0) {
        args = args[0].split('&');
        
        _.each(args,function(arg){
          var parts = arg.split('=');
          args_kv[parts[0]] = parts[1];
        });
      }
      
      return args_kv;
    }
  });
  
  Backbone.SPWA.Controller.handleEvents = Backbone.View.handleEvents;
  
  Backbone.SPWA.InitializeViews = function(view_list) {
    _.each(view_list, function(view,view_name,views){
      if(view instanceof Backbone.View) {} // do nothing
      else { views[view_name] = new view(); }
    });
  }
  
  Backbone.SPWA.Controller.extend = Backbone.SPWA.View.extend;
  
  // Backbone.SPWA.bindHashChange
  // ----------------------------
  // We're using jQuery ba-hashchange to watch for hashchange events
  // Overwrite this method with your own if you want to use another 
  // hashchange event, write your own or if you don't want to respond
  // to hashchanges.
  
  Backbone.SPWA.bindHashChange = function(controller) {
    $(window).hashchange(function() { controller._router(location.hash); });
  }
  
})();