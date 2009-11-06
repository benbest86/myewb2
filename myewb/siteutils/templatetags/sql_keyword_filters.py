from django import template
register = template.Library()

try:
    import pygments
    import pygments.lexers
    from pygments.formatters import TerminalFormatter
except ImportError:
    pygments = None

@register.filter("colorsql")
def colorsql(value):
  if pygments:
    lexer = {'mysql': pygments.lexers.MySqlLexer}['mysql']
    return pygments.highlight(value, lexer(), TerminalFormatter())
  else:
    return value
