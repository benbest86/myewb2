import os

from django import template
from django.conf import settings
from siteutils.helpers import fix_encoding

register = template.Library()

_abbrevs = [
    (1<<50L, ' PB'),
    (1<<40L, ' TB'),
    (1<<30L, ' GB'),
    (1<<20L, ' MB'),
    (1<<10L, ' kB'),
    (1, ' bytes')
    ]

def bytestr(size, precision=1):
    """
    Taken from http://mail.python.org/pipermail/python-list/2008-August/143772.html
    Author rkmr.em at gmail.com 
    Returns a string representing the greek/metric suffix of a size
    """
    if size==1:
        return '1 byte'
    for factor, suffix in _abbrevs:
        if size >= factor:
            break

    float_string_split = `size/float(factor)`.split('.')
    integer_part = float_string_split[0]
    decimal_part = float_string_split[1]
    if int(decimal_part[0:precision]):
        float_string = '.'.join([integer_part, decimal_part[0:precision]])
    else:
        float_string = integer_part
    return float_string + suffix

def filesize_for_filename(attachment_path):
    """
    Takes the attachment path and gets the associated file size in bytes.
    The filesize is formatted using the bytestr method and returned as a string.
    """

    path = os.path.join(settings.MEDIA_ROOT, attachment_path)
    path = fix_encoding(path)
    size = os.path.getsize(path)
    formatted_size = bytestr(size)
    
    return {
            'STATIC_URL': settings.STATIC_URL,
            'filesize': formatted_size,
            }
register.inclusion_tag('filesize_tags/filesize.html')(filesize_for_filename)

@register.filter(name='filesize')
def filesize(value):
    try:
        value = int(value)
    except:
        return ""
    
    return bytestr(value)
