from django.http import HttpResponseForbidden, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

class owner_required(object):
    """
    Checks to see whether the user is an owner or an admin.
    """
    def __init__(self, object_model):
        self.object_model = object_model

    def __call__(self, f):
        def newf(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated():
                # deny access - would set this to redirect
                # to a custom template eventually
                return render_to_response('denied.html', context_instance=RequestContext(request))
            elif user.is_superuser: # or is_staff
                return f(request, *args, **kwargs)
            object = kwargs.get('object', None)
            if object is None:
                # custom manager method get_from_view_args is required!!
                object = self.object_model.objects.get_from_view_args(*args, **kwargs)
                if object is None:
                    raise Http404('No %s matches the given query.' % self.object_model._meta.object_name)
            # NOTE: if the object does not have an is_owner property, we ALLOW access by default.
            # Is this the best default?
            if not hasattr(object, 'is_owner') or object.is_owner(user):
                # add object to list of kwargs because we had to hit
                # the database to get it - no point in doing that
                # again in the view function
                kwargs['object'] = object
                return f(request, *args, **kwargs)
            else:
                # deny access
                return render_to_response('denied.html', context_instance=RequestContext(request))
        return newf
