# -*- coding: utf-8 -*-

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='truncate_head')
def truncate_head(value, character_count, ellipsis=True):
  try:
    length = int(character_count)
  except ValueError: # Invalid literal for int().
    return value # Fail silently.

  if len(value) < length:
    return value

  # if we're already on a word boundary, done
  if value[-(length+1)] == " ":
    result = value[-length:].strip()
  else:
    original_length = len(value)
    delta = (original_length-length)
    first_space = value.find(" ", delta, original_length)
  
    if first_space == -1:
      length = delta
    elif first_space > length:
      length = first_space

    result = value[length:].strip()
  
  if ellipsis:
    return u"…" + result
  else:
    return result
  
@register.filter(name='truncate_tail')
def truncate_tail(value, character_count, ellipsis=True):
  try:
    length = int(character_count)
  except ValueError: # Invalid literal for int().
    return value # Fail silently.

  if len(value) < length:
    return value

  # if we're already on a word boundary, done
  if value[length] == " ":
    result = value[:length].strip()
  else:
    last_space = value.rfind(" ", 0, length)
    if last_space != -1 and last_space <= length:
      length = last_space

    result = value[:length].strip()

  if ellipsis:
    return result + u"…"
  else:
    return result


@register.filter(name='truncate_middle')
def truncate_middle(value, character_count):
  try:
    length = int(character_count)
  except ValueError: # Invalid literal for int().
    return value # Fail silently.

  if len(value) < length:
    return value

  half_size = length / 2
  first_half = truncate_tail(value, half_size, False)
  last_half = truncate_head(value, half_size, False)
  
  return  u"%s…%s" % (first_half, last_half)

@register.filter(name='truncatechars')
def truncatechars(value, character_count, truncate_type='tail'):
    """
    truncatechars(value, character_count, truncate_type='tail')
    
    Returns a copy of the string containg only character_counr characters. Try to break on word boundaries.

    Arguments: Number of characters to truncate after, truncation type (tail/head/middle).
    """
    
    if truncate_type not in ["head", "tail", "middle"]:
      raise ValueError
    
    try:
      length = int(character_count)
    except ValueError: # Invalid literal for int().
      return value # Fail silently.

    if len(value) < length:
      return value

    if truncate_type == "tail":
      return truncate_tail(value, character_count)

    elif truncate_type == "head":
      return truncate_head(value, character_count)

    elif truncate_type == "middle":
      return truncate_middle(value, character_count)
    

truncatechars.is_safe = True
truncate_head.is_safe = True
truncate_tail.is_safe = True
truncate_middle.is_safe = True
