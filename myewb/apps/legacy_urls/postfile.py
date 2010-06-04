from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404

from attachments.models import Attachment
from group_topics.models import GroupTopic
from threadedcomments.models import ThreadedComment

import settings
import urllib

urlpatterns = patterns('legacy_urls.postfile',
    url(r'^(?P<post_id>\d+)/(?P<filename>.*)$', 'findfile'),
    )

def findfile(request, post_id, filename):
    # find the post... whether it's a topic or comment
    try:
        topic = GroupTopic.objects.get(id=post_id)
        parent = topic.parent_group
    except:
        try:
            topic = ThreadedComment.objects.get(id=post_id)
            parent = topic.content_object.parent_group
        except:
            raise Http404

    # check visibility
    if not parent.is_visible(request.user):
        return render_to_response('denied.html', context_instance=RequestContext(request))
        
    # get content type info
    ctype = ContentType.objects.get_for_model(topic)
    
    # build path to attachment
    filename = urllib.unquote_plus(filename)
    path = "attachments/" + ctype.app_label.lower() + "_" + ctype.model.lower() + "/" + str(post_id) + "/" + filename
    
    # ensure the attachment exists, and return it 
    try:
        file = Attachment.objects.get(content_type=ctype,
                                      object_id=post_id,
                                      attachment_file=path)
    
        return HttpResponseRedirect("%s%s" % (settings.STATIC_URL, file.attachment_file.name))
    except:
        raise Http404
