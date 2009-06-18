# core.py
#
# Copyright (c) 2009 Stephen Day
#
# This module is part of Creoleparser and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#

import re

import genshi.builder as bldr

__docformat__ = 'restructuredtext en'

escape_char = '~'
esc_neg_look = '(?<!' + re.escape(escape_char) + ')'
esc_to_remove = re.compile(''.join([r'(?<!',re.escape(escape_char),')',re.escape(escape_char),r'(?!([ \n]|$))']))
place_holder_re = re.compile(r'<<<(-?\d+?)>>>')


class Parser(object):
    
    def __init__(self,dialect, method='xhtml', strip_whitespace=False, encoding='utf-8'):
        """Constructor for Parser objects

        :parameters:
          dialect
            Usually created using :func:`creoleparser.dialects.create_dialect`
          method
            This value is passed to Genshies Steam.render(). Possible values
            include ``xhtml``, ``html``, ``xml``, and ``text``.
          strip_whitespace
            This value is passed to Genshies Steam.render().
          encoding
            This value is passed to Genshies Steam.render().
            
        """
    
        if isinstance(dialect,type):
            self.dialect = dialect()
        else:
            # warning message here in next major version
            self.dialect = dialect
        self.method = method
        self.strip_whitespace = strip_whitespace
        self.encoding=encoding

    def generate(self,text,element_store=None,context='block', environ=None):
        """Returns a Genshi Stream.

        :parameters:
          text
            The text to be parsed.
          context
            This is useful for marco development where (for example) supression
            of paragraph tags is desired. Can be 'inline', 'block', or a list
            of WikiElement objects (use with caution).
          element_store
            Internal dictionary that's passed around a lot ;)
          environ
            This can be any type of object. It will be passed to ``macro_func``
            unchanged (for a description of ``macro_func``, see
            :func:`~creoleparser.dialects.create_dialect`).
            
        """
        
        if element_store is None:
            element_store = {}
        if not isinstance(context,list):
            if context == 'block':
                top_level_elements = self.dialect.block_elements
                do_preprocess = True
            elif context == 'inline':
                top_level_elements = self.dialect.inline_elements
                do_preprocess = False
        else:
            top_level_elements = context
            do_preprocess = False

        if do_preprocess:
            text = preprocess(text,self.dialect)

        return bldr.tag(fragmentize(text,top_level_elements,element_store, environ)).generate()


    def render(self, text, element_store=None, context='block', environ=None, **kwargs):
        """Returns the final output string (e.g., xhtml). See
        :meth:`~creoleparser.core.Parser.generate` for named parameter descriptions.

        Left over keyword arguments (``kwargs``) will be passed to Genshi's Stream.render() method,
        overriding the corresponding attributes of the Parser object. For more infomation on Streams,
        see the `Genshi documentation <http://genshi.edgewall.org/wiki/Documentation/streams.html#serialization-options>`_.
        
        """

        if element_store is None:
            element_store = {}
        kwargs.setdefault('method',self.method)
        kwargs.setdefault('encoding',self.encoding)
        if kwargs['method'] != "text":
            kwargs.setdefault('strip_whitespace',self.strip_whitespace)
        stream = self.generate(text, element_store, context, environ)
        return stream.render(**kwargs)

    def __call__(self,text, **kwargs):
        """Wrapper for the render method. Returns final output string.

        """

        return self.render(text, **kwargs)



class ArgParser(object):
    """Creates a callable object for parsing macro argument strings

    >>> from dialects import creepy20_base
    >>> my_parser = ArgParser(dialect=creepy20_base())
    >>> my_parser(" one two foo='three' boo='four' ")
    (['one', 'two'], {'foo': 'three', 'boo': 'four'})
 
    A parser returns a two-tuple, the first item being a list of positional
    arguments and the second a dictionary of keyword arguments. Argument
    values are either strings or lists.
    
    """
    
    def __init__(self,dialect, convert_implicit_lists=True,
                 key_func=None, illegal_keys=(), convert_unicode_keys=True):
        """Constructor for ArgParser objects

        :parameters:
          convert_unicode_keys
            If *True*, keys will be converted using ``str(key)`` before being
            added to the output dictionary. This allows the dictionary to be
            safely passed to functions using the special ``**`` form (i.e.,
            ``func(**kwargs)``).
          dialect
            Usually created using :func:`~creoleparser.dialects.creepy10_base`
            or :func:`~creoleparser.dialects.creepy20_base`
          convert_implicit_lists
            If *True*, all implicit lists will be converted to strings
            using ``' '.join(list)``. "Implicit" lists are created when
            positional arguments follow keyword arguments
            (see :func:`~creoleparser.dialects.creepy10_base`). 
          illegal_keys
            A tuple of keys that will be post-fixed with an underscore if found
            during parsing. 
          key_func
            If supplied, this function will be used to transform the names of
            keyword arguments. It must accept a single positional argument.
            For example, this can be used to make keywords case insensitive:
            
            >>> from string import lower
            >>> from dialects import creepy20_base
            >>> my_parser = ArgParser(dialect=creepy20_base(),key_func=lower)
            >>> my_parser(" Foo='one' ")
            ([], {'foo': 'one'})
            
        """
    
        self.dialect = dialect()
        self.convert_implicit_lists = convert_implicit_lists
        self.key_func = key_func
        self.illegal_keys = illegal_keys
        self.convert_unicode_keys = convert_unicode_keys


    def __call__(self, arg_string, **kwargs): 
        """Parses the ``arg_string`` returning a two-tuple 

        Keyword arguments (``kwargs``) can be used to override the corresponding
        attributes of the ArgParser object (see above). However, the
        ``dialect`` attribute **cannot** be overridden.
        
        """
        
        kwargs.setdefault('convert_implicit_lists',self.convert_implicit_lists)
        kwargs.setdefault('key_func',self.key_func)
        kwargs.setdefault('illegal_keys',self.illegal_keys)
        kwargs.setdefault('convert_unicode_keys',self.convert_unicode_keys)

        return self._parse(arg_string,**kwargs)


    def _parse(self,arg_string, convert_implicit_lists, key_func, illegal_keys,
               convert_unicode_keys):
        
        frags = fragmentize(arg_string,self.dialect.top_elements,{},{})
        positional_args = []
        kw_args = {}
        for arg in frags:
           if isinstance(arg,tuple):
             k, v  = arg
             if convert_unicode_keys:
                 k = str(k)
             if key_func:
                 k =  key_func(k)
             if k in illegal_keys:
                 k = k + '_'
             if k in kw_args:
                if isinstance(v,list):
                   try:
                      kw_args[k].extend(v)
                   except AttributeError:
                      v.insert(0,kw_args[k])
                      kw_args[k] = v
                elif isinstance(kw_args[k],list):
                   kw_args[k].append(v)
                else:
                   kw_args[k] = [kw_args[k], v]
                kw_args[k] = ImplicitList(kw_args[k])
             else:
                kw_args[k] = v
             if isinstance(kw_args[k],ImplicitList) and convert_implicit_lists:
                 kw_args[k] = ' ' .join(kw_args[k])
           else:
             positional_args.append(arg)

        return (positional_args, kw_args)
        



def fragmentize(text,wiki_elements, element_store, environ, remove_escapes=True):

    """Takes a string of wiki markup and outputs a list of genshi
    Fragments (Elements and strings).

    This recursive function, with help from the WikiElement objects,
    does almost all the parsing.

    When no WikiElement objects are supplied, escapes are removed from
    ``text`` (except if remove_escapes=True)  and it is
    returned as-is. This is the only way for recursion to stop.

    :parameters:
      text
        the text to be parsed
      wiki_elements
        list of WikiElement objects to be searched for
      environ
        object that may by used by macros
      remove_escapes
        If False, escapes will not be removed
    
    """

    while wiki_elements:
        # If the first supplied wiki_element is actually a list of elements, \
        # search for all of them and match the closest one only.
        if isinstance(wiki_elements[0],(list,tuple)):
            x = None
            mos = None
            for element in wiki_elements[0]:
                mo = element.regexp.search(text)
                if mo:
                    if x is None or mo.start() < x:
                        x,wiki_element,mos = mo.start(),element,[mo]
        else:
            wiki_element = wiki_elements[0]
            mos = [mo for mo in wiki_element.regexp.finditer(text)]
             
        if mos:
            frags = wiki_element._process(mos, text, wiki_elements, element_store, environ)
            break
        else:
            wiki_elements = wiki_elements[1:]

    # remove escape characters 
    else: 
        if remove_escapes:
            text = esc_to_remove.sub('',text)
        frags = fill_from_store(text,element_store)
        
    return frags


def fill_from_store(text,element_store):
    frags = []
    mos = place_holder_re.finditer(text)
    start = 0
    for mo in mos:
        if mo.start() > start:
            frags.append(text[start:mo.start()])
        frags.append(element_store.get(mo.group(1),
                       mo.group(1).join(['<<<','>>>'])))
        start = mo.end()
    if start < len(text):
        frags.append(text[start:])
    return frags


def preprocess(text, dialect):
    """This should generally be called before fragmentize().

    :parameters:
      text
        text to be processsed.
      dialect
        a ``Dialect`` object.
    """
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    return text


def chunk(text, blank_lines, hard_elements, limit):
    """Safely breaks large Creole documents into a list of smaller
    ones (strings) - DEPRECIATED
    """
    hard_spans = []
    for e in hard_elements:
        for mo in e.regexp.finditer(text):
            hard_spans.append(mo.span())

    hard_chars = []
    for x,y in hard_spans:
        hard_chars.extend(range(x,y))
    hard_chars = set(hard_chars)

    chunks = []
    start = 0
    for i in range(len(blank_lines)/limit):
        for mo in blank_lines[limit/2 + i*limit:limit*3/2+i*limit:10]:
            if mo.start() not in hard_chars:
                chunks.append(text[start:mo.start()])
                start = mo.end()
                break
    chunks.append(text[start:])
    
    return chunks


class ImplicitList(list):
    """This class marks argument lists as implicit"""
    pass

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

