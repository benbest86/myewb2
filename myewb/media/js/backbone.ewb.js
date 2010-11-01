/*
 * modified backbone code for MyEWB
 */
;(function() {
  // Helper function to get a URL from a Model or Collection as a property
  // or as a function.
  var getUrl = function(object) {
    if (!(object && object.url)) throw new Error("A 'url' property or function must be specified");
    return _.isFunction(object.url) ? object.url() : object.url;
  };
  // Map from CRUD to HTTP for our default `Backbone.sync` implementation.
  var methodMap = {
    'create': 'POST',
    'update': 'PUT',
    'delete': 'DELETE',
    'read'  : 'GET'
  };
  Backbone.sync = function(method, model, success, error) {
    var sendModel = method === 'create' || method === 'update';
    // changing data to remove the {'model':} namespace on the data - required for
    // piston.
    var data = sendModel ? JSON.stringify(model) : {};
    var type = methodMap[method];
    if (Backbone.emulateHttp && (type === 'PUT' || type === 'DELETE')) {
      data._method = type;
      type = 'POST';
    }
    // kill any pending requests that haven't completed
    if (model.pending_request && model.pending_request.readyState != 4) {
        model.pending_request.abort();
    }
    model.pending_request = $.ajax({
      url       : getUrl(model),
      type      : type,
      data      : data,
      dataType  : 'json',
      success   : success,
      error     : error,
      contentType : 'application/json'
    });
  };
  })();
