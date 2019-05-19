# pcombinators

Working on parser combinators for Python, in an understandable manner. I've
always been fascinated by them, so I wanted to try if I can implement them :-)

For example:

```python

import pcombinators.combinators as c

st = c.ParseState('Hello, World!')
p = c.String('Hello') + c.Regex('([,.]) +') + c.String('World') + c.Regex('[.,?!]')

p.parse(st)
# >> (['Hello', ',', 'World', '!'], ParseState(Hello, World!<>))<Paste>

(Float() + String(" ") + NonEmptyString()).parse(ParseState('1.22 abc'))
# >> ([1.22, ' ', 'abc'], ParseState(1.22 abc<>))

def upper(s):
    return s.upper()

# You can transform parser results with the >> (right shift) operator, and
# repeat parsers with the * (multiplication) operator.

# Parse two non-whitespace strings, converting them to uppercase, and a float,
# multiplying the latter by 2.
(
 (NonEmptyString() >> upper) * 2 +
 (Float() >> (lambda f: f * 2))
).parse(ParseState("hello world 2.2"))
# >> (['HELLO', 'WORLD', 4.4], ParseState(hello world 2.2<>))
```
