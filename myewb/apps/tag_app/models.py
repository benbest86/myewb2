from django.db import models
from django.utils.translation import ugettext_lazy as _

from tagging.models import Tag

class TagAlias(models.Model):
    """A simple class to hold aliased tags.  The idea is to link similar tags:
    if someone types "hso" for example, it should be linked to "school outreach"
    which is the proper term.
    """
    tag = models.ForeignKey(Tag, related_name="aliased_tags", verbose_name=_('tag'))
    alias = models.TextField(_('alias'), blank=False)

    def __unicode__(self):
        return "%s => %s" % (self.alias, self.tag)
    