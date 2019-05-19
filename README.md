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
```
