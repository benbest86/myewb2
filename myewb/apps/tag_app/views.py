from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from group_topics.models import GroupTopic
from tagging.models import Tag, TaggedItem

def tags(request, tag, template_name='tags/index.html'):
    tag = get_object_or_404(Tag, name=tag)
    
    # Get topics that match this tag
    # filter to visible topics first
    topics = GroupTopic.objects.visible(request.user)

    topictags = TaggedItem.objects.get_by_model(topics, tag)

    return render_to_response(template_name, {
        'tag': tag,
        'topictags': topictags,
    }, context_instance=RequestContext(request))

    # NOTE there was a lot more stuff here before, checking tags against
    # blogs, wikis, photos, etc... check the svn history if you want to 
    # recover and use that eventually!
    # but for now, it's only possible to tag posts. (GroupPosts in particular)
    
