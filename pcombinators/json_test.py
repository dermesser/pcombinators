#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example on how to write a JSON parser.

@author: lbo
"""

from combinators import *
from primitives import *

JString = Last(Skip(String('"')) + NoneInSet('"') + Skip(String('"')))

wrapl = lambda l: [l]

class Value(Parser):
    """Bare-bones, but fully functioning, JSON parser. Doesn't like escaped quotes.

    Example:
        >>> Value().parse(ParseState(my_json_string))
        ({'id': 1.0,
          'name': 'Foo',
          'price': 123.0,
          'tags': ['Bar', 'Eek'],
          'stock': {'warehouse': 300.0, 'retail': 20.0}},
         ParseState({"id":1,"name":"Foo","price":123,"tags":["Bar","Eek"],"stock":{"warehouse":300, "retail":20}}<>))
    """
    def parse(self, st):
        return Last(Skip(Whitespace()) + (Dict | List | JString | Float()) + Skip(Whitespace())).parse(st)

# We moved out all the piece parsers out of functions to reduce allocation overhead.
# It improves performance by roughly 2x.

# LISTS

# An entry is any value.
entry = Value()
# A mid entry is a value followed by a comma.
midentry = entry + Skip(String(','))
# A list is a [, followed by mid entries, followed by a final entry, and a
# closing ]. The list is wrapped in a list to prevent merging in other parsers.
List = (Skip(String('[')) +
        Repeat(midentry, -1) +
        entry +
        Skip(String(']'))) >> wrapl # Wrap list inside another list to protect it from flattening.

# DICTS

# A separator is whitespace, a colon, and more whitespace (Whitespace() also accepts empty string)
separator = Skip((Whitespace() + String(":") + Whitespace()))
# Entry is a String followed by a separator and a value. Wrap the value in a list to prevent merging.
# The two-element list is converted to a tuple.
entry = (JString + separator + (Value() >> wrapl)) >> (lambda l: tuple(l))
# A mid entry is followed by a comma.
midentry = Last(entry + Skip(String(',') + Skip(Whitespace())))
# A dict is a {, followed by entries, followed by a final entry, followed by a closing }
dct = Flatten(
        Skip(String("{")) + ((Repeat(midentry, -1) + entry)) + Skip(String("}")))
# Convert the list of tuples into a dict.
Dict = dct >> dict
